# -*- coding: utf-8 -*-
PORTAL_DATA_KEY = "legend_forest:portal_data"

FOREST_DIMENSION_ID = 340654
OVERWORLD_DIMENSION_ID = 0

SKILL_ANIMATE_MOLANG_NAME = "q.mod.skill_id"

# 传送危险方块
DANGEROUS_BLOCKS = frozenset([
    "minecraft:air",
    "legend_forest:log_shimmer",
    "legend_forest:leaves_shimmer",
    "legend_forest:shimmer_vine",
    "minecraft:cave_vines",
    "minecraft:cave_vines_body_with_berries",
    "minecraft:cave_vines_head_with_berries",
    "minecraft:lava",
    "minecraft:flowing_lava",
    "minecraft:fire"
])

# 可剥皮的方块
CAN_STRIPPED_LOGS = frozenset([
    "legend_forest:log_shimmer",
    "legend_forest:root_shimmer",
])

# 重生锚方块
RESPAWN_ANCHOR = frozenset([
    "legend_forest:forest_anchor"
])

# 剪刀精准采集方块
SHEARS_SILK_TOUCH_BLOCKS = frozenset([
    "legend_forest:leaves_shimmer",
    "legend_forest:shimmer_bud",
    "legend_forest:shimmer_grass",
    "legend_forest:shimmer_reed_top"
])

# 禁止精准采集
CANT_SILK_TOUCH_BLOCKS = SHEARS_SILK_TOUCH_BLOCKS | frozenset([
    "legend_forest:candle_flower_bottom",
    "legend_forest:dead_sword_easter_block",
    "legend_forest:ice_thorn",
    "legend_forest:shimmer_grass_block_check",
    "legend_forest:shimmer_lily",
    "legend_forest:shimmer_reed_bottom",
    "legend_forest:spawn_goblin_block",
    "legend_forest:twig_shimmer",
])

# 刷怪方块
SPAWN_BLOCKS = frozenset([
    "legend_forest:goblin_spawn_block",
    "legend_forest:bookshelf_golem_spawn_block"
])

# 不受冰刺影响的生物
ICE_THORN_FILTER = [
    "legend_forest:malfurion"
]

# 棱花乐事食物效果
ARRIS_FOOD_EFFECT = {
    "legend_forest:blue_stew": [
        {
            "name": "arris:comfort",
            "duration": 180,
            "amplifier": 0,
            "chance": 1.0
        }
    ],
    "legend_forest:goblin_soup": [
        {
            "name": "arris:comfort",
            "duration": 60,
            "amplifier": 0,
            "chance": 1.0
        }
    ]
}
