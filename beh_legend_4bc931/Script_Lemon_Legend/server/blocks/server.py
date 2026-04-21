# -*- coding: utf-8 -*-
import random
import re

from mod.common import minecraftEnum

from Script_Lemon_Legend.common.utils import commonUtils

from Script_Lemon_Legend.server.blocks.anchorService import AnchorService
from Script_Lemon_Legend.common.config import modConfig
from Script_Lemon_Legend.QuModLibs.Modules.Services.Server import BaseService
from Script_Lemon_Legend.QuModLibs.Server import *
from Script_Lemon_Legend.common.config.modConfig import FOREST_DIMENSION_ID
from Script_Lemon_Legend.server.utils import serverUtils
from Script_Lemon_Legend.common.utils.ItemFactory import ItemFactory
from Script_Lemon_Legend.server.utils.serverUtils import compFactory


@BaseService.Init
class ServerService(BaseService):

    def __init__(self):
        BaseService.__init__(self)

    @BaseService.Listen(Events.BlockNeighborChangedServerEvent)
    def onBlockNeighborChangedEvent(self, data):
        data = Events.BlockNeighborChangedServerEvent(data)
        pos = data.posX, data.posY, data.posZ
        if (
            data.blockName == "legend_forest:ice_thorn"
            and data.toBlockName == "minecraft:air"
            and data.neighborPosY == data.posY - 1
        ):
            comp = compFactory.CreateBlockInfo(levelId)
            comp.SetBlockNew(pos, {"name": "minecraft:air"}, dimensionId=data.dimensionId, oldBlockHandling=1)

    @BaseService.Listen(Events.ServerBlockEntityTickEvent)
    def onEntityTickEvent(self, data):
        data = Events.ServerBlockEntityTickEvent(data)
        pos = data.posX, data.posY, data.posZ
        # 刷怪石产生怪物
        if data.blockName in modConfig.SPAWN_BLOCKS:
            comp = compFactory.CreateBlockInfo(levelId)
            comp.SetBlockNew(pos, {"name": "minecraft:air"}, dimensionId=data.dimension, updateNeighbors=False)
            spawnEntity = None
            if data.blockName == "legend_forest:goblin_spawn_block":
                if random.random() < 0.2:
                    return
                spawnEntity = "legend_forest:goblin"
            elif data.blockName == "legend_forest:bookshelf_golem_spawn_block":
                spawnEntity = "legend_forest:bookshelf_golem"
            if spawnEntity:
                System.CreateEngineEntityByTypeStr(spawnEntity, pos, (0, 0), data.dimension)

    @BaseService.Listen(Events.OnEntityInsideBlockServerEvent)
    def onEntityInsideBlockEvent(self, data):
        data = Events.OnEntityInsideBlockServerEvent(data)
        ids = Entity(data.entityId).Identifier
        pos = data.blockX, data.blockY, data.blockZ

        # ---------冰刺伤害-----------
        if data.blockName == "legend_forest:ice_thorn" and ids not in modConfig.ICE_THORN_FILTER:
            comp = compFactory.CreateHurt(data.entityId)
            comp.Hurt(random.randint(4, 6), minecraftEnum.ActorDamageCause.Magic, None, None, False)
            comp = compFactory.CreateBlockInfo(data.entityId)
            comp.SetBlockNew(pos, {"name": "minecraft:air"}, 1, Entity(data.entityId).Dm)
            comp = compFactory.CreateEffect(data.entityId)
            comp.AddEffectToEntity("slowness", 5, 0, True)

    @BaseService.REG_API("blocks/server/itemUseOn")
    def onClientItemUseOn(self, data):
        data = Events.ServerItemUseOnEvent(data)
        pos = (data.x, data.y, data.z)
        playerId = getLoaderSystem().rpcPlayerId

        # --------落叶堆叠放置--------
        if (
            "legend_forest" in data.blockName
            and "leaves_cape" in data.blockName
            and "leaves_cape" in data.itemDict["newItemName"]
        ):
            if "3" not in data.blockName and serverUtils.setCooldown(playerId, 3):
                # 检查玩家是否手持目标物品
                item = compFactory.CreateItem(playerId)
                itemDict = item.GetPlayerItem(minecraftEnum.ItemPosType.CARRIED, 0)
                if not ItemFactory.compireItems(itemDict, data.itemDict):
                    return

                serverUtils.decreaseItem(playerId, 1)
                serverUtils.swing(playerId)
                serverUtils.playSoundAll("dig.grass", pos, playerId)

                comp = compFactory.CreateBlockInfo(playerId)
                num = re.findall(r"\d+", data.blockName)[0]
                num = int(num) + 1
                capeName = data.blockName.replace(re.findall(r"\d+", data.blockName)[0], str(num))
                comp.SetBlockNew(pos, {"name": capeName}, dimensionId=Entity(playerId).Dm)

    @BaseService.Listen(Events.ServerItemUseOnEvent)
    def onItemUseOnEvent(self, events):
        data = Events.ServerItemUseOnEvent(events)
        pos = (data.x, data.y, data.z)

        # ---------去树皮------------
        itemComp = compFactory.CreateItem(entityId=data.entityId)
        itemBaseInfo = itemComp.GetItemBasicInfo(data.itemDict["newItemName"])
        if (
            "axe" in data.itemDict["newItemName"] or itemBaseInfo.get("itemType") == "axe"
        ) and data.blockName in modConfig.CAN_STRIPPED_LOGS:
            serverUtils.decreaseDurability(data.entityId, 1)
            serverUtils.swing(data.entityId)
            comp = compFactory.CreateBlockInfo(data.entityId)
            block = comp.GetBlockNew(pos, data.dimensionId)
            identifier = data.blockName.split(":")[0]
            strippedName = identifier + ":stripped_" + data.blockName.split(":")[1]
            comp.SetBlockNew(pos, {"name": strippedName, "aux": block["aux"]}, dimensionId=data.dimensionId)

        # --------森林复苏锚充能-----------
        elif (
            data.itemDict["newItemName"] == "legend_forest:moon_crystal"
            and data.blockName == "legend_forest:forest_anchor"
        ):
            if serverUtils.setCooldown(data.entityId):
                comp = compFactory.CreateBlockState(levelId)
                blockState = comp.GetBlockStates(pos, data.dimensionId)
                level = blockState.get("legend_forest:charged_level", 0)
                if level < 3:
                    serverUtils.swing(data.entityId)
                    serverUtils.playSoundAll("respawn_anchor.charge", pos, data.entityId)
                    serverUtils.decreaseItem(data.entityId, 1)
                    blockState.update({"legend_forest:charged_level": level + 1})
                    comp.SetBlockStates(pos, blockState, data.dimensionId)

    @BaseService.Listen(Events.ServerBlockUseEvent)
    def onBlockUseEvent(self, events):
        data = Events.ServerBlockUseEvent(events)
        pos = (data.x, data.y, data.z)
        # 按下使用获取彩蛋武器
        if data.blockName == "legend_forest:dead_sword_easter_block":
            if serverUtils.setCooldown(data.playerId):
                comp = compFactory.CreateBlockInfo(data.playerId)
                comp.SetBlockNew(pos, {"name": "minecraft:air"}, dimensionId=data.dimensionId, oldBlockHandling=1)
                serverUtils.givePlayerItem(
                    ItemFactory().setItemName("legend_forest:dead_sword_easter").build(), data.playerId
                )
        # 森林锚设置重生点
        elif data.blockName == "legend_forest:forest_anchor":
            comp = compFactory.CreateItem(data.playerId)
            itemDict = comp.GetPlayerItem(minecraftEnum.ItemPosType.CARRIED, 0)
            if not itemDict or itemDict["newItemName"] != "legend_forest:moon_crystal":
                if serverUtils.setCooldown(data.playerId):
                    comp = compFactory.CreateBlockState(levelId)
                    blockState = comp.GetBlockStates(pos, data.dimensionId)
                    if blockState.get("legend_forest:charged_level", 0) > 0:
                        serverUtils.swing(data.playerId)
                        serverUtils.playSoundAll("respawn_anchor.set_spawn", pos, data.playerId)
                        AnchorService.access().setPlayerSpawnAnchor(data.playerId, pos, data.dimensionId)

    @BaseService.Listen("PlayerTrySleepServerEvent")
    def onPlayerTrySleepEvent(self, data):
        playerId = data["playerId"]
        pos = commonUtils.getIntPos(Entity(playerId).Pos)
        dimensionId = Entity(playerId).Dm
        if dimensionId == FOREST_DIMENSION_ID:
            data["cancel"] = True
            comp = compFactory.CreateGame(levelId)
            comp.SetOneTipMessage(playerId, "§6维度中无法使用床绑定重生点§r")

    @BaseService.Listen(Events.ServerPlayerTryDestroyBlockEvent)
    def onPlayerTryDestroyBlockEvent(self, events):
        data = Events.ServerPlayerTryDestroyBlockEvent(events)
        pos = data.x, data.y, data.z

        # ---------剪刀破坏可以采集----------
        if data.fullName in modConfig.SHEARS_SILK_TOUCH_BLOCKS:
            itemComp = compFactory.CreateItem(data.playerId)
            item = itemComp.GetPlayerItem(minecraftEnum.ItemPosType.CARRIED, 0, True)
            itemBasicInfo = itemComp.GetItemBasicInfo(item["newItemName"]) if item else None

            if itemBasicInfo and (itemBasicInfo.get("itemType") == "shears" or "shears" in item["newItemName"]):
                events["spawnResources"] = False
                comp = compFactory.CreateBlockInfo(levelId)
                comp.SpawnResourcesSilkTouched(data.fullName, pos, 0, data.dimensionId)
                return

        # ---------禁用精准采集-----------
        if data.fullName in modConfig.CANT_SILK_TOUCH_BLOCKS:
            itemComp = compFactory.CreateItem(data.playerId)
            item = itemComp.GetPlayerItem(minecraftEnum.ItemPosType.CARRIED, 0, True)

            if ItemFactory(item).getEnchantLevel(minecraftEnum.EnchantType.MiningSilkTouch) > 0:
                events["spawnResources"] = False
                comp = compFactory.CreateBlockInfo(levelId)
                comp.SpawnResources(data.fullName, pos, 0, 1.0, 0, data.dimensionId)
                return
