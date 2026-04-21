# -*- coding: utf-8 -*-
import random

from Script_Lemon_Legend.QuModLibs.Modules.Services.Server import BaseService, QRequests
from Script_Lemon_Legend.QuModLibs.Server import *
from Script_Lemon_Legend.server.entity.attack.attackComp import AttackComp
from Script_Lemon_Legend.server.entity.stateMachine.baseSkill import BaseSkill
from Script_Lemon_Legend.server.utils import serverUtils
from Script_Lemon_Legend.server.utils.serverUtils import compFactory


class FireSpellSkill(BaseSkill):
    """
    火焰法术技能
    """

    def __init__(self):
        BaseSkill.__init__(self, skillId="fire_spell", cooldown=4.0, duration=2.25)
        self.molangValue = 102.0

    def onEnter(self, skillManager):
        # type: ("FireSpellSkill", "MalfurionSkillComp") -> None
        BaseSkill.onEnter(self, skillManager)
        entityId = skillManager.getEntityId()

        # 触发生物事件
        eventComp = compFactory.CreateEntityEvent(entityId)
        eventComp.TriggerCustomEvent(entityId, "legend_forest:skill_start")

        # 设置技能动画
        BaseService().syncRequest(
            "*", "entity/client/skill/setSkillAnimate", QRequests.Args(entityId, self.molangValue)
        )
        # 播放施法音效
        serverUtils.playSoundAll(
            "legend_forest_mob.malfurion.fire_spell.cast", Entity(entityId).Pos, pitch=random.uniform(0.7, 1.1)
        )

        attackComp = skillManager.getAttackComp()  # type: AttackComp
        # 火焰法术技能伤害
        timeLine = [1.6, 1.8, 2.0, 2.2, 2.4]
        comp = compFactory.CreateAction(entityId)
        targetId = comp.GetAttackTarget()
        targetPos = Entity(targetId).Pos
        for t in timeLine:
            attackComp.summonEntity(
                delayTime=t,
                entityName="legend_forest:meteorite",
                pos=(
                    targetPos[0] + random.uniform(-2.0, 2.0),
                    targetPos[1] + 8,
                    targetPos[2] + random.uniform(-2.0, 2.0),
                ),
            )

    def onExit(self, skillManager):
        # type: ("FireSpellSkill", "MalfurionSkillComp") -> None
        BaseSkill.onExit(self, skillManager)

        # 重置技能动画
        entityId = skillManager.getEntityId()
        BaseService().syncRequest("*", "entity/client/skill/setSkillAnimate", QRequests.Args(entityId, 0.0))
        # 触发生物事件
        eventComp = compFactory.CreateEntityEvent(entityId)
        eventComp.TriggerCustomEvent(entityId, "legend_forest:skill_end")
