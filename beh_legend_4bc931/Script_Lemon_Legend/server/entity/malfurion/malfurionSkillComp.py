# -*- coding: utf-8 -*-
from Script_Lemon_Legend.QuModLibs.Modules.EntityComps.Server import QBaseEntityComp, QEntityCompFlags
from Script_Lemon_Legend.server.entity.attack.attackComp import AttackComp
from Script_Lemon_Legend.server.entity.malfurion.skill.fireSpell import FireSpellSkill
from Script_Lemon_Legend.server.entity.malfurion.skill.iceThorn import IceThornSkill
from Script_Lemon_Legend.server.entity.malfurion.skill.normalAttack import NormalAttack
from Script_Lemon_Legend.server.entity.malfurion.skill.teleport import TeleportSkill
from Script_Lemon_Legend.server.entity.malfurion.skill.vineChain import VineChain
from Script_Lemon_Legend.server.entity.malfurion.skill.vineCircle import VineCircle
from Script_Lemon_Legend.server.entity.stateMachine.skillManager import SkillManagerComp


@QBaseEntityComp.regEntity("legend_forest:malfurion", )
@QBaseEntityComp.setFlags(QEntityCompFlags.IGNORE_RENDERING_STATUS)
class MalfurionSkillComp(SkillManagerComp):
    class Skill:
        FIRE_SPELL = "fire_spell"
        ICE_THORN = "ice_thorn"
        NORMAL_ATTACK = "normal_attack"
        TELEPORT = "teleport_skill"
        VINE_CHAIN = "vine_chain"
        VINE_CIRCLE = "vine_circle"

    def __init__(self):
        SkillManagerComp.__init__(self)
        self._attackComp = None  # type: AttackComp|None

    def getAttackComp(self):
        return self._attackComp

    def onBind(self):
        SkillManagerComp.onBind(self)
        self._attackComp = AttackComp(self.entityId)
        skillList = [FireSpellSkill(), IceThornSkill(), NormalAttack(), TeleportSkill(), VineChain(), VineCircle()]
        for skill in skillList:
            self.registerSkill(skill)
