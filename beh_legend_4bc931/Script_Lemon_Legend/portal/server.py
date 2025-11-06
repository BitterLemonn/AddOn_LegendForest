# -*- coding: utf-8 -*-
from .config import PortalFrameConfig
from ..QuModLibs.Modules.Services.Server import BaseService
from ..QuModLibs.Server import *
from ..logging import logging
from ..manager.portalManager import PortalManager
from ..modConfig import PORTAL_DATA_KEY
from ..utils import serverUtils


class PortalValidator(object):
    """传送门验证器"""

    def __init__(self, playerId, dimensionId):
        self.playerId = playerId
        self.dimensionId = dimensionId
        self.blockComp = serverApi.GetEngineCompFactory().CreateBlockInfo(playerId)
        self.gameComp = serverApi.GetEngineCompFactory().CreateGame(playerId)

    def validateFrame(self, centerPos, direction):
        """验证传送门框架"""
        framePos, middlePos, _ = PortalFrameConfig.getFramePositions(centerPos, direction)
        errors = []

        # 检查框架方块
        for pos in framePos:
            if self.blockComp.GetBlockNew(pos, self.dimensionId)["name"] != PortalFrameConfig.FRAME_BLOCK:
                errors.append({"pos": pos, "block": PortalFrameConfig.FRAME_BLOCK})

        # 检查中间方块
        for pos in middlePos:
            if self.blockComp.GetBlockNew(pos, self.dimensionId)["name"] != PortalFrameConfig.MIDDLE_BLOCK:
                errors.append({"pos": pos, "block": PortalFrameConfig.MIDDLE_BLOCK})

        return len(errors) == 0, errors

    def validateEmpty(self, centerPos, direction):
        """验证传送门内部是否为空"""
        _, _, emptyPos = PortalFrameConfig.getFramePositions(centerPos, direction)

        for pos in emptyPos:
            blockName = self.blockComp.GetBlockNew(pos, self.dimensionId)["name"]
            if blockName != "minecraft:air":
                # 如果已经是传送门方块，允许通过
                if blockName in [PortalFrameConfig.OVERWORLD_PORTAL, PortalFrameConfig.FOREST_PORTAL]:
                    continue
                return False, pos

        return True, None

    def showError(self, errorMsg, title, pos=None):
        """显示错误信息"""
        self.gameComp.SetOnePopupNotice(self.playerId, errorMsg, serverApi.GenerateColor("RED") + title)
        if pos:
            serverUtils.createParticle("legend_forest:error_block", pos, self.playerId)


