# -*- coding: utf-8 -*-
import random

from Script_Lemon_Legend.QuModLibs.Modules.Services.Server import BaseService, QRequests
from Script_Lemon_Legend.QuModLibs.Server import *
from Script_Lemon_Legend.server.entity.attack.attackComp import AttackComp
from Script_Lemon_Legend.server.entity.stateMachine.baseSkill import BaseSkill
from Script_Lemon_Legend.server.utils import serverUtils
from Script_Lemon_Legend.server.utils.serverUtils import compFactory


class VineChain(BaseSkill):
    """
    普通攻击
    """

    def __init__(self):
        BaseSkill.__init__(self, skillId="vine_chain", cooldown=3.0, duration=2.35)
        self.molangValue = 103.0

    def onEnter(self, skillManager):
        # type: ("VineChain", "MalfurionSkillComp") -> None
        BaseSkill.onEnter(self, skillManager)
        entityId = skillManager.getEntityId()

        # 触发生物事件
        eventComp = compFactory.CreateEntityEvent(entityId)
        eventComp.TriggerCustomEvent(entityId, "legend_forest:skill_start")

        # 播放施法音效
        serverUtils.playSoundAll(
            "legend_forest_mob.malfurion.attack", Entity(entityId).Pos, pitch=random.uniform(0.7, 1.1)
        )
        # 设置技能动画
        BaseService().syncRequest(
            "*", "entity/client/skill/setSkillAnimate", QRequests.Args(entityId, self.molangValue)
        )

        # 召唤生物
        attackComp = skillManager.getAttackComp()  # type: AttackComp
        actorComp = compFactory.CreateAction(entityId)
        targetId = actorComp.GetAttackTarget()

        startPos = Entity(entityId).FootPos
        targetPos = Entity(targetId).FootPos

        attackComp.summonEntityLine(
            0.35, "legend_forest:spawn_vine", startPos, targetPos, count=random.randint(5, 8), summonDelay=0.25
        )

    def onExit(self, skillManager):
        # type: ("VineChain", "MalfurionSkillComp") -> None
        BaseSkill.onExit(self, skillManager)
        # 重置技能动画
        entityId = skillManager.getEntityId()
        BaseService().syncRequest("*", "entity/client/skill/setSkillAnimate", QRequests.Args(entityId, 0.0))

        # 触发生物事件
        eventComp = compFactory.CreateEntityEvent(entityId)
        eventComp.TriggerCustomEvent(entityId, "legend_forest:skill_end")
