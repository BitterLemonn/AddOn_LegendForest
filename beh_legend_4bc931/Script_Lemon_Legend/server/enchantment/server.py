# -*- encoding=utf-8 -*-
import random

from Script_Lemon_Legend.QuModLibs.Modules.Services.Server import BaseService
from Script_Lemon_Legend.QuModLibs.Server import *
from Script_Lemon_Legend.common.utils.ItemFactory import ItemFactory
from Script_Lemon_Legend.server.enchantment.playerEnchantmentComp import PlayerEnchantmentComp
from Script_Lemon_Legend.server.utils import serverUtils
from Script_Lemon_Legend.server.utils.serverUtils import compFactory
from mod.common import minecraftEnum


@BaseService.Init
class EnchantmentServerService(BaseService):

    def __init__(self):
        BaseService.__init__(self)
        itemComp = compFactory.CreateItem(levelId)
        itemComp.GetUserDataInEvent("OnNewArmorExchangeServerEvent")
        itemComp.GetUserDataInEvent("OnCarriedNewItemChangedServerEvent")

    @BaseService.Listen(Events.OnNewArmorExchangeServerEvent)
    def onNewArmorExchangeServerEvent(self, data):
        data = Events.OnNewArmorExchangeServerEvent(data)
        oldEnchantMentList = ItemFactory.fromDict(data.oldArmorDict).getAllEnchantments()
        newEnchantMentList = ItemFactory.fromDict(data.newArmorDict).getAllEnchantments()

        self.handleTakeOff(oldEnchantMentList, data.playerId)
        self.handlePutOn(newEnchantMentList, data.playerId)

    @BaseService.Listen(Events.MobDieEvent)
    def onMobDieEvent(self, data):
        data = Events.MobDieEvent(data)
        if not Entity(data.attacker).IsPlayer:
            return
        itemComp = compFactory.CreateItem(data.attacker)
        carriedItem = itemComp.GetPlayerItem(minecraftEnum.ItemPosType.CARRIED, 0, True)
        if not carriedItem:
            return
        enchantMentList = ItemFactory.fromDict(carriedItem).getAllEnchantments()
        for enchantMent in enchantMentList:
            if enchantMent.get("modEnchant") == "legend_forest:soul_shield":
                level = enchantMent.get("lvl", 0)
                if random.random() < max(0.15 * level, 0.3):
                    effectComp = compFactory.CreateEffect(data.attacker)
                    effectComp.AddEffectToEntity("absorption", 10, level - 1, True)
                    x, y, z = Entity(data.id).Pos
                    targetPos = (x, y + 1.5, z)
                    serverUtils.createParticle("legend_forest:soul_shield", targetPos, data.attacker)
                break

    @BaseService.Listen(Events.OnCarriedNewItemChangedServerEvent)
    def onCarriedNewItemChangedServerEvent(self, data):
        data = Events.OnCarriedNewItemChangedServerEvent(data)
        oldEnchantMentList = ItemFactory.fromDict(data.oldItemDict).getAllEnchantments()
        newEnchantMentList = ItemFactory.fromDict(data.newItemDict).getAllEnchantments()

        self.handlePutOnWithItem(newEnchantMentList, data.playerId, data.newItemDict)
        self.handleTakeOffWithItem(oldEnchantMentList, data.playerId, data.oldItemDict)

    @staticmethod
    def handleTakeOff(enchantMentList, playerId):
        comp = PlayerEnchantmentComp.getComp(playerId)
        if not comp:
            comp = PlayerEnchantmentComp(playerId)
            comp.bind(playerId)
        comp.handleTakeOff(enchantMentList)

    @staticmethod
    def handlePutOn(enchantMentList, playerId):
        comp = PlayerEnchantmentComp.getComp(playerId)
        if not comp:
            comp = PlayerEnchantmentComp(playerId)
            comp.bind(playerId)
        comp.handlePutOn(enchantMentList)

    @staticmethod
    def handleTakeOffWithItem(enchantMentList, playerId, itemDict):
        comp = PlayerEnchantmentComp.getComp(playerId)
        if not comp:
            comp = PlayerEnchantmentComp(playerId)
            comp.bind(playerId)
        comp.handleTakeOffWithItem(enchantMentList, itemDict)

    @staticmethod
    def handlePutOnWithItem(enchantMentList, playerId, itemDict):
        comp = PlayerEnchantmentComp.getComp(playerId)
        if not comp:
            comp = PlayerEnchantmentComp(playerId)
            comp.bind(playerId)
        comp.handlePutOnWithItem(enchantMentList, itemDict)
