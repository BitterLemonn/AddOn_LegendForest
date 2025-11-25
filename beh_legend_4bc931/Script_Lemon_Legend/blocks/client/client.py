# -*- coding: utf-8 -*-
from ...QuModLibs.Client import *
from ...QuModLibs.Modules.Services.Client import BaseService
from ...QuModLibs.Modules.Services.Globals import QRequests
from ...data import biomeData
from ...utils.clientUtils import compFactory


@BaseService.Init
class ClientService(BaseService):

    def __init__(self):
        BaseService.__init__(self)

    @BaseService.Listen(Events.ClientItemUseOnEvent)
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