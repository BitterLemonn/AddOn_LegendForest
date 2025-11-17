# -*- coding: utf-8 -*-
from .destroyer import PortalDestroyer
from .validator import PortalValidator
from ...QuModLibs.Modules.Services.Server import BaseService
from ...QuModLibs.Server import *
from ...manager.portalManager import PortalManager
from ...modConfig import PORTAL_DATA_KEY
from ...portal.config import PortalFrameConfig
from ...utils import serverUtils
from ...utils.commonUtils import FormatColorStr
from ...utils.serverUtils import compFactory


@BaseService.Init
class PortalServerService(BaseService):

    def __init__(self):
        BaseService.__init__(self)
        self.portalManager = PortalManager()
        self.commandComp = compFactory.CreateCommand(levelId)

        # 读取世界数据
        comp = compFactory.CreateExtraData(levelId)
        portalData = comp.GetExtraData(PORTAL_DATA_KEY)
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

            if blockName != PortalFrameConfig.CORE_BLOCK:
                compFactory.CreateGame(levelId) \
                    .SetOnePopupNotice(playerId, "请在传送门核心上使用月结晶",
                                       FormatColorStr.RED + "传送门开启失败")
                return

            self.createPortal(playerId, pos, dimensionId)

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
            # aux值无效，直接销毁传送门（不传递方向，让destroyPortal自己查找）
            destroyer = PortalDestroyer(dimensionId, self.portalManager)
            destroyer.destroyPortal(blockPos)
            return

        # 检查传送门完整性
        destroyer = PortalDestroyer(dimensionId, self.portalManager)
        if not destroyer.checkPortalIntegrity(blockPos, changePos, toBlockName, direction):
            destroyer.destroyPortal(blockPos, direction)

    @BaseService.Listen()

    @BaseService.Listen(Events)

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
            dataComp = compFactory.CreateExtraData(levelId)
            dataComp.SetExtraData(PORTAL_DATA_KEY, self.portalManager.serialize())

        # 放置传送门方块
        portalBlock = PortalFrameConfig.getPortalBlock(dimensionId)
        auxValue = 1 if direction == "x" else 2
        _, _, emptyPosList = PortalFrameConfig.getFramePositions(pos, direction)

        for emptyPos in emptyPosList:
            validator.blockComp.SetBlockNew(emptyPos, {"name": portalBlock, "aux": auxValue},
                                            dimensionId=dimensionId, updateNeighbors=False)

        # 播放音效
        self.commandComp.SetCommand("/playsound block.end_portal.spawn {} {} {}".format(pos[0], pos[1], pos[2]))

    @staticmethod
    def handleFrameError(validator, allErrors):
        """处理框架错误"""
        # 选择错误较少的方向
        xErrors = allErrors.get("x", [])
        zErrors = allErrors.get("z", [])
        minErrors = xErrors if len(xErrors) <= len(zErrors) else zErrors

        if minErrors:
            errorPos = minErrors[0]["pos"]
            errorPos = (float(errorPos[0]), float(errorPos[1]), float(errorPos[2]))
            errorBlock = minErrors[0]["block"]
            blockName = validator.gameComp.GetChinese("tile.{}.name".format(errorBlock))
            errorMsg = "可能的位置: {} 应为 {}".format(errorPos, blockName)
            validator.showError(errorMsg, "传送门框架搭建不正确", errorPos)
