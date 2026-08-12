# -*- coding: utf-8 -*-
from Script_Lemon_Legend.QuModLibs.Modules.Services.Server import BaseService, QRequests
from Script_Lemon_Legend.QuModLibs.Server import *
from Script_Lemon_Legend.common.utils import commonUtils
from Script_Lemon_Legend.server.entity.stateMachine.baseSkill import BaseSkill
from Script_Lemon_Legend.server.utils import serverUtils
from Script_Lemon_Legend.server.utils.serverUtils import compFactory

ATTACK_FILTER = {
    "all_of": [
        {"test": "is_family", "subject": "other", "operator": "!=", "value": "bookshelf_golem"},
        {"test": "has_component", "value": "minecraft:health"},
    ]
}


class AdditionalMotion(object):
    def __init__(self, backwardMotion, upwardMotion):
        self.backwardMotion = backwardMotion
        self.upwardMotion = upwardMotion


class BookshelfSkill(BaseSkill):
    molangValue = 0.0

    def __init__(self, skillId, cooldown, duration):
        BaseSkill.__init__(self, skillId, cooldown, duration)
        self._tick = 0

    def onEnter(self, skillManager):
        self._tick = 0
        entityId = skillManager.getEntityId()
        targetId = compFactory.CreateAction(entityId).GetAttackTarget()
        if targetId and targetId != "-1":
            serverUtils.setLookAt(entityId, targetId)
        compFactory.CreateEntityEvent(entityId).TriggerCustomEvent(entityId, "legend_forest:skill_start")
        BaseService().syncRequest("*", "entity/client/skill/setSkillAnimate", QRequests.Args(entityId, self.molangValue))

    def onUpdate(self, skillManager):
        self._tick += 1

    def onExit(self, skillManager):
        entityId = skillManager.getEntityId()
        BaseService().syncRequest("*", "entity/client/skill/setSkillAnimate", QRequests.Args(entityId, 0.0))
        compFactory.CreateEntityEvent(entityId).TriggerCustomEvent(entityId, "legend_forest:skill_end")

    def _shake(self, skillManager, intensity=0.8, duration=0.5, radius=12.0):
        entityId = skillManager.getEntityId()
        targets = serverUtils.getEntityAround(entityId, radius, ATTACK_FILTER)
        serverUtils.shakeCamera([target for target in targets if Entity(target).Identifier == "minecraft:player"], intensity, duration)


class GroundNormalSkill(BookshelfSkill):
    molangValue = 1.0

    def __init__(self):
        BookshelfSkill.__init__(self, "ground_normal", 0.5, 2.5)

    def onUpdate(self, skillManager):
        BookshelfSkill.onUpdate(self, skillManager)
        if self._tick == 30:
            skillManager.getAttackComp().doAoeAttack(6.0, [0, 8, 12, 18], ATTACK_FILTER)
            self._shake(skillManager)


class GroundFastSkill(BookshelfSkill):
    molangValue = 2.0

    def __init__(self):
        BookshelfSkill.__init__(self, "ground_fast", 0.5, 2.25)

    def onUpdate(self, skillManager):
        BookshelfSkill.onUpdate(self, skillManager)
        if self._tick == 20:
            skillManager.getAttackComp().doAoeAttack(6.0, [0, 6, 10, 12], ATTACK_FILTER)
            self._shake(skillManager)


class GroundHardSkill(BookshelfSkill):
    molangValue = 3.0

    def __init__(self):
        BookshelfSkill.__init__(self, "ground_hard", 0.5, 3.75)

    def onUpdate(self, skillManager):
        BookshelfSkill.onUpdate(self, skillManager)
        attacks = {
            30: (6.0, [0, 8, 12, 18]),
            60: (5.0, [0, 4, 6, 10]),
            71: (5.0, [0, 4, 6, 10]),
        }
        attack = attacks.get(self._tick)
        if attack:
            skillManager.getAttackComp().doAoeAttack(attack[0], attack[1], ATTACK_FILTER)
            self._shake(skillManager)


class LitAttackSkill(BookshelfSkill):
    molangValue = 4.0

    def __init__(self):
        BookshelfSkill.__init__(self, "lit_attack", 0.5, 3.0)

    def onUpdate(self, skillManager):
        BookshelfSkill.onUpdate(self, skillManager)
        if self._tick == 10:
            skillManager.getAttackComp().doSectorAttack(
                3.5,
                120,
                [0, 4, 8, 14],
                ATTACK_FILTER,
                checkBlock=False,
                additionalMotion=AdditionalMotion(1.0, 0.85),
            )


class LeapSlamSkill(BookshelfSkill):
    molangValue = 5.0

    def __init__(self):
        BookshelfSkill.__init__(self, "leap_slam", 1.0, 2.0)

    def onUpdate(self, skillManager):
        BookshelfSkill.onUpdate(self, skillManager)
        attackComp = skillManager.getAttackComp()
        if self._tick in (12, 21):
            entityId = skillManager.getEntityId()
            targetId = compFactory.CreateAction(entityId).GetAttackTarget()
            if targetId and targetId != "-1":
                motion = commonUtils.unitVector(Entity(entityId).FootPos, Entity(targetId).FootPos)
                compFactory.CreateActorMotion(entityId).SetMotion((motion[0] * 0.9, 0.35, motion[2] * 0.9))
        elif self._tick == 30:
            attackComp.doAoeAttack(4.0, [0, 7, 11, 16], ATTACK_FILTER, checkBlock=False)
            self._shake(skillManager, 1.0, 0.6)


class ShockwaveSkill(BookshelfSkill):
    molangValue = 6.0

    def __init__(self):
        BookshelfSkill.__init__(self, "shockwave", 1.0, 1.7)

    def onUpdate(self, skillManager):
        BookshelfSkill.onUpdate(self, skillManager)
        if self._tick == 36:
            skillManager.getAttackComp().doAoeAttack(8.0, [0, 10, 16, 22], ATTACK_FILTER, checkBlock=False)
            self._shake(skillManager, 1.4, 0.8, 16.0)
