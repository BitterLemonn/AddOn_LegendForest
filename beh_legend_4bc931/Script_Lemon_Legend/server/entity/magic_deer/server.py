# -*- coding: utf-8 -*-
from Script_Lemon_Legend.QuModLibs.Modules.Services.Server import BaseService
from Script_Lemon_Legend.QuModLibs.Server import *
from Script_Lemon_Legend.common.config.modConfig import FOREST_DIMENSION_ID
from Script_Lemon_Legend.server.utils.serverUtils import compFactory

@BaseService.Init
class MagicDeerServerService(BaseService):
    @BaseService.Listen("AddEntityServerEvent")
    def onAddEntityServerEvent(self, data):
        if data.get("engineTypeStr") != "legend_forest:magic_deer":
            return
        dataComp = compFactory.CreateExtraData(data["id"])
        variant = dataComp.GetExtraData("legend_forest_birth_variant")
        if variant is None:
            variant = 1 if data.get("dimensionId") == FOREST_DIMENSION_ID else 0
            dataComp.SetExtraData("legend_forest_birth_variant", variant)
        compFactory.CreateEntityDefinitions(data["id"]).SetVariant(variant)
