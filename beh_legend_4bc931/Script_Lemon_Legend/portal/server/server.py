# -*- coding: utf-8 -*-
from .destroyer import PortalDestroyer
from .portalService import PortalManagerService
from .validator import PortalValidator
from ..manager.portalManager import PortalManager
from ... import modConfig
from ...QuModLibs.Modules.Services.Server import BaseService
from ...QuModLibs.Server import *
from ...data.biomeData import BiomesEnum
from ...logging import logging
from ...modConfig import PORTAL_DATA_KEY
from ...portal.config import PortalFrameConfig
from ...utils import serverUtils, commonUtils
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
                    .SetOnePopupNotice(playerId, "请在传送门核心上使用月结晶", FormatColorStr.RED + "传送门开启失败")
                return

            self.createPortalByFrame(playerId, pos, dimensionId)

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

    @BaseService.Listen("OnEntityInsideBlockServerEvent")
    def onEntityInsideBlock(self, data):
        """玩家进入传送门方块 添加传送门检测组件"""
        blockName = data.get("blockName")
        entityId = data.get("entityId")
        if blockName in PortalFrameConfig.PORTAL_BLOCK and Entity(entityId).IsPlayer:
            portalService = PortalManagerService.access()  # type: PortalManagerService
            portalService.addInPortalBlockPlayer(entityId)

    @BaseService.Listen(Events.DimensionChangeServerEvent)
    def onDimensionChangeServerEvent(self, data):
        """玩家传送维度时 检测是否使用传送门传送"""
        data = Events.DimensionChangeServerEvent(data)
        if Entity(data.playerId).IsPlayer and \
                PortalFrameConfig.isChangeByLegendPortal(data.fromDimensionId, data.toDimensionId):
            fromPos = data.fromX, data.fromY, data.fromZ
            portalService = PortalManagerService.access()  # type: PortalManagerService
            portalComp = portalService.changeDimension(data.playerId, data.fromDimensionId, fromPos)

    @BaseService.Listen(Events.DimensionChangeFinishServerEvent)
    def onDimensionChangeFinish(self, data):
        data = Events.DimensionChangeFinishServerEvent(data)
        if PortalFrameConfig.isChangeByLegendPortal(data.fromDimensionId, data.toDimensionId):
            portalService = PortalManagerService.access()  # type: PortalManagerService
            if portalService.isPlayerNeedCheckPos(data.playerId):
                self.findAndTeleportToPortal(data.playerId, data.toDimensionId, data.toPos)
                return

    def findAndTeleportToPortal(self, playerId, toDimensionId, originPos):
        """寻找传送点并传送玩家
        
        流程:
        1. 查找来源维度传送门的toPos(已绑定的目标传送门位置)
        2. 如果有toPos,直接传送到该位置
        3. 如果没有toPos,查找目标群系 -> 传送到高空 -> 等待地形加载 -> 创建传送门 -> 传送玩家
        """
        posComp = compFactory.CreatePos(playerId)
        gameComp = compFactory.CreateGame(levelId)

        # 获取来源维度和位置
        portalService = PortalManagerService.access()  # type: PortalManagerService
        fromDimensionId, fromPos = portalService.getPlayerFromDimAndPos(playerId)

        # 查找来源维度的传送门
        fromPortalData = self.portalManager.findPortalData(fromPos, fromDimensionId)

        # 如果来源传送门已经绑定了目标传送门位置,直接传送
        if fromPortalData and fromPortalData.toPos:
            teleportPos = fromPortalData.toPos
            self._teleportToGround(playerId, teleportPos)
            return

        # 确定目标位置
        targetPos = originPos
        if toDimensionId == 340654:
            # 传送到神话维度,查找目标群系
            biomePos = serverUtils.searchNearestTargetBiome(originPos, toDimensionId, BiomesEnum.getShimmerBiomes())
            if biomePos:
                targetPos = (biomePos[0], 65, biomePos[1])
            else:
                logging.warning("未找到目标群系,使用默认位置")

        # 传送到高空等待地形加载
        highPos = (targetPos[0], targetPos[1] + 10000, targetPos[2])
        posComp.SetPos(highPos)

        # 定时器检查地形加载
        def waitingLoadingTerrain():
            chunkComp = serverApi.GetEngineCompFactory().CreateChunkSource(levelId)
            blockComp = compFactory.CreateBlockInfo(levelId)

            if chunkComp.CheckChunkState(toDimensionId, targetPos):
                # 寻找地面高度
                groundPos = self._searchGround(targetPos, toDimensionId)
                # 创建传送门并传送玩家
                self._createNewPortal(groundPos, toDimensionId, fromDimensionId, fromPos, playerId)
            else:
                # 继续等待地形加载
                gameComp.AddTimer(1, waitingLoadingTerrain)

        gameComp.AddTimer(1, waitingLoadingTerrain)

    def createPortalByFrame(self, playerId, pos, dimensionId):
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
            if errorPos:
                validator.showError("框架内含有非空气方块", "传送门框架搭建不正确", errorPos)
            return

        # 生成传送门
        self.generatePortal(playerId, pos, dimensionId, validDirection, validator)

    def generatePortal(self, playerId, pos, dimensionId, direction, validator):
        """生成传送门"""
        # 消耗物品
        serverUtils.decreaseItem(playerId, 1)
        serverUtils.swing(playerId)

        # 添加传送门数据,只设置目标维度ID,toPos在实际传送时创建目标传送门后设置
        if not self.portalManager.findPortalData(pos, dimensionId):
            # 计算本传送门的传送出口位置（传送门前方一格）
            selfTeleportPos = self._calculateTeleportPos(pos, direction)
            # 根据当前维度确定目标维度
            targetDim = 340654 if dimensionId == 0 else 0
            self.portalManager.addPortalData(
                direction=direction,
                pos=pos,
                dm=dimensionId,
                toDm=targetDim,
                toPos=None  # 首次创建时不设置toPos,等待目标维度传送门创建后再绑定
            )
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
        serverUtils.playSoundAll("block.end_portal.spawn", pos, playerId)

    def _createNewPortal(self, targetPos, toDimensionId, fromDimensionId, fromPos, playerId, retryCount=0):
        """在目标位置创建新传送门"""
        # 重试上限
        if retryCount > 5:
            logging.error("传送门生成失败,超过重试次数")
            gameComp = compFactory.CreateGame(levelId)
            gameComp.SetNotifyMsg("神话之森: 传送门生成失败", FormatColorStr.RED)
            # 传送玩家到安全位置
            safePos = (targetPos[0], 65, targetPos[2] + 2)
            self._teleportToGround(playerId, safePos)
            # 清理空间防止窒息
            blockComp = compFactory.CreateBlockInfo(levelId)
            blockComp.SetBlockNew(safePos, {"name": "minecraft:air"}, dimensionId=toDimensionId, oldBlockHandling=1)
            blockComp.SetBlockNew((safePos[0], safePos[1] + 1, safePos[2]), {"name": "minecraft:air"},
                                  dimensionId=toDimensionId, oldBlockHandling=1)
            return

        # 传送门位置(核心方块在targetPos,传送门在z-2位置)
        direction = "x"
        centerPos = (targetPos[0], targetPos[1], targetPos[2] - 2)
        blockComp = compFactory.CreateBlockInfo(levelId)

        # 获取框架位置
        framePosList, middlePosList, emptyPosList = PortalFrameConfig.getFramePositions(centerPos, direction)

        # 清理传送门前后空间
        self._clearPortalSpace(centerPos, direction, toDimensionId, blockComp)

        # 构建框架方块
        for framePos in framePosList:
            blockComp.SetBlockNew(framePos, {"name": PortalFrameConfig.FRAME_BLOCK, "aux": 0},
                                  dimensionId=toDimensionId, oldBlockHandling=1, updateNeighbors=False)

        # 构建中间装饰方块
        for middlePos in middlePosList:
            blockComp.SetBlockNew(middlePos, {"name": PortalFrameConfig.MIDDLE_BLOCK, "aux": 0},
                                  dimensionId=toDimensionId, oldBlockHandling=1, updateNeighbors=False)

        # 放置核心方块
        blockComp.SetBlockNew(centerPos, {"name": PortalFrameConfig.CORE_BLOCK, "aux": 0},
                              dimensionId=toDimensionId, oldBlockHandling=1, updateNeighbors=False)

        # 放置传送门方块
        portalBlock = PortalFrameConfig.getPortalBlock(toDimensionId)
        auxValue = 1 if direction == "x" else 2
        for emptyPos in emptyPosList:
            blockComp.SetBlockNew(emptyPos, {"name": portalBlock, "aux": auxValue},
                                  dimensionId=toDimensionId, oldBlockHandling=1, updateNeighbors=False)

        # 防止传送门生成在空中 - 生成平台
        self._createPortalPlatform(centerPos, toDimensionId, blockComp)

        # 传送玩家到传送门前方
        teleportPos = self._calculateTeleportPos(centerPos, direction)
        self._teleportToGround(playerId, teleportPos)

        # 添加传送门数据并建立双向绑定
        self._bindPortalData(centerPos, toDimensionId, fromPos, fromDimensionId, direction)

        # 播放音效
        serverUtils.playSoundAll("block.end_portal.spawn", centerPos, playerId)

    @staticmethod
    def _calculateTeleportPos(portalCenterPos, direction):
        """计算传送门的目标传送位置（传送门前方一格的中心位置）"""
        x, y, z = portalCenterPos

        # 传送到传送门前方一格，y+1是传送门的底部
        if direction == "x":
            # x方向传送门，向z轴正方向传送（传送门前方）
            return x, y + 1, z + 2
        else:  # direction == "z"
            # z方向传送门，向x轴正方向传送（传送门前方）
            return x + 2, y + 1, z

    @staticmethod
    def _clearPortalSpace(centerPos, direction, dimensionId, blockComp):
        """清理传送门前后方向的空间"""
        x, y, z = commonUtils.getIntPos(centerPos)

        # 传送门的高度范围是 y+1 到 y+3 (3格高)
        # 传送门的宽度范围是 -1 到 +1 (3格宽)
        # 需要在前后各清理一层，深度为2格

        if direction == "x":
            # x方向的传送门，清理z方向的前后空间
            # 传送门在x轴上的范围是 x-1 到 x+1
            for clearZ in [z - 1, z - 2, z + 1, z + 2]:  # 前后各2格
                for clearX in range(x - 1, x + 2):  # x方向3格宽
                    for clearY in range(y + 1, y + 4):  # y方向3格高
                        blockComp.SetBlockNew((clearX, clearY, clearZ),
                                              {"name": "minecraft:air", "aux": 0},
                                              dimensionId=dimensionId, oldBlockHandling=1)
        else:  # direction == "z"
            # z方向的传送门，清理x方向的前后空间
            # 传送门在z轴上的范围是 z-1 到 z+1
            for clearX in [x - 1, x - 2, x + 1, x + 2]:  # 前后各2格
                for clearZ in range(z - 1, z + 2):  # z方向3格宽
                    for clearY in range(y + 1, y + 4):  # y方向3格高
                        blockComp.SetBlockNew((clearX, clearY, clearZ),
                                              {"name": "minecraft:air", "aux": 0},
                                              dimensionId=dimensionId, oldBlockHandling=1)

    @staticmethod
    def _createPortalPlatform(centerPos, dimensionId, blockComp):
        """在传送门底部创建平台，防止生成在空中或液体中"""
        x, y, z = commonUtils.getIntPos(centerPos)
        bottomBlock = blockComp.GetBlockNew((x, y - 1, z), dimensionId)["name"]

        # 如果底部是空气、水或岩浆，生成平台
        if bottomBlock in ["minecraft:air", "minecraft:water", "minecraft:lava"]:
            platformPosList = [
                (x - 1, y - 1, z), (x + 1, y - 1, z),
                (x, y - 1, z - 1), (x, y - 1, z + 1),
                (x, y - 1, z),
                (x - 1, y - 1, z - 1), (x + 1, y - 1, z - 1),
                (x - 1, y - 1, z + 1), (x + 1, y - 1, z + 1)
            ]
            for platformPos in platformPosList:
                blockComp.SetBlockNew(platformPos, {"name": "legend_forest:root_shimmer", "aux": 0},
                                      dimensionId=dimensionId, oldBlockHandling=1, updateNeighbors=False)

    @staticmethod
    def _searchGround(pos, dimensionId):
        """搜索地面位置，避免危险方块"""
        blockComp = compFactory.CreateBlockInfo(levelId)
        height = blockComp.GetTopBlockHeight((pos[0], pos[2]), dimensionId)
        if not height:
            height = pos[1]

        targetPos = (pos[0], height + 1, pos[2])

        # 向下搜索80格，找到安全位置
        for i in range(80):
            checkY = targetPos[1] - i
            if checkY < 0:
                break
            block = blockComp.GetBlockNew((targetPos[0], checkY, targetPos[2]), dimensionId)["name"]
            if block in modConfig.DANGEROUS_BLOCKS:
                bottomBlock = blockComp.GetBlockNew((targetPos[0], checkY - 1, targetPos[2]), dimensionId)["name"]
                if bottomBlock not in modConfig.DANGEROUS_BLOCKS:
                    targetPos = (targetPos[0], checkY, targetPos[2])
                    break

        # 返回位置高度(传送门核心位置)
        return targetPos[0], targetPos[1], targetPos[2]

    def _bindPortalData(self, newPortalPos, newPortalDim, oldPortalPos, oldPortalDim, direction):
        """绑定传送门数据，建立双向映射关系"""
        # 计算传送出口位置
        newTeleportPos = self._calculateTeleportPos(newPortalPos, direction)
        oldTeleportPos = self._calculateTeleportPos(oldPortalPos, direction)

        # 1. 添加新传送门数据，指向旧传送门
        self.portalManager.addPortalData(
            direction=direction,
            pos=newPortalPos,
            dm=newPortalDim,
            toDm=oldPortalDim,
            toPos=oldTeleportPos
        )

        # 2. 更新旧传送门数据，指向新传送门
        oldPortalData = self.portalManager.findPortalData(oldPortalPos, oldPortalDim)
        if oldPortalData:
            spatialGrid = self.portalManager.getSpatialGrid(oldPortalDim)
            spatialGrid.remove(oldPortalData)
            oldPortalData.toPos = newTeleportPos
            oldPortalData.toDm = newPortalDim
            spatialGrid.add(oldPortalData)

        # 保存数据
        dataComp = compFactory.CreateExtraData(levelId)
        dataComp.SetExtraData(PORTAL_DATA_KEY, self.portalManager.serialize())

    @staticmethod
    def _teleportToGround(playerId, targetPos, retryCount=0):
        """传送玩家到指定位置，带重试机制"""
        posComp = compFactory.CreatePos(playerId)
        if not posComp.SetFootPos(targetPos) and retryCount < 5:
            # 传送失败，重试
            logging.warning("玩家传送失败，1秒后重试")
            gameComp = compFactory.CreateGame(levelId)
            gameComp.AddTimer(1, PortalServerService._teleportToGround, playerId, targetPos, retryCount + 1)
        elif retryCount >= 5:
            logging.error("玩家传送失败，超过重试次数: {}".format(playerId))
        else:
            logging.debug("玩家传送成功: {}".format(targetPos))

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
