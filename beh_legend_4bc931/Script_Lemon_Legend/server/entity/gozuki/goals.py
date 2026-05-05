# -*- coding: utf-8 -*-
import random

from Script_Lemon_Legend.QuModLibs.Modules.Services.Server import BaseService, QRequests
from Script_Lemon_Legend.QuModLibs.Server import *
from Script_Lemon_Legend.server.entity.attack.attackComp import AttackComp
from Script_Lemon_Legend.server.utils import serverUtils
from Script_Lemon_Legend.server.utils.serverUtils import compFactory, getDistance

compFactory = serverApi.GetEngineCompFactory()
CustomGoalCls = serverApi.GetCustomGoalCls()

_sharedState = {}


def _getState(entityId):
    if entityId not in _sharedState:
        _sharedState[entityId] = {
            "onGcd": False,
            "blockHitCount": 0,
            "triggerCounter": False,
            "blocking": False,
            "skillCd": {},
        }
    return _sharedState[entityId]


def _isSkillReady(entityId, skillName):
    state = _getState(entityId)
    return not state.get("skillCd", {}).get(skillName, False)


def _startSkillCd(entityId, skillName, seconds):
    state = _getState(entityId)
    state.setdefault("skillCd", {})[skillName] = True
    compFactory.CreateGame(levelId).AddTimer(seconds, lambda: state.get("skillCd", {}).pop(skillName, None))


def _startGcd(entityId, seconds):
    state = _getState(entityId)
    state["onGcd"] = True
    compFactory.CreateGame(levelId).AddTimer(seconds, lambda: state.update({"onGcd": False}))


def _setSkillAnimate(entityId, value):
    BaseService().syncRequest("*", "entity/client/skill/setSkillAnimate", QRequests.Args(entityId, value))


def _hasTarget(entityId):
    targetId = compFactory.CreateAction(entityId).GetAttackTarget()
    if not targetId or targetId == "-1":
        return None
    return targetId


def _getVariant(entityId):
    entityDefComp = compFactory.CreateEntityDefinitions(entityId)
    return entityDefComp.GetVariant() if entityDefComp else 0


class AxeHeavyCleaveGoal(CustomGoalCls):
    """重劈 - 斧变种高伤害宽面攻击, 优先级高于劈砍"""

    def __init__(self, entityId, argsJson):
        CustomGoalCls.__init__(self, entityId, argsJson)
        self._durationTimer = 0
        self._active = False

    def CanUse(self):
        entityId = self.GetEntityId()
        state = _getState(entityId)
        if state.get("onGcd", False):
            return False
        if not _isSkillReady(entityId, "heavy_cleave"):
            return False
        if _getVariant(entityId) != 1:
            return False
        targetId = _hasTarget(entityId)
        if not targetId:
            return False
        if getDistance(entityId, targetId) > 5.0:
            return False
        return random.random() < 0.45

    def CanContinueToUse(self):
        return self._active and self._durationTimer > 0

    def Start(self):
        entityId = self.GetEntityId()
        self._active = True
        self._durationTimer = int(1.5 * 30)
        serverUtils.playSoundAll(
            "legend_forest_mob.gozuki.heavy_attack", Entity(entityId).Pos, pitch=random.uniform(0.6, 0.8)
        )
        _setSkillAnimate(entityId, 2.0)
        AttackComp(entityId).setSectorAttackArgs(
            delayTime=0.8, distance=4.0, angle=150, damageList=[5, 7, 10], checkBlock=True, knocked=True
        )

    def Stop(self):
        entityId = self.GetEntityId()
        self._active = False
        _setSkillAnimate(entityId, 0.0)
        _startGcd(entityId, 2.5)
        _startSkillCd(entityId, "heavy_cleave", 4.0)

    def Tick(self):
        self._durationTimer -= 1

    def CanBeInterrupted(self):
        return False


class AxeChopGoal(CustomGoalCls):
    """劈砍 - 斧变种基础攻击, 作为fallback"""

    def __init__(self, entityId, argsJson):
        CustomGoalCls.__init__(self, entityId, argsJson)
        self._durationTimer = 0
        self._active = False

    def CanUse(self):
        entityId = self.GetEntityId()
        state = _getState(entityId)
        if state.get("onGcd", False):
            return False
        if _getVariant(entityId) != 1:
            return False
        targetId = _hasTarget(entityId)
        if not targetId:
            return False
        return getDistance(entityId, targetId) <= 4.0

    def CanContinueToUse(self):
        return self._active and self._durationTimer > 0

    def Start(self):
        entityId = self.GetEntityId()
        self._active = True
        self._durationTimer = int(1.5 * 30)
        serverUtils.playSoundAll(
            "legend_forest_mob.gozuki.attack", Entity(entityId).Pos, pitch=random.uniform(0.8, 1.0)
        )
        _setSkillAnimate(entityId, 1.0)
        AttackComp(entityId).setSectorAttackArgs(
            delayTime=0.7, distance=3.5, angle=120, damageList=[3, 4, 6], checkBlock=True, knocked=True
        )

    def Stop(self):
        entityId = self.GetEntityId()
        self._active = False
        _setSkillAnimate(entityId, 0.0)
        _startGcd(entityId, 1.5)

    def Tick(self):
        self._durationTimer -= 1

    def CanBeInterrupted(self):
        return False


