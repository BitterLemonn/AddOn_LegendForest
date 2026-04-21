# -*- coding: utf-8 -*-
import random

from Script_Lemon_Legend.QuModLibs.Modules.Services.Server import BaseService
from Script_Lemon_Legend.QuModLibs.Server import *
from Script_Lemon_Legend.common.utils.ItemFactory import ItemFactory
from Script_Lemon_Legend.server.utils.serverUtils import compFactory
from mod.common import minecraftEnum


class _OreData(object):

    def __init__(self, blockName, minXp=0, maxXp=0):
        self.blockName = blockName
        self.minXp = minXp
        self.maxXp = maxXp


@BaseService.Init
class BaseOreClass(BaseService):

    def __init__(self):
        BaseService.__init__(self)
        self.__oreDict = {}  # type: dict[str, _OreData]

    def addOre(self, blockName, maxXp=0, minXp=0):
        if blockName not in self.__oreDict.keys():
            self.__oreDict[blockName] = _OreData(blockName, minXp, maxXp)

    def addOres(self, oreDict):
        for blockName, xpData in oreDict.items():
            self.addOre(blockName, **xpData)

    @BaseService.Listen(Events.LoadServerAddonScriptsAfter)
    def _onLoadServerAddonScriptsAfter(self, data):
        # 注册矿石
        self.addOres(
            {
                "legend_forest:amber_ore": {"minXp": 3, "maxXp": 7},
                "legend_forest:deepslate_amber_ore": {"minXp": 3, "maxXp": 7},
                "legend_forest:star_ore": {"minXp": 0, "maxXp": 2},
                "legend_forest:deepslate_star_ore": {"minXp": 0, "maxXp": 2},
                "legend_forest:moon_stone": {"minXp": 0, "maxXp": 0},
                "legend_forest:deepslate_moon_stone": {"minXp": 0, "maxXp": 0},
                "legend_forest:ash_coal_ore": {"minXp": 0, "maxXp": 2},
                "legend_forest:ash_copper_ore": {"minXp": 0, "maxXp": 0},
                "legend_forest:ash_diamond_ore": {"minXp": 3, "maxXp": 7},
                "legend_forest:ash_emerald_ore": {"minXp": 3, "maxXp": 7},
                "legend_forest:ash_gold_ore": {"minXp": 0, "maxXp": 0},
                "legend_forest:ash_iron_ore": {"minXp": 0, "maxXp": 0},
                "legend_forest:ash_lapis_ore": {"minXp": 2, "maxXp": 5},
                "legend_forest:ash_redstone_ore": {"minXp": 1, "maxXp": 5},
            }
        )

    @BaseService.Listen(Events.DestroyBlockEvent)
    def _onPlayerTryDestroyBlock(self, data):
        data = Events.DestroyBlockEvent(data)
        pos = (data.x, data.y, data.z)
        if data.fullName in self.__oreDict.keys():
            oreData = self.__oreDict[data.fullName]
            maxXp = oreData.maxXp
            minXp = oreData.minXp

            comp = compFactory.CreateItem(data.playerId)
            level = ItemFactory(comp.GetPlayerItem(minecraftEnum.ItemPosType.CARRIED, 0, True)).getEnchantLevel(
                minecraftEnum.EnchantType.MiningLoot
            )
            # 检测时运 - 使用 Minecraft 官方算法
            # 对于时运等级 X: 掉落1个的权重为2,掉落2到(X+1)个的权重各为1
            if level > 0:
                infoComp = compFactory.CreateBlockInfo(levelId)

                # 构建权重列表: [1的权重=2, 2的权重=1, 3的权重=1, ..., (level+1)的权重=1]
                # 总权重 = 2 + level
                totalWeight = 2 + level

                # 随机选择掉落数量
                rand = random.randint(1, totalWeight)
                if rand <= 2:
                    dropCount = 1
                else:
                    dropCount = rand - 1  # 权重3对应掉落2,权重4对应掉落3...

                # 生成掉落物品
                for _ in range(dropCount - 1):
                    infoComp.SpawnResources(data.fullName, pos, data.auxData, dimensionId=data.dimensionId)

            # 生成经验
            if maxXp > 0 and minXp >= 0:
                randomXp = random.randint(minXp, maxXp)
                xpId = System.CreateEngineEntityByTypeStr(
                    "minecraft:xp_orb", (data.x + 0.5, data.y + 0.5, data.z + 0.5), (0, 0), data.dimensionId
                )
                comp = compFactory.CreateExp(xpId)
                comp.SetOrbExperience(randomXp)
