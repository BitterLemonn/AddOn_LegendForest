# -*- coding: utf-8 -*-
from ...portal.config import PortalFrameConfig
from ...utils import serverUtils
from ...utils.commonUtils import FormatColorStr
from ...utils.serverUtils import compFactory


class PortalValidator(object):
    """传送门验证器"""

    def __init__(self, playerId, dimensionId):
        self.playerId = playerId
        self.dimensionId = dimensionId
        self.blockComp = compFactory.CreateBlockInfo(playerId)
        self.gameComp = compFactory.CreateGame(playerId)

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
                    return False, None
                return False, pos

        return True, None

    def showError(self, errorMsg, title, pos=None):
        """显示错误信息"""
        self.gameComp.SetOnePopupNotice(self.playerId, errorMsg, FormatColorStr.RED + title)
        if pos:
            serverUtils.createParticle("legend_forest:error_block", pos, self.playerId)
