# -*- coding: utf-8 -*-
import math
import random
from math import floor

from mod.common import minecraftEnum


class FormatColorStr(object):
    RED = "§c"
    GREEN = "§a"
    YELLOW = "§e"
    BLUE = "§9"
    WHITE = "§f"
    GRAY = "§7"
    DARK_GRAY = "§8"
    BLACK = "§0"
    GOLD = "§6"
    DARK_RED = "§4"
    DARK_GREEN = "§2"
    DARK_BLUE = "§1"
    DARK_AQUA = "§3"
    DARK_PURPLE = "§5"
    LIGHT_PURPLE = "§d"
    MINECOIN_GOLD = "§g"
    MATERIAL_QUARTZ = "§h"
    MATERIAL_IRON = "§i"
    MATERIAL_NETHERITE = "§j"
    MATERIAL_REDSTONE = "§m"
    MATERIAL_COPPER = "§n"
    MATERIAL_GOLD = "§p"
    MATERIAL_EMERALD = "§q"
    MATERIAL_DIAMOND = "§s"
    MATERIAL_LAPIS = "§t"
    MATERIAL_AMETHYST = "§u"
    MATERIAL_RESIN = "§v"
    FORMATTER = "§"


def weightChoice(weightDict):
    """根据权重字典随机选择一个键"""
    totalWeight = sum(weightDict.values())
    randValue = random.uniform(0, totalWeight)
    cumulativeWeight = 0
    for key, weight in weightDict.items():
        cumulativeWeight += weight
        if randValue <= cumulativeWeight:
            return key
    return None


def normalizeVector(vector):
    """向量归一化"""
    length = math.sqrt(sum(coord ** 2 for coord in vector))
    return (coord / length for coord in vector)


# type: (tuple, tuple, float) -> tuple[int, int]
def findPointBehind(posXZ, sight, distance):
    """获取指定位置后方一定距离的点"""
    dir_x, dir_y = normalizeVector(sight)
    new_x = posXZ[0] - dir_x * distance
    new_y = posXZ[1] - dir_y * distance
    return int(new_x), int(new_y)


def isInChunk(pos, chunk):
    """检查位置是否在区块内"""
    chunkIndexX, chunkIndexZ = chunk
    return chunkIndexX * 16 <= pos[0] < chunkIndexX * 16 + 15 and chunkIndexZ * 16 <= pos[2] < chunkIndexZ * 16 + 15


def rotateVectorY(vector, angleDegrees):
    """以y轴为旋转轴旋转向量"""
    angleRadians = math.radians(angleDegrees)
    x = vector[0] * math.cos(angleRadians) - vector[2] * math.sin(angleRadians)
    z = vector[0] * math.sin(angleRadians) + vector[2] * math.cos(angleRadians)
    return x, vector[1], z


def rotateVectorX(vector, angleDegrees):
    """以x轴为旋转轴旋转向量"""
    angleRadians = math.radians(angleDegrees)
    y = vector[1] * math.cos(angleRadians) - vector[2] * math.sin(angleRadians)
    z = vector[1] * math.sin(angleRadians) + vector[2] * math.cos(angleRadians)
    return vector[0], y, z


def unitVector(fromPos, toPos):
    """计算fromPos到toPos两点之间的单位向量"""
    delta_x = toPos[0] - fromPos[0]
    delta_y = toPos[1] - fromPos[1]
    delta_z = toPos[2] - fromPos[2]
    magnitude = math.sqrt(delta_x ** 2 + delta_y ** 2 + delta_z ** 2)
    return delta_x / magnitude, delta_y / magnitude, delta_z / magnitude


def getAngleBetweenVectors(v1, v2, isDismissY=False):
    """计算两个单位向量之间的夹角"""
    if isDismissY:
        v1 = (v1[0], 0, v1[2])
        v2 = (v2[0], 0, v2[2])
    dot_product = sum(v1[i] * v2[i] for i in range(3))
    mod_product = math.sqrt(
        sum(v1[i] ** 2 for i in range(3)) * sum(v2[i] ** 2 for i in range(3)))
    cos_angle = dot_product / mod_product
    return math.acos(cos_angle)


def isFrontOf(p1, p2, sight):
    """判断p2是否在p1的视线前方"""
    return sum((p2[i] - p1[i]) * sight[i] for i in range(3)) > 0


def getIntPos(floatPos):
    """将浮点坐标转换为整数坐标 """
    return tuple(int(floor(i)) for i in floatPos)


def getDistance(p1, p2):
    """计算两点之间的距离"""
    return math.sqrt(sum((p1[i] - p2[i]) ** 2 for i in range(3)))


def getTargetPosWithFacing(pos, facing, opposite=False):
    """根据朝向获取目标位置"""
    x, y, z = pos
    if facing == minecraftEnum.Facing.North:  # north
        z -= 1 if not opposite else -1
    elif facing == minecraftEnum.Facing.South:  # south
        z += 1 if not opposite else -1
    elif facing == minecraftEnum.Facing.West:  # west
        x -= 1 if not opposite else -1
    elif facing == minecraftEnum.Facing.East:  # east
        x += 1 if not opposite else -1
    elif facing == minecraftEnum.Facing.Up:  # up
        y += 1 if not opposite else -1
    elif facing == minecraftEnum.Facing.Down:  # down
        y -= 1 if not opposite else -1
    return x, y, z


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def getChunkCenter(x, z):
    """获取区块中心坐标"""
    chunkX = (x // 16) * 16 + 8
    chunkZ = (z // 16) * 16 + 8
    return chunkX, chunkZ


def getRGBFloatByStr(colorStr):
    """通过十六进制颜色字符串获取RGB浮点值"""
    colorStr = colorStr[1:]
    r = int(colorStr[0:2], 16) / 255.0
    g = int(colorStr[2:4], 16) / 255.0
    b = int(colorStr[4:6], 16) / 255.0
    return r, g, b


def compireDict(dict1, dict2):
    """比较两个字典是否相等"""
    if dict1 is None and dict2 is None:
        return True
    if dict1 is None or dict2 is None:
        print("其中一个字典为None，dict1：{}, dict2：{}".format(dict1, dict2))
        return False
    if dict1.keys() != dict2.keys():
        print("字典键不相等，键1：{}, 键2：{}".format(dict1.keys(), dict2.keys()))
        return False
    for key in dict1.keys():
        if dict1[key] != dict2[key]:
            print("字典不相等，键：{}, 值1：{}， 值2：{}".format(key, dict1[key], dict2[key]))
            return False
    return True
