# -*- coding: utf-8 -*-
import random

from Script_Lemon_Legend.QuModLibs.Modules.Services.Server import BaseService
from Script_Lemon_Legend.QuModLibs.Server import *
from Script_Lemon_Legend.common.config import modConfig
from Script_Lemon_Legend.common.config.modConfig import FOREST_DIMENSION_ID
from Script_Lemon_Legend.common.utils import commonUtils
from Script_Lemon_Legend.common.utils.ItemFactory import ItemFactory
from Script_Lemon_Legend.server.blocks.anchorService import AnchorService
from Script_Lemon_Legend.server.utils import serverUtils
from Script_Lemon_Legend.server.utils.serverUtils import compFactory
from mod.common import minecraftEnum


@BaseService.Init
class ServerService(BaseService):

    def __init__(self):
        BaseService.__init__(self)

    @BaseService.Listen("BlockNeighborChangedServerEvent")
    def onBlockNeighborChangedEvent(self, data):
        pos = data["posX"], data["posY"], data["posZ"]
        if (
            data["blockName"] == "legend_forest:ice_thorn"
            and data["toBlockName"] == "minecraft:air"
            and data["neighborPosY"] == data["posY"] - 1
        ):
            comp = compFactory.CreateBlockInfo(levelId)
            comp.SetBlockNew(pos, {"name": "minecraft:air"}, dimensionId=data["dimensionId"], oldBlockHandling=1)

    @BaseService.Listen("ServerBlockEntityTickEvent")
    def onEntityTickEvent(self, data):
        pos = data["posX"], data["posY"], data["posZ"]
        # 刷怪石产生怪物
        if data["blockName"] in modConfig.SPAWN_BLOCKS:
            # 检测附近是否有玩家
            comp = compFactory.CreateGame(levelId)
            startPos = (data["posX"] - 24, data["posY"] - 24, data["posZ"] - 24)
            endPos = (data["posX"] + 24, data["posY"] + 24, data["posZ"] + 24)
            entityList = comp.GetEntitiesInSquareArea(None, startPos, endPos, data["dimension"])
            if not any(
                serverApi.serverlevel.get_entity_identifier(entityId) == "minecraft:player" for entityId in entityList
            ):
                return

            comp = compFactory.CreateBlockInfo(levelId)
            comp.SetBlockNew(pos, {"name": "minecraft:air"}, dimensionId=data["dimension"], updateNeighbors=False)
            spawnEntity = None
            if data["blockName"] == "legend_forest:goblin_spawn_block":
                if random.random() < 0.2:
                    return
                spawnEntity = "legend_forest:goblin"
            elif data["blockName"] == "legend_forest:bookshelf_golem_spawn_block":
                spawnEntity = "legend_forest:bookshelf_golem"
            if spawnEntity:
                pos = data["posX"] + 0.5, data["posY"], data["posZ"] + 0.5
                System.CreateEngineEntityByTypeStr(spawnEntity, pos, (0, 0), data["dimension"])

    @BaseService.Listen("OnEntityInsideBlockServerEvent")
    def onEntityInsideBlockEvent(self, data):
        ids = Entity(data["entityId"]).Identifier
        pos = data["blockX"], data["blockY"], data["blockZ"]

        # ---------冰刺伤害-----------
        if data["blockName"] == "legend_forest:ice_thorn" and ids not in modConfig.ICE_THORN_FILTER:
            comp = compFactory.CreateHurt(data["entityId"])
            comp.Hurt(random.randint(4, 6), minecraftEnum.ActorDamageCause.Magic, None, None, False)
            comp = compFactory.CreateBlockInfo(data["entityId"])
            comp.SetBlockNew(pos, {"name": "minecraft:air"}, 1, Entity(data["entityId"]).Dm)
            comp = compFactory.CreateEffect(data["entityId"])
            comp.AddEffectToEntity("slowness", 5, 0, True)

    @BaseService.Listen("ServerItemUseOnEvent")
    def onItemUseOnEvent(self, data):
        pos = (data["x"], data["y"], data["z"])

        # ---------去树皮------------
        itemComp = compFactory.CreateItem(entityId=data["entityId"])
        itemBaseInfo = itemComp.GetItemBasicInfo(data["itemDict"]["newItemName"])
        if (
            "axe" in data["itemDict"]["newItemName"] or itemBaseInfo.get("itemType") == "axe"
        ) and data["blockName"] in modConfig.CAN_STRIPPED_LOGS:
            serverUtils.decreaseDurability(data["entityId"], 1)
            serverUtils.swing(data["entityId"])
            comp = compFactory.CreateBlockInfo(data["entityId"])
            block = comp.GetBlockNew(pos, data["dimensionId"])
            identifier = data["blockName"].split(":")[0]
            strippedName = identifier + ":stripped_" + data["blockName"].split(":")[1]
            comp.SetBlockNew(pos, {"name": strippedName, "aux": block["aux"]}, dimensionId=data["dimensionId"])

        # --------森林复苏锚充能-----------
        elif (
            data["itemDict"]["newItemName"] == "legend_forest:moon_crystal"
            and data["blockName"] == "legend_forest:forest_anchor"
        ):
            if serverUtils.setCooldown(data["entityId"]):
                comp = compFactory.CreateBlockState(levelId)
                blockState = comp.GetBlockStates(pos, data["dimensionId"])
                level = blockState.get("legend_forest:charged_level", 0)
                if level < 3:
                    serverUtils.swing(data["entityId"])
                    serverUtils.playSoundAll("respawn_anchor.charge", pos, data["entityId"])
                    serverUtils.decreaseItem(data["entityId"], 1)
                    blockState.update({"legend_forest:charged_level": level + 1})
                    comp.SetBlockStates(pos, blockState, data["dimensionId"])

    @BaseService.Listen("ServerBlockUseEvent")
    def onBlockUseEvent(self, data):
        pos = (data["x"], data["y"], data["z"])
        # 按下使用获取彩蛋武器
        if data["blockName"] == "legend_forest:dead_sword_easter_block":
            if serverUtils.setCooldown(data["playerId"]):
                comp = compFactory.CreateBlockInfo(data["playerId"])
                comp.SetBlockNew(pos, {"name": "minecraft:air"}, dimensionId=data["dimensionId"], oldBlockHandling=1)
                serverUtils.givePlayerItem(
                    ItemFactory().setItemName("legend_forest:dead_sword_easter").build(), data["playerId"]
                )
        # 森林锚设置重生点
        elif data["blockName"] == "legend_forest:forest_anchor":
            comp = compFactory.CreateItem(data["playerId"])
            itemDict = comp.GetPlayerItem(minecraftEnum.ItemPosType.CARRIED, 0)
            if not itemDict or itemDict["newItemName"] != "legend_forest:moon_crystal":
                if serverUtils.setCooldown(data["playerId"]):
                    comp = compFactory.CreateBlockState(levelId)
                    blockState = comp.GetBlockStates(pos, data["dimensionId"])
                    if blockState.get("legend_forest:charged_level", 0) > 0:
                        serverUtils.swing(data["playerId"])
                        serverUtils.playSoundAll("respawn_anchor.set_spawn", pos, data["playerId"])
                        AnchorService.access().setPlayerSpawnAnchor(data["playerId"], pos, data["dimensionId"])

    @BaseService.Listen("PlayerTrySleepServerEvent")
    def onPlayerTrySleepEvent(self, data):
        playerId = data["playerId"]
        pos = commonUtils.getIntPos(Entity(playerId).Pos)
        dimensionId = Entity(playerId).Dm
        if dimensionId == FOREST_DIMENSION_ID:
            data["cancel"] = True
            comp = compFactory.CreateGame(levelId)
            comp.SetOneTipMessage(playerId, "§6维度中无法使用床绑定重生点§r")

    @BaseService.Listen("ServerPlayerTryDestroyBlockEvent")
    def onPlayerTryDestroyBlockEvent(self, data):
        pos = data["x"], data["y"], data["z"]

        # ---------剪刀破坏可以采集----------
        if data["fullName"] in modConfig.SHEARS_SILK_TOUCH_BLOCKS:
            itemComp = compFactory.CreateItem(data["playerId"])
            item = itemComp.GetPlayerItem(minecraftEnum.ItemPosType.CARRIED, 0, True)
            itemBasicInfo = itemComp.GetItemBasicInfo(item["newItemName"]) if item else None

            if itemBasicInfo and (itemBasicInfo.get("itemType") == "shears" or "shears" in item["newItemName"]):
                data["spawnResources"] = False
                comp = compFactory.CreateBlockInfo(levelId)
                comp.SpawnResourcesSilkTouched(data["fullName"], pos, 0, data["dimensionId"])
                return

        # ---------禁用精准采集-----------
        if data["fullName"] in modConfig.CANT_SILK_TOUCH_BLOCKS:
            itemComp = compFactory.CreateItem(data["playerId"])
            item = itemComp.GetPlayerItem(minecraftEnum.ItemPosType.CARRIED, 0, True)

            if ItemFactory(item).getEnchantLevel(minecraftEnum.EnchantType.MiningSilkTouch) > 0:
                data["spawnResources"] = False
                comp = compFactory.CreateBlockInfo(levelId)
                comp.SpawnResources(data["fullName"], pos, 0, 1.0, 0, data["dimensionId"])
                return
