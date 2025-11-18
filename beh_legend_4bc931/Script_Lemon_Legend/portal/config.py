# -*- coding: utf-8 -*-
class PortalFrameConfig(object):
    """传送门框架配置类"""

    # 框架方块类型
    FRAME_BLOCK = "legend_forest:log_shimmer"
    MIDDLE_BLOCK = "legend_forest:rimmed_log_shimmer"
    CORE_BLOCK = "legend_forest:log_shimmer_core"

    # 传送门方块类型
    OVERWORLD_PORTAL = "legend_forest:forest_portal"
    FOREST_PORTAL = "legend_forest:overworld_portal"

    FOREST_DIMENSION_ID = 340654
    OVERWORLD_DIMENSION_ID = 0

    PORTAL_BLOCK = frozenset([
        OVERWORLD_PORTAL,
        FOREST_PORTAL
    ])

    @classmethod
    def isChangeByLegendPortal(cls, fromDimensionId, toDimensionId):
        """判断传送是否由神话之森引起"""
        return (toDimensionId == cls.FOREST_DIMENSION_ID) or \
            (fromDimensionId == cls.FOREST_DIMENSION_ID and toDimensionId == cls.OVERWORLD_DIMENSION_ID)

    @staticmethod
    def getPortalBlock(dimensionId):
        """根据维度ID获取传送门方块类型"""
        return PortalFrameConfig.OVERWORLD_PORTAL if dimensionId == 0 else PortalFrameConfig.FOREST_PORTAL

    @staticmethod
    def isPortalBlock(blockName):
        """检查是否为传送门方块"""
        return "legend_forest:" in blockName and "portal" in blockName

    @staticmethod
    def isSafeBlock(blockName):
        """检查是否为安全方块（不会破坏传送门的方块）"""
        # 复用已定义的常量，避免重复定义
        return blockName in [
            PortalFrameConfig.FRAME_BLOCK,
            PortalFrameConfig.MIDDLE_BLOCK,
            PortalFrameConfig.CORE_BLOCK
        ]

    @staticmethod
    def getDirectionFromAux(aux):
        """根据aux值获取传送门方向"""
        if aux == 1:
            return "x"
        elif aux == 2:
            return "z"
        else:
            return None

    @staticmethod
    def getAdjacentPositions(pos, direction):
        """获取传送门方块的相邻关键位置（用于破坏检测）"""
        x, y, z = pos

        if direction == "x":
            return [
                (x - 1, y, z), (x + 1, y, z),  # 左右
                (x, y + 1, z), (x, y - 1, z)  # 上下
            ]
        elif direction == "z":
            return [
                (x, y, z - 1), (x, y, z + 1),  # 前后
                (x, y + 1, z), (x, y - 1, z)  # 上下
            ]
        else:
            return []

    @staticmethod
    def getCenterPosFromPortalBlock(portalBlockPos, direction):
        """从传送门方块位置反推核心位置"""
        x, y, z = portalBlockPos

        # 传送门方块的y坐标范围是 centerY+1 到 centerY+3
        # 所以核心的y坐标是传送门方块的y-1, y-2, 或 y-3
        # 我们需要检查多个可能的核心位置
        possibleCenters = []

        if direction == "x":
            # x方向的传送门方块可能在 centerX-1, centerX, centerX+1
            for dx in [-1, 0, 1]:
                for dy in [1, 2, 3]:
                    possibleCenters.append((x - dx, y - dy, z))
        else:  # direction == "z"
            # z方向的传送门方块可能在 centerZ-1, centerZ, centerZ+1
            for dz in [-1, 0, 1]:
                for dy in [1, 2, 3]:
                    possibleCenters.append((x, y - dy, z - dz))

        return possibleCenters

    @staticmethod
    def getFramePositions(centerPos, direction):
        """获取框架位置列表"""
        x, y, z = centerPos

        if direction == "x":
            framePos = [
                (x - 1, y, z), (x + 1, y, z),
                (x - 1, y + 4, z), (x + 1, y + 4, z),
                (x - 2, y + 1, z), (x + 2, y + 1, z),
                (x - 2, y + 3, z), (x + 2, y + 3, z)
            ]
            middlePos = [
                (x + 2, y + 2, z), (x - 2, y + 2, z), (x, y + 4, z)
            ]
            emptyPos = [
                (x - 1, y + 1, z), (x + 1, y + 1, z),
                (x - 1, y + 2, z), (x + 1, y + 2, z),
                (x - 1, y + 3, z), (x + 1, y + 3, z),
                (x, y + 1, z), (x, y + 2, z), (x, y + 3, z)
            ]
        else:  # direction == "z"
            framePos = [
                (x, y, z - 1), (x, y, z + 1),
                (x, y + 4, z - 1), (x, y + 4, z + 1),
                (x, y + 1, z - 2), (x, y + 1, z + 2),
                (x, y + 3, z - 2), (x, y + 3, z + 2)
            ]
            middlePos = [
                (x, y + 2, z - 2), (x, y + 2, z + 2), (x, y + 4, z)
            ]
            emptyPos = [
                (x, y + 1, z - 1), (x, y + 1, z + 1),
                (x, y + 2, z - 1), (x, y + 2, z + 1),
                (x, y + 3, z - 1), (x, y + 3, z + 1),
                (x, y + 1, z), (x, y + 2, z), (x, y + 3, z)
            ]

        return framePos, middlePos, emptyPos
