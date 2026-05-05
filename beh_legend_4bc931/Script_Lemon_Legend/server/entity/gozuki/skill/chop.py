# -*- coding: utf-8 -*-
import random

from Script_Lemon_Legend.QuModLibs.Modules.Services.Server import BaseService, QRequests
from Script_Lemon_Legend.QuModLibs.Server import *
from Script_Lemon_Legend.server.entity.attack.attackComp import AttackComp
from Script_Lemon_Legend.server.entity.stateMachine.baseSkill import BaseSkill
from Script_Lemon_Legend.server.utils import serverUtils


class ChopSkill(BaseSkill):
    """
    劈砍技能 - 斧变种基础攻击
    """

    def __init__(self):
        BaseSkill.__init__(self, skillId="axe_chop", cooldown=1.5, duration=1.5)
        self.molangValue = 1.0

    def onEnter(self, skillManager):
        BaseSkill.onEnter(self, skillManager)
        entityId = skillManager.getEntityId()

        # 播放攻击音效
        serverUtils.playSoundAll(
            "legend_forest_mob.gozuki.attack", Entity(entityId).Pos, pitch=random.uniform(0.8, 1.0)
        )
        # 设置技能动画 (molangValue=1 -> attack0)
        BaseService().syncRequest(
            "*", "entity/client/skill/setSkillAnimate", QRequests.Args(entityId, self.molangValue)
        )

        # 扇形攻击伤害: 120度角, 3.5格范围
        attackComp = skillManager.getAttackComp()  # type: AttackComp
        attackComp.setSectorAttackArgs(
            delayTime=0.7,
            distance=3.5,
            angle=120,
            damageList=[3, 4, 6],
            checkBlock=True,
            knocked=True
        )

    def onExit(self, skillManager):
        BaseSkill.onExit(self, skillManager)
        entityId = skillManager.getEntityId()
        # 重置动画
        BaseService().syncRequest("*", "entity/client/skill/setSkillAnimate", QRequests.Args(entityId, 0.0))
