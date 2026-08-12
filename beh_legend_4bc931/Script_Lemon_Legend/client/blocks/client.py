# -*- coding: utf-8 -*-
from Script_Lemon_Legend.QuModLibs.Client import *
from Script_Lemon_Legend.QuModLibs.Modules.Services.Client import BaseService, QRequests
from Script_Lemon_Legend.client.utils.clientUtils import compFactory
from Script_Lemon_Legend.common.data import biomeData


@BaseService.Init
class ClientService(BaseService):

    def __init__(self):
        BaseService.__init__(self)

    @BaseService.Listen("ClientItemUseOnEvent")
    def onClientItemUseOnEvent(self, data):
        blockName = data["blockName"]
        itemDict = data["itemDict"]
        pos = data["x"], data["y"], data["z"]
        # --------落叶堆叠放置--------
        if "legend_forest" in blockName and "leaves_cape" in blockName and "leaves_cape" in itemDict["newItemName"]:
            data["ret"] = True
            self.syncRequest("blocks/server/itemUseOn", QRequests.Args(data))
        # --------森林复苏锚放置----------
        elif itemDict["newItemName"] == "legend_forest:forest_anchor":
            comp = compFactory.CreateBiome(levelId)
            biomeName = comp.GetBiomeName(pos)
            if biomeName not in biomeData.BiomesEnum.getShimmerBiomes():
                data["ret"] = True
                comp = compFactory.CreateGame(levelId)
                comp.SetTipMessage("§6森林复苏锚只能在微光森林中放置§r")
