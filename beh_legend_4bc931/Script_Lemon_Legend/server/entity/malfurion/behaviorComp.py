# -*- coding=utf-8 -*-
import math
import random

from Script_Lemon_Legend.QuModLibs.Modules.EntityComps.Server import QBaseEntityComp
from Script_Lemon_Legend.QuModLibs.Server import *
from Script_Lemon_Legend.common.utils import commonUtils
from Script_Lemon_Legend.server.entity.malfurion.malfurionSkillComp import MalfurionSkillComp
from Script_Lemon_Legend.server.utils.serverUtils import compFactory, getDistance, getEntityAround, isInLineOfSight


@QBaseEntityComp.regEntity("legend_forest:malfurion")
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
        print("Malfurion BehaviorComp bound. EntityId:", self.entityId)

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
    森茂祭司AI组件 - 智能决策系统

    特性:
    1. 血量阶段感知: 根据血量比例切换战斗阶段，不同阶段有不同的技能权重和策略
    2. 技能历史记忆: 记录最近使用的技能，避免重复，实现多样化攻击
    3. 玩家行为分析: 根据玩家距离变化趋势判断玩家意图（接近/远离/静止）
    4. 连招系统: 技能释放后的回调会根据战斗状态智能选择下一个技能
    5. 环境感知: 考虑视野、周围实体数量等因素
    6. 紧急反应: 受到大量伤害时优先瞬移脱身
    """

    # 战斗阶段定义
    PHASE_NORMAL = 0  # > 70% 血量
    PHASE_PRESSURED = 1  # 40%~70% 血量
    PHASE_ENRAGED = 2  # < 40% 血量

    # 技能历史最大记录数
    MAX_SKILL_HISTORY = 3

    def __init__(self):
        QBaseEntityComp.__init__(self)
        self.skillComp = None  # type: MalfurionSkillComp|None
        self.canUseSkill = False
        self.lastCountDamage = 0.0

        self.attackComp = compFactory.CreateAction(self.entityId)

        # === 智能AI新增状态 ===
        self._skillHistory = []  # 技能使用历史（最近N个技能ID）
        self._combatPhase = self.PHASE_NORMAL  # 当前战斗阶段
        self._consecutiveNormalAttacks = 0  # 连续普通攻击计数

        # 玩家行为追踪
        self._lastTargetPos = None  # 上一tick目标位置
        self._targetMoveSamples = []  # 目标移动采样（用于分析趋势）
        self._tickCounter = 0  # tick计数器（用于降频采样）

        # 冷却控制
        self._lastTeleportTick = -999  # 上次瞬移的tick
        self._combatStartTick = 0  # 战斗开始tick

    def onBind(self):
        self.skillComp = MalfurionSkillComp.getComp(self.entityId)  # type: MalfurionSkillComp
        self.attackComp = compFactory.CreateAction(self.entityId)

        QBaseEntityComp.onBind(self)
        self.skillComp.addListener(self.onSkillCooldownChange)

        self.canUseSkill = self.skillComp.getIsInCooldown() == False
        self._combatStartTick = self._tickCounter
        if self.canUseSkill:
            self.decideNextSkill()

    def onUnBind(self):
        QBaseEntityComp.onUnBind(self)
        self.skillComp.removeListener(self.onSkillCooldownChange)

    def onGameTick(self):
        QBaseEntityComp.onGameTick(self)
        self._tickCounter += 1

        # 每10tick采样一次目标位置（用于分析玩家行为，降低性能开销）
        if self._tickCounter % 10 == 0:
            self._sampleTargetPosition()

    # =====================
    # 伤害计数与紧急反应
    # =====================

    def addDamageCount(self, damage):
        """累积伤害计数，超过阈值触发瞬移"""
        self.lastCountDamage += damage

        # 根据战斗阶段调整瞬移阈值
        health = Entity(self.entityId).Health
        healthRatio = health.Value / health.Max if health.Max > 0 else 1.0

        # 低血量时更容易触发瞬移
        threshold = 30.0
        if healthRatio < 0.4:
            threshold = 15.0
        elif healthRatio < 0.7:
            threshold = 22.0

        if self.lastCountDamage >= threshold:
            self._forceTeleport()

    def _forceTeleport(self):
        """强制瞬移，并重置状态"""
        self.lastCountDamage = 0
        ticksSinceLastTp = self._tickCounter - self._lastTeleportTick
        # 防止短时间内连续瞬移（至少5秒=150tick间隔）
        if ticksSinceLastTp < 150:
            return
        self.skillComp.forceCastSkill(self.skillComp.Skill.TELEPORT)
        self._lastTeleportTick = self._tickCounter
        self._recordSkill(self.skillComp.Skill.TELEPORT)

    def resetDamageCount(self):
        self.lastCountDamage = 0

    # =====================
    # 技能历史管理
    # =====================

    def _recordSkill(self, skillId):
        """记录使用的技能到历史"""
        self._skillHistory.append(skillId)
        if len(self._skillHistory) > self.MAX_SKILL_HISTORY:
            self._skillHistory.pop(0)

    def _getRecentSkillCount(self, skillId):
        """获取最近N次中某技能的使用次数"""
        return self._skillHistory.count(skillId)

    def _isSkillInHistory(self, skillId):
        """检查技能是否在最近的记录中"""
        return skillId in self._skillHistory

    # =====================
    # 战斗阶段判定
    # =====================

    def _updateCombatPhase(self):
        """根据当前血量更新战斗阶段"""
        health = Entity(self.entityId).Health
        healthRatio = health.Value / health.Max if health.Max > 0 else 1.0

        oldPhase = self._combatPhase
        if healthRatio > 0.7:
            self._combatPhase = self.PHASE_NORMAL
        elif healthRatio > 0.4:
            self._combatPhase = self.PHASE_PRESSURED
        else:
            self._combatPhase = self.PHASE_ENRAGED

        return oldPhase != self._combatPhase

    def _getHealthRatio(self):
        """获取当前血量比例"""
        health = Entity(self.entityId).Health
        return health.Value / health.Max if health.Max > 0 else 1.0

    # =====================
    # 玩家行为分析
    # =====================

    def _sampleTargetPosition(self):
        """采样目标位置（每10tick调用一次）"""
        targetId = self.attackComp.GetAttackTarget()
        if not targetId or targetId == "-1":
            self._targetMoveSamples = []
            return

        currentPos = Entity(targetId).FootPos
        if self._lastTargetPos is not None:
            dx = currentPos[0] - self._lastTargetPos[0]
            dz = currentPos[2] - self._lastTargetPos[2]
            distanceMoved = math.sqrt(dx * dx + dz * dz)

            # 记录移动距离样本
            self._targetMoveSamples.append(distanceMoved)
            if len(self._targetMoveSamples) > 6:
                self._targetMoveSamples.pop(0)

        self._lastTargetPos = currentPos

    def _getPlayerBehaviorType(self):
        """
        分析玩家行为类型
        :return: "approaching"(接近中), "retreating"(远离中), "circling"(绕圈), "stationary"(静止), "unknown"(未知)
        """
        if len(self._targetMoveSamples) < 3:
            return "unknown"

        targetId = self.attackComp.GetAttackTarget()
        if not targetId or targetId == "-1":
            return "unknown"

        # 计算平均移动速度
        avgMove = sum(self._targetMoveSamples) / len(self._targetMoveSamples)

        if avgMove < 0.3:
            return "stationary"

        # 计算玩家是接近还是远离Boss
        myPos = Entity(self.entityId).FootPos
        targetPos = Entity(targetId).FootPos
        currentDist = getDistance(self.entityId, targetId)

        # 对比最近几帧的距离变化趋势
        if len(self._targetMoveSamples) >= 4:
            recentMove = sum(self._targetMoveSamples[-2:]) / 2.0
            olderMove = sum(self._targetMoveSamples[:2]) / 2.0

            # 计算距离变化（简单方法：看最近采样和较早采样的距离对比）
            if recentMove > 1.5 and olderMove > 1.5:
                # 高速移动可能是绕圈
                return "circling"

        # 简单判断：如果玩家距离很近且在移动，认为在接近
        if currentDist < 8 and avgMove > 0.5:
            return "approaching"
        elif currentDist > 15 and avgMove > 0.5:
            return "retreating"

        return "unknown"

    # =====================
    # 环境感知
    # =====================

    def _getNearbyEnemyCount(self, radius=12):
        """获取附近敌人数量"""
        entities = getEntityAround(self.entityId, radius)
        if not entities:
            return 0
        # 排除自身
        return len([e for e in entities if e != self.entityId])

    def _hasLineOfSight(self):
        """检查是否有对目标的直线视野"""
        targetId = self.attackComp.GetAttackTarget()
        if not targetId or targetId == "-1":
            return False
        return isInLineOfSight(self.entityId, targetId)

    # =====================
    # 智能技能决策（核心）
    # =====================

    def onSkillCooldownChange(self, isOffCooldown):
        """冷却结束回调"""
        self.canUseSkill = isOffCooldown
        if self.canUseSkill:
            self.decideNextSkill()

    def decideNextSkill(self):
        """
        核心决策方法：综合考虑多种因素选择最优技能
        """
        targetId = self.attackComp.GetAttackTarget()
        if not targetId or targetId == "-1":
            return

        # 更新战斗阶段
        self._updateCombatPhase()

        # 获取战斗上下文
        distance = getDistance(self.entityId, targetId)
        healthRatio = self._getHealthRatio()
        playerBehavior = self._getPlayerBehaviorType()
        nearbyEnemies = self._getNearbyEnemyCount(10)
        hasLOS = self._hasLineOfSight()

        skill = self._evaluateBestSkill(distance, healthRatio, playerBehavior, nearbyEnemies, hasLOS)
        if skill:
            self._recordSkill(skill)
            # 某些技能需要特殊回调
            if skill in (self.skillComp.Skill.VINE_CIRCLE, self.skillComp.Skill.VINE_CHAIN):
                self.skillComp.castSkill(skill, self._afterSkillCallback)
            else:
                self.skillComp.castSkill(skill)

    def _evaluateBestSkill(self, distance, healthRatio, playerBehavior, nearbyEnemies, hasLOS):
        """
        评估并选择最佳技能

        决策逻辑:
        1. 紧急情况优先（低血量+被多人围攻 → 瞬移）
        2. 根据距离选择技能大类
        3. 根据战斗阶段调整权重
        4. 根据玩家行为调整权重
        5. 考虑技能历史避免重复
        6. 考虑环境因素（视野、敌人数）
        """
        Skill = self.skillComp.Skill

        # === 紧急情况处理 ===
        if self._shouldEmergencyTeleport(healthRatio, nearbyEnemies, distance):
            ticksSinceLastTp = self._tickCounter - self._lastTeleportTick
            if ticksSinceLastTp >= 90:  # 至少3秒间隔
                return Skill.TELEPORT

        # === 根据距离和上下文构建技能权重 ===
        weightMap = {}

        if distance < 6:
            # === 极近距离 ===
            # 优先使用近战范围技能，或者瞬移拉开距离
            weightMap = self._buildCloseRangeWeights(healthRatio, playerBehavior, nearbyEnemies)

        elif distance < 12:
            # === 中距离（核心战斗距离） ===
            weightMap = self._buildMidRangeWeights(healthRatio, playerBehavior, nearbyEnemies, hasLOS)

        elif distance < 22:
            # === 中远距离 ===
            weightMap = self._buildLongRangeWeights(healthRatio, playerBehavior, hasLOS)

        else:
            # === 远距离 ===
            weightMap = self._buildVeryLongRangeWeights(healthRatio, playerBehavior)

        if not weightMap:
            return Skill.NORMAL_ATTACK

        # === 应用技能历史惩罚（减少重复） ===
        weightMap = self._applyHistoryPenalty(weightMap)

        # === 愤怒阶段增强（更多攻击性技能） ===
        if self._combatPhase == self.PHASE_ENRAGED:
            weightMap = self._applyEnrageBonus(weightMap)

        return commonUtils.weightChoice(weightMap)

    def _shouldEmergencyTeleport(self, healthRatio, nearbyEnemies, distance):
        """判断是否需要紧急瞬移"""
        # 血量极低且被围攻
        if healthRatio < 0.25 and nearbyEnemies >= 2:
            return True
        # 极近距离且血量较低
        if healthRatio < 0.4 and distance < 5 and nearbyEnemies >= 1:
            return True
        # 持续累积大量伤害
        if self.lastCountDamage > 20:
            return True
        return False

    # --- 不同距离的权重构建 ---

    def _buildCloseRangeWeights(self, healthRatio, playerBehavior, nearbyEnemies):
        """极近距离 (<6格) 的技能权重"""
        Skill = self.skillComp.Skill
        weights = {}

        # 近距离总是优先藤蔓圈
        weights[Skill.VINE_CIRCLE] = 4.0

        if healthRatio < 0.5:
            # 低血量：更倾向瞬移逃跑
            weights[Skill.TELEPORT] = 3.5
            weights[Skill.NORMAL_ATTACK] = 1.0
        elif playerBehavior == "approaching":
            # 玩家在冲过来：用藤蔓圈+普通攻击
            weights[Skill.VINE_CIRCLE] = 5.0
            weights[Skill.NORMAL_ATTACK] = 2.0
            weights[Skill.ICE_THORN] = 1.5
        elif playerBehavior == "circling":
            # 玩家在绕圈：冰刺覆盖范围大
            weights[Skill.ICE_THORN] = 3.0
            weights[Skill.VINE_CIRCLE] = 2.5
            weights[Skill.NORMAL_ATTACK] = 1.5
        else:
            weights[Skill.NORMAL_ATTACK] = 2.0
            weights[Skill.ICE_THORN] = 1.5
            weights[Skill.TELEPORT] = 1.0

        # 被多人围攻时增加瞬移概率
        if nearbyEnemies >= 2:
            weights[Skill.TELEPORT] = weights.get(Skill.TELEPORT, 0) + 2.0

        return weights

    def _buildMidRangeWeights(self, healthRatio, playerBehavior, nearbyEnemies, hasLOS):
        """中距离 (6~12格) 的技能权重"""
        Skill = self.skillComp.Skill
        weights = {}

        # 中距离是核心战斗距离，所有技能都可用
        weights[Skill.VINE_CIRCLE] = 2.0
        weights[Skill.VINE_CHAIN] = 2.5
        weights[Skill.ICE_THORN] = 2.0
        weights[Skill.NORMAL_ATTACK] = 1.5

        if playerBehavior == "approaching":
            # 玩家接近中：用藤蔓链阻止，或者准备藤蔓圈
            weights[Skill.VINE_CHAIN] = 4.0
            weights[Skill.VINE_CIRCLE] = 3.0
            weights[Skill.ICE_THORN] = 2.5
        elif playerBehavior == "retreating":
            # 玩家在逃跑：远程追击
            weights[Skill.FIRE_SPELL] = 3.5
            weights[Skill.ICE_THORN] = 3.0
            weights[Skill.VINE_CHAIN] = 2.0
        elif playerBehavior == "stationary":
            # 玩家站着不动（可能在远程攻击）：用远程高伤害技能
            weights[Skill.FIRE_SPELL] = 4.0
            weights[Skill.ICE_THORN] = 3.0
        elif playerBehavior == "circling":
            # 玩家绕圈：冰刺扇形覆盖
            weights[Skill.ICE_THORN] = 4.0
            weights[Skill.VINE_CIRCLE] = 2.5

        if not hasLOS:
            # 没有视野时优先瞬移到更好的位置，或使用范围技能
            weights[Skill.TELEPORT] = weights.get(Skill.TELEPORT, 0) + 2.0
            weights[Skill.VINE_CIRCLE] = weights.get(Skill.VINE_CIRCLE, 0) + 1.0

        if nearbyEnemies >= 2:
            weights[Skill.ICE_THORN] = weights.get(Skill.ICE_THORN, 0) + 1.5
            weights[Skill.VINE_CIRCLE] = weights.get(Skill.VINE_CIRCLE, 0) + 1.5

        return weights

    def _buildLongRangeWeights(self, healthRatio, playerBehavior, hasLOS):
        """中远距离 (12~22格) 的技能权重"""
        Skill = self.skillComp.Skill
        weights = {}

        weights[Skill.FIRE_SPELL] = 3.0
        weights[Skill.ICE_THORN] = 3.0
        weights[Skill.VINE_CHAIN] = 1.5

        if playerBehavior == "retreating":
            # 目标在逃跑：火焰法术和冰刺追击
            weights[Skill.FIRE_SPELL] = 5.0
            weights[Skill.ICE_THORN] = 4.0
        elif playerBehavior == "stationary":
            weights[Skill.FIRE_SPELL] = 4.5
            weights[Skill.ICE_THORN] = 3.5

        if not hasLOS:
            # 没有视野：瞬移到目标身边
            weights[Skill.TELEPORT] = 3.0

        # 偶尔用藤蔓链做远程控制
        if not self._isSkillInHistory(Skill.VINE_CHAIN):
            weights[Skill.VINE_CHAIN] = 2.0

        return weights

    def _buildVeryLongRangeWeights(self, healthRatio, playerBehavior):
        """远距离 (>22格) 的技能权重"""
        Skill = self.skillComp.Skill
        weights = {}

        # 远距离优先瞬移接近或远程攻击
        weights[Skill.TELEPORT] = 3.0
        weights[Skill.FIRE_SPELL] = 3.5
        weights[Skill.ICE_THORN] = 2.0

        if playerBehavior == "retreating":
            weights[Skill.TELEPORT] = 5.0
            weights[Skill.FIRE_SPELL] = 3.0

        return weights

    # --- 权重修正方法 ---

    def _applyHistoryPenalty(self, weightMap):
        """根据技能历史对重复技能降低权重"""
        adjusted = {}
        for skillId, weight in weightMap.items():
            recentCount = self._getRecentSkillCount(skillId)
            if recentCount > 0:
                # 每在历史中出现过一次，权重降低40%
                penalty = max(0.2, 1.0 - recentCount * 0.4)
                adjusted[skillId] = weight * penalty
            else:
                adjusted[skillId] = weight
        return adjusted

    def _applyEnrageBonus(self, weightMap):
        """愤怒阶段（<40%血量）增强攻击性技能权重"""
        Skill = self.skillComp.Skill
        enrageBonus = {
            Skill.FIRE_SPELL: 1.8,
            Skill.ICE_THORN: 1.5,
            Skill.VINE_CIRCLE: 1.4,
            Skill.VINE_CHAIN: 1.3,
        }
        adjusted = {}
        for skillId, weight in weightMap.items():
            bonus = enrageBonus.get(skillId, 1.0)
            adjusted[skillId] = weight * bonus
        return adjusted

    # =====================
    # 技能回调（连招系统）
    # =====================

    def _afterSkillCallback(self):
        """
        技能释放后的智能回调
        根据当前战斗状态决定是否追加技能（连招）
        """
        targetId = self.attackComp.GetAttackTarget()
        if not targetId or targetId == "-1":
            return

        Skill = self.skillComp.Skill
        distance = getDistance(self.entityId, targetId)
        healthRatio = self._getHealthRatio()
        playerBehavior = self._getPlayerBehaviorType()

        # 获取上一个使用的技能
        lastSkill = self._skillHistory[-1] if self._skillHistory else None

        weightMap = {}

        if lastSkill == Skill.VINE_CIRCLE:
            # 藤蔓圈后：根据情况追加
            if distance < 8:
                # 近距离追加冰刺或普通攻击
                weightMap = {
                    Skill.NORMAL_ATTACK: 3.0,
                    Skill.ICE_THORN: 2.5,
                    Skill.TELEPORT: 1.0 if healthRatio < 0.5 else 0.0,
                }
            else:
                # 中远距离追加远程
                weightMap = {
                    Skill.ICE_THORN: 3.0,
                    Skill.FIRE_SPELL: 2.0,
                    Skill.NORMAL_ATTACK: 1.5,
                }

        elif lastSkill == Skill.VINE_CHAIN:
            # 藤蔓链后：追击或拉开距离
            if distance < 10:
                weightMap = {
                    Skill.NORMAL_ATTACK: 3.0,
                    Skill.VINE_CIRCLE: 2.5,
                    Skill.ICE_THORN: 2.0,
                }
            else:
                weightMap = {
                    Skill.ICE_THORN: 3.0,
                    Skill.FIRE_SPELL: 2.5,
                    Skill.NORMAL_ATTACK: 1.5,
                }

        else:
            # 默认回调
            weightMap = {
                Skill.NORMAL_ATTACK: 2.0,
                Skill.ICE_THORN: 2.0,
                Skill.TELEPORT: 1.0,
            }

        # 愤怒阶段连招更积极
        if self._combatPhase == self.PHASE_ENRAGED:
            weightMap = self._applyEnrageBonus(weightMap)

        # 避免回调中和之前完全一样的技能
        if lastSkill and lastSkill in weightMap:
            weightMap[lastSkill] = weightMap[lastSkill] * 0.3

        # 避免瞬移后回调再次瞬移
        if lastSkill == Skill.TELEPORT:
            weightMap.pop(Skill.TELEPORT, None)

        # 选择并记录技能
        if weightMap:
            skill = commonUtils.weightChoice(weightMap)
            if skill:
                self._recordSkill(skill)
                if skill in (Skill.VINE_CIRCLE, Skill.VINE_CHAIN):
                    self.skillComp.castSkill(skill, self._afterSkillCallback)
                else:
                    self.skillComp.castSkill(skill)