class ShieldBlockGoal(CustomGoalCls):
    """格挡 - 盾变种举盾防御, 优先级高于盾击"""

    def __init__(self, entityId, argsJson):
        CustomGoalCls.__init__(self, entityId, argsJson)
        self._durationTimer = 0
        self._active = False

    def CanUse(self):
        entityId = self.GetEntityId()
        state = _getState(entityId)
        if state.get("onGcd", False):
            return False
        if state.get("triggerCounter", False):
            return False
        if not _isSkillReady(entityId, "shield_block"):
            return False
        if _getVariant(entityId) != 0:
            return False
        targetId = _hasTarget(entityId)
        if not targetId:
            return False
        if getDistance(entityId, targetId) > 4.0:
            return False
        return random.random() < 0.4

    def CanContinueToUse(self):
        if not self._active or self._durationTimer <= 0:
            return False
        state = _getState(self.GetEntityId())
        if state.get("triggerCounter", False):
            return False
        return True

    def Start(self):
        entityId = self.GetEntityId()
        self._active = True
        self._durationTimer = int(3.0 * 30)
        state = _getState(entityId)
        state["blockHitCount"] = 0
        state["blocking"] = True
        state["triggerCounter"] = False
        _setSkillAnimate(entityId, 1.0)

    def Stop(self):
        entityId = self.GetEntityId()
        self._active = False
        _setSkillAnimate(entityId, 0.0)
        state = _getState(entityId)
        state["blockHitCount"] = 0
        state["blocking"] = False
        state["triggerCounter"] = False
        _startSkillCd(entityId, "shield_block", 5.0)

    def Tick(self):
        self._durationTimer -= 1

    def CanBeInterrupted(self):
        return False


class ShieldBashGoal(CustomGoalCls):
    """盾击 - 盾变种快速前方盾击, 作为fallback"""

    def __init__(self, entityId, argsJson):
        CustomGoalCls.__init__(self, entityId, argsJson)
        self._durationTimer = 0
        self._active = False

    def CanUse(self):
        entityId = self.GetEntityId()
        state = _getState(entityId)
        if state.get("onGcd", False):
            return False
        if state.get("triggerCounter", False):
            return False
        if not _isSkillReady(entityId, "shield_bash"):
            return False
        if _getVariant(entityId) != 0:
            return False
        targetId = _hasTarget(entityId)
        if not targetId:
            return False
        return getDistance(entityId, targetId) <= 3.5

    def CanContinueToUse(self):
        return self._active and self._durationTimer > 0

    def Start(self):
        entityId = self.GetEntityId()
        self._active = True
        self._durationTimer = int(0.5 * 30)
        serverUtils.playSoundAll(
            "legend_forest_mob.gozuki.shield_bash", Entity(entityId).Pos, pitch=random.uniform(1.0, 1.2)
        )
        _setSkillAnimate(entityId, 2.0)
        AttackComp(entityId).setSectorAttackArgs(
            delayTime=0.2, distance=2.5, angle=90, damageList=[2, 3, 5], checkBlock=True, knocked=True
        )

    def Stop(self):
        entityId = self.GetEntityId()
        self._active = False
        _setSkillAnimate(entityId, 0.0)
        _startGcd(entityId, 2.0)
        _startSkillCd(entityId, "shield_bash", 3.0)

    def Tick(self):
        self._durationTimer -= 1

    def CanBeInterrupted(self):
        return False


class ChargeRushGoal(CustomGoalCls):
    """冲撞 - 远距离接近目标"""

    def __init__(self, entityId, argsJson):
        CustomGoalCls.__init__(self, entityId, argsJson)
        self._durationTimer = 0
        self._active = False
        self._isAxe = self.GetArgs().get("is_axe", True) if isinstance(self.GetArgs(), dict) else True
        if self._isAxe:
            self._damageList = [4, 6, 8]
            self._gcdSeconds = 6.0
        else:
            self._damageList = [3, 5, 7]
            self._gcdSeconds = 8.0

    def CanUse(self):
        entityId = self.GetEntityId()
        state = _getState(entityId)
        if state.get("onGcd", False):
            return False
        if state.get("triggerCounter", False):
            return False
        variant = _getVariant(entityId)
        if self._isAxe and variant != 1:
            return False
        if not self._isAxe and variant != 0:
            return False
        targetId = _hasTarget(entityId)
        if not targetId:
            return False
        return getDistance(entityId, targetId) > 5.0

    def CanContinueToUse(self):
        return self._active and self._durationTimer > 0

    def Start(self):
        entityId = self.GetEntityId()
        self._active = True
        self._durationTimer = int(2.0 * 30)
        serverUtils.playSoundAll(
            "legend_forest_mob.gozuki.charge", Entity(entityId).Pos, pitch=random.uniform(0.9, 1.1)
        )
        attackComp = AttackComp(entityId)
        attackComp.setMotion(0.3)
        attackComp.setMotion(0.8)
        attackComp.setSectorAttackArgs(
            delayTime=1.0, distance=3.0, angle=90, damageList=self._damageList, checkBlock=True, knocked=True
        )

    def Stop(self):
        entityId = self.GetEntityId()
        self._active = False
        _startGcd(entityId, self._gcdSeconds)

    def Tick(self):
        self._durationTimer -= 1

    def CanBeInterrupted(self):
        return False
