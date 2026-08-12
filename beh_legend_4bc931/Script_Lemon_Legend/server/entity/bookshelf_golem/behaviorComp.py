# -*- coding: utf-8 -*-
import random

from Script_Lemon_Legend.QuModLibs.Modules.EntityComps.Server import QBaseEntityComp
from Script_Lemon_Legend.QuModLibs.Server import Entity
from Script_Lemon_Legend.server.entity.bookshelf_golem import decision
from Script_Lemon_Legend.server.entity.bookshelf_golem.skillComp import BookshelfGolemSkillComp
from Script_Lemon_Legend.server.utils.serverUtils import compFactory, getDistance


@QBaseEntityComp.regEntity("legend_forest:bookshelf_golem")
class BehaviorComp(QBaseEntityComp):
    def __init__(self):
        QBaseEntityComp.__init__(self)
        self._actionComp = None
        self._definitionComp = None
        self._active = False

    def onBind(self):
        QBaseEntityComp.onBind(self)
        self._actionComp = compFactory.CreateAction(self.entityId)
        self._definitionComp = compFactory.CreateEntityDefinitions(self.entityId)

    def onGameTick(self):
        QBaseEntityComp.onGameTick(self)
        targetId = self._actionComp.GetAttackTarget()
        active = bool(targetId and targetId != "-1" and self._definitionComp.GetVariant() == 2)
        if active == self._active:
            return
        self._active = active
        aiComp = AIComp.getComp(self.entityId)
        if active:
            (aiComp or AIComp()).rebind(self.entityId)
        elif aiComp:
            aiComp.unbind()


class AIComp(QBaseEntityComp):
    MAX_HISTORY = 3

    def __init__(self):
        QBaseEntityComp.__init__(self)
        self._skillComp = None  # type: BookshelfGolemSkillComp|None
        self._actionComp = None
        self._canUseSkill = False
        self._groundCooldown = 0
        self._leapCooldown = 0
        self._shockwaveCooldown = 0
        self._history = []

    def onBind(self):
        QBaseEntityComp.onBind(self)
        self._skillComp = BookshelfGolemSkillComp.getComp(self.entityId)
        self._actionComp = compFactory.CreateAction(self.entityId)
        self._skillComp.addListener(self._onCooldownChange)
        self._canUseSkill = not self._skillComp.getIsInCooldown()

    def onUnBind(self):
        if self._skillComp:
            self._skillComp.removeListener(self._onCooldownChange)
            self._skillComp.interruptCurrentSkill()
        self._skillComp = None
        self._actionComp = None
        QBaseEntityComp.onUnBind(self)

    def onGameTick(self):
        QBaseEntityComp.onGameTick(self)
        self._groundCooldown = max(0, self._groundCooldown - 1)
        self._leapCooldown = max(0, self._leapCooldown - 1)
        self._shockwaveCooldown = max(0, self._shockwaveCooldown - 1)
        if self._canUseSkill:
            self._decideNextSkill()

    def _onCooldownChange(self, isOffCooldown):
        self._canUseSkill = isOffCooldown

    def _decideNextSkill(self):
        targetId = self._actionComp.GetAttackTarget()
        if not targetId or targetId == "-1":
            return
        health = Entity(self.entityId).Health
        skillId = decision.chooseSkill(
            getDistance(self.entityId, targetId),
            health.Value <= health.Max * 0.5,
            self._groundCooldown == 0,
            self._leapCooldown == 0,
            self._shockwaveCooldown == 0,
            self._history,
        )
        if not skillId or not self._skillComp.castSkill(skillId):
            return
        self._canUseSkill = False
        self._history.append(skillId)
        if len(self._history) > self.MAX_HISTORY:
            self._history.pop(0)
        if skillId in decision.GROUND_SKILLS:
            durations = {decision.GROUND_NORMAL: 2.5, decision.GROUND_FAST: 2.25, decision.GROUND_HARD: 3.75}
            self._groundCooldown = int((durations[skillId] + random.uniform(3.0, 10.0)) * 30)
        elif skillId == decision.LEAP_SLAM:
            self._leapCooldown = int((2.0 + 6.0) * 30)
        elif skillId == decision.SHOCKWAVE:
            self._shockwaveCooldown = int((1.7 + 8.0) * 30)
