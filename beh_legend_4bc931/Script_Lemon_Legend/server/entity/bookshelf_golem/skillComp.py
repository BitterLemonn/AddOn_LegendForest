# -*- coding: utf-8 -*-
from Script_Lemon_Legend.QuModLibs.Modules.EntityComps.Server import QBaseEntityComp, QEntityCompFlags
from Script_Lemon_Legend.server.entity.attack.attackComp import AttackComp
from Script_Lemon_Legend.server.entity.bookshelf_golem.skill.skills import (
    GroundFastSkill,
    GroundHardSkill,
    GroundNormalSkill,
    LeapSlamSkill,
    LitAttackSkill,
    ShockwaveSkill,
)
from Script_Lemon_Legend.server.entity.stateMachine.skillManager import SkillManagerComp


@QBaseEntityComp.regEntity("legend_forest:bookshelf_golem")
@QBaseEntityComp.setFlags(QEntityCompFlags.IGNORE_RENDERING_STATUS)
class BookshelfGolemSkillComp(SkillManagerComp):
    class Skill:
        GROUND_NORMAL = "ground_normal"
        GROUND_FAST = "ground_fast"
        GROUND_HARD = "ground_hard"
        LIT_ATTACK = "lit_attack"
        LEAP_SLAM = "leap_slam"
        SHOCKWAVE = "shockwave"

    def __init__(self):
        SkillManagerComp.__init__(self)
        self._attackComp = None  # type: AttackComp|None

    def getAttackComp(self):
        return self._attackComp

    def onBind(self):
        SkillManagerComp.onBind(self)
        self._attackComp = AttackComp(self.entityId)
        for skill in (
            GroundNormalSkill(),
            GroundFastSkill(),
            GroundHardSkill(),
            LitAttackSkill(),
            LeapSlamSkill(),
            ShockwaveSkill(),
        ):
            self.registerSkill(skill)
