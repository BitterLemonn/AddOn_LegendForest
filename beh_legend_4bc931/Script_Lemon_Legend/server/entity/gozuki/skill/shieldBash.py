# -*- coding: utf-8 -*-
import random

from Script_Lemon_Legend.QuModLibs.Modules.Services.Server import BaseService, QRequests
from Script_Lemon_Legend.QuModLibs.Server import *
from Script_Lemon_Legend.server.entity.attack.attackComp import AttackComp
from Script_Lemon_Legend.server.entity.stateMachine.baseSkill import BaseSkill
from Script_Lemon_Legend.server.utils import serverUtils


class ShieldBashSkill(BaseSkill):
    """
    盾击技能 - 盾变种快速前方盾击，短持续快恢复
    """

    def __init__(self):
        BaseSkill.__init__(self, skillId="shield_bash", cooldown=2.0, duration=0.5)
        self.molangValue = 2.0

    def onEnter(self, skillManager):
        BaseSkill.onEnter(self, skillManager)
        entityId = skillManager.getEntityId()

        # 播放盾击音效
        serverUtils.playSoundAll(
            "legend_forest_mob.gozuki.shield_bash", Entity(entityId).Pos, pitch=random.uniform(1.0, 1.2)
        )
        # 设置技能动画 (molangValue=2 -> shield_attack 动画)
        BaseService().syncRequest(
            "*", "entity/client/skill/setSkillAnimate", QRequests.Args(entityId, self.molangValue)
        )

        # 盾击攻击: 90度角, 2.5格范围, 低伤害
        attackComp = skillManager.getAttackComp()  # type: AttackComp
        attackComp.setSectorAttackArgs(
            delayTime=0.2,
            distance=2.5,
            angle=90,
            damageList=[2, 3, 5],
            checkBlock=True,
            knocked=True
        )

    def onExit(self, skillManager):
        BaseSkill.onExit(self, skillManager)
        entityId = skillManager.getEntityId()
        BaseService().syncRequest("*", "entity/client/skill/setSkillAnimate", QRequests.Args(entityId, 0.0))
