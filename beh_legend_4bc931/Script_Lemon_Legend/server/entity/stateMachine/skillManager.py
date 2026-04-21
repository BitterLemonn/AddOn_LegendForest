# coding=utf-8

from Script_Lemon_Legend.QuModLibs.Modules.EntityComps.Server import QBaseEntityComp
from Script_Lemon_Legend.server.entity.stateMachine.baseSkill import BaseSkill
from Script_Lemon_Legend.server.utils.serverUtils import compFactory, logging


class SkillManagerComp(QBaseEntityComp):
    """
    基于ECS的技能状态机组件
    管理实体的所有技能、冷却时间和状态转换
    """

    def __init__(self):
        QBaseEntityComp.__init__(self)
        self._sharedCooldownTimer = 0  # 共享冷却倒计时 (Tick)

        self._skills = {}  # 注册的技能 {skillId: SkillObj}

        self._currentSkill = None  # type: BaseSkill|None  # 当前正在释放/持续的技能
        self._currentSkillCallback = None  # 当前技能结束回调
        self._skillDurationTimer = 0  # 当前技能已持续时间 (Tick)

        self._listeners = []

    def getAttackComp(self):
        raise NotImplementedError

    def onUnBind(self):
        QBaseEntityComp.onUnBind(self)
        # 清理状态
        if self._currentSkill:
            self._currentSkill.onExit(self)
        self._currentSkill = None

    def addListener(self, listener):
        self._listeners.append(listener)

    def removeListener(self, listener):
        if listener in self._listeners:
            self._listeners.remove(listener)

    def _notifyCooldownStart(self):
        """通知所有监听器进入冷却"""
        for listener in self._listeners:
            listener(False)

    def _notifyCooldownEnd(self):
        """通知所有监听器冷却结束"""
        for listener in self._listeners:
            listener(True)

    def getIsInCooldown(self):
        return self._sharedCooldownTimer > 0

    def onGameTick(self):
        """
        每帧更新 (30 ticks/s)
        负责驱动当前技能的状态更新
        """
        QBaseEntityComp.onGameTick(self)

        # 更新冷却倒计时
        if self._sharedCooldownTimer > 0:
            self._sharedCooldownTimer -= 1
            # 冷却结束时通知监听器
            if self._sharedCooldownTimer == 0:
                self._notifyCooldownEnd()

        self._updateState()

    def registerSkill(self, skill):
        # type: ("SkillManagerComp", BaseSkill) -> None
        """注册一个技能实例"""
        self._skills[skill.skillId] = skill

    def canCastSkill(self, skillId):
        # type: ("SkillManagerComp", str) -> bool
        """
        检查是否可以释放指定技能
        :param skillId: 技能ID
        :return: bool 是否可以释放
        """
        skill = self._skills.get(skillId)

        if not skill:
            logging.error("[SkillManager] 无法找到技能ID: {}".format(skillId))
            return False

        # 检查技能自定义条件
        if not skill.canCast(self):
            return False

        return True

    def castSkill(self, skillId, onEndCallback=None):
        # type: ("SkillManagerComp", str, callable) -> bool
        """
        尝试释放技能
        :param skillId: 技能ID
        :param onEndCallback: 技能释放结束回调
        :return: bool 是否成功释放
        """
        skill = self._skills.get(skillId)

        if not skill:
            logging.error("[SkillManager] 无法找到技能ID: {}".format(skillId))
            return False

        # 1. 检查共享冷却
        if self._sharedCooldownTimer > 0:
            remaining = self._sharedCooldownTimer / 30.0
            logging.warning("[SkillManager] 共享冷却中，剩余时间: {:.2f}s".format(remaining))
            return False

        # 2. 检查状态机 (是否正在释放其他技能)
        # 如果当前有技能且不允许打断(这里简化为不允许打断)，则失败
        if self._currentSkill:
            logging.warning(
                "[SkillManager] 当前正在释放技能: {}, 无法释放新技能: {}".format(self._currentSkill.skillId, skillId)
            )
            return False

        # 3. 检查技能自定义条件
        if not skill.canCast(self):
            logging.warning("[SkillManager] 技能 {} 释放条件不满足".format(skillId))
            return False

        # --- 执行释放 ---
        self._enterSkill(skill, onEndCallback)
        return True

    def forceCastSkill(self, skillId, onEndCallback=None):
        """强制释放技能，打断当前技能, 无视当前冷却"""
        skill = self._skills.get(skillId)

        if not skill:
            logging.error("[SkillManager] 无法找到技能ID: {}".format(skillId))
            return False

        # 检查是否有仇恨目标
        attackComp = compFactory.CreateAction(self.entityId)
        targetId = attackComp.GetAttackTarget()
        if not targetId or targetId == "-1":
            logging.warning("[SkillManager] 强制释放技能 {} 失败，无有效仇恨目标".format(skillId))
            return False

        # 打断当前技能
        self.interruptCurrentSkill()

        # 强制释放时清空冷却
        self._sharedCooldownTimer = 0

        # 直接进入新技能
        self._enterSkill(skill, onEndCallback)
        return True

    # 打断当前技能释放 不进入cd
    def interruptCurrentSkill(self):
        """打断当前技能释放"""
        if self._currentSkill:
            logging.warning("[SkillManager] 技能 {} 被打断，未进入冷却".format(self._currentSkill.skillId))
            self._currentSkill.onExit(self)
            self._currentSkill = None

    def _enterSkill(self, skill, onEndCallback=None):
        """内部方法：进入技能状态"""
        self._currentSkill = skill
        self._skillDurationTimer = 0

        # logging.debug("[SkillManager] 释放技能: {}".format(skill.skillId))
        self._currentSkillCallback = onEndCallback
        skill.onEnter(self)

    def _updateState(self):
        """内部方法：更新状态机"""
        if not self._currentSkill:
            return

        # 调用技能的每帧更新
        self._currentSkill.onUpdate(self)
        self._skillDurationTimer += 1

        # 检查持续时间是否结束
        # 如果 duration 为 0，通常视为瞬发技能，执行完 onEnter 后下一帧即可退出
        # 或者可以在 onEnter 中直接处理完逻辑，这里为了统一状态机流程，瞬发技能也占一帧或由 duration 控制

        durationTicks = int(self._currentSkill.duration * 30)
        if durationTicks <= 0:
            # 瞬发技能，立即结束
            self._exitCurrentSkill()
        elif self._skillDurationTimer >= durationTicks:
            # 持续技能，时间到结束
            self._exitCurrentSkill()

    def _exitCurrentSkill(self):
        """内部方法：退出当前技能状态"""
        if self._currentSkill:
            # 技能完全释放完成后，才开始计算共享冷却
            # 冷却时间取决于当前技能的 cooldown 属性
            skill = self._currentSkill

            # 调用结束回调
            self._currentSkill.onExit(self)
            self._currentSkill = None

            if self._currentSkillCallback:
                self._currentSkillCallback()
                self._currentSkillCallback = None
                return

            if skill.triggersGcd:
                self._sharedCooldownTimer = int(skill.cooldown * 30)
                self._notifyCooldownStart()
