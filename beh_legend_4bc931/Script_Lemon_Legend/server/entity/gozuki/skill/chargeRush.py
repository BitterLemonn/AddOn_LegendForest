# -*- coding: utf-8 -*-
import random

from Script_Lemon_Legend.QuModLibs.Server import *
from Script_Lemon_Legend.server.entity.attack.attackComp import AttackComp
from Script_Lemon_Legend.server.entity.stateMachine.baseSkill import BaseSkill
from Script_Lemon_Legend.server.utils import serverUtils


class ChargeRushSkill(BaseSkill):
    """
    冲撞技能 - 斧/盾变种共用，快速冲向目标并造成伤害
    """

    def __init__(self, isAxe=True):
        if isAxe:
            BaseSkill.__init__(self, skillId="charge_rush", cooldown=6.0, duration=2.0)
            self.damageList = [4, 6, 8]
        else:
            BaseSkill.__init__(self, skillId="charge_rush", cooldown=8.0, duration=2.0)
            self.damageList = [3, 5, 7]
        self.molangValue = 0  # 冲撞使用默认动画 (走动)
        self.isAxe = isAxe

    def onEnter(self, skillManager):
        BaseSkill.onEnter(self, skillManager)
        entityId = skillManager.getEntityId()

        # 播放冲锋音效
        serverUtils.playSoundAll(
            "legend_forest_mob.gozuki.charge", Entity(entityId).Pos, pitch=random.uniform(0.9, 1.1)
        )

        attackComp = skillManager.getAttackComp()  # type: AttackComp
        # 冲撞动量: 向目标冲刺
        attackComp.setMotion(delayTime=0.3)
        attackComp.setMotion(delayTime=0.8)
        # 1.0s后落地伤害: 90度角, 3格范围
        attackComp.setSectorAttackArgs(
            delayTime=1.0,
            distance=3.0,
            angle=90,
            damageList=self.damageList,
            checkBlock=True,
            knocked=True
        )

    def onExit(self, skillManager):
        BaseSkill.onExit(self, skillManager)
