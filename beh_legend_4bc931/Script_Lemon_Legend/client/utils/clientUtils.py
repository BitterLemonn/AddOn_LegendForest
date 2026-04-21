# -*- coding: utf-8 -*-
from Script_Lemon_Legend.QuModLibs.Client import *

compFactory = clientApi.GetEngineCompFactory()


@AllowCall
@CallBackKey("swing")
def swing():
    comp = compFactory.CreatePlayer(playerId)
    comp.Swing()


@AllowCall
@CallBackKey("playSound")
def playSound(data):
    soundName = data["soundName"]
    pos = data.get("pos")
    volume = data.get("volume", 1.0)
    pitch = data.get("pitch", 1.0)

    if not pos:
        pos = Entity(playerId).Pos
    comp = compFactory.CreateCustomAudio(levelId)
    comp.PlayCustomMusic(soundName, pos, entityId=playerId, volume=volume, pitch=pitch)


@AllowCall
@CallBackKey("setShadowFalse")
def setShadowFalse(entityId):
    comp = compFactory.CreateModel(entityId)
    comp.SetEntityShadowShow(False)
