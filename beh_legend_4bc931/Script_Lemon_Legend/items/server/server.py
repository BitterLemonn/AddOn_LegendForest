import random

from mod.common import minecraftEnum

from ... import modConfig
from ...QuModLibs.Server import *
from ...QuModLibs.Modules.Services.Server import BaseService
from ...bean.initBookData import InitBookData
from ...logging import logging
from ...utils import serverUtils
from ...utils.ItemFactory import ItemFactory
from ...utils.commonUtils import getTargetPosWithFacing
from ...utils.serverUtils import compFactory


@BaseService.Init
class BaseServerService(BaseService):

    def __init__(self):
        BaseService.__init__(self)
        compFactory.CreateItem(levelId).GetUserDataInEvent("ServerItemTryUseEvent")

    @BaseService.Listen(Events.ClientLoadAddonsFinishServerEvent)
    def onClientLoadAddonsFinishServerEvent(self, data):
        data = Events.ClientLoadAddonsFinishServerEvent(data)
        if InitBookData.IS_GIVEN_BOOK.get(data.playerId):
            return
        InitBookData.IS_GIVEN_BOOK[data.playerId] = True
        InitBookData.mSignNeedUpdate()
        comp = compFactory.CreateItem(data.playerId)
        guideBook = ItemFactory().setItemName("legend_forest:pnakotic_manuscript").build()
        serverUtils.givePlayerItem(guideBook, data.playerId)

    @BaseService.Listen(Events.ItemUseOnAfterServerEvent)
    def onItemUseOnAfterServerEvent(self, data):
        data = Events.ItemUseOnAfterServerEvent(data)
        # 米诺鱼桶
        if data.itemDict["newItemName"] == "legend_forest:bucket_minnow" and serverUtils.setCooldown(data.entityId):
            comp = compFactory.CreateItem(data.entityId)
            itemDict = comp.GetPlayerItem(minecraftEnum.ItemPosType.CARRIED, 0, True)
            if itemDict is None:
                return

            targetPos = getTargetPosWithFacing((data.x, data.y, data.z), data.face)
            targetPos = (targetPos[0] + 0.5, targetPos[1], targetPos[2] + 0.5)

            health = 2
            userData = itemDict.get("userData")
            if userData and userData.get("health"):
                health = userData["health"]["__value__"]
            entityId = System.CreateEngineEntityByTypeStr("legend_forest:minnow", targetPos, (0, 0), data.dimensionId)
            Entity(entityId).Health.SetValue(health)
        # 微光楼梯测试
        # elif data.itemDict["newItemName"] == "minecraft:stick" and \
        #         UsingCooldownServerService.access().setCooldown(data.entityId):
        #     blockName = data.blockName
        #     if blockName == "legend_forest:shimmer_stairs":
        #         comp = serverApi.GetEngineCompFactory().CreateBlockState(levelId)
        #         blockState = comp.GetBlockStates((data.x, data.y, data.z), data.dimensionId)
        #         upsideDown = blockState.get("legend_forest:upside_down_bit")
        #         blockState["legend_forest:upside_down_bit"] = 1 if upsideDown == 0 else 0
        #         comp.SetBlockStates((data.x, data.y, data.z), blockState, data.dimensionId)

    @BaseService.Listen(Events.OnCarriedNewItemChangedServerEvent)
    def onCarriedNewItemChangedServerEvent(self, data):
        data = Events.OnCarriedNewItemChangedServerEvent(data)

        # 替换鲑鱼桶为米诺鱼桶
        if data.newItemDict and data.newItemDict["newItemName"] == "minecraft:salmon_bucket":
            comp = compFactory.CreateItem(data.playerId)
            itemDict = comp.GetPlayerItem(minecraftEnum.ItemPosType.CARRIED, 0, True)
            if itemDict.get("userData") and itemDict["userData"].get("identifier"):
                identifier = itemDict["userData"]["identifier"]

                if identifier["__value__"] == "legend_forest:minnow":
                    newItem = {"newItemName": "legend_forest:bucket_minnow", "count": 1}
                    attributes = itemDict["userData"].get("Attributes", [])

                    curHealth = None
                    for attribute in attributes:
                        if attribute.get("Name") and attribute["Name"].get("__value__") == "minecraft:health":
                            curHealth = attribute.get("Current", {}).get("__value__")
                            break
                    if curHealth:
                        newItem["userData"] = {"health": curHealth}
                        print(newItem["userData"])

                    comp.SpawnItemToPlayerCarried(newItem, data.playerId)
                    print(comp.GetPlayerItem(minecraftEnum.ItemPosType.CARRIED, 0, True))

    @BaseService.REG_API("items/server/disenchant")
    def onDisenchantBookUsed(self, data):
        data = Events.ServerItemTryUseEvent(data)
        comp = compFactory.CreateItem(data.playerId)
        offHandItem = comp.GetPlayerItem(minecraftEnum.ItemPosType.OFFHAND, 0)
        # 祛魔
        if offHandItem and offHandItem["newItemName"] == "legend_forest:book_disenchanted":
            if serverUtils.setCooldown(data.playerId):
                data.cancel = True
                try:
                    itemEnchants = ItemFactory.fromDict(data.itemDict).getAllEnchantments()
                    if itemEnchants:
                        # 给予附魔书
                        for enchantData in itemEnchants:
                            enchantId = enchantData["id"]
                            enchantLevel = enchantData["lvl"]
                            if enchantId == minecraftEnum.EnchantType.ModEnchant:
                                enchantId = enchantData["modEnchant"]
                            enchantBook = (ItemFactory().setItemName("minecraft:enchanted_book")
                                           .addEnchantment(enchantId, enchantLevel).build())
                            serverUtils.givePlayerItem(enchantBook, data.playerId)
                        # 清空副手物品
                        comp.SetEntityItem(minecraftEnum.ItemPosType.OFFHAND,
                                           {"newItemName": "minecraft:air", "count": 1}, 0)
                        # 祛魔主手物品
                        targetHandItem = (ItemFactory.fromDict(data.itemDict).removeAllEnchantments()
                                          .addCustomData("legend_forest", {"disenchanted": True}).build())
                        comp.SetInvItemNum(comp.GetSelectSlotId(), 0)
                        comp.SpawnItemToPlayerInv(targetHandItem, data.playerId)
                        print(comp.GetPlayerItem(minecraftEnum.ItemPosType.CARRIED, 0, True))
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    logging.error("祛魔失败: {}".format(data.itemDict))

    @BaseService.Listen(Events.PlayerEatFoodServerEvent)
    def onPlayerEatFoodServerEvent(self, data):
        data = Events.PlayerEatFoodServerEvent(data)
        # 棱花乐事食物效果相关
        if data.itemDict["newItemName"] in modConfig.ARRIS_FOOD_EFFECT.keys():
            effectList = modConfig.ARRIS_FOOD_EFFECT[data.itemDict["newItemName"]]
            interface = serverApi.GetEngineCompFactory().CreateModAttr("arris").GetAttr("ArrisFarmersDelightInterface")
            if interface is None:
                return
            for effect in effectList:
                if random.random() < effect["chance"]:
                    comp = serverApi.GetEngineCompFactory().CreateEffect(data.playerId)
                    comp.AddEffectToEntity(effect["name"], effect["duration"], effect["amplifier"], True)
