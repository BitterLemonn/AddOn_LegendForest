# -*- coding: utf-8 -*-
import random

from Script_Lemon_Legend.QuModLibs.Modules.Services.Server import BaseService, QRequests
from Script_Lemon_Legend.QuModLibs.Server import *
from Script_Lemon_Legend.server.entity.attack.attackComp import AttackComp
from Script_Lemon_Legend.server.entity.stateMachine.baseSkill import BaseSkill
from Script_Lemon_Legend.server.utils import serverUtils


class HeavyCleaveSkill(BaseSkill):
    """
    重劈技能 - 斧变种高伤害宽面攻击 + 击退
    """

    def __init__(self):
        BaseSkill.__init__(self, skillId="axe_heavy_cleave", cooldown=2.5, duration=1.5)
        self.molangValue = 2.0

    def onEnter(self, skillManager):
        BaseSkill.onEnter(self, skillManager)
        entityId = skillManager.getEntityId()

        # 播放重击音效
        serverUtils.playSoundAll(
            "legend_forest_mob.gozuki.heavy_attack", Entity(entityId).Pos, pitch=random.uniform(0.6, 0.8)
        )
        # 设置技能动画 (molangValue=2 -> attack1)
        BaseService().syncRequest(
            "*", "entity/client/skill/setSkillAnimate", QRequests.Args(entityId, self.molangValue)
        )

        # 重劈攻击: 150度角, 4格范围, 高伤害 + 击退
        attackComp = skillManager.getAttackComp()  # type: AttackComp
        attackComp.setSectorAttackArgs(
            delayTime=0.8,
            distance=4.0,
            angle=150,
            damageList=[5, 7, 10],
            checkBlock=True,
            knocked=True
        )

    def onExit(self, skillManager):
        BaseSkill.onExit(self, skillManager)
        entityId = skillManager.getEntityId()
        BaseService().syncRequest("*", "entity/client/skill/setSkillAnimate", QRequests.Args(entityId, 0.0))
