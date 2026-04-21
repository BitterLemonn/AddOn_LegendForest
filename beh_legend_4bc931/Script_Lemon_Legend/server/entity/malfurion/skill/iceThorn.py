# -*- coding: utf-8 -*-
import random

from Script_Lemon_Legend.QuModLibs.Modules.Services.Server import BaseService, QRequests
from Script_Lemon_Legend.QuModLibs.Server import *
from Script_Lemon_Legend.server.entity.attack.attackComp import AttackComp
from Script_Lemon_Legend.server.entity.stateMachine.baseSkill import BaseSkill
from Script_Lemon_Legend.server.utils import serverUtils
from Script_Lemon_Legend.server.utils.serverUtils import compFactory


class IceThornSkill(BaseSkill):
    """
    冰刺技能
    """

    def __init__(self):
        BaseSkill.__init__(self, skillId="ice_thorn", cooldown=2.0, duration=1.0)
        self.molangValue = 101.0

    def onEnter(self, skillManager):
        # type: ("IceThornSkill", "MalfurionSkillComp") -> None
        BaseSkill.onEnter(self, skillManager)
        entityId = skillManager.getEntityId()

        # 触发生物事件
        eventComp = compFactory.CreateEntityEvent(entityId)
        eventComp.TriggerCustomEvent(entityId, "legend_forest:skill_start")

        # 播放施法音效
        serverUtils.playSoundAll(
            "legend_forest_mob.malfurion.ice_thorn.cast", Entity(entityId).Pos, pitch=random.uniform(0.7, 1.1)
        )
        # 设置技能动画
        BaseService().syncRequest(
            "*", "entity/client/skill/setSkillAnimate", QRequests.Args(entityId, self.molangValue)
        )

        attackComp = skillManager.getAttackComp()  # type: AttackComp
        # 冰刺技能伤害
        comp = compFactory.CreateAction(entityId)
        targetId = comp.GetAttackTarget()
        timeLine = [0.8, 1.5, 1.8]
        for t in timeLine:
            attackComp.setSectorProjectileAttackArgs(
                delayTime=t, targetId=targetId, angle=90, num=6, projectileName="legend_forest:ice_bolt"
            )

    def onExit(self, skillManager):
        # type: ("IceThornSkill", "MalfurionSkillComp") -> None
        BaseSkill.onExit(self, skillManager)
        # 重置技能动画
        entityId = skillManager.getEntityId()
        BaseService().syncRequest("*", "entity/client/skill/setSkillAnimate", QRequests.Args(entityId, 0.0))

        # 触发生物事件
        eventComp = compFactory.CreateEntityEvent(entityId)
        eventComp.TriggerCustomEvent(entityId, "legend_forest:skill_end")
