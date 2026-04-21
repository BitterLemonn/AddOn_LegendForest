# coding=utf-8
from Script_Lemon_Legend.common.utils import commonUtils

from Script_Lemon_Legend.common.config import modConfig
from Script_Lemon_Legend.QuModLibs.Modules.Services.Server import BaseService
from Script_Lemon_Legend.QuModLibs.Server import *
from Script_Lemon_Legend.server.utils import serverUtils
from Script_Lemon_Legend.server.utils.serverUtils import compFactory


@BaseService.Init
class AnchorService(BaseService):

    def __init__(self):
        BaseService.__init__(self)
        self.__anchorMap = {}
        self.__anchorOverList = []

    def setPlayerSpawnAnchor(self, playerId, pos, dimensionId):
        # 获取重生锚对应的玩家
        for player, anchor in self.__anchorMap.items():
            if anchor["pos"] == pos and anchor["dimensionId"] == dimensionId:
                self._removePlayerSpawnAnchor(player)
                break
        if playerId in self.__anchorOverList:
            self.__anchorOverList.remove(playerId)
        # 设置重生锚
        self.__anchorMap[playerId] = {"pos": pos, "dimensionId": dimensionId}
        spawnPos = (pos[0], pos[1] + 1, pos[2])
        compFactory.CreatePlayer(playerId).SetPlayerRespawnPos(spawnPos, dimensionId)
        compFactory.CreateMsg(playerId).NotifyOneMessage(playerId, commonUtils.FormatColorStr.GRAY + "已设置重生点")

    @BaseService.Listen(Events.PlayerRespawnFinishServerEvent)
    def _onPlayerRespawnFinish(self, data):
        playerId = data["playerId"]
        if playerId in self.__anchorOverList:
            self.__anchorOverList.remove(playerId)
            comp = compFactory.CreateMsg(levelId)
            comp.NotifyOneMessage(playerId, "你已充能的重生锚不存在或被阻挡")

        if playerId in self.__anchorMap:
            pos = self.__anchorMap[playerId]["pos"]
            dimensionId = self.__anchorMap[playerId]["dimensionId"]
            # 重生锚消耗
            comp = compFactory.CreateBlockState(levelId)
            blockState = comp.GetBlockStates(pos, dimensionId)
            level = blockState.get("legend_forest:charged_level", 1) - 1
            blockState.update({"legend_forest:charged_level": level})
            comp.SetBlockStates(pos, blockState, dimensionId)
            serverUtils.playSound("respawn_anchor.deplete", playerId, pos)
            # 重生锚消耗完毕
            if level <= 0:
                self._removePlayerSpawnAnchor(playerId)

    @BaseService.Listen(Events.ServerPlayerTryDestroyBlockEvent)
    def _onPlayerTryDestroyBlock(self, data):
        pos = (data["x"], data["y"], data["z"])
        blockName = data["fullName"]
        dimensionId = data["dimensionId"]

        if blockName in modConfig.RESPAWN_ANCHOR:
            # 获取重生锚对应的玩家
            for playerId, anchor in self.__anchorMap.items():
                if anchor["pos"] == pos and anchor["dimensionId"] == dimensionId:
                    self._removePlayerSpawnAnchor(playerId)
                    break

    def _removePlayerSpawnAnchor(self, playerId):
        if playerId in self.__anchorMap:
            self.__anchorMap.pop(playerId)
            if playerId not in self.__anchorOverList:
                self.__anchorOverList.append(playerId)
            comp = compFactory.CreateGame(levelId)
            spawnPos = comp.GetSpawnPosition()
            spawnDimension = comp.GetSpawnDimension()
            compFactory.CreatePlayer(playerId).SetPlayerRespawnPos(spawnPos, spawnDimension)
