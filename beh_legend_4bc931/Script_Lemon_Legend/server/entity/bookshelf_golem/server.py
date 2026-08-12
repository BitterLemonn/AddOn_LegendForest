# -*- coding: utf-8 -*-
import random

from mod.common import minecraftEnum
from Script_Lemon_Legend.QuModLibs.Modules.Services.Server import BaseService
from Script_Lemon_Legend.QuModLibs.Server import *
from Script_Lemon_Legend.common.utils import commonUtils
from Script_Lemon_Legend.common.utils.ItemFactory import ItemFactory
from Script_Lemon_Legend.server.entity.bookshelf_golem.behaviorComp import BehaviorComp
from Script_Lemon_Legend.server.entity.bookshelf_golem.skillComp import BookshelfGolemSkillComp
from Script_Lemon_Legend.server.utils import serverUtils
from Script_Lemon_Legend.server.utils.serverUtils import compFactory


@BaseService.Init
class BookshelfGolemServerService(BaseService):
    IDENTIFIER = "legend_forest:bookshelf_golem"

    def __init__(self):
        BaseService.__init__(self)
        compFactory.CreateItem(levelId).GetUserDataInEvent("OnPlayerBlockedByShieldAfterServerEvent")

    @BaseService.Listen("OnPlayerBlockedByShieldAfterServerEvent")
    def onPlayerBlockedByShieldAfterServerEvent(self, data):
        if Entity(data["sourceId"]).Identifier != self.IDENTIFIER:
            return

        itemComp = compFactory.CreateItem(data["playerId"])
        for posType in (minecraftEnum.ItemPosType.CARRIED, minecraftEnum.ItemPosType.OFFHAND):
            shield = itemComp.GetPlayerItem(posType, 0, True)
            if shield and ItemFactory.compireItems(shield, data["itemDict"]):
                break
        else:
            return

        player = Entity(data["playerId"])
        itemEntityId = System.CreateEngineItemEntity(shield, player.Dm, player.Pos)
        if not itemEntityId:
            return
        if posType == minecraftEnum.ItemPosType.CARRIED:
            removed = itemComp.SetInvItemNum(itemComp.GetSelectSlotId(), 0)
        else:
            removed = itemComp.SetEntityItem(posType, None, 0)
        if not removed:
            System.DestroyEntity(itemEntityId)
            return
        motion = commonUtils.unitVector(player.Pos, Entity(data["sourceId"]).Pos)
        compFactory.CreateActorMotion(itemEntityId).SetMotion((motion[0] / 3, 0.05, motion[2] / 3))

    @BaseService.Listen("HealthChangeBeforeServerEvent")
    def onHealthChangeBeforeServerEvent(self, data):
        if Entity(data["entityId"]).Identifier != self.IDENTIFIER or data["to"] > 0:
            return
        data["cancel"] = True
        extraComp = compFactory.CreateExtraData(data["entityId"])
        if extraComp.GetExtraData("legend_forest:isDead"):
            return
        extraComp.SetExtraData("legend_forest:isDead", True)

        def die():
            skillComp = BookshelfGolemSkillComp.getComp(data["entityId"])
            if skillComp:
                skillComp.interruptCurrentSkill()
            Entity(data["entityId"]).Health.SetValue(0.1)
            compFactory.CreateEntityEvent(data["entityId"]).TriggerCustomEvent(data["entityId"], "legend_forest:die")

        serverUtils.runNextTick(die)

    @BaseService.Listen("EntityDefinitionsEventServerEvent")
    def onEntityDefinitionsEventServerEvent(self, data):
        if Entity(data["entityId"]).Identifier != self.IDENTIFIER or data["eventName"] != "legend_forest:dead":
            return
        extraComp = compFactory.CreateExtraData(data["entityId"])
        if extraComp.GetExtraData("legend_forest:lootSpawned"):
            return
        extraComp.SetExtraData("legend_forest:lootSpawned", True)

        pos = commonUtils.getIntPos(Entity(data["entityId"]).FootPos)
        dimensionId = Entity(data["entityId"]).Dm
        nearPlayer = Entity(data["entityId"]).getNearPlayer()
        items = compFactory.CreateLoot(nearPlayer or data["entityId"]).GetLootItems(
            "loot_tables/legend_forest/entities/bookshelf_golem.json"
        )
        compFactory.CreateBlockInfo(data["entityId"]).SetBlockNew(pos, {"name": "minecraft:chest"}, 1, dimensionId)

        def fillChest():
            slots = list(range(27))
            random.shuffle(slots)
            itemComp = compFactory.CreateItem(levelId)
            for item, slotId in zip(items, slots):
                itemComp.SpawnItemToContainer(item, slotId, pos, dimensionId)

        serverUtils.runNextTick(fillChest)
