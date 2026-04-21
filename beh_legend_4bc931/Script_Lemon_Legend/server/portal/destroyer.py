# -*- coding: utf-8 -*-
from Script_Lemon_Legend.QuModLibs.Server import levelId
from Script_Lemon_Legend.common.config.modConfig import PORTAL_DATA_KEY
from Script_Lemon_Legend.common.config.portalFrameConfig import PortalFrameConfig
from Script_Lemon_Legend.common.config.portalManager import PortalManager
from Script_Lemon_Legend.common.utils.logging import logging
from Script_Lemon_Legend.server.utils.serverUtils import compFactory


class PortalDestroyer(object):
    """传送门破坏检测器"""

    def __init__(self, dimensionId, portalManager=None):
        self.dimensionId = dimensionId
        self.blockComp = compFactory.CreateBlockInfo(dimensionId)
        self.portalManager = portalManager or PortalManager()

    def checkPortalIntegrity(self, portalBlockPos, changedPos, newBlockName, direction):
        """检查传送门完整性

        Args:
            portalBlockPos: 传送门方块的位置
            changedPos: 变化的位置
            newBlockName: 新方块的名称
            direction: 传送门方向
        """
        # 尝试查找传送门数据（使用附近查找，因为portalBlockPos可能不是核心位置）
        portalData = self.portalManager.findPortalData(portalBlockPos, self.dimensionId)

        # 如果找不到，尝试从传送门方块位置反推核心位置
        if not portalData:
            possibleCenters = PortalFrameConfig.getCenterPosFromPortalBlock(portalBlockPos, direction)
            for testCenter in possibleCenters:
                portalData = self.portalManager.findPortalData(testCenter, self.dimensionId)
                if portalData:
                    break

        if not portalData:
            logging.warning("PortalDestroyer: 完整性检查时未找到传送门数据")
            return False

        adjacentPositions = PortalFrameConfig.getAdjacentPositions(portalBlockPos, direction)

        # 检查变化的位置是否是关键位置
        if changedPos in adjacentPositions:
            # 检查新方块是否为安全方块
            if not PortalFrameConfig.isSafeBlock(newBlockName):
                return False

        return True

    def destroyPortal(self, portalBlockPos, direction=None):
        """销毁传送门

        Args:
            portalBlockPos: 传送门方块的位置
            direction: 传送门方向，如果为None则尝试查找
        """
        # 如果没有提供方向，尝试从传送门数据中获取
        portalData = None
        centerPos = None

        if direction is None:
            # 直接查找附近的传送门数据
            portalData = self.portalManager.findPortalData(portalBlockPos, self.dimensionId)
            if portalData:
                direction = portalData.direction
                centerPos = portalData.pos

        # 如果仍然没有方向信息，无法销毁
        if direction is None:
            logging.error("PortalDestroyer: 无法确定传送门方向，无法销毁")
            return

        # 如果没有找到传送门数据，尝试从传送门方块位置反推核心位置
        if centerPos is None:
            possibleCenters = PortalFrameConfig.getCenterPosFromPortalBlock(portalBlockPos, direction)
            # 尝试每个可能的核心位置
            for testCenter in possibleCenters:
                portalData = self.portalManager.findPortalData(testCenter, self.dimensionId)
                if portalData:
                    centerPos = portalData.pos
                    break

            # 如果还是没找到，使用第一个可能的核心位置
            if centerPos is None and possibleCenters:
                centerPos = possibleCenters[0]
                logging.warning("PortalDestroyer: 未找到传送门数据，使用推测的核心位置: {}".format(centerPos))

        # 获取所有传送门方块位置
        _, _, emptyPositions = PortalFrameConfig.getFramePositions(centerPos, direction)

        # 将所有传送门方块替换为空气
        for pos in emptyPositions:
            blockInfo = self.blockComp.GetBlockNew(pos, self.dimensionId)
            # 只替换传送门方块
            if PortalFrameConfig.isPortalBlock(blockInfo.get("name", "")):
                self.blockComp.SetBlockNew(
                    pos, {"name": "minecraft:air", "aux": 0}, 1, self.dimensionId, updateNeighbors=False
                )

        # 从传送门管理器中移除数据（使用核心位置）
        if portalData or centerPos:
            self.portalManager.removePortalData(centerPos, self.dimensionId)
            # 保存数据到世界
            dataComp = compFactory.CreateExtraData(levelId)
            dataComp.SetExtraData(PORTAL_DATA_KEY, self.portalManager.serialize())
