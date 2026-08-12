# -*- coding: utf-8 -*-
import random

GROUND_NORMAL = "ground_normal"
GROUND_FAST = "ground_fast"
GROUND_HARD = "ground_hard"
LIT_ATTACK = "lit_attack"
LEAP_SLAM = "leap_slam"
SHOCKWAVE = "shockwave"
GROUND_SKILLS = (GROUND_NORMAL, GROUND_FAST, GROUND_HARD)


def buildWeights(distance, enraged, groundReady, leapReady, shockwaveReady, history):
    if distance > 12.0:
        return {}

    weights = {}
    if distance > 8.0:
        if leapReady:
            weights[LEAP_SLAM] = 8.0
    elif distance > 6.0:
        if leapReady:
            weights[LEAP_SLAM] = 6.0
        if enraged and shockwaveReady:
            weights[SHOCKWAVE] = 4.0
    elif distance > 3.5:
        if groundReady:
            weights.update({GROUND_FAST: 4.0, GROUND_NORMAL: 3.0, GROUND_HARD: 2.0 if enraged else 1.0})
        if distance > 4.5 and leapReady:
            weights[LEAP_SLAM] = 1.0
        if enraged and shockwaveReady:
            weights[SHOCKWAVE] = 4.0
    else:
        weights[LIT_ATTACK] = 5.0
        if groundReady:
            weights.update({GROUND_FAST: 3.0, GROUND_NORMAL: 2.0, GROUND_HARD: 2.0 if enraged else 1.0})
        if enraged and shockwaveReady:
            weights[SHOCKWAVE] = 4.0

    for skillId in weights:
        recentCount = history.count(skillId)
        if recentCount:
            weights[skillId] *= max(0.2, 1.0 - recentCount * 0.4)
    return weights


def chooseSkill(distance, enraged, groundReady, leapReady, shockwaveReady, history, roll=None):
    weights = buildWeights(distance, enraged, groundReady, leapReady, shockwaveReady, history)
    if not weights:
        return None
    total = sum(weights.values())
    choice = (random.random() if roll is None else roll) * total
    for skillId, weight in sorted(weights.items()):
        choice -= weight
        if choice < 0:
            return skillId
    return sorted(weights)[-1]


def _selfCheck():
    assert buildWeights(13.0, False, True, True, True, []) == {}
    assert buildWeights(10.0, False, True, True, True, []) == {LEAP_SLAM: 8.0}
    assert SHOCKWAVE not in buildWeights(7.0, False, True, True, True, [])
    assert SHOCKWAVE in buildWeights(7.0, True, True, True, True, [])
    assert buildWeights(3.0, False, False, False, False, []) == {LIT_ATTACK: 5.0}
    weights = buildWeights(3.0, False, True, False, False, [GROUND_FAST, GROUND_FAST])
    assert abs(weights[GROUND_FAST] - 0.6) < 0.000001
    assert chooseSkill(10.0, False, True, True, True, [], 0.5) == LEAP_SLAM


if __name__ == "__main__":
    _selfCheck()
