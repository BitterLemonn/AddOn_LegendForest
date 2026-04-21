# -*- coding: utf-8 -*-
import random

from mod.common import minecraftEnum
from Script_Lemon_Legend.QuModLibs.Modules.Services.Server import BaseService
from Script_Lemon_Legend.QuModLibs.Server import *
from Script_Lemon_Legend.common.config import modConfig
from Script_Lemon_Legend.server.entity.malfurion.malfurionSkillComp import MalfurionSkillComp
from Script_Lemon_Legend.server.utils import serverUtils
from Script_Lemon_Legend.server.utils.serverUtils import compFactory


@BaseService.Init
class MalfurionServerService(BaseService):
    """
    森茂祭司服务类
    """

    def __init__(self):
        BaseService.__init__(self)
        # 可以被替换成冰块的方块
        self.iceReplaceBlocks = [
            "minecraft:water",
            "minecraft:flowing_water",
            "minecraft:ice",
            "minecraft:snow_layer",
            "minecraft:tallgrass",
            "minecraft:deadbush",
            "minecraft:double_plant",
            "minecraft:yellow_flower",
            "minecraft:red_flower",
            "minecraft:brown_mushroom",
            "minecraft:red_mushroom",
            "legend_forest:shimmer_grass",
            "legend_forest:shimmer_bud",
            "legend_forest:shimmer_flower",
            "legend_forest:shimmer_rose",
            "legend_forest:blue_mushroom",
            "legend_forest:golden_bush",
            "legend_forest:touch_flower_upper",
            "legend_forest:touch_flower_down",
            "legend_forest:yellower_leaves_cape_1",
            "legend_forest:yellower_leaves_cape_2",
            "legend_forest:yellower_leaves_cape_3",
        ]
        self.iceBoltDamageList = [0, 2, 5, 7]

    @BaseService.Listen(Events.EntityDefinitionsEventServerEvent)
    def onEntityDefinitionsEvent(self, data):
        data = Events.EntityDefinitionsEventServerEvent(data)
        if not Entity(data.entityId).Identifier == "legend_forest:malfurion":
            return

        malComp = MalfurionSkillComp.getComp(data.entityId)  # type: MalfurionSkillComp
        if not malComp:
            return

    @BaseService.Listen(Events.HealthChangeBeforeServerEvent)
    def onHealthChangeBeforeEvent(self, events):
        data = Events.HealthChangeBeforeServerEvent(events)
        entity = Entity(data.entityId)
        if entity.Identifier == "legend_forest:malfurion" and data.to <= 0:
            events["cancel"] = True

            def suicide():
                extraComp = compFactory.CreateExtraData(data.entityId)
                extraComp.SetExtraData("legend_forest:isDead", True)
                entity.Health.SetValue(0.01)
                eventComp = compFactory.CreateEntityEvent(data.entityId)
                eventComp.TriggerCustomEvent(data.entityId, "legend_forest:dying")

            serverUtils.runNextTick(suicide)

    @BaseService.Listen(Events.ProjectileDoHitEffectEvent)
    def onProjectileDoHitEffectEvent(self, data):
        data = Events.ProjectileDoHitEffectEvent(data)
        if Entity(data.id).Identifier == "legend_forest:ice_bolt":
            targetType = data.hitTargetType

            if targetType == "ENTITY":
                entityId = data.targetId
                if Entity(entityId).Identifier in modConfig.ICE_THORN_FILTER:
                    return

                serverUtils.doHurt(
                    data.srcId,
                    self.iceBoltDamageList,
                    entityId,
                    cause=minecraftEnum.ActorDamageCause.Magic,
                    checkBlock=False,
                )
                return
            blockPos = data.x, data.y, data.z

            # 生成冰块 冰锥
            dimensionId = Entity(data.id).Dm
            randomPosList = [(random.randint(-5, 5), 0, random.randint(-5, 5)) for _ in range(0, random.randint(1, 3))]
            for randomPos in randomPosList:
                x, y, z = randomPos
                targetPos = targetX, targetY, targetZ = data.x + x, data.y, data.z + z
                upPos = targetX, targetY + 1, targetZ
                downPos = targetX, targetY - 1, targetZ
                blockComp = compFactory.CreateBlockInfo(levelId)
                targetBlock = blockComp.GetBlockNew(targetPos, dimensionId)["name"]
                upBlock = blockComp.GetBlockNew(upPos, dimensionId)["name"]
                downBlock = blockComp.GetBlockNew(downPos, dimensionId)["name"]

                if targetBlock in self.iceReplaceBlocks:
                    if 0 <= blockComp.GetBlockBasicInfo(downBlock)["destroyTime"] <= 10:
                        blockComp.SetBlockNew(downPos, {"name": "minecraft:packed_ice"}, dimensionId=dimensionId)
                    if random.random() < 0.3:
                        blockComp.SetBlockNew(targetPos, {"name": "legend_forest:ice_thorn"}, dimensionId=dimensionId)

                elif (
                    upBlock == "minecraft:air"
                    and targetBlock != "minecraft:air"
                    and targetBlock != "legend_forest:ice_thorn"
                ):
                    if 0 <= blockComp.GetBlockBasicInfo(targetBlock)["destroyTime"] <= 10:
                        blockComp.SetBlockNew(targetPos, {"name": "minecraft:packed_ice"}, dimensionId=dimensionId)
                    if random.random() < 0.3:
                        blockComp.SetBlockNew(upPos, {"name": "legend_forest:ice_thorn"}, dimensionId=dimensionId)

    @BaseService.Listen("ActuallyHurtServerEvent")
    def onActuallyHurtServerEvent(self, data):
        srcId = data["srcId"]
        entityId = data["entityId"]
        cause = data["cause"]
        damage = data["damage"]

        if Entity(entityId).Identifier == "legend_forest:malfurion":
            # 分段限制伤害
            damageL1 = min(damage, 15)
            damageL2 = 0
            damageL3 = 0
            if damageL1 == 15:
                damageL2 = min(damage - 20, 15)
            if damageL2 == 15:
                damageL3 = min(damage - 35, 15)
            damage = damageL1 + damageL2 * 0.5 + damageL3 * 0.25
            data["damage_f"] = damage

            # 累积伤害计数
            from Script_Lemon_Legend.server.entity.malfurion.behaviorComp import AIComp

            aiComp = AIComp.getComp(entityId)  # type: AIComp|None
            if aiComp:
                aiComp.addDamageCount(damage)

            # # 受伤计数 触发瞬移
            # if cause == minecraftEnum.ActorDamageCause.EntityAttack \
            #         or cause == minecraftEnum.ActorDamageCause.Projectile \
            #         or cause == minecraftEnum.ActorDamageCause.Magic or Entity(
            #     srcId).Identifier == "minecraft:player":
            #     dataComp = serverApi.GetEngineCompFactory().CreateExtraData(entityId)
            #     hurtCount = dataComp.GetExtraData("hurtCount")
            #     hurtCount = dataComp.SetExtraData("hurtCount", 1) if hurtCount is None else hurtCount
            #     dataComp.SetExtraData("hurtCount", hurtCount + random.randint(1, 2))
            #
            #     eventComp = serverApi.GetEngineCompFactory().CreateEntityEvent(entityId)
            #     if hurtCount >= random.randint(12, 16) and \
            #             Entity(entityId).Health.Value > Entity(entityId).Health.Max / 5.0:
            #         dataComp.SetExtraData("hurtCount", 0)
            #         eventComp.TriggerCustomEvent(entityId, "legend_forest:teleport")

            # if Entity(srcId).Identifier == "minecraft:player":
            #     MalManager().SetAttacker(entityId, srcId)
