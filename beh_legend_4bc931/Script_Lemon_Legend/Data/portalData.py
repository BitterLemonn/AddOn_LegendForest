# coding=utf-8

import json
import pickle
import math
from collections import defaultdict
from ..logging import logging


class SpatialGrid:
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
    
    def getNeighborKeys(self, gridKey, radiusGrids=1):
        """获取周围网格的键，用于范围查询"""
        x, y, z = gridKey
        neighbors = []
        for dx in range(-radiusGrids, radiusGrids + 1):
            for dy in range(-radiusGrids, radiusGrids + 1):
                for dz in range(-radiusGrids, radiusGrids + 1):
                    neighbors.append((x + dx, y + dy, z + dz))
        return neighbors
    
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


# 单例模式
class PortalManager:
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
            self.__targetDistance = 50
            PortalManager._initialized = True

    def getSpatialGrid(self, dm):
        """获取指定维度的空间网格，如果不存在则创建"""
        if dm not in self.spatialGrids:
            self.spatialGrids[dm] = SpatialGrid()
        return self.spatialGrids[dm]

    # 找到距离最近的在self.__targetDistance以内的传送门（优化版本）
    def findPortalData(self, pos, dm):
        """使用空间网格优化的最近邻查询"""
        if dm not in self.spatialGrids:
            return None
        
        spatialGrid = self.spatialGrids[dm]
        return spatialGrid.findNearest(pos, self.__targetDistance)

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
        return {
            'pos': self.pos,
            'dm': self.dm,
            'toDm': self.toDm,
            'toPos': self.toPos,
            'direction': self.direction
        }
