# coding=utf-8
import random

from Script_Lemon_Legend.QuModLibs.Modules.Services.Server import BaseService
from Script_Lemon_Legend.QuModLibs.Server import *
from Script_Lemon_Legend.common.utils.ItemFactory import ItemFactory
from Script_Lemon_Legend.server.utils.serverUtils import compFactory
from mod.common import minecraftEnum


class _OreData(object):

    def __init__(self, blockName, dropItem, baseCount=1, minXp=0, maxXp=0):
        self.blockName = blockName
        self.dropItem = dropItem
        self.baseCount = baseCount
        self.minXp = minXp
        self.maxXp = maxXp


class OreService(BaseService):
    """
    矿石服务类
    处理矿石被挖掘事件，驱动矿石掉落与经验奖励
    """

    def __init__(self):
        BaseService.__init__(self)
        self.__oreMap = {}

    def register(self, oreData):
        """
        注册矿石
        :param oreData: _OreData 实例
        """
        self.__oreMap[oreData.blockName] = oreData

    @BaseService.Listen("ServerPlayerTryDestroyBlockEvent")
    def OnPlayerTryDestroyBlock(self, data):
        playerId = data["playerId"]
        x, y, z = data["x"], data["y"], data["z"]
        dimensionId = data["dimensionId"]
        blockName = data["fullName"]
        if blockName not in self.__oreMap:
            return
        ore = self.__oreMap[blockName]
        data["spawnResources"] = False
        # 检测玩家手中物品时运等级
        itemComp = compFactory.CreateItem(playerId)
        carried = itemComp.GetPlayerItem(minecraftEnum.ItemPosType.CARRIED, 0, True)
        enchantLevel = ItemFactory(carried).getEnchantLevel(minecraftEnum.EnchantType.MiningLoot)
        if enchantLevel > 0:
            totalWeight = enchantLevel + 2
            roll = random.randint(1, totalWeight)
            multiplier = 1 if roll <= 2 else roll - 1
        else:
            multiplier = 1
        base = ore.baseCount
        baseCount = random.randint(base[0], base[1]) if isinstance(base, tuple) else base
        dropCount = baseCount * multiplier
        itemDict = ItemFactory().setItemName(ore.dropItem).setCount(dropCount).build()
        System.CreateEngineItemEntity(itemDict, dimensionId, (x + 0.5, y + 0.5, z + 0.5))
        # 经验奖励
        xp = 0
        if ore.maxXp > 0:
            xp = random.randint(ore.minXp, ore.maxXp)
            if xp > 0:
                compFactory.CreateExp(playerId).CreateExperienceOrb(xp, (x + 0.5, y + 0.5, z + 0.5), False)


oreService = OreService.access()

_ORE_DATA = [
    _OreData("legend_forest:ash_coal_ore", "minecraft:coal", minXp=0, maxXp=2),
    _OreData("legend_forest:ash_copper_ore", "minecraft:raw_copper", (2, 5)),
    _OreData("legend_forest:ash_diamond_ore", "minecraft:diamond", minXp=3, maxXp=7),
    _OreData("legend_forest:ash_emerald_ore", "minecraft:emerald", minXp=3, maxXp=7),
    _OreData("legend_forest:ash_gold_ore", "minecraft:raw_gold"),
    _OreData("legend_forest:ash_iron_ore", "minecraft:raw_iron"),
    _OreData("legend_forest:ash_lapis_ore", "minecraft:lapis_lazuli", (4, 9), minXp=2, maxXp=5),
    _OreData("legend_forest:ash_redstone_ore", "minecraft:redstone", (4, 5), minXp=1, maxXp=5),
]

for _ore in _ORE_DATA:
    oreService.register(_ore)
