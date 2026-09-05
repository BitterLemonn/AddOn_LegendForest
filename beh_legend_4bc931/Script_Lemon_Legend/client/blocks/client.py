# -*- coding: utf-8 -*-
from Script_Lemon_Legend.QuModLibs.Client import *
from Script_Lemon_Legend.QuModLibs.Modules.Services.Client import BaseService
from Script_Lemon_Legend.client.utils.clientUtils import compFactory
from Script_Lemon_Legend.common.data import biomeData


@BaseService.Init
class ClientService(BaseService):

    def __init__(self):
        BaseService.__init__(self)

    @BaseService.Listen("ClientItemUseOnEvent")
    def onClientItemUseOnEvent(self, data):
        itemDict = data["itemDict"]
        pos = data["x"], data["y"], data["z"]
        # --------森林复苏锚放置----------
        if itemDict["newItemName"] == "legend_forest:forest_anchor":
            comp = compFactory.CreateBiome(levelId)
            biomeName = comp.GetBiomeName(pos)
            if biomeName not in biomeData.BiomesEnum.getShimmerBiomes():
                data["ret"] = True
                comp = compFactory.CreateGame(levelId)
                comp.SetTipMessage("§6森林复苏锚只能在微光森林中放置§r")
