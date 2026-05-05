# -*- coding: utf-8 -*-
import random

from Script_Lemon_Legend.QuModLibs.Modules.Services.Server import BaseService, QRequests
from Script_Lemon_Legend.QuModLibs.Server import *
from Script_Lemon_Legend.server.entity.attack.attackComp import AttackComp
from Script_Lemon_Legend.server.entity.stateMachine.baseSkill import BaseSkill
from Script_Lemon_Legend.server.utils import serverUtils


class CounterSkill(BaseSkill):
    """
    盾反技能 - 格挡被击中后触发，高伤害 + 击退
    """

    def __init__(self):
        BaseSkill.__init__(self, skillId="shield_counter", cooldown=0.0, duration=1.5, triggersGcd=True)
        self.molangValue = 3.0

    def onEnter(self, skillManager):
        BaseSkill.onEnter(self, skillManager)
        entityId = skillManager.getEntityId()

        # 播放盾反音效
        serverUtils.playSoundAll(
            "legend_forest_mob.gozuki.counter", Entity(entityId).Pos, pitch=random.uniform(0.8, 1.0)
        )
        # 设置技能动画 (molangValue=3 -> counter 动画)
        BaseService().syncRequest(
            "*", "entity/client/skill/setSkillAnimate", QRequests.Args(entityId, self.molangValue)
        )

        # 盾反攻击: 120度角, 3.5格范围, 高伤害
        attackComp = skillManager.getAttackComp()  # type: AttackComp
        attackComp.setSectorAttackArgs(
            delayTime=0.5,
            distance=3.5,
            angle=120,
            damageList=[6, 9, 13],
            checkBlock=True,
            knocked=True
        )

    def onExit(self, skillManager):
        BaseSkill.onExit(self, skillManager)
        entityId = skillManager.getEntityId()
        BaseService().syncRequest("*", "entity/client/skill/setSkillAnimate", QRequests.Args(entityId, 0.0))
