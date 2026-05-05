# -*- coding: utf-8 -*-
import random

from Script_Lemon_Legend.QuModLibs.Modules.Services.Server import BaseService, QRequests
from Script_Lemon_Legend.QuModLibs.Server import *
from Script_Lemon_Legend.server.entity.stateMachine.baseSkill import BaseSkill
from Script_Lemon_Legend.server.utils import serverUtils


class BlockSkill(BaseSkill):
    """
    格挡技能 - 盾变种举盾防御，持续3秒
    期间受到攻击会累积 hitCount，>=2次触发强制盾反
    """

    def __init__(self):
        BaseSkill.__init__(self, skillId="shield_block", cooldown=4.0, duration=3.0, triggersGcd=False)
        self.molangValue = 1.0
        self._hitCount = 0

    def onEnter(self, skillManager):
        BaseSkill.onEnter(self, skillManager)
        self._hitCount = 0
        entityId = skillManager.getEntityId()

        # 播放举盾音效
        serverUtils.playSoundAll(
            "legend_forest_mob.gozuki.block", Entity(entityId).Pos, pitch=random.uniform(0.9, 1.1)
        )
        # 设置技能动画 (molangValue=1 -> block 动画)
        BaseService().syncRequest(
            "*", "entity/client/skill/setSkillAnimate", QRequests.Args(entityId, self.molangValue)
        )

        # 通知 AIComp 进入格挡状态
        from Script_Lemon_Legend.server.entity.gozuki.behaviorComp import AIComp
        aiComp = AIComp.getComp(entityId)
        if aiComp:
            aiComp.setBlocking(True)

    def onExit(self, skillManager):
        BaseSkill.onExit(self, skillManager)
        entityId = skillManager.getEntityId()
        BaseService().syncRequest("*", "entity/client/skill/setSkillAnimate", QRequests.Args(entityId, 0.0))

        # 通知 AIComp 退出格挡状态
        from Script_Lemon_Legend.server.entity.gozuki.behaviorComp import AIComp
        aiComp = AIComp.getComp(entityId)
        if aiComp:
            aiComp.setBlocking(False)

    def onBlockHit(self, skillManager):
        """格挡期间被击中时调用"""
        self._hitCount += 1
        if self._hitCount >= 2:
            # 强制盾反: 打断格挡，强制释放 counter
            skillComp = skillManager
            skillComp.interruptCurrentSkill()
            skillComp.forceCastSkill("shield_counter")

    def canCast(self, manager):
        return True
