# -*- coding: utf-8 -*-

from ..QuModLibs.Server import *
from ..QuModLibs.Modules.Services.Server import BaseService
from ..logging import logging
import commonUtils
import math

minecraftEnum = serverApi.GetMinecraftEnum()


def givePlayerItem(itemDict, playerId):
    comp = serverApi.GetEngineCompFactory().CreateItem(playerId)
    for i in range(0, 36):
        item = comp.GetPlayerItem(minecraftEnum.ItemPosType.INVENTORY, i, True)
        if item is None:
            comp.SpawnItemToPlayerInv(itemDict, playerId, -1)
            return
    player = Entity(playerId)
    System.CreateEngineItemEntity(itemDict, player.Dm, player.FootPos)


def getPlayerMode(playerId):
    comp = serverApi.GetEngineCompFactory().CreateGame(levelId)
    return comp.GetPlayerGameType(playerId)


def decreaseItem(playerId, count, slot=-1):
    if getPlayerMode(playerId) != minecraftEnum.GameType.Creative:
        comp = serverApi.GetEngineCompFactory().CreateItem(playerId)
        if slot == -1:
            slot = comp.GetSelectSlotId()

        item = comp.GetPlayerItem(minecraftEnum.ItemPosType.INVENTORY, slot, True)
        restCount = item["count"] - count if item["count"] - count > 0 else 0
        comp.SetInvItemNum(slot, restCount)


def decreaseDurability(playerId, dur, slot=-1):
    if getPlayerMode(playerId) != minecraftEnum.GameType.Creative:
        comp = serverApi.GetEngineCompFactory().CreateItem(playerId)
        if slot == -1:
            slot = comp.GetSelectSlotId()

        item = comp.GetPlayerItem(minecraftEnum.ItemPosType.INVENTORY, slot, True)
        restDur = item["durability"] - dur if item["durability"] - dur > 0 else 0
        if restDur <= 0:
            comp.SetInvItemNum(slot, item["count"] - 1)
        comp.SetItemDurability(minecraftEnum.ItemPosType.INVENTORY, slot, restDur)


def createParticle(particleName, pos, playerId):
    x, y, z = pos
    comp = serverApi.GetEngineCompFactory().CreateCommand(playerId)
    comp.SetCommand("/particle " + particleName + " " + str(x) + " " + str(y) + " " + str(z))


@BaseService.Init
class UsingCooldownServerService(BaseService):

    def __init__(self):
        BaseService.__init__(self)
        self.cooldownList = {}

    def setCooldown(self, playerId, time=5):
        if playerId not in self.cooldownList.keys():
            self.cooldownList[playerId] = time
            return True
        else:
            return False

    def onServiceUpdate(self):
        for playerId, cooldownTime in self.cooldownList.items():
            if cooldownTime == 0:
                del self.cooldownList[playerId]
            else:
                self.cooldownList[playerId] = cooldownTime - 1
        return BaseService.onServiceUpdate(self)


def getDistance(entityId1, entityId2):
    pos1 = Entity(entityId1).FootPos
    pos2 = Entity(entityId2).FootPos
    return commonUtils.getDistance(pos1, pos2)


def searchNearestTargetBiome(pos, dm, targetList, maxRadius=25):
    biomeComp = serverApi.GetEngineCompFactory().CreateBiome(levelId)

    x, z = commonUtils.getChunkCenter(pos[0], pos[2])

    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # 方向：上、右、下、左
    stepSize = 1  # 每次移动的步数
    currentRadius = 1  # 当前搜索半径
    currentX, currentZ = x, z  # 当前坐标

    while currentRadius <= maxRadius:
        for direction in directions:
            for _ in range(stepSize):
                currentX += direction[0] * 16
                currentZ += direction[1] * 16
                biomeName = biomeComp.GetBiomeName((currentX, 63, currentZ), dm)
                logging.debug("当前坐标：{}，生物群系：{}".format((currentX, currentZ), biomeName))
                if biomeName in targetList:
                    return currentX, currentZ
            if direction in [(0, 1), (0, -1)]:
                stepSize += 1
        currentRadius += 1

    return None  # 如果没有找到符合条件的位置


