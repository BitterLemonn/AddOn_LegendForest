from ..QuModLibs.Client import *

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
    pos = data["pos"]
    comp = compFactory.CreateCustomAudio(levelId)
    comp.PlayCustomMusic(soundName, pos, entityId=playerId)
