# -*- coding: utf-8 -*-
class BiomesEnum:
    SHIMMER_BIOMES = "shimmer_biomes"
    # 微光森林群系
    SHIMMER_FOREST = "shimmer_forest"
    SHIMMER_FOREST_HILLS = "shimmer_forest_hills"
    SHIMMER_FOREST_POND = "shimmer_forest_pond"

    ABANDONED_BIOMES = "abandoned_biomes"
    # 神弃之地群系
    ABANDONED_LAND = "abandoned_land"

    @classmethod
    def getShimmerBiomes(cls):
        return [
            BiomesEnum.SHIMMER_FOREST,
            BiomesEnum.SHIMMER_FOREST_HILLS,
            BiomesEnum.SHIMMER_FOREST_POND,
        ]

    @classmethod
    def getAbandonedBiomes(cls):
        return [
            BiomesEnum.ABANDONED_LAND,
        ]

    @classmethod
    def getBiomesType(cls, biomeName):
        if biomeName in cls.getShimmerBiomes():
            return cls.SHIMMER_BIOMES
        elif biomeName in cls.getAbandonedBiomes():
            return cls.ABANDONED_BIOMES
        else:
            return None