def setLookAt(entityId, targetId):
    comp = serverApi.GetEngineCompFactory().CreateRot(entityId)
    targetPos = Entity(targetId).Pos
    comp.SetEntityLookAtPos(targetPos, 0.5, 1, False)


def getEntityAround(entityId, radius, entityFilter=None):
    """
    获取指定半径内的实体
    :param entityId: 生物id
    :param radius: 正方形半径
    :param entityFilter: 过滤条件(默认为带有生命值组件的所有生物)
    :return: 实体列表 type: list[str]
    """
    if entityFilter is None:
        entityFilter = {
            "test": "has_component",
            "value": "minecraft:health"
        }

    comp = serverApi.GetEngineCompFactory().CreateGame(entityId)
    return comp.GetEntitiesAround(entityId, int(radius), entityFilter)


def getEntityInSector(entityId, radius, angle, entityFilter=None):
    """
    获取指定实体视野扇形范围内的实体
    :param entityId: 生物id
    :param radius: 扇形半径
    :param angle: 扇形角度
    :param entityFilter: 过滤条件(默认为带有生命值组件的所有生物)
    :return: 实体列表 type: list[str]
    """
    targetList = getEntityAround(entityId, radius, entityFilter)
    entityPos = Entity(entityId).FootPos
    # 获取生物的朝向单位向量
    sightDir = Entity(entityId).DirFromRot
    result = []
    for target in targetList:
        if target == entityId:
            continue
        targetPos = Entity(target).FootPos
        # 计算生物与目标的向量
        vector = commonUtils.unitVector(entityPos, targetPos)
        # 计算生物与目标的夹角
        angleBetween = math.degrees(commonUtils.getAngleBetweenVectors(vector, sightDir, isDismissY=True))
        # 判断是否在扇形范围内
        if -angle / 2 <= angleBetween <= angle / 2:
            result.append(target)
    return result


def doHurt(entityId, damageList, targetId, cause=None, checkBlock=True, knock=True):
    """
    对目标造成伤害
    :param entityId: 伤害源实体id
    :param damageList: 伤害值列表(对应不同难度)
    :param targetId: 目标实体id
    :param cause: 伤害类型
    :param checkBlock: 是否检测有无障碍物阻挡
    :param knock: 是否击退
    """
    if cause is None:
        cause = minecraftEnum.ActorDamageCause.EntityAttack
    comp = serverApi.GetEngineCompFactory().CreateBlockInfo(levelId)
    if checkBlock:
        if comp.CheckBlockToPos(Entity(entityId).Pos, Entity(targetId).Pos, Entity(entityId).Dm):
            return

    difficulty = serverApi.GetEngineCompFactory().CreateGame(levelId).GetGameDiffculty()
    damage = damageList[difficulty] if isinstance(damageList, list) else damageList
    serverApi.GetEngineCompFactory().CreateHurt(targetId).Hurt(damage, cause, entityId, knocked=knock)


def shakeCamera(playerList, intensity, duration, shakeType="positional"):
    """
    摄像机抖动
    :param playerList: 玩家列表
    :param intensity: 抖动强度
    :param duration: 持续时间
    :param shakeType: 抖动类型
    """
    for player in playerList:
        Call(player, "OpenCameraShakeAfterReset", duration)
        comp = serverApi.GetEngineCompFactory().CreateCommand(player)
        comp.SetCommand("/camerashake add @s {intensity} {duration} {shakeType}".format(
            intensity=intensity, duration=duration, shakeType=shakeType
        ))


def getSnapFloorPos(pos, dimensionId, limit=10):
    """
    获取指定位置最近的地面坐标
    :param pos: 位置
    :param dimensionId: 维度id
    :param limit: 最大垂直搜索距离
    :return: 地面坐标
    """
    comp = serverApi.GetEngineCompFactory().CreateBlockInfo(levelId)
    for i in range(0, limit):
        block = comp.GetBlockNew((pos[0], pos[1] - i, pos[2]), dimensionId)
        if block and block["name"] != "minecraft:air":
            return pos[0], pos[1] - i, pos[2]
    return None
