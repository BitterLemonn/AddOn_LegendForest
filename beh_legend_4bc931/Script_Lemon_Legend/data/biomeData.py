class BiomesEnum:
    SHIMMER_FOREST = "shimmer_forest"
    SHIMMER_FOREST_HILLS = "shimmer_forest_hills"
    SHIMMER_FOREST_POND = "shimmer_forest_pond"

    ABANDONED_LAND = "abandoned_land"

    @classmethod
    def getShimmerBiomes(cls):
        return [
            BiomesEnum.SHIMMER_FOREST,
            BiomesEnum.SHIMMER_FOREST_HILLS,
            BiomesEnum.SHIMMER_FOREST_POND,
        ]
