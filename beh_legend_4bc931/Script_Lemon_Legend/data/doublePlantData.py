# -*- coding=utf-8 -*-

class DoublePlantData(object):
    """双层植物数据"""

    _CommonSoil = [
        "minecraft:grass",
        "minecraft:dirt",
        "minecraft:podzol",
        "minecraft:farmland",
        "minecraft:mycelium",
        "minecraft:dirt_with_roots",
        "legend_forest:shimmer_grass_block",
        "legend_forest:shimmer_grass_block_check"
    ]

    DoublePlant = {
        "legend_forest:candle_flower_upper": {
            "plantSoil": _CommonSoil,
            "plantBottom": "legend_forest:candle_flower_bottom",
            "isNeedWater": False
        },
        "legend_forest:reed_shimmer_top": {
            "plantSoil": _CommonSoil,
            "plantBottom": "legend_forest:reed_shimmer_bottom",
            "isNeedWater": True
        }
    }

    class PlantData(object):
        def __init__(self, name, plantSoil, plantBottom, needWater):
            self.name = name
            self.plantSoil = plantSoil
            self.plantBottom = plantBottom
            self.needWater = needWater

    @classmethod
    def isDoublePlant(cls, blockName):
        bottomNames = [data["plantBottom"] for data in cls.DoublePlant.values()]
        return blockName in cls.DoublePlant.keys() or blockName in bottomNames

    @classmethod
    def getPlantData(cls, blockName):
        if blockName in cls.DoublePlant:
            data = cls.DoublePlant[blockName]
            return cls.PlantData(blockName, data["plantSoil"], data["plantBottom"], data["isNeedWater"])
        else:
            for name, data in cls.DoublePlant.items():
                if blockName == data["plantBottom"]:
                    return cls.PlantData(name, data["plantSoil"], data["plantBottom"], data["isNeedWater"])
        return None
