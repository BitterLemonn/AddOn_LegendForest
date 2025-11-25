from mod.common import minecraftEnum

from ...QuModLibs.Client import *
from ...QuModLibs.Modules.Services.Client import BaseService
from ...QuModLibs.Modules.Services.Globals import QRequests
from ...utils.clientUtils import compFactory


@BaseService.Init
class ItemClientService(BaseService):

    def __init__(self):
        BaseService.__init__(self)
        self.itemComp = compFactory.CreateItem(playerId)
        self.itemComp.GetUserDataInEvent("ClientItemTryUseEvent")

    @BaseService.Listen(Events.ClientItemTryUseEvent)
    def onClientItemTryUseEvent(self, data):
        offItem = self.itemComp.GetPlayerItem(minecraftEnum.ItemPosType.OFFHAND, 0, True)
        if offItem and offItem["newItemName"] == "legend_forest:book_disenchanted":
            data["cancel"] = True
            self.syncRequest("items/server/disenchant", QRequests.Args(data))
