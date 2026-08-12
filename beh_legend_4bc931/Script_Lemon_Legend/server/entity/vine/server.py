# -*- coding: utf-8 -*-
from Script_Lemon_Legend.QuModLibs.Modules.Services.Server import BaseService
from Script_Lemon_Legend.QuModLibs.Server import *
from Script_Lemon_Legend.server.utils import serverUtils
from Script_Lemon_Legend.server.utils.serverUtils import compFactory
from mod.common import minecraftEnum

enum = serverApi.GetMinecraftEnum()


@BaseService.Init
class SpawnVineServerService(BaseService):
    def __init__(self):
        BaseService.__init__(self)
        self.gameComp = compFactory.CreateGame(levelId)
        self.damageList = [0, 3, 5, 8]

    @BaseService.Listen("OnMobHitMobServerEvent")
    def onMobHitMobServerEvent(self, data):
        def onPlayerCanMove():
            playerComp.SetPlayerMovable(True)

        def onMobCanMove():
            aiComp.SetBlockControlAi(True, False)

        dataComp = compFactory.CreateExtraData(data["mobId"])
        isAttack = dataComp.GetExtraData("attack")
        isHurt = dataComp.GetExtraData("hurt")

        if not isAttack or isHurt:
            return

        for entityId in data["hittedMobList"]:
            if Entity(entityId).Identifier in frozenset(["legend_forest:spawn_vine", "legend_forest:malfurion"]):
                continue

            effectComp = compFactory.CreateEffect(entityId)
            effectComp.AddEffectToEntity("poison", 5, 0, True)

            dataComp.SetExtraData("hurt", True)
            serverUtils.doHurt(
                data["mobId"], self.damageList, entityId, minecraftEnum.ActorDamageCause.Magic, False, False
            )

            if serverUtils.playerIsNotCreative(entityId):
                playerComp = compFactory.CreatePlayer(entityId)
                playerComp.SetPlayerMovable(False)
                self.gameComp.AddTimer(2.0, lambda: onPlayerCanMove())

            else:
                aiComp = compFactory.CreateControlAi(entityId)
                aiComp.SetBlockControlAi(False, False)
                self.gameComp.AddTimer(2.0, lambda: onMobCanMove())

    @BaseService.Listen("AddEntityServerEvent")
    def onAddEntityServerEvent(self, data):
        if data["engineTypeStr"] == "legend_forest:spawn_vine":
            entityId = data["id"]
            comp = compFactory.CreatePlayer(entityId)
            comp.OpenPlayerHitMobDetection()
            Call("*", "setShadowFalse", entityId)

    @BaseService.Listen("EntityDefinitionsEventServerEvent")
    def onEntityDefinitionsEventServerEvent(self, data):
        if Entity(data["entityId"]).Identifier == "legend_forest:spawn_vine" and data["eventName"] == "legend_forest:attack":
            entityComp = compFactory.CreateExtraData(data["entityId"])
            entityComp.SetExtraData("attack", True)