@BaseService.Init
class PortalServerService(BaseService):

    def __init__(self):
        BaseService.__init__(self)
        self.portalManager = PortalManager()

        # 读取世界数据
        comp = serverApi.GetEngineCompFactory().CreateExtraData(levelId)
        portalData = comp.GetExtraData(PORTAL_DATA_KEY)
        logging.debug("PortalServerService: 读取传送门数据: {}".format(portalData))
        self.portalManager.deserialize(portalData)

    @BaseService.Listen(Events.ItemUseOnAfterServerEvent)
    def onItemUseOn(self, data):
        playerId = data.get("entityId")
        itemDict = data.get("itemDict")
        pos = (data.get("x"), data.get("y"), data.get("z"))  # 修复pos变量
        dimensionId = data.get("dimensionId")
        blockName = data.get("blockName")

        if itemDict.get("itemName") == "legend_forest:moon_crystal" and \
                dimensionId in [0, 928808, 340654] and \
                serverUtils.UsingCooldownServerService.access().setCooldown(playerId):

            logging.debug("blockName:{}".format(blockName))
            if blockName != PortalFrameConfig.CORE_BLOCK:
                serverApi.GetEngineCompFactory().CreateGame(levelId) \
                    .SetOnePopupNotice(playerId, "请在传送门核心上使用月结晶",
                                       serverApi.GenerateColor("RED") + "传送门开启失败")
                return

            self.createPortal(playerId, pos, dimensionId)

    def createPortal(self, playerId, pos, dimensionId):
        """创建传送门的主要逻辑"""
        validator = PortalValidator(playerId, dimensionId)

        # 尝试两个方向的门框检测
        directions = ["x", "z"]
        validDirection = None
        allErrors = {}

        for direction in directions:
            isValid, errors = validator.validateFrame(pos, direction)
            if isValid:
                validDirection = direction
                break
            allErrors[direction] = errors

        if validDirection is None:
            self.handleFrameError(validator, allErrors)
            return

        # 检测中空
        isEmpty, errorPos = validator.validateEmpty(pos, validDirection)
        if not isEmpty:
            validator.showError("框架内含有非空气方块", "传送门框架搭建不正确", errorPos)
            return

        # 生成传送门
        self.generatePortal(playerId, pos, dimensionId, validDirection, validator)

    def generatePortal(self, playerId, pos, dimensionId, direction, validator):
        """生成传送门"""
        # 消耗物品
        serverUtils.decreaseItem(playerId, 1)
        Call(playerId, "Swing")

        # 添加传送门数据
        if not self.portalManager.findPortalData(pos, dimensionId):
            self.portalManager.addPortalData(direction=direction, pos=pos, dm=dimensionId, toDm=928808)
            # 保存数据到世界
            dataComp = serverApi.GetEngineCompFactory().CreateExtraData(levelId)
            dataComp.SetExtraData(PORTAL_DATA_KEY, self.portalManager.serialize())

        # 放置传送门方块
        portalBlock = PortalFrameConfig.getPortalBlock(dimensionId)
        auxValue = 1 if direction == "x" else 2
        _, _, emptyPosList = PortalFrameConfig.getFramePositions(pos, direction)

        for emptyPos in emptyPosList:
            validator.blockComp.SetBlockNew(emptyPos, {"name": portalBlock, "aux": auxValue},
                                            dimensionId=dimensionId, updateNeighbors=False)

        # 播放音效（可选）
        # Call("*", "PlaySound", {"soundName": "block.end_portal.spawn", "pos": pos})

    @staticmethod
    def handleFrameError(validator, allErrors):
        """处理框架错误"""
        # 选择错误较少的方向
        xErrors = allErrors.get("x", [])
        zErrors = allErrors.get("z", [])
        minErrors = xErrors if len(xErrors) <= len(zErrors) else zErrors

        if minErrors:
            errorPos = minErrors[0]["pos"]
            errorBlock = minErrors[0]["block"]
            blockName = validator.gameComp.GetChinese("tile.{}.name".format(errorBlock))
            errorMsg = "可能的位置: {} 应为 {}".format(errorPos, blockName)
            validator.showError(errorMsg, "传送门框架搭建不正确", errorPos)

    @BaseService.Listen(Events.BlockNeighborChangedServerEvent)
    def onBlockNeighborChangedServerEvent(self, data):
        """传送门方块邻接变化事件处理"""
        blockPos = (data["posX"], data["posY"], data["posZ"])
        changePos = (data["neighborPosX"], data["neighborPosY"], data["neighborPosZ"])
        dimensionId = data["dimensionId"]
        blockName = data["blockName"]
        aux = data["auxValue"]
        toBlockName = data["toBlockName"]

        # 检查是否为传送门方块
        if not PortalFrameConfig.isPortalBlock(blockName):
            return

        # 获取传送门方向
        direction = PortalFrameConfig.getDirectionFromAux(aux)
        if direction is None:
            # aux值无效，直接销毁传送门
            destroyer = PortalDestroyer(dimensionId, self.portalManager)
            destroyer.destroyPortal(blockPos)
            return

        # 检查传送门完整性
        destroyer = PortalDestroyer(dimensionId, self.portalManager)
        if not destroyer.checkPortalIntegrity(blockPos, changePos, toBlockName):
            destroyer.destroyPortal(blockPos)


class PortalDestroyer(object):
    """传送门破坏检测器"""

    def __init__(self, dimensionId, portalManager=None):
        self.dimensionId = dimensionId
        self.blockComp = serverApi.GetEngineCompFactory().CreateBlockInfo(dimensionId)
        self.portalManager = portalManager or PortalManager()

    def checkPortalIntegrity(self, portalPos, changedPos, newBlockName):
        """检查传送门完整性"""
        # 获取传送门数据
        portalData = self.portalManager.findPortalData(portalPos, self.dimensionId)
        if not portalData:
            return False

        direction = portalData.direction
        adjacentPositions = PortalFrameConfig.getAdjacentPositions(portalPos, direction)

        # 检查变化的位置是否是关键位置
        if changedPos in adjacentPositions:
            # 检查新方块是否为安全方块
            if not PortalFrameConfig.isSafeBlock(newBlockName):
                return False

        return True

    def destroyPortal(self, portalPos):
        """销毁传送门"""
        # 获取传送门数据以确定方向和范围
        portalData = self.portalManager.findPortalData(portalPos, self.dimensionId)
        if not portalData:
            return

        direction = portalData.direction
        _, _, emptyPositions = PortalFrameConfig.getFramePositions(portalPos, direction)

        # 将所有传送门方块替换为空气
        for pos in emptyPositions:
            self.blockComp.SetBlockNew(pos, {"name": "minecraft:air", "aux": 0}, 1, self.dimensionId)

        # 从传送门管理器中移除数据
        self.portalManager.removePortalData(portalPos, self.dimensionId)
        # 保存数据到世界
        dataComp = serverApi.GetEngineCompFactory().CreateExtraData(levelId)
        dataComp.SetExtraData(PORTAL_DATA_KEY, self.portalManager.serialize())
