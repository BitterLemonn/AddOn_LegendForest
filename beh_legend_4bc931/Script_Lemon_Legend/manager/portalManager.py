# -*- coding: utf-8 -*-
import math
import pickle

from ..data.portalData import SpatialGrid, PortalData
from ..logging import logging


# 单例模式
class PortalManager(object):
    INSTANCE = None
    _initialized = False

    def __new__(cls):
        if cls.INSTANCE is None:
            cls.INSTANCE = super(PortalManager, cls).__new__(cls)
        return cls.INSTANCE

    def __init__(self):
        # 防止重复初始化
        if not PortalManager._initialized:
            self.portalDict = {}  # type: dict[int, list[PortalData]]
            self.spatialGrids = {}  # 每个维度一个空间网格 type: dict[int, SpatialGrid]
            self._targetDistance = 50
            PortalManager._initialized = True

    def getSpatialGrid(self, dm):
        """获取指定维度的空间网格，如果不存在则创建"""
        if dm not in self.spatialGrids:
            self.spatialGrids[dm] = SpatialGrid()
        return self.spatialGrids[dm]

    # 找到距离最近的在self._targetDistance以内的传送门（优化版本）
    def findPortalData(self, pos, dm):
        """使用空间网格优化的最近邻查询"""
        if dm not in self.spatialGrids:
            return None

        spatialGrid = self.spatialGrids[dm]
        return spatialGrid.findNearest(pos, self._targetDistance)

    def addPortalData(self, direction, pos, dm, toDm, toPos=None):
        """添加传送门数据，同时更新空间索引"""
        portalData = self.findPortalData(pos, dm)
        if portalData:
            logging.debug("PortalManager: 附近已有传送门: {}".format(portalData))
            if toPos is not None:
                # 需要从空间网格中移除旧数据并添加新数据
                spatialGrid = self.getSpatialGrid(dm)
                spatialGrid.remove(portalData)
                portalData.toPos = toPos
                spatialGrid.add(portalData)
                logging.debug("PortalManager: 更新传送门信息: {}".format(portalData))
            return

        portalData = PortalData(direction=direction, pos=pos, dm=dm, toDm=toDm, toPos=toPos)

        # 添加到字典中
        if self.portalDict.get(dm, None):
            self.portalDict[dm].append(portalData)
        else:
            self.portalDict[dm] = [portalData]

        # 添加到空间网格中
        spatialGrid = self.getSpatialGrid(dm)
        spatialGrid.add(portalData)

        logging.debug("PortalManager: 添加传送门: {}".format(portalData))

        # 添加双向传送门
        if toPos is not None:
            self.addPortalData(direction=direction, pos=toPos, dm=toDm, toDm=dm, toPos=pos)

    def serialize(self):
        """序列化传送门数据"""
        return pickle.dumps(self.portalDict)

    def deserialize(self, data):
        """反序列化传送门数据并重建空间索引"""
        if data is None:
            # 如果没有数据，使用空字典
            self.portalDict = {}
        else:
            self.portalDict = pickle.loads(data)

        self.spatialGrids = {}  # 清空现有的空间网格

        # 重建空间索引
        for dm, portals in self.portalDict.items():
            spatialGrid = self.getSpatialGrid(dm)
            for portal in portals:
                spatialGrid.add(portal)

    def removePortalData(self, pos, dm):
        """移除传送门数据，同时更新空间索引"""
        portalData = self.findPortalData(pos, dm)
        if portalData:
            # 从字典中移除
            self.portalDict[dm].remove(portalData)
            # 从空间网格中移除
            if dm in self.spatialGrids:
                self.spatialGrids[dm].remove(portalData)
            logging.debug("PortalManager: 移除传送门: {}".format(portalData))
        else:
            logging.error("PortalManager: 未找到传送门数据, pos: {}, dm: {}".format(pos, dm))

    def findPortalsInRange(self, pos, dm, maxDistance):
        """查找指定范围内的所有传送门"""
        if dm not in self.spatialGrids:
            return []

        spatialGrid = self.spatialGrids[dm]
        gridKey = spatialGrid.getGridKey(pos)
        radiusGrids = math.ceil(maxDistance / spatialGrid.gridSize) + 1

        portalsInRange = []
        maxDistanceSq = maxDistance * maxDistance

        for neighborKey in spatialGrid.getNeighborKeys(gridKey, radiusGrids):
            if neighborKey in spatialGrid.grid:
                for portalData in spatialGrid.grid[neighborKey]:
                    distanceSq = SpatialGrid.calculateDistanceSquared(pos, portalData.pos)
                    if distanceSq <= maxDistanceSq:
                        portalsInRange.append((portalData, math.sqrt(distanceSq)))

        # 按距离排序
        portalsInRange.sort(key=lambda x: x[1])
        return portalsInRange

    def getPortalCount(self, dm=None):
        """获取传送门数量"""
        if dm is None:
            return sum(len(portals) for portals in self.portalDict.values())
        else:
            return len(self.portalDict.get(dm, []))

    def clearPortals(self, dm=None):
        """清空传送门数据"""
        if dm is None:
            self.portalDict.clear()
            self.spatialGrids.clear()
        else:
            if dm in self.portalDict:
                del self.portalDict[dm]
            if dm in self.spatialGrids:
                del self.spatialGrids[dm]
