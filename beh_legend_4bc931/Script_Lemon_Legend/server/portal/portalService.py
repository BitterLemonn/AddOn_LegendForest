# -*- coding: utf-8 -*-
from Script_Lemon_Legend.QuModLibs.Modules.Services.Server import BaseService
from Script_Lemon_Legend.QuModLibs.Server import *
from Script_Lemon_Legend.common.utils.logging import logging


class PortalManagerService(BaseService):

    def __init__(self):
        BaseService.__init__(self)
        self.inPortalBlockPlayers = {}  # 处于传送门方块内的玩家ID
        self.needCheckPosPlayers = {}  # 需要检查位置的玩家ID

    def addInPortalBlockPlayer(self, playerId):
        """添加处于传送门方块内的玩家ID"""
        if len(self.inPortalBlockPlayers) == 0:
            self.listenForEvent("OnScriptTickServer", self.onScriptTick)
        self.inPortalBlockPlayers[playerId] = 30

    def onScriptTick(self):
        """脚本每帧更新事件处理"""
        for playerId, time in self.inPortalBlockPlayers.items():
            if time > 0:
                self.inPortalBlockPlayers[playerId] = time - 1
        # 移除时间到期的玩家ID
        expiredPlayers = [playerId for playerId, time in self.inPortalBlockPlayers.items() if time <= 0]
        for playerId in expiredPlayers:
            del self.inPortalBlockPlayers[playerId]
        if len(self.inPortalBlockPlayers) == 0:
            self.unListenForEvent("OnScriptTickServer", self.onScriptTick)

    def changeDimension(self, playerId, fromDim, fromPos):
        """当玩家维度更改时 判断是否需要检查位置"""
        if playerId in self.inPortalBlockPlayers.keys():
            self.needCheckPosPlayers[playerId] = (fromDim, fromPos)
            del self.inPortalBlockPlayers[playerId]

    def isPlayerNeedCheckPos(self, playerId):
        """检查玩家是否需要检查位置"""
        return playerId in self.needCheckPosPlayers.keys()

    def getPlayerFromDimAndPos(self, playerId):
        """获取玩家的原始维度和位置"""
        fromDim, fromPos = self.needCheckPosPlayers.pop(playerId, None)
        return fromDim, fromPos
