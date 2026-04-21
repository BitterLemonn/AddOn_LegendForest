# -*- coding=utf-8 -*-
import random

from Script_Lemon_Legend.common.utils import commonUtils
from Script_Lemon_Legend.server.entity.malfurion.malfurionSkillComp import MalfurionSkillComp
from Script_Lemon_Legend.QuModLibs.Modules.EntityComps.Server import QBaseEntityComp
from Script_Lemon_Legend.server.utils.serverUtils import compFactory, getDistance
from Script_Lemon_Legend.QuModLibs.Server import *


@QBaseEntityComp.regEntity(
    "legend_forest:malfurion",
)
class BehaviorComp(QBaseEntityComp):
    """
    森茂祭司行为组件
    """

    def __init__(self):
        QBaseEntityComp.__init__(self)
        self.targetComp = compFactory.CreateAction(self.entityId)
        self.targetId = None  # type: str | None

    def onBind(self):
        QBaseEntityComp.onBind(self)
        self.targetComp = compFactory.CreateAction(self.entityId)

    def onGameTick(self):
        QBaseEntityComp.onGameTick(self)
        oldTargetId = self.targetId
        self.targetId = self.targetComp.GetAttackTarget()
        self.targetId = self.targetId if self.targetId != "-1" else None
        if oldTargetId != self.targetId:
            self.changeTarget(oldTargetId, self.targetId)

    def changeTarget(self, oldTargetId, newTargetId):
        if not oldTargetId and newTargetId:
            aiComp = AIComp.getComp(self.entityId) or AIComp()
            aiComp.rebind(self.entityId)
        elif oldTargetId and not newTargetId:
            aiComp = AIComp.getComp(self.entityId)
            if aiComp:
                aiComp.unbind()


class AIComp(QBaseEntityComp):
    """
    森茂祭司AI组件
    """

    def __init__(self):
        QBaseEntityComp.__init__(self)
        self.skillComp = None  # type: MalfurionSkillComp|None
        self.canUseSkill = False
        self.lastCountDamage = 0.0

        self.attackComp = compFactory.CreateAction(self.entityId)

    def onBind(self):
        self.skillComp = MalfurionSkillComp.getComp(self.entityId)  # type: MalfurionSkillComp
        self.attackComp = compFactory.CreateAction(self.entityId)

        QBaseEntityComp.onBind(self)
        self.skillComp.addListener(self.onSkillCooldownChange)

        self.canUseSkill = self.skillComp.getIsInCooldown() == False
        if self.canUseSkill:
            self.randomCastSkill()

    def onUnBind(self):
        QBaseEntityComp.onUnBind(self)
        self.skillComp.removeListener(self.onSkillCooldownChange)

    def addDamageCount(self, damage):
        # 累积伤害计数 如果距离上次瞬移受伤超过30点 则触发瞬移
        self.lastCountDamage += damage
        if self.lastCountDamage >= 30.0:
            self.skillComp.forceCastSkill(self.skillComp.Skill.TELEPORT)

    def resetDamageCount(self):
        self.lastCountDamage = 0

    def onSkillCooldownChange(self, isOffCooldown):
        self.canUseSkill = isOffCooldown
        if self.canUseSkill:
            self.randomCastSkill()

    def _afterVine(self):
        weightMap = {
            self.skillComp.Skill.NORMAL_ATTACK: 0.5,
            self.skillComp.Skill.TELEPORT: 0.3,
            self.skillComp.Skill.ICE_THORN: 0.2,
        }
        skill = commonUtils.weightChoice(weightMap)
        self.skillComp.castSkill(skill)

    def randomCastSkill(self):
        # 获取仇恨目标
        targetId = self.attackComp.GetAttackTarget()
        if not targetId:
            return

        # 获取距离
        distance = getDistance(self.entityId, targetId)
        if distance < 10:
            weightMap = {self.skillComp.Skill.VINE_CIRCLE: 0.7, self.skillComp.Skill.NORMAL_ATTACK: 0.3}
            skill = commonUtils.weightChoice(weightMap)
            if skill == self.skillComp.Skill.VINE_CIRCLE:
                self.skillComp.castSkill(skill, self._afterVine)
            else:
                self.skillComp.castSkill(skill)
        elif distance < 15:
            weightMap = {
                self.skillComp.Skill.VINE_CHAIN: 0.5,
                self.skillComp.Skill.ICE_THORN: 0.3,
                self.skillComp.Skill.FIRE_SPELL: 0.2,
            }
            skill = commonUtils.weightChoice(weightMap)
            if skill == self.skillComp.Skill.VINE_CHAIN:
                self.skillComp.castSkill(skill, self._afterVine)
            else:
                self.skillComp.castSkill(skill)
        elif distance < 25:
            weightMap = {
                self.skillComp.Skill.ICE_THORN: 0.5,
                self.skillComp.Skill.VINE_CHAIN: 0.2,
                self.skillComp.Skill.FIRE_SPELL: 0.3,
            }
            skill = commonUtils.weightChoice(weightMap)
            if skill == self.skillComp.Skill.VINE_CHAIN:
                self.skillComp.castSkill(skill, self._afterVine)
            else:
                self.skillComp.castSkill(skill)
        else:
            weightMap = {
                self.skillComp.Skill.FIRE_SPELL: 0.5,
                self.skillComp.Skill.ICE_THORN: 0.3,
                self.skillComp.Skill.NORMAL_ATTACK: 0.2,
            }
            self.skillComp.castSkill(commonUtils.weightChoice(weightMap))
