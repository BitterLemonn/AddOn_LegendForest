# -*- coding: utf-8 -*-
import random

from Script_Lemon_Legend.QuModLibs.Modules.Services.Server import BaseService, QRequests
from Script_Lemon_Legend.QuModLibs.Server import *
from Script_Lemon_Legend.common.utils import commonUtils
from Script_Lemon_Legend.server.entity.stateMachine.baseSkill import BaseSkill
from Script_Lemon_Legend.server.utils import serverUtils
from Script_Lemon_Legend.server.utils.serverUtils import compFactory


class TeleportSkill(BaseSkill):
    """
    传送技能
    """

    def __init__(self):
        BaseSkill.__init__(self, skillId="teleport_skill", cooldown=0.1, duration=2.75)
        self.molangValue = 201.0

    def canCast(self, manager):
        # type: ("TeleportSkill", "MalfurionSkillComp") -> bool
        comp = compFactory.CreateAction(manager.getEntityId())
        target = comp.GetAttackTarget()
        if target is None or target == "-1":
            return False
        return True

    def onEnter(self, skillManager):
        # type: ("TeleportSkill", "MalfurionSkillComp") -> None
        BaseSkill.onEnter(self, skillManager)
        entityId = skillManager.getEntityId()

        from Script_Lemon_Legend.server.entity.malfurion.behaviorComp import AIComp

        aiComp = AIComp.getComp(entityId)  # type: AIComp|None
        # 重置伤害计数
        if aiComp:
            aiComp.resetDamageCount()

        # 触发生物事件
        eventComp = compFactory.CreateEntityEvent(entityId)
        eventComp.TriggerCustomEvent(entityId, "legend_forest:teleport")
        eventComp.TriggerCustomEvent(entityId, "legend_forest:skill_start")

        # 设置技能动画
        BaseService().syncRequest(
            "*", "entity/client/skill/setSkillAnimate", QRequests.Args(entityId, self.molangValue)
        )

        gameComp = compFactory.CreateGame(levelId)
        gameComp.AddTimer(
            0.65, lambda: serverUtils.playSoundAll("legend_forest_mob.malfurion.teleporting", Entity(entityId).Pos)
        )
        # 1.3秒后传送到目标身后
        gameComp.AddTimer(1.3, lambda: self.tpBackPlayer(entityId))

    def onExit(self, skillManager):
        # type: ("TeleportSkill", "MalfurionSkillComp") -> None
        BaseSkill.onExit(self, skillManager)
        entityId = skillManager.getEntityId()

        # 触发生物事件
        eventComp = compFactory.CreateEntityEvent(entityId)
        eventComp.TriggerCustomEvent(entityId, "legend_forest:skill_end")
        eventComp.TriggerCustomEvent(entityId, "legend_forest:teleport_end")

        # 重置技能动画
        BaseService().syncRequest("*", "entity/client/skill/setSkillAnimate", QRequests.Args(entityId, 0.0))

    @staticmethod
    def tpBackPlayer(entityId):
        dimensionId = Entity(entityId).Dm
        comp = compFactory.CreateAction(entityId)
        target = comp.GetAttackTarget()
        if target is None or target == "-1":
            return

        targetPos = Entity(target).Pos
        targetFace = Entity(target).DirFromRot
        face = targetFace[0], targetFace[2]
        behindPos = commonUtils.findPointBehind((targetPos[0], targetPos[2]), face, random.randint(6, 15))

        height = Entity(entityId).FootPos[1]
        testPos = behindPos[0], height, behindPos[1]
        comp = compFactory.CreateBlockInfo(levelId)
        isSave = False
        for i in range(0, 10):
            height = int(testPos[1] + i)
            checkPos = testPos[0], height, testPos[2]
            headPos = testPos[0], height + 1, testPos[2]

            footBlock = comp.GetBlockNew(checkPos, dimensionId)["name"]
            headBlock = comp.GetBlockNew(headPos, dimensionId)["name"]

            if footBlock != "minecraft:air" and headBlock == "minecraft:air":
                isSave = True
                break
            else:
                height = int(testPos[1] - i)
                checkPos = (testPos[0], height, testPos[2])
                headPos = (testPos[0], height + 1, testPos[2])

                footBlock = comp.GetBlockNew(checkPos, dimensionId)["name"]
                headBlock = comp.GetBlockNew(headPos, dimensionId)["name"]

                if footBlock != "minecraft:air" and headBlock == "minecraft:air":
                    isSave = True
                    break

        testPos = testPos[0], height + 1, testPos[2]
        if not isSave:
            return
        comp = compFactory.CreatePos(entityId)
        comp.SetFootPos(testPos)
