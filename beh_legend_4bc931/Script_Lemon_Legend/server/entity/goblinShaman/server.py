# -*- coding: utf-8 -*-
from Script_Lemon_Legend.QuModLibs.Server import *
from Script_Lemon_Legend.QuModLibs.Modules.Services.Server import BaseService


@BaseService.Init
class ShamanServerService(BaseService):
    def __init__(self):
        BaseService.__init__(self)

    @BaseService.Listen(Events.EntityDefinitionsEventServerEvent)
    def EntityDefinitionsEventServerEvent(self, data):
        entityId = data['entityId']
        event = data['eventName']
        if Entity(entityId).Identifier == "legend_forest:goblin" and event == "legend_forest:shaman_spelling":
            entityComp = serverApi.GetEngineCompFactory().CreateControlAi(entityId)

            def recover():
                entityComp.SetBlockControlAi(True)

            entityComp.SetBlockControlAi(False)
            serverApi.GetEngineCompFactory().CreateGame(levelId).AddTimer(2.0, recover)

            filters = {"all_of": [{"subject": "other", "test": "is_family", "value": "goblin"}]}
            comp = serverApi.GetEngineCompFactory().CreateGame(levelId)
            entityList = comp.GetEntitiesAround(entityId, 20, filters)

            for entity in entityList:
                effectComp = serverApi.GetEngineCompFactory().CreateEffect(entity)
                effectComp.AddEffectToEntity("regeneration", 6, 2, True)
                effectComp.AddEffectToEntity("strength", 5, 0, True)
