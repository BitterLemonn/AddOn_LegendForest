# -*- encoding: utf-8 -*-
import json

from mod.common import minecraftEnum

from Script_Lemon_Legend.QuModLibs.Modules.EntityComps.Server import QBaseEntityComp
from Script_Lemon_Legend.QuModLibs.Server import *
from Script_Lemon_Legend.common.utils.logging import logging
from Script_Lemon_Legend.common.utils.ItemFactory import ItemFactory
from Script_Lemon_Legend.server.utils.serverUtils import compFactory


class _EnchantData(object):

    def __init__(self, enchantDict):
        self.enchantId = enchantDict.get("id", -1)
        self.level = enchantDict.get("lvl", 0)
        self.modEnchant = enchantDict.get("modEnchant", None)


class PlayerEnchantmentComp(QBaseEntityComp):
    def __init__(self, playerId):
        QBaseEntityComp.__init__(self)
        self.playerId = playerId
        self.magneticLevel = 0  # 磁力等级
        self.weightlessnessLevel = 0  # 失重等级
        self.magicProtectionLevel = 0  # 魔法保护等级
        self.starRecoveryMap = {}  # 星芒修补计时器映射

    def handleTakeOff(self, enchantmentList):
        if enchantmentList is None:
            return
        enchantDataList = [_EnchantData(enchantDict) for enchantDict in enchantmentList]
        for enchantData in enchantDataList:
            if enchantData.modEnchant == "legend_forest:magnetic_force":
                self.magneticLevel = max(0, self.magneticLevel - enchantData.level)
                self.changeMagneticLevel()
            elif enchantData.modEnchant == "legend_forest:weightlessness":
                self.weightlessnessLevel = max(0, self.weightlessnessLevel - enchantData.level)
                self.changeWeightlessnessLevel()
            elif enchantData.modEnchant == "legend_forest:magic_protection":
                self.magicProtectionLevel = max(0, self.magicProtectionLevel - enchantData.level)
                self.changeMagicProtectionLevel()

    def handlePutOn(self, enchantmentList):
        if enchantmentList is None:
            return
        enchantDataList = [_EnchantData(enchantDict) for enchantDict in enchantmentList]
        for enchantData in enchantDataList:
            if enchantData.modEnchant == "legend_forest:magnetic_force":
                self.magneticLevel += enchantData.level
                self.changeMagneticLevel()
            elif enchantData.modEnchant == "legend_forest:weightlessness":
                self.weightlessnessLevel += enchantData.level
                self.changeWeightlessnessLevel()
            elif enchantData.modEnchant == "legend_forest:magic_protection":
                self.magicProtectionLevel += enchantData.level
                self.changeMagicProtectionLevel()

    def handleTakeOffWithItem(self, enchantmentList, itemDict):
        if enchantmentList is None:
            return
        enchantDataList = [_EnchantData(enchantDict) for enchantDict in enchantmentList]
        for enchantData in enchantDataList:
            if enchantData.modEnchant == "legend_forest:star_recovery":
                timerId = self.starRecoveryMap.get(enchantData.enchantId)
                if timerId is not None:
                    gameComp = compFactory.CreateGame(levelId)
                    gameComp.CancelTimer(timerId)
                    logging.debug("为玩家物品{}移除星芒修补定时器".format(itemDict.get("newItemName")))
                    del self.starRecoveryMap[enchantData.enchantId]

    def handlePutOnWithItem(self, enchantmentList, itemDict):
        if enchantmentList is None:
            return
        enchantDataList = [_EnchantData(enchantDict) for enchantDict in enchantmentList]
        for enchantData in enchantDataList:
            # 星芒修补
            if enchantData.modEnchant == "legend_forest:star_recovery":

                def recoverFunc():
                    comp = compFactory.CreateItem(self.playerId)
                    carriedItem = comp.GetPlayerItem(minecraftEnum.ItemPosType.CARRIED, 0, True)
                    if not carriedItem:
                        return
                    # 判断当前是否为夜晚
                    timeComp = compFactory.CreateTime(levelId)
                    if timeComp.GetTime() % 24000 < 13000:
                        return
                    comp.SetItemDurability(
                        minecraftEnum.ItemPosType.CARRIED, 0, ItemFactory(carriedItem).getDurability() + 1
                    )

                gameComp = compFactory.CreateGame(levelId)
                timerId = gameComp.AddRepeatedTimer(5, recoverFunc)
                self.starRecoveryMap[enchantData.enchantId] = timerId
                logging.debug("为玩家物品{}添加星芒修补定时器".format(itemDict.get("newItemName")))

    def changeMagneticLevel(self):
        """磁力"""
        area = self.magneticLevel * 0.5 + 1
        comp = serverApi.GetEngineCompFactory().CreatePlayer(self.playerId)
        logging.debug("设置玩家磁力区域: {}".format(area))
        comp.SetPickUpArea((area, area, area))

    def changeWeightlessnessLevel(self):
        """失重"""
        gameComp = compFactory.CreateGame(levelId)
        gravityComp = compFactory.CreateGravity(self.playerId)

        levelGravity = gameComp.GetLevelGravity()
        gravity = levelGravity + self.weightlessnessLevel * 0.015 + (0.015 if self.weightlessnessLevel > 0 else 0)
        logging.debug("设置玩家重力: {}".format(gravity))
        if not gravityComp.SetGravity(gravity):
            logging.warning("设置玩家重力失败，延时重试")
            gameComp.AddTimer(1, lambda: self.changeWeightlessnessLevel())

    def changeMagicProtectionLevel(self):
        """魔法保护"""
        entityComp = compFactory.CreateEntityEvent(self.playerId)
        damageSensor = (entityComp.GetComponents().get("minecraft:damage_sensor") or {}).get("triggers", [])
        triggerMap = {trigger.get("cause"): trigger for trigger in damageSensor if trigger.get("cause")}
        magicTrigger = triggerMap.get("magic") or {"cause": "magic"}  # type: dict[str, any]
        magicTrigger["damage_multiplier"] = max(
            0.2, 1 - 0.0375 * self.magicProtectionLevel - (0.05 if self.magicProtectionLevel > 0 else 0)
        )
        triggerMap["magic"] = magicTrigger
        damageSensor = list(triggerMap.values())
        targetJson = '{"triggers": %s}' % json.dumps(damageSensor)
        entityComp.AddActorComponent("minecraft:damage_sensor", targetJson)
