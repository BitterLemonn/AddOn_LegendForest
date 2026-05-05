# -*- coding: utf-8 -*-
import random

from Script_Lemon_Legend.QuModLibs.Modules.Services.Server import BaseService
from Script_Lemon_Legend.QuModLibs.Server import *
from Script_Lemon_Legend.common.utils import commonUtils
from Script_Lemon_Legend.server.utils import serverUtils
from Script_Lemon_Legend.server.utils.serverUtils import compFactory


@BaseService.Init
class GozukiServerService(BaseService):
    """
    牛头鬼服务类
    处理实体受伤事件，驱动盾反判定
    """

    def __init__(self):
        BaseService.__init__(self)

    @BaseService.Listen("DamageEvent")
    def onDamageEvent(self, data):
        entityId = data["entityId"]

        if Entity(entityId).Identifier == "legend_forest:gozuki_demon":
            from Script_Lemon_Legend.server.entity.gozuki.goals import _getState, _setSkillAnimate, _startGcd

            state = _getState(entityId)

            if state.get("blocking", False):
                data["damage"] = 0
                data["knock"] = False
                state["blockHitCount"] = state.get("blockHitCount", 0) + 1

                serverUtils.playSoundAll(
                    "item.shield.block", Entity(entityId).Pos, pitch=random.uniform(0.9, 1.1)
                )
                if state.get("blockHitCount", 0) >= 2:
                    srcId = data.get("srcId")
                    state["triggerCounter"] = True
                    state["blocking"] = False
                    state["blockHitCount"] = 0
                    serverUtils.playSoundAll(
                        "legend_forest_mob.gozuki.counter", Entity(entityId).Pos, pitch=random.uniform(0.8, 1.0)
                    )
                    _setSkillAnimate(entityId, 3.0)
                    if srcId and srcId != "-1":
                        compFactory.CreateGame(levelId).AddTimer(0.3, lambda: self._counterHit(entityId, srcId))
                    _startGcd(entityId, 2.5)

    def _counterHit(self, entityId, srcId):
        if Entity(entityId).Health.Value <= 0.1:
            return
        difficulty = compFactory.CreateGame(levelId).GetGameDiffculty()
        damageList = [10, 14, 18]
        damage = damageList[difficulty] if isinstance(damageList, list) else damageList
        compFactory.CreateHurt(srcId).Hurt(damage, 0, entityId, knocked=False)
        unitVector = commonUtils.unitVector(Entity(entityId).Pos, Entity(srcId).Pos)
        motion = (unitVector[0] * 1.5, 0.4, unitVector[2] * 1.5)
        if Entity(srcId).Identifier == "minecraft:player":
            compFactory.CreateActorMotion(srcId).SetPlayerMotion(motion)
        else:
            compFactory.CreateActorMotion(srcId).SetMotion(motion)
