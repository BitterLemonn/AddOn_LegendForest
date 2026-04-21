# -*- coding: utf-8 -*-
import math

from Script_Lemon_Legend.common.utils import commonUtils

from Script_Lemon_Legend.QuModLibs.Server import *
from Script_Lemon_Legend.server.utils import serverUtils
from Script_Lemon_Legend.server.utils.serverUtils import compFactory


class AttackComp(object):

    def __init__(self, entityId):
        self._entityId = entityId

        self.gameComp = compFactory.CreateGame(levelId)

    def setSectorAttackArgs(self, delayTime, distance, angle, damageList, entityFilter=None, checkBlock=True,
                            knocked=True, additionalMotion=None):
        """
        释放扇形攻击
        :param delayTime: 延迟时间
        :type delayTime: float
        :param distance: 半径
        :type distance: float
        :param angle: 角度
        :type angle: int
        :param damageList: 伤害值列表(根据难度变化)
        :type damageList: list[float]
        :param entityFilter: 过滤器
        :type entityFilter: dict | None
        :param checkBlock: 是否被方块阻挡
        :param knocked: 是否击退
        :param additionalMotion: 施加给受伤者额外动量(与击退冲突)
        :type additionalMotion: AttackServer.AdditionalMotion
        """

        self.gameComp.AddTimer(delayTime,
                               lambda: self._onAttack(distance, angle, damageList, entityFilter, checkBlock, knocked,
                                                      additionalMotion))

    def setAoeAttackArgs(self, delayTime, radius, damageList, entityFilter=None, checkBlock=True, knocked=True):
        """
        释放aoe攻击
        :param delayTime: 延迟时间
        :type delayTime: float
        :param radius: 半径
        :type radius: float
        :param damageList: 伤害值列表(根据难度变化)
        :type damageList: list[float]
        :param entityFilter: 过滤器
        :type entityFilter: dict | None
        :param checkBlock: 是否被方块阻挡
        :param knocked: 是否击退
        """
        self.gameComp.AddTimer(delayTime,
                               lambda: self._onAoeAttack(radius, damageList, entityFilter, checkBlock, knocked))

    def setSectorProjectileAttackArgs(self, delayTime, targetId, angle, num, projectileName):
        """
        扇形范围内发射弹射物
        :param delayTime: 延迟时间
        :type delayTime: float
        :param targetId: 目标Id
        :type targetId: int
        :param angle: 扇形角度
        :type angle: int
        :param num: 弹射物数量(计算步长)
        :type num: int
        :param projectileName: 弹射物名称
        :type projectileName: str
        """
        self.gameComp.AddTimer(delayTime,
                               lambda: self._setStepSectorProjectile(targetId, angle, num, projectileName))

    def summonEntity(self, delayTime, entityName, pos, rot=(0, 0), isSnapToFloor=False, limit=10):
        """
        召唤实体
        :param delayTime: 延迟时间
        :type delayTime: float
        :param entityName: 实体名称
        :type entityName: str
        :param pos: 位置
        :type pos: tuple[float, float, float]
        :param rot: 朝向
        :type rot: tuple[float, float]
        :param isSnapToFloor: 是否贴地
        :type isSnapToFloor: bool
        :param limit: 垂直搜索最大范围(仅在贴地时有效)
        :type limit: int
        """
        self.gameComp.AddTimer(delayTime,
                               lambda: self._summonEntity(entityName, pos, rot, isSnapToFloor, limit))

    def summonEntityCircle(self, delayTime, entityName, centerPos, radius, count=None, summonDelay=0.0, rot=(0, 0),
                           isSnapToFloor=True, limit=10):
        """
        召唤实体 centerPos为中心，radius为半径的圆周上均匀分布
        :param delayTime: 延迟时间
        :type delayTime: float
        :param summonDelay: 召唤间隔时间
        :type summonDelay: float
        :param entityName: 实体名称
        :type entityName: str
        :param centerPos: 中心位置
        :type centerPos: tuple[float, float, float]
        :param radius: 半径
        :type radius: float
        :param count: 实体数量
        :type count: int
        :param rot: 朝向
        :type rot: tuple[float, float]
        :param isSnapToFloor: 是否贴地
        :type isSnapToFloor: bool
        :param limit: 垂直搜索最大范围(仅在贴地时有效)
        :type limit: int
        """
        # 如果未指定数量,按1.5单位弧长间距计算
        finalCount = count
        if finalCount is None:
            circumference = 2 * math.pi * radius
            finalCount = max(4, int(circumference / 3))

        if finalCount <= 0:
            return

        def _summonEntityCircle():
            angle_step = 2 * math.pi / finalCount

            for i in range(finalCount):
                angle = angle_step * i
                # 计算位置时使用临时变量,避免浮点精度问题
                x = centerPos[0] + radius * math.cos(angle)
                z = centerPos[2] + radius * math.sin(angle)
                pos = (x, centerPos[1], z)

                # 使用默认参数捕获位置值
                self.gameComp.AddTimer(summonDelay * i,
                                       lambda p=pos: self._summonEntity(entityName, p, rot, isSnapToFloor, limit))

        self.gameComp.AddTimer(delayTime, _summonEntityCircle)

    def summonEntityLine(self, delayTime, entityName, startPos, endPos, summonDelay=0.0, count=5, rot=(0, 0),
                         isSnapToFloor=True, limit=10, spacing=None):
        """
        召唤实体(线性分布)
        :param delayTime: 延迟时间
        :type delayTime: float
        :param summonDelay: 召唤间隔时间
        :type summonDelay: float
        :param entityName: 实体名称
        :type entityName: str
        :param startPos: 起始位置
        :type startPos: tuple[float, float, float]
        :param endPos: 结束位置
        :type endPos: tuple[float, float, float]
        :param count: 实体数量
        :type count: int
        :param rot: 朝向
        :type rot: tuple[float, float]
        :param isSnapToFloor: 是否贴地
        :type isSnapToFloor: bool
        :param limit: 垂直搜索最大范围(仅在贴地时有效)
        :type limit: int
        :param spacing: 实体间距 (若为None则默认为3)
        :type spacing: float | None
        """

        def _summonEntityLine():
            # 计算起点到终点的总距离
            if isSnapToFloor:
                totalDistance = math.sqrt((startPos[0] - endPos[0]) ** 2 + (startPos[2] - endPos[2]) ** 2)
            else:
                totalDistance = commonUtils.getDistance(startPos, endPos)

            if totalDistance <= 0.001:
                self.gameComp.AddTimer(0, lambda: self._summonEntity(entityName, startPos, rot, isSnapToFloor, limit))
                return

            # 确定间距
            actualSpacing = spacing if spacing is not None else 3.0

            # 根据总距离和间距计算实际可以召唤的数量
            actualCount = min(count, int(totalDistance / actualSpacing) + 1)

            # 计算方向单位向量
            if isSnapToFloor:
                dx = endPos[0] - startPos[0]
                dz = endPos[2] - startPos[2]
                dy = endPos[1] - startPos[1]
                direction = (dx / totalDistance, dy / totalDistance, dz / totalDistance)
            else:
                direction = commonUtils.unitVector(startPos, endPos)

            for i in range(actualCount):
                # 计算当前实体的位置偏移
                offset = actualSpacing * i
                pos = (startPos[0] + direction[0] * offset,
                       startPos[1] + direction[1] * offset,
                       startPos[2] + direction[2] * offset)

                self.gameComp.AddTimer(summonDelay * i,
                                       lambda p=pos: self._summonEntity(entityName, p, rot, isSnapToFloor, limit))

        self.gameComp.AddTimer(delayTime, _summonEntityLine)

    def setMotion(self, delayTime, motion=None):
        """
        设置自身动量
        :param delayTime: 延迟时间
        :param motion: 动量
        """
        if motion is None:
            targetId = compFactory.CreateAction(self._entityId).GetAttackTarget()
            motion = commonUtils.unitVector(Entity(self._entityId).FootPos, Entity(targetId).FootPos)
            motion = (motion[0], 0.1, motion[2])
        self.gameComp.AddTimer(delayTime,
                               lambda: compFactory.CreateActorMotion(self._entityId).SetMotion(motion))

    def _onAttack(self, radius, angle, damageList, entityFilter, checkBlock, knocked, additionalMotion):
        if Entity(self._entityId).Health.Value > 0.1:
            # 扇形攻击包含1格内的aoe攻击
            self._onAoeAttack(1, damageList, entityFilter, checkBlock, knocked, additionalMotion)

            targetList = serverUtils.getEntityInSector(self._entityId, radius, angle, entityFilter)
            targetList = [target for target in targetList if
                          target != self._entityId and Entity(target).Identifier != "minecraft:item"]
            knocked = False if additionalMotion is not None else knocked
            for target in targetList:
                motionComp = compFactory.CreateActorMotion(target)
                serverUtils.doHurt(self._entityId, damageList, target, checkBlock=checkBlock, knock=knocked)
                if additionalMotion is not None:
                    # 解析额外动量
                    unitVector = commonUtils.unitVector(Entity(self._entityId).Pos, Entity(target).Pos)
                    targetMotion = (unitVector[0] * additionalMotion.backwardMotion, additionalMotion.upwardMotion,
                                    unitVector[2] * additionalMotion.backwardMotion)
                    if Entity(target).Identifier == "minecraft:player":
                        motionComp.SetPlayerMotion(targetMotion)
                    else:
                        motionComp.SetMotion(targetMotion)

    def _onAoeAttack(self, radius, damageList, entityFilter, checkBlock, knocked, additionalMotion=None):
        if Entity(self._entityId).Health.Value > 0.1:
            targetList = serverUtils.getEntityAround(self._entityId, radius, entityFilter)
            targetList = [target for target in targetList if
                          target != self._entityId and Entity(target).Identifier != "minecraft:item"]
            for target in targetList:
                motionComp = compFactory.CreateActorMotion(target)
                serverUtils.doHurt(self._entityId, damageList, target, checkBlock=checkBlock, knock=knocked)
                if additionalMotion is not None:
                    # 解析额外动量
                    unitVector = commonUtils.unitVector(Entity(self._entityId).Pos, Entity(target).Pos)
                    targetMotion = (unitVector[0] * additionalMotion.backwardMotion, additionalMotion.upwardMotion,
                                    unitVector[2] * additionalMotion.backwardMotion)
                    if Entity(target).Identifier == "minecraft:player":
                        motionComp.SetPlayerMotion(targetMotion)
                    else:
                        motionComp.SetMotion(targetMotion)

    def _setStepSectorProjectile(self, targetId, angle, num, projectileName):
        # 获取碰撞箱
        comp = compFactory.CreateCollisionBox(targetId)
        _, targetSizeY = comp.GetSize()
        comp = compFactory.CreateCollisionBox(self._entityId)
        _, sizeY = comp.GetSize()
        # 计算起始点与目标点
        x, y, z = Entity(self._entityId).FootPos
        fromPos = (x, y + sizeY / 2, z)
        x, y, z = Entity(targetId).FootPos
        toPos = (x, y + targetSizeY / 3 * 2, z)
        # 获取距离
        distance = commonUtils.getDistance(fromPos, toPos)
        unitVect = commonUtils.unitVector(fromPos, toPos)
        # 计算步长
        targetVect = []
        for i in range(0, angle // 2, angle // num):
            targetVect.append(commonUtils.rotateVectorY(unitVect, i))
            targetVect.append(commonUtils.rotateVectorY(unitVect, -i))
        # 发射弹射物
        for dire in targetVect:
            param = {
                "position": (fromPos[0] + dire[0], fromPos[1] + dire[1], fromPos[2] + dire[2]),
                "direction": dire,
                "power": max(1.6, 0.1 * distance)
            }
            comp = compFactory.CreateProjectile(levelId)
            comp.CreateProjectileEntity(self._entityId, projectileName, param)

    def _summonEntity(self, entityName, pos, rot, isSnapToFloor, limit):
        if isSnapToFloor:
            pos = serverUtils.getSnapFloorPos(pos, Entity(self._entityId).Dm, limit)
            if not pos:
                return
        System.CreateEngineEntityByTypeStr(entityName, pos, rot, Entity(self._entityId).Dm)
