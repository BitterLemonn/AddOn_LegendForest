# -*- coding=utf-8 -*-
import random

from mod.common import minecraftEnum

from ...QuModLibs.Modules.Services.Server import BaseService
from ...QuModLibs.Server import *
from ...data.doublePlantData import DoublePlantData
from ...logging import logging
from ...utils import serverUtils
from ...utils.serverUtils import compFactory


@BaseService.Init
class ServerService(BaseService):

    def __init__(self):
        BaseService.__init__(self)
        self.saplings = ["legend_forest:sapling_shimmer"]

    @BaseService.Listen(Events.BlockNeighborChangedServerEvent)
    def onBlockNeighborChangedServerEvent(self, data):
        data = Events.BlockNeighborChangedServerEvent(data)
        pos = data.posX, data.posY, data.posZ
        # 微光草方块更新后改为tick
        if data.blockName == "legend_forest:shimmer_grass_block_check":
            comp = compFactory.CreateBlockInfo(levelId)
            comp.SetBlockNew(pos, {"name": "legend_forest:shimmer_grass_block"}, dimensionId=data.dimensionId,
                             updateNeighbors=False)
        # 蜡烛花和微光芦苇破坏
        elif "legend_forest:candle_flower_bottom" == data.blockName and "legend_forest:candle_flower_upper" == data.fromBlockName:
            comp = compFactory.CreateBlockInfo(levelId)
            comp.SetBlockNew(pos, {"name": "minecraft:air"}, dimensionId=data.dimensionId, updateNeighbors=False)
        elif "legend_forest:reed_shimmer_bottom" == data.blockName and "legend_forest:reed_shimmer_top" == data.fromBlockName:
            comp = compFactory.CreateBlockInfo(levelId)
            comp.SetBlockNew(pos, {"name": "minecraft:water", "aux": 0}, dimensionId=data.dimensionId,
                             updateNeighbors=False)

    @BaseService.Listen(Events.ServerItemUseOnEvent)
    def onServerItemUseOnEvent(self, data):
        data = Events.ServerItemUseOnEvent(data)
        pos = data.x, data.y, data.z

        # 双层植物放置
        if DoublePlantData.isDoublePlant(data.itemDict["newItemName"]):
            plantData = DoublePlantData.getPlantData(data.itemDict["newItemName"])
            plantSoil = plantData.plantSoil
            if data.blockName in plantSoil and data.face == minecraftEnum.Facing.Up:
                if serverUtils.setCooldown(data.entityId):
                    comp = compFactory.CreateBlockInfo(data.entityId)
                    replacePos = (data.x, data.y + 1, data.z)
                    upperPos = (replacePos[0], replacePos[1] + 1, replacePos[2])
                    # 判断是否可替换
                    upperBlock = comp.GetBlockNew(upperPos, data.dimensionId)
                    replaceBlock = comp.GetBlockNew(replacePos, data.dimensionId)
                    if not upperBlock["name"] == "minecraft:air":
                        return
                    if (plantData.needWater and replaceBlock["name"] == "minecraft:water") or \
                            (not plantData.needWater and replaceBlock["name"] == "minecraft:air"):
                        serverUtils.decreaseItem(data.entityId, 1)
                        serverUtils.swing(data.entityId)
                        serverUtils.playSoundAll("dig.grass", pos, data.entityId)
                        comp.SetBlockNew(replacePos, {"name": plantData.plantBottom}, dimensionId=data.dimensionId,
                                         updateNeighbors=False)
                        comp.SetBlockNew(upperPos, {"name": data.itemDict["newItemName"]}, dimensionId=data.dimensionId,
                                         updateNeighbors=False)

        if data.blockName in self.saplings and "bone_meal" in data.itemDict["newItemName"]:
            if serverUtils.setCooldown(data.entityId):
                serverUtils.decreaseItem(data.entityId, 1)
                serverUtils.swing(data.entityId)
                serverUtils.playSoundAll("item.bone_meal.use", pos, data.entityId)
                serverUtils.playParticle("minecraft:crop_growth_emitter", pos)
                randomNum = random.randint(0, 3)
                if randomNum == 0:
                    self.checkSaplingGrow(data.blockName, pos, data.dimensionId)
        elif "legend_forest:shimmer_grass_block" in data.blockName and "bone_meal" in data.itemDict["newItemName"]:
            if serverUtils.setCooldown(data.entityId):
                comp = compFactory.CreateBlockInfo(data.entityId)
                topPos = data.x, data.y + 1, data.z
                topBlock = comp.GetBlockNew(topPos, data.dimensionId)
                particlePos = (data.x + random.random(), data.y + 1, data.z + random.random())
                if topBlock["name"] == "minecraft:air":
                    serverUtils.decreaseItem(data.entityId, 1)
                    serverUtils.swing(data.entityId)
                    serverUtils.playSoundAll("item.bone_meal.use", pos, data.entityId)
                    serverUtils.playParticle("minecraft:crop_growth_area_emitter", particlePos)

                    comp = compFactory.CreateGame(levelId)
                    comp.PlaceFeature("legend_forest:shimmer_plants_scatter_feature", data.dimensionId, topPos)

    @staticmethod
    def checkSaplingGrow(saplingName, pos, dimensionId):
        x, y, z = pos
        if saplingName == "legend_forest:sapling_shimmer":
            # 判断上方5*6*5的方块是否为空气
            startPos = x - 2, y + 1, z - 2
            endPos = x + 2, y + 6, z + 2
            blockComp = compFactory.CreateBlock(levelId)
            palette = blockComp.GetBlockPaletteBetweenPos(dimensionId, startPos, endPos, False)
            airCount = palette.GetBlockCountInBlockPalette("minecraft:air")
            if airCount >= 120:
                # 判断周围是否为2*2树苗，检查4个可能的位置模式
                # 定义4种2x2排列模式：左下、左上、右下、右上
                patterns = [
                    [(x, y, z), (x, y, z + 1), (x + 1, y, z), (x + 1, y, z + 1)],  # 左下
                    [(x, y, z), (x, y, z + 1), (x - 1, y, z), (x - 1, y, z + 1)],  # 左上
                    [(x, y, z), (x, y, z - 1), (x + 1, y, z), (x + 1, y, z - 1)],  # 右下
                    [(x, y, z), (x, y, z - 1), (x - 1, y, z), (x - 1, y, z - 1)]  # 右上
                ]

                comp = compFactory.CreateBlockInfo(levelId)
                checkPos = None

                # 遍历所有模式，找到第一个符合条件的
                for pattern in patterns:
                    canGrow = True
                    for p in pattern:
                        block = comp.GetBlockNew(p, dimensionId)
                        if block["name"] != "legend_forest:sapling_shimmer":
                            canGrow = False
                            break
                    if canGrow:
                        checkPos = pattern
                        break

                if checkPos:
                    # 生成树
                    for p in checkPos:
                        comp.SetBlockNew(p, {"name": "minecraft:air"}, dimensionId=dimensionId, updateNeighbors=False)
                    comp = compFactory.CreateGame(levelId)
                    comp.PlaceFeature("legend_forest:overworld_shimmer_tree_feature", dimensionId, pos)
                else:
                    logging.info("无法生成树")
