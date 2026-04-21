# -*- coding: utf-8 -*-
class BaseSkill(object):
    """
    基础技能类
    """

    def __init__(self, skillId, cooldown=5.0, duration=0.0, triggersGcd=True):
        self.skillId = skillId
        self.cooldown = cooldown
        self.duration = duration  # 技能持续时间 (0表示瞬发)
        self.triggersGcd = triggersGcd

    def onEnter(self, manager):
        """进入技能状态回调"""
        pass

    def onUpdate(self, manager):
        """技能持续更新回调"""
        pass

    def onExit(self, manager):
        """退出技能状态回调"""
        pass

    def canCast(self, manager):
        """是否满足释放条件"""
        return True
