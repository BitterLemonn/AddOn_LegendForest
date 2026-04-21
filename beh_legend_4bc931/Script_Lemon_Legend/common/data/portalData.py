# -*- coding: utf-8 -*-

import json
import math
from collections import defaultdict


class SpatialGrid(object):
    """3D空间网格，用于优化传送门的空间查询"""

    def __init__(self, gridSize=100):
        self.gridSize = gridSize
        self.grid = defaultdict(list)  # type: dict[tuple, list[PortalData]]

    def getGridKey(self, pos):
        """获取位置对应的网格键"""
        x, y, z = pos
        return (
            int(x // self.gridSize),
            int(y // self.gridSize),
            int(z // self.gridSize)
        )

    def add(self, portalData):
        """添加传送门到空间网格"""
        gridKey = self.getGridKey(portalData.pos)
        self.grid[gridKey].append(portalData)

    def remove(self, portalData):
        """从空间网格中移除传送门"""
        gridKey = self.getGridKey(portalData.pos)
        if gridKey in self.grid and portalData in self.grid[gridKey]:
            self.grid[gridKey].remove(portalData)
            if not self.grid[gridKey]:  # 如果网格为空，删除该网格
                del self.grid[gridKey]

    def findNearest(self, pos, maxDistance):
        """在指定范围内查找最近的传送门"""
        gridKey = self.getGridKey(pos)
        # 计算需要搜索的网格半径
        radiusGrids = math.ceil(maxDistance / self.gridSize) + 1

        minDistanceSq = maxDistance * maxDistance
        nearestPortal = None

        # 搜索周围的网格
        for neighborKey in self.getNeighborKeys(gridKey, radiusGrids):
            if neighborKey in self.grid:
                for portalData in self.grid[neighborKey]:
                    distanceSq = self.calculateDistanceSquared(pos, portalData.pos)
                    if distanceSq < minDistanceSq:
                        minDistanceSq = distanceSq
                        nearestPortal = portalData

        return nearestPortal

    @staticmethod
    def calculateDistanceSquared(pos1, pos2):
        """计算两点间距离的平方（避免开方运算）"""
        return (pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2 + (pos1[2] - pos2[2]) ** 2

    @staticmethod
    def getNeighborKeys(gridKey, radiusGrids=1):
        """获取周围网格的键，用于范围查询"""
        x, y, z = gridKey
        neighbors = []
        radiusGrids = int(radiusGrids)
        for dx in range(-radiusGrids, radiusGrids + 1):
            for dy in range(-radiusGrids, radiusGrids + 1):
                for dz in range(-radiusGrids, radiusGrids + 1):
                    neighbors.append((x + dx, y + dy, z + dz))
        return neighbors


class PortalData(object):
    """传送门数据类"""

    def __init__(self, direction, pos, dm, toDm, toPos=None):
        self.pos = tuple(pos) if isinstance(pos, list) else pos  # 确保位置是元组，提高哈希效率
        self.dm = dm
        self.toDm = toDm
        self.toPos = tuple(toPos) if isinstance(toPos, list) and toPos is not None else toPos
        self.direction = direction

    def __str__(self):
        return json.dumps(self.__dict__, ensure_ascii=False)

    def __eq__(self, other):
        """重写相等性比较，用于在列表中查找和移除"""
        if not isinstance(other, PortalData):
            return False
        return (self.pos == other.pos and
                self.dm == other.dm and
                self.toDm == other.toDm)

    def __hash__(self):
        """添加哈希支持，提高查找效率"""
        return hash((self.pos, self.dm, self.toDm))

    def getDistanceTo(self, pos):
        """计算到指定位置的距离"""
        return math.sqrt(SpatialGrid.calculateDistanceSquared(self.pos, pos))

    def getDistanceSquaredTo(self, pos):
        """计算到指定位置的距离平方（避免开方运算）"""
        return SpatialGrid.calculateDistanceSquared(self.pos, pos)

    def isBidirectional(self):
        """检查是否为双向传送门"""
        return self.toPos is not None

    def toDict(self):
        """转换为字典格式"""
        return self.__dict__
