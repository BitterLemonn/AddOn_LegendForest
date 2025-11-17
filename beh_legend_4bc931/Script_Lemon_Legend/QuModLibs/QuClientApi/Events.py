# -*- coding: utf-8 -*-
class Events:
    ''' 客户端事件类 '''
    class GridComponentSizeChangedClientEvent:
        ''' 触发时机：UI grid组件里格子数目发生变化时触发 '''
        def __init__(self, dic):
            pass

    class ClientBlockUseEvent:
        ''' 触发时机：玩家右键点击新版自定义方块（或者通过接口AddBlockItemListenForUseEvent增加监听的MC原生游戏方块）时客户端抛出该事件（该事件tick执行，需要注意效率问题）。 '''
        def __init__(self, dic):
            self.playerId = dic.get("playerId")  # type: str
            ''' 玩家Id '''
            self.blockName = dic.get("blockName")  # type: str
            ''' 方块的identifier，包含命名空间及名称 '''
            self.aux = dic.get("aux")  # type: int
            ''' 方块附加值 '''
            self.cancel = dic.get("cancel")  # type: bool
            ''' 设置为True可拦截与方块交互的逻辑。 '''
            self.x = dic.get("x")  # type: int
            ''' 方块x坐标 '''
            self.y = dic.get("y")  # type: int
            ''' 方块y坐标 '''
            self.z = dic.get("z")  # type: int
            ''' 方块z坐标 '''

    class PlayerTryDestroyBlockClientEvent:
        ''' 当玩家试图破坏方块时，客户端线程触发该事件。主要用于床，旗帜，箱子这些根据方块实体数据进行渲染的方块，一般情况下请使用ServerPlayerTryDestroyBlockEvent '''
        def __init__(self, dic):
            self.x = dic.get("x")  # type: int
            ''' 方块x坐标 '''
            self.y = dic.get("y")  # type: int
            ''' 方块y坐标 '''
            self.z = dic.get("z")  # type: int
            ''' 方块z坐标 '''
            self.face = dic.get("face")  # type: int
            ''' 方块被敲击的面向id，参考Facing '''
            self.blockName = dic.get("blockName")  # type: str
            ''' 方块的identifier，包含命名空间及名称 '''
            self.auxData = dic.get("auxData")  # type: int
            ''' 方块附加值 '''
            self.playerId = dic.get("playerId")  # type: str
            ''' 试图破坏方块的玩家ID '''
            self.cancel = dic.get("cancel")  # type: bool
            ''' 默认为False，在脚本层设置为True就能取消该方块的破坏 '''

    class StepOnBlockClientEvent:
        ''' 触发时机：生物脚踩红石矿 '''
        def __init__(self, dic):
            self.cancel = dic.get("cancel")  # type: bool
            ''' 是否允许触发，默认为False，若设为True，可阻止触发后续物理交互事件 '''
            self.blockX = dic.get("blockX")  # type: int
            ''' 方块x坐标 '''
            self.blockY = dic.get("blockY")  # type: int
            ''' 方块y坐标 '''
            self.blockZ = dic.get("blockZ")  # type: int
            ''' 方块z坐标 '''
            self.entityId = dic.get("entityId")  # type: str
            ''' 触发的entity的唯一ID '''
            self.blockName = dic.get("blockName")  # type: str
            ''' 方块的identifier，包含命名空间及名称 '''

    class ClientChestCloseEvent:
        ''' 关闭箱子界面时触发，包括小箱子，合并后大箱子和末影龙箱子 '''
        def __init__(self, dic):
            pass

    class ClientChestOpenEvent:
        ''' 打开箱子界面时触发，包括小箱子，合并后大箱子和末影龙箱子 '''
        def __init__(self, dic):
            self.playerId = dic.get("playerId")  # type: str
            ''' 玩家实体id '''
            self.x = dic.get("x")  # type: int
            ''' 箱子位置x值 '''
            self.y = dic.get("y")  # type: int
            ''' 箱子位置y值 '''
            self.z = dic.get("z")  # type: int
            ''' 箱子位置z值 '''

    class ClientPlayerInventoryCloseEvent:
        ''' 关闭物品背包界面时触发 '''
        def __init__(self, dic):
            pass

    class ClientPlayerInventoryOpenEvent:
        ''' 打开物品背包界面时触发 '''
        def __init__(self, dic):
            self.cancel = dic.get("cancel")  # type: bool
            ''' 取消打开物品背包界面 '''

    class PlayerChatButtonClickClientEvent:
        ''' 玩家点击聊天按钮或回车键触发呼出聊天窗口时客户端抛出的事件 '''
        def __init__(self, dic):
            pass

    class PopScreenEvent:
        ''' screen移除触发 '''
        def __init__(self, dic):
            self.screenName = dic.get("screenName")  # type: str
            ''' UI名字 '''

    class PushScreenEvent:
        ''' screen创建触发 '''
        def __init__(self, dic):
            self.screenName = dic.get("screenName")  # type: str
            ''' UI名字 '''

    class UiInitFinished:
        ''' UI初始化框架完成,此时可以创建UI '''
        def __init__(self, dic):
            pass

    class ClientJumpButtonPressDownEvent:
        ''' 跳跃按钮按下事件，返回值设置参数只对当次按下事件起作用 '''
        def __init__(self, dic):
            self.continueJump = dic.get("continueJump")  # type: bool
            ''' 设置是否执行跳跃逻辑 '''

    class ClientJumpButtonReleaseEvent:
        ''' 跳跃按钮按下释放事件 '''
        def __init__(self, dic):
            pass

    class HoldBeforeClientEvent:
        ''' 玩家长按屏幕，即将响应到游戏内时触发。仅在移动端或pc的F11模式下触发。pc的非F11模式可以使用RightClickBeforeClientEvent事件监听鼠标右键 '''
        def __init__(self, dic):
            self.cancel = dic.get("cancel")  # type: bool
            ''' 设置为True可拦截原版的挖方块/使用物品/与实体交互响应 '''

    class LeftClickBeforeClientEvent:
        ''' 玩家按下鼠标左键时触发。仅在pc的普通控制模式（即非F11模式）下触发。 '''
        def __init__(self, dic):
            self.cancel = dic.get("cancel")  # type: bool
            ''' 设置为True可拦截原版的挖方块或攻击响应 '''

    class LeftClickReleaseClientEvent:
        ''' 玩家松开鼠标左键时触发。仅在pc的普通控制模式（即非F11模式）下触发。 '''
        def __init__(self, dic):
            pass

    class OnClientPlayerStartMove:
        ''' 移动按钮按下触发事件 '''
        def __init__(self, dic):
            pass

    class OnClientPlayerStopMove:
        ''' 移动按钮按下释放时触发事件 '''
        def __init__(self, dic):
            pass

    class OnKeyPressInGame:
        ''' 按键按下时触发 '''
        def __init__(self, dic):
            self.screenName = dic.get("screenName")  # type: str
            ''' 当前screenName '''
            self.key = dic.get("key")  # type: str
            ''' 键码（注：这里的int型被转成了str型，比如"1"对应的就是枚举值文档中的1），详见枚举值文档KeyBoardType '''
            self.isDown = dic.get("isDown")  # type: str
            ''' 是否按下，按下为1，弹起为0 '''

    class RightClickBeforeClientEvent:
        ''' 玩家按下鼠标右键时触发。仅在pc下触发（普通控制模式及F11模式都会触发）。 '''
        def __init__(self, dic):
            self.cancel = dic.get("cancel")  # type: bool
            ''' 设置为True可拦截原版的物品使用/实体交互响应 '''

    class RightClickReleaseClientEvent:
        ''' 玩家松开鼠标右键时触发。仅在pc的普通控制模式（即非F11模式）下触发。在F11下右键，按下会触发RightClickBeforeClientEvent，松开时会触发TapOrHoldReleaseClientEvent '''
        def __init__(self, dic):
            pass

    class TapBeforeClientEvent:
        ''' 玩家点击屏幕并松手，即将响应到游戏内时触发。仅在移动端或pc的F11模式下触发。pc的非F11模式可以使用LeftClickBeforeClientEvent事件监听鼠标左键 '''
        def __init__(self, dic):
            self.cancel = dic.get("cancel")  # type: bool
            ''' 设置为True可拦截原版的攻击或放置响应 '''

    class TapOrHoldReleaseClientEvent:
        ''' 玩家点击屏幕后松手时触发。仅在移动端或pc的F11模式下触发。pc的非F11模式可以使用LeftClickReleaseClientEvent与RightClickReleaseClientEvent事件监听鼠标松开 '''
        def __init__(self, dic):
            pass

    class ChunkAcquireDiscardedClientEvent:
        ''' 触发时机：通过AddChunkPosWhiteList接口添加监听的客户端区块即将被卸载时 '''
        def __init__(self, dic):
            self.dimension = dic.get("dimension")  # type: int
            ''' 区块所在维度 '''
            self.chunkPosX = dic.get("chunkPosX")  # type: int
            ''' 区块的x坐标，对应方块X坐标区间为[x * 16, x * 16 + 15] '''
            self.chunkPosZ = dic.get("chunkPosZ")  # type: int
            ''' 区块的z坐标，对应方块Z坐标区间为[z * 16, z * 16 + 15] '''

    class ChunkLoadedClientEvent:
        ''' 触发时机：通过AddChunkPosWhiteList接口添加监听的客户端区块加载完成时 '''
        def __init__(self, dic):
            self.dimension = dic.get("dimension")  # type: int
            ''' 区块所在维度 '''
            self.chunkPosX = dic.get("chunkPosX")  # type: int
            ''' 区块的x坐标，对应方块X坐标区间为[x * 16, x * 16 + 15] '''
            self.chunkPosZ = dic.get("chunkPosZ")  # type: int
            ''' 区块的z坐标，对应方块Z坐标区间为[z * 16, z * 16 + 15] '''

    class GameTypeChangedClientEvent:
        ''' 个人游戏模式发生变化时客户端触发。 '''
        def __init__(self, dic):
            self.playerId = dic.get("playerId")  # type: str
            ''' 玩家Id '''
            self.oldGameType = dic.get("oldGameType")  # type: int
            ''' 切换前的游戏模式 '''
            self.newGameType = dic.get("newGameType")  # type: int
            ''' 切换后的游戏模式 '''

    class LoadClientAddonScriptsAfter:
        ''' 客户端加载mod完成事件 '''
        def __init__(self, dic):
            pass

    class OnCommandOutputClientEvent:
        ''' 当command命令有成功消息输出时触发 '''
        def __init__(self, dic):
            self.command = dic.get("command")  # type: str
            ''' 命令名称 '''
            self.message = dic.get("message")  # type: str
            ''' 命令返回的消息 '''

    class OnScriptTickClient:
        ''' 客户端tick事件,1秒30次 '''
        def __init__(self, dic):
            pass

    class UnLoadClientAddonScriptsBefore:
        ''' 客户端卸载mod之前触发 '''
        def __init__(self, dic):
            pass

    class AddEntityClientEvent:
        ''' actor实体增加，事件触发 '''
        def __init__(self, dic):
            self.id = dic.get("id")  # type: str
            ''' 实体id '''
            self.posX = dic.get("posX")  # type: float
            ''' 位置x '''
            self.posY = dic.get("posY")  # type: float
            ''' 位置y '''
            self.posZ = dic.get("posZ")  # type: float
            ''' 位置z '''
            self.dimensionId = dic.get("dimensionId")  # type: int
            ''' 实体维度 '''
            self.isBaby = dic.get("isBaby")  # type: bool
            ''' 是否为幼儿 '''
            self.engineTypeStr = dic.get("engineTypeStr")  # type: str
            ''' 实体类型 '''
            self.itemName = dic.get("itemName")  # type: str
            ''' 物品identifier（仅当物品实体时存在该字段） '''
            self.auxValue = dic.get("auxValue")  # type: int
            ''' 物品附加值（仅当物品实体时存在该字段） '''

    class AttackAnimBeginClientEvent:
        ''' modelComp替换骨骼动画后，攻击动作开始，事件触发 '''
        def __init__(self, dic):
            self.id = dic.get("id")  # type: str
            ''' 实体id '''

    class AttackAnimEndClientEvent:
        ''' modelComp替换骨骼动画后，攻击动作结束，事件触发 '''
        def __init__(self, dic):
            self.id = dic.get("id")  # type: str
            ''' 实体id '''

    class EntityStopRidingEvent:
        ''' 触发时机：当实体停止骑乘时 '''
        def __init__(self, dic):
            self.id = dic.get("id")  # type: str
            ''' 实体id '''
            self.rideId = dic.get("rideId")  # type: str
            ''' 坐骑id '''
            self.exitFromRider = dic.get("exitFromRider")  # type: bool
            ''' 是否下坐骑 '''
            self.entityIsBeingDestroyed = dic.get("entityIsBeingDestroyed")  # type: bool
            ''' 坐骑是否将要销毁 '''
            self.switchingRides = dic.get("switchingRides")  # type: bool
            ''' 是否换乘坐骑 '''
            self.cancel = dic.get("cancel")  # type: bool
            ''' 设置为True可以取消（需要与服务端事件一同取消） '''

    class GetEntityByCoordEvent:
        ''' 玩家点击屏幕时触发，多个手指点在屏幕上时，只有第一个会触发。 '''
        def __init__(self, dic):
            pass

    class GetEntityByCoordReleaseClientEvent:
        ''' 玩家点击屏幕后松开时触发，多个手指点在屏幕上时，只有第一个点击的手指松开会触发。 '''
        def __init__(self, dic):
            pass

    class OnGroundClientEvent:
        ''' 实体着地时触发。除了玩家落地之外，沙子，铁砧，掉落的物品，点燃的TNT掉落地面时也会触发 '''
        def __init__(self, dic):
            self.id = dic.get("id")  # type: str
            ''' 实体id '''

    class RemoveEntityClientEvent:
        ''' 实体被移除时，事件触发 '''
        def __init__(self, dic):
            self.id = dic.get("id")  # type: str
            ''' 移除的实体id '''

    class StartRidingClientEvent:
        ''' 触发时机：一个实体即将骑乘另外一个实体 '''
        def __init__(self, dic):
            self.cancel = dic.get("cancel")  # type: bool
            ''' 是否允许触发，默认为False，若设为True，可阻止触发后续的实体交互事件 '''
            self.actorId = dic.get("actorId")  # type: str
            ''' 骑乘者的唯一ID '''
            self.victimId = dic.get("victimId")  # type: str
            ''' 被骑乘实体的唯一ID '''

    class WalkAnimBeginClientEvent:
        ''' modelComp替换骨骼动画后，走路动作开始，事件触发 '''
        def __init__(self, dic):
            self.id = dic.get("id")  # type: str
            ''' 实体id '''

    class WalkAnimEndClientEvent:
        ''' modelComp替换骨骼动画后，走路动作结束，事件触发 '''
        def __init__(self, dic):
            self.id = dic.get("id")  # type: str
            ''' 实体id '''

    class AddPlayerAOIClientEvent:
        ''' 玩家加入游戏或者其余玩家进入当前玩家所在的区块时触发的AOI事件，替换AddPlayerEvent '''
        def __init__(self, dic):
            self.playerId = dic.get("playerId")  # type: str
            ''' 玩家id '''

    class ApproachEntityClientEvent:
        ''' 玩家靠近生物时触发 '''
        def __init__(self, dic):
            self.playerId = dic.get("playerId")  # type: str
            ''' 玩家实体id '''
            self.entityId = dic.get("entityId")  # type: str
            ''' 靠近的生物实体id '''

    class ClientShapedRecipeTriggeredEvent:
        ''' 玩家获取配方物品时触发 '''
        def __init__(self, dic):
            self.recipeId = dic.get("recipeId")  # type: str
            ''' 配方id '''

    class DimensionChangeClientEvent:
        ''' 玩家维度改变时客户端抛出 '''
        def __init__(self, dic):
            self.playerId = dic.get("playerId")  # type: str
            ''' 玩家实体id '''
            self.fromDimensionId = dic.get("fromDimensionId")  # type: int
            ''' 维度改变前的维度 '''
            self.toDimensionId = dic.get("toDimensionId")  # type: int
            ''' 维度改变后的维度 '''
            self.fromX = dic.get("fromX")  # type: float
            ''' 改变前的位置x '''
            self.fromY = dic.get("fromY")  # type: float
            ''' 改变前的位置Y '''
            self.fromZ = dic.get("fromZ")  # type: float
            ''' 改变前的位置Z '''
            self.toX = dic.get("toX")  # type: float
            ''' 改变后的位置x '''
            self.toY = dic.get("toY")  # type: float
            ''' 改变后的位置Y '''
            self.toZ = dic.get("toZ")  # type: float
            ''' 改变后的位置Z '''

    class ExtinguishFireClientEvent:
        ''' 玩家扑灭火焰时触发。下雨，倒水等方式熄灭火焰不会触发。 '''
        def __init__(self, dic):
            self.pos = dic.get("pos")  # type: tuple(float,float,float)
            ''' 火焰方块的坐标 '''
            self.playerId = dic.get("playerId")  # type: str
            ''' 玩家id '''
            self.cancel = dic.get("cancel")  # type: bool
            ''' 修改为True时，可阻止玩家扑灭火焰。需要与ExtinguishFireServerEvent一起修改。 '''

    class LeaveEntityClientEvent:
        ''' 玩家远离生物时触发 '''
        def __init__(self, dic):
            self.playerId = dic.get("playerId")  # type: str
            ''' 玩家实体id '''
            self.entityId = dic.get("entityId")  # type: str
            ''' 远离的生物实体id '''

    class OnLocalPlayerStopLoading:
        ''' 触发时机：玩家进入存档，出生点地形加载完成时触发。该事件触发时可以进行切换维度的操作。 '''
        def __init__(self, dic):
            self.playerId = dic.get("playerId")  # type: str
            ''' 加载完成的玩家id '''

    class OnPlayerHitBlockClientEvent:
        ''' 触发时机：通过OpenPlayerHitBlockDetection打开方块碰撞检测后，当玩家碰撞到方块时触发该事件。玩家着地时会触发OnGroundClientEvent，而不是该事件。客户端和服务端分别作碰撞检测，可能两个事件返回的结果略有差异。 '''
        def __init__(self, dic):
            self.playerId = dic.get("playerId")  # type: str
            ''' 碰撞到方块的玩家Id '''
            self.posX = dic.get("posX")  # type: int
            ''' 碰撞方块x坐标 '''
            self.posY = dic.get("posY")  # type: int
            ''' 碰撞方块y坐标 '''
            self.posZ = dic.get("posZ")  # type: int
            ''' 碰撞方块z坐标 '''
            self.blockId = dic.get("blockId")  # type: str
            ''' 碰撞方块的identifier '''
            self.auxValue = dic.get("auxValue")  # type: int
            ''' 碰撞方块的附加值 '''

    class OnPlayerHitMobClientEvent:
        ''' 触发时机：通过OpenPlayerHitMobDetection打开生物碰撞检测后，当有生物与玩家碰撞时触发该事件。注：客户端和服务端分别作碰撞检测，可能两个事件返回的结果略有差异。 '''
        def __init__(self, dic):
            self.playerList = dic.get("playerList")  # type: list
            ''' 生物碰撞到的玩家id的list '''

    class PerspChangeClientEvent:
        ''' 视角切换时会触发的事件 '''
        def __init__(self, dic):
            self.From = dic.get("from")  # type: int
            ''' 切换前的视角 '''
            self.to = dic.get("to")  # type: int
            ''' 切换后的视角 '''

    class RemovePlayerAOIClientEvent:
        ''' 玩家离开当前玩家同一个区块时触发AOI事件 '''
        def __init__(self, dic):
            self.playerId = dic.get("playerId")  # type: str
            ''' 玩家id '''

    class StartDestroyBlockClientEvent:
        ''' 玩家开始挖方块时触发。创造模式下不触发。 '''
        def __init__(self, dic):
            self.pos = dic.get("pos")  # type: tuple(float,float,float)
            ''' 方块的坐标 '''
            self.blockName = dic.get("blockName")  # type: str
            ''' 方块的identifier，包含命名空间及名称 '''
            self.auxValue = dic.get("auxValue")  # type: int
            ''' 方块的附加值 '''
            self.playerId = dic.get("playerId")  # type: str
            ''' 玩家id '''
            self.cancel = dic.get("cancel")  # type: bool
            ''' 修改为True时，可阻止玩家进入挖方块的状态。需要与StartDestroyBlockServerEvent一起修改。 '''

    class ActorAcquiredItemClientEvent:
        ''' 触发时机：玩家获得物品时客户端抛出的事件（有些获取物品方式只会触发客户端事件，有些获取物品方式只会触发服务端事件，在使用时注意一点。） '''
        def __init__(self, dic):
            self.actor = dic.get("actor")  # type: str
            ''' 获得物品玩家实体id '''
            self.secondaryActor = dic.get("secondaryActor")  # type: str
            ''' 物品给予者玩家实体id，如果不存在给予者的话，这里为空字符串 '''
            self.itemDict = dic.get("itemDict")  # type: dict
            ''' 获取到的物品的物品信息字典 '''
            self.acquireMethod = dic.get("acquireMethod")  # type: int
            ''' 获得物品的方法，详见ItemAcquisitionMethod '''

    class ActorUseItemClientEvent:
        ''' 触发时机：玩家使用物品时客户端抛出的事件（比较特殊不走该事件的例子：1）喝牛奶；2）染料对有水的炼药锅使用；3）盔甲架装备盔甲） '''
        def __init__(self, dic):
            self.playerId = dic.get("playerId")  # type: str
            ''' 玩家实体id '''
            self.itemDict = dic.get("itemDict")  # type: dict
            ''' 使用的物品的物品信息字典 '''
            self.useMethod = dic.get("useMethod")  # type: int
            ''' 使用物品的方法，详见ItemUseMethodEnum '''

    class ClientItemTryUseEvent:
        ''' 玩家点击右键尝试使用物品时客户端抛出的事件，可以通过设置cancel为True取消使用物品 '''
        def __init__(self, dic):
            self.playerId = dic.get("playerId")  # type: str
            ''' 玩家id '''
            self.itemDict = dic.get("itemDict")  # type: dict
            ''' 使用的物品的物品信息字典 '''
            self.cancel = dic.get("cancel")  # type: bool
            ''' 取消使用物品 '''

    class ClientItemUseOnEvent:
        ''' 玩家在对方块使用物品时客户端抛出的事件。注：如果需要取消物品的使用需要同时在ClientItemUseOnEvent和ServerItemUseOnEvent中将ret设置为True才能正确取消。 '''
        def __init__(self, dic):
            self.entityId = dic.get("entityId")  # type: str
            ''' 玩家实体id '''
            self.itemDict = dic.get("itemDict")  # type: dict
            ''' 使用的物品的物品信息字典 '''
            self.x = dic.get("x")  # type: int
            ''' 方块 x 坐标值 '''
            self.y = dic.get("y")  # type: int
            ''' 方块 y 坐标值 '''
            self.z = dic.get("z")  # type: int
            ''' 方块 z 坐标值 '''
            self.blockName = dic.get("blockName")  # type: str
            ''' 方块的identifier '''
            self.blockAuxValue = dic.get("blockAuxValue")  # type: int
            ''' 方块的附加值 '''
            self.face = dic.get("face")  # type: int
            ''' 点击方块的面，参考Facing '''
            self.clickX = dic.get("clickX")  # type: float
            ''' 点击点的x比例位置 '''
            self.clickY = dic.get("clickY")  # type: float
            ''' 点击点的y比例位置 '''
            self.clickZ = dic.get("clickZ")  # type: float
            ''' 点击点的z比例位置 '''
            self.ret = dic.get("ret")  # type: bool
            ''' 设为True可取消物品的使用 '''

    class ItemReleaseUsingClientEvent:
        ''' 触发时机：释放正在使用的物品 '''
        def __init__(self, dic):
            self.playerId = dic.get("playerId")  # type: str
            ''' 玩家id '''
            self.durationLeft = dic.get("durationLeft")  # type: float
            ''' 蓄力剩余时间 '''
            self.itemDict = dic.get("itemDict")  # type: dict
            ''' 使用的物品的物品信息字典 '''
            self.maxUseDuration = dic.get("maxUseDuration")  # type: int
            ''' 最大蓄力时长 '''
            self.cancel = dic.get("cancel")  # type: bool
            ''' 设置为True可以取消 '''

    class OnCarriedNewItemChangedClientEvent:
        ''' 手持物品发生变化时，触发该事件；数量改变不会通知 '''
        def __init__(self, dic):
            self.itemDict = dic.get("itemDict")  # type: dict
            ''' 切换后物品的物品信息字典 '''

    class OnItemSlotButtonClickedEvent:
        ''' 点击快捷栏和背包栏的物品槽时触发 '''
        def __init__(self, dic):
            self.slotIndex = dic.get("slotIndex")  # type: int
            ''' 点击的物品槽的编号 '''

    class StartUsingItemClientEvent:
        ''' 玩家使用物品（目前仅支持Bucket、Trident、RangedWeapon、Medicine、Food、Potion、Crossbow、ChemistryStick）时抛出 '''
        def __init__(self, dic):
            self.playerId = dic.get("playerId")  # type: str
            ''' 玩家实体id '''
            self.itemDict = dic.get("itemDict")  # type: dict
            ''' 使用的物品的物品信息字典 '''

    class StopUsingItemClientEvent:
        ''' 玩家停止使用物品（目前仅支持Bucket、Trident、RangedWeapon、Medicine、Food、Potion、Crossbow、ChemistryStick）时抛出 '''
        def __init__(self, dic):
            self.playerId = dic.get("playerId")  # type: str
            ''' 玩家实体id '''
            self.itemDict = dic.get("itemDict")  # type: dict
            ''' 使用的物品的物品信息字典 '''

    class OnMusicStopClientEvent:
        ''' 音乐停止时，当玩家调用StopCustomMusic来停止自定义背景音乐时，会触发该事件 '''
        def __init__(self, dic):
            self.musicName = dic.get("musicName")  # type: str
            ''' 音乐名称 '''

    class AddPlayerCreatedClientEvent:
        ''' 玩家创建时触发 '''
        def __init__(self, dic):
            self.playerId = dic.get("playerId")  # type: str
            ''' 玩家id '''

    class GameRenderTickEvent:
        ''' 游戏渲染tick事件 '''
        def __init__(self, dic):
            pass

    class CameraMotionStartClientEvent:
        ''' 相机运动器开始事件。相机添加运动器后，运动器开始运行时触发 '''
        def __init__(self, dic):
            self.motionId = dic.get("motionId")  # type: int
            ''' 运动器id '''

    class CameraMotionStopClientEvent:
        ''' 相机运动器停止事件。相机添加运动器并开始运行后，运动器自动停止时触发 '''
        def __init__(self, dic):
            self.motionId = dic.get("motionId")  # type: int
            ''' 运动器id '''
            self.remove = dic.get("remove")  # type: bool
            ''' 是否移除该运动器，设置为False则保留，默认为True，即运动器停止后自动移除 '''

    class DimensionChangeFinishClientEvent:
        ''' 玩家维度改变完成后客户端抛出 '''
        def __init__(self, dic):
            self.playerId = dic.get("playerId")  # type: str
            ''' 玩家实体id '''
            self.fromDimensionId = dic.get("fromDimensionId")  # type: int
            ''' 维度改变前的维度 '''
            self.toDimensionId = dic.get("toDimensionId")  # type: int
            ''' 维度改变后的维度 '''
            self.toPos = dic.get("toPos")  # type: tuple
            ''' 改变后的位置x,y,z,其中y值为脚底加上角色的身高值 '''

    class OnLocalPlayerActionClientEvent:
        ''' 玩家动作事件，当本地玩家开始/停止某些动作时触发该事件 '''
        def __init__(self, dic):
            self.actionType = dic.get("actionType")  # type: int
            ''' 动作事件枚举，详见Minecraft枚举值文档的PlayerActionType '''

    class OnLocalPlayerStartJumpClientEvent:
        ''' 本地玩家开始跳跃时触发 '''
        def __init__(self, dic):
            pass

    class PlayerAttackEntityEvent:
        ''' 触发时机：当本地玩家攻击时触发该事件 '''
        def __init__(self, dic):
            self.playerId = dic.get("playerId")  # type: str
            ''' 玩家id '''
            self.victimId = dic.get("victimId")  # type: str
            ''' 受击者id '''
            self.damage = dic.get("damage")  # type: float
            ''' 客户端收到的是真实伤害值，且修改无效 '''
            self.isCrit = dic.get("isCrit")  # type: bool
            ''' 本次攻击是否产生暴击,不支持修改 '''

    class PlayerPermissionChangeClientEvent:
        ''' 玩家权限变更事件 '''
        def __init__(self, dic):
            self.causePlayerId = dic.get("causePlayerId")  # type: str
            ''' 发起者id '''
            self.playerId = dic.get("playerId")  # type: str
            ''' 玩家id '''
            self.oldPermission = dic.get("oldPermission")  # type: dict
            ''' 变化前的权限字典 '''
            self.newPermission = dic.get("newPermission")  # type: dict
            ''' 变化后的权限字典 '''
            self.changeCause = dic.get("changeCause")  # type: int
            ''' 变化原因，详见Minecraft枚举值文档的PermissionChangeCause '''

    class UpdatePlayerSkinClientEvent:
        ''' 触发时机：玩家加入游戏或通过更衣室局内换肤后 同步皮肤信息至客户端后触发 '''
        def __init__(self, dic):
            self.playerId = dic.get("playerId")  # type: str
            ''' 玩家id '''

    class AnvilCreateResultItemAfterClientEvent:
        ''' 玩家点击铁砧合成得到的物品时抛出的事件 '''
        def __init__(self, dic):
            self.playerId = dic.get("playerId")  # type: str
            ''' 玩家实体id '''
            self.itemShowName = dic.get("itemShowName")  # type: str
            ''' 合成后的物品显示名称 '''
            self.itemDict = dic.get("itemDict")  # type: dict
            ''' 合成后的物品的物品信息字典 '''
            self.oldItemDict = dic.get("oldItemDict")  # type: dict
            ''' 合成前的物品的物品信息字典（铁砧内第一个物品） '''
            self.materialItemDict = dic.get("materialItemDict")  # type: dict
            ''' 合成所使用材料的物品信息字典（铁砧内第二个物品） '''

    class CraftUpdateResultItemClientEvent:
        ''' 玩家工作台界面更新显示可合成物品时抛出的事件 '''
        def __init__(self, dic):
            self.playerId = dic.get("playerId")  # type: str
            ''' 玩家实体id '''
            self.itemDict = dic.get("itemDict")  # type: dict
            ''' 合成后的物品的物品信息字典 '''

    class GrindStoneRemovedEnchantClientEvent:
        ''' 玩家点击砂轮合成得到的物品时抛出的事件 '''
        def __init__(self, dic):
            self.playerId = dic.get("playerId")  # type: str
            ''' 玩家实体id '''
            self.oldItemDict = dic.get("oldItemDict")  # type: dict
            ''' 合成前的物品物品信息字典（砂轮内第一个物品） '''
            self.additionalItemDict = dic.get("additionalItemDict")  # type: dict
            ''' 作为合成材料的物品物品信息字典（砂轮内第二个物品） '''
            self.newItemDict = dic.get("newItemDict")  # type: dict
            ''' 合成后的物品物品信息字典 '''
            self.exp = dic.get("exp")  # type: int
            ''' 本次合成返还的经验 '''

    class InventoryItemChangedClientEvent:
        ''' 玩家背包物品变化时客户端抛出的事件 '''
        def __init__(self, dic):
            self.playerId = dic.get("playerId")  # type: str
            ''' 玩家实体id '''
            self.slot = dic.get("slot")  # type: int
            ''' 背包槽位 '''
            self.oldItemDict = dic.get("oldItemDict")  # type: dict
            ''' 变化前槽位中的物品，格式参考物品信息字典 '''
            self.newItemDict = dic.get("newItemDict")  # type: dict
            ''' 变化后槽位中的物品，格式参考物品信息字典 '''

    class PlayerTryAddCustomContainerItemClientEvent:
        ''' 玩家尝试将物品添加到自定义容器时触发该事件 '''
        def __init__(self, dic):
            self.itemDict = dic.get("itemDict")  # type: dict
            ''' 尝试添加物品的物品信息字典 '''
            self.collectionName = dic.get("collectionName")  # type: str
            ''' 放入容器名称，对应容器json中"custom_description"字段 '''
            self.collectionType = dic.get("collectionType")  # type: str
            ''' 放入容器类型，目前仅支持netease_container和netease_ui_container '''
            self.collectionIndex = dic.get("collectionIndex")  # type: int
            ''' 放入容器索引 '''
            self.x = dic.get("x")  # type: int
            ''' 容器方块x坐标 '''
            self.y = dic.get("y")  # type: int
            ''' 容器方块y坐标 '''
            self.z = dic.get("z")  # type: int
            ''' 容器方块z坐标 '''
            self.cancel = dic.get("cancel")  # type: bool
            ''' 是否取消该操作，默认为false，事件中改为true时拒绝此次放入自定义容器的操作 '''

    class PlayerTryDropItemClientEvent:
        ''' 触发时机：玩家丢弃物品时触发 '''
        def __init__(self, dic):
            self.playerId = dic.get("playerId")  # type: str
            ''' 玩家id '''
            self.itemDict = dic.get("itemDict")  # type: dict
            ''' 物品dict '''
            self.cancel = dic.get("cancel")  # type: bool
            ''' 是否取消此次操作 '''

    class PlayerTryPutCustomContainerItemClientEvent:
        ''' 玩家尝试将物品放入自定义容器时触发该事件 '''
        def __init__(self, dic):
            self.itemDict = dic.get("itemDict")  # type: dict
            ''' 尝试放入物品的物品信息字典 '''
            self.collectionName = dic.get("collectionName")  # type: str
            ''' 放入容器名称，对应容器json中"custom_description"字段 '''
            self.collectionType = dic.get("collectionType")  # type: str
            ''' 放入容器类型，目前仅支持netease_container和netease_ui_container '''
            self.collectionIndex = dic.get("collectionIndex")  # type: int
            ''' 放入容器索引 '''
            self.x = dic.get("x")  # type: int
            ''' 容器方块x坐标 '''
            self.y = dic.get("y")  # type: int
            ''' 容器方块y坐标 '''
            self.z = dic.get("z")  # type: int
            ''' 容器方块z坐标 '''
            self.cancel = dic.get("cancel")  # type: bool
            ''' 是否取消该操作，默认为false，事件中改为true时拒绝此次放入自定义容器的操作 '''

    class PlayerTryRemoveCustomContainerItemClientEvent:
        ''' 玩家尝试从自定义容器中移除物品时触发该事件 '''
        def __init__(self, dic):
            self.itemDict = dic.get("itemDict")  # type: dict
            ''' 尝试移除物品的物品信息字典 '''
            self.collectionName = dic.get("collectionName")  # type: str
            ''' 放入容器名称，对应容器json中"custom_description"字段 '''
            self.collectionType = dic.get("collectionType")  # type: str
            ''' 放入容器类型，目前仅支持netease_container和netease_ui_container '''
            self.collectionIndex = dic.get("collectionIndex")  # type: int
            ''' 目标容器索引 '''
            self.x = dic.get("x")  # type: int
            ''' 容器方块x坐标 '''
            self.y = dic.get("y")  # type: int
            ''' 容器方块y坐标 '''
            self.z = dic.get("z")  # type: int
            ''' 容器方块z坐标 '''
            self.cancel = dic.get("cancel")  # type: bool
            ''' 是否取消该操作，默认为false，事件中改为true时拒绝此次移除物品的操作 '''

    class BlockAnimateRandomTickEvent:
        ''' 触发时机：以摄像机为中心，随机选取周围的方块触发Tick，触发的数量取决于设备性能。只有添加了netease:block_animate_random_tick的自定义方块才会触发此事件 '''
        def __init__(self, dic):
            self.blockPos = dic.get("blockPos")  # type: tuple
            ''' 方块坐标 '''
            self.blockName = dic.get("blockName")  # type: str
            ''' 方块的identifier，包含命名空间及名称 '''
            self.auxData = dic.get("auxData")  # type: int
            ''' 方块附加值 '''

    class FallingBlockCauseDamageBeforeClientEvent:
        ''' 触发时机：当下落的方块开始计算砸到实体的伤害时，客户端触发该事件 '''
        def __init__(self, dic):
            self.fallingBlockId = dic.get("fallingBlockId")  # type: str
            ''' 下落的方块实体id '''
            self.fallingBlockX = dic.get("fallingBlockX")  # type: float
            ''' 下落的方块实体位置x '''
            self.fallingBlockY = dic.get("fallingBlockY")  # type: float
            ''' 下落的方块实体位置y '''
            self.fallingBlockZ = dic.get("fallingBlockZ")  # type: float
            ''' 下落的方块实体位置z '''
            self.blockName = dic.get("blockName")  # type: str
            ''' 重力方块的identifier，包含命名空间及名称 '''
            self.fallTickAmount = dic.get("fallTickAmount")  # type: int
            ''' 下落的方块实体持续下落了多少tick '''
            self.fallDistance = dic.get("fallDistance")  # type: float
            ''' 下落距离 '''
            self.collidingEntitys = dic.get("collidingEntitys")  # type: list
            ''' 碰撞到的实体id列表 '''
            self.fallDamage = dic.get("fallDamage")  # type: float
            ''' 下落伤害 '''
            self.dimensionId = dic.get("dimensionId")  # type: int
            ''' 下落的方块实体维度id '''

    class ModBlockEntityLoadedClientEvent:
        ''' 客户端自定义方块实体初始化完成时触发 '''
        def __init__(self, dic):
            self.posX = dic.get("posX")  # type: int
            ''' 自定义方块实体的位置X '''
            self.posY = dic.get("posY")  # type: int
            ''' 自定义方块实体的位置Y '''
            self.posZ = dic.get("posZ")  # type: int
            ''' 自定义方块实体的位置Z '''
            self.dimensionId = dic.get("dimensionId")  # type: int
            ''' 维度id '''
            self.blockName = dic.get("blockName")  # type: str
            ''' 方块的identifier，包含命名空间及名称 '''

    class ModBlockEntityRemoveClientEvent:
        ''' 客户端自定义方块实体卸载时触发 '''
        def __init__(self, dic):
            self.posX = dic.get("posX")  # type: int
            ''' 自定义方块实体的位置X '''
            self.posY = dic.get("posY")  # type: int
            ''' 自定义方块实体的位置Y '''
            self.posZ = dic.get("posZ")  # type: int
            ''' 自定义方块实体的位置Z '''
            self.dimensionId = dic.get("dimensionId")  # type: int
            ''' 维度id '''
            self.blockName = dic.get("blockName")  # type: str
            ''' 方块的identifier，包含命名空间及名称 '''

    class ModBlockEntityTickClientEvent:
        ''' 客户端自定义方块实体tick事件 '''
        def __init__(self, dic):
            self.posX = dic.get("posX")  # type: int
            ''' 自定义方块实体的位置X '''
            self.posY = dic.get("posY")  # type: int
            ''' 自定义方块实体的位置Y '''
            self.posZ = dic.get("posZ")  # type: int
            ''' 自定义方块实体的位置Z '''
            self.dimensionId = dic.get("dimensionId")  # type: int
            ''' 维度id '''
            self.blockName = dic.get("blockName")  # type: str
            ''' 方块的identifier，包含命名空间及名称 '''

    class OnAfterFallOnBlockClientEvent:
        ''' 触发时机：当实体降落到方块后客户端触发，主要用于力的计算 '''
        def __init__(self, dic):
            self.entityId = dic.get("entityId")  # type: str
            ''' 实体id '''
            self.posX = dic.get("posX")  # type: float
            ''' 实体位置x '''
            self.posY = dic.get("posY")  # type: float
            ''' 实体位置y '''
            self.posZ = dic.get("posZ")  # type: float
            ''' 实体位置z '''
            self.motionX = dic.get("motionX")  # type: float
            ''' 瞬时移动X方向的力 '''
            self.motionY = dic.get("motionY")  # type: float
            ''' 瞬时移动Y方向的力 '''
            self.motionZ = dic.get("motionZ")  # type: float
            ''' 瞬时移动Z方向的力 '''
            self.blockName = dic.get("blockName")  # type: str
            ''' 方块的identifier，包含命名空间及名称 '''
            self.calculate = dic.get("calculate")  # type: bool
            ''' 是否按脚本层传值计算力 '''

    class OnEntityInsideBlockClientEvent:
        ''' 触发时机：当实体碰撞盒所在区域有方块时，客户端持续触发 '''
        def __init__(self, dic):
            self.entityId = dic.get("entityId")  # type: str
            ''' 实体id '''
            self.dimensionId = dic.get("dimensionId")  # type: int
            ''' 实体所在维度id '''
            self.slowdownMultiX = dic.get("slowdownMultiX")  # type: float
            ''' 实体移速X方向的减速比例 '''
            self.slowdownMultiY = dic.get("slowdownMultiY")  # type: float
            ''' 实体移速Y方向的减速比例 '''
            self.slowdownMultiZ = dic.get("slowdownMultiZ")  # type: float
            ''' 实体移速Z方向的减速比例 '''
            self.blockX = dic.get("blockX")  # type: int
            ''' 方块位置x '''
            self.blockY = dic.get("blockY")  # type: int
            ''' 方块位置y '''
            self.blockZ = dic.get("blockZ")  # type: int
            ''' 方块位置z '''
            self.blockName = dic.get("blockName")  # type: str
            ''' 方块的identifier，包含命名空间及名称 '''
            self.cancel = dic.get("cancel")  # type: bool
            ''' 可由脚本层回传True给引擎，阻止触发后续原版逻辑 '''

    class OnModBlockNeteaseEffectCreatedClientEvent:
        ''' 自定义方块实体绑定的特效创建成功事件，在自定义方块实体中绑定的特效创建成功时触发以及使用接口CreateFrameEffectForBlockEntity或CreateParticleEffectForBlockEntity为自定义方块实体添加特效成功时触发 '''
        def __init__(self, dic):
            self.posX = dic.get("posX")  # type: int
            ''' 自定义方块实体的位置X '''
            self.posY = dic.get("posY")  # type: int
            ''' 自定义方块实体的位置Y '''
            self.posZ = dic.get("posZ")  # type: int
            ''' 自定义方块实体的位置Z '''
            self.dimensionId = dic.get("dimensionId")  # type: int
            ''' 维度id '''
            self.blockName = dic.get("blockName")  # type: str
            ''' 方块的identifier，包含命名空间及名称 '''
            self.effectType = dic.get("effectType")  # type: int
            ''' 特效类型，0为序列帧，1为粒子 '''
            self.effectName = dic.get("effectName")  # type: str
            ''' 特效名称 '''

    class OnStandOnBlockClientEvent:
        ''' 触发时机：当实体站立到方块上时客户端持续触发 '''
        def __init__(self, dic):
            self.cancel = dic.get("cancel")  # type: bool
            ''' 是否允许触发，默认为False，若设为True，可阻止触发后续物理交互事件 '''
            self.blockX = dic.get("blockX")  # type: int
            ''' 方块x坐标 '''
            self.blockY = dic.get("blockY")  # type: int
            ''' 方块y坐标 '''
            self.blockZ = dic.get("blockZ")  # type: int
            ''' 方块z坐标 '''
            self.entityId = dic.get("entityId")  # type: str
            ''' 触发的entity的唯一ID '''
            self.blockName = dic.get("blockName")  # type: str
            ''' 方块的identifier，包含命名空间及名称 '''

    class ShearsDestoryBlockBeforeClientEvent:
        ''' 触发时机：玩家手持剪刀破坏方块时，有剪刀特殊效果的方块会在客户端线程触发该事件 '''
        def __init__(self, dic):
            self.playerId = dic.get("playerId")  # type: str
            ''' 玩家id '''
            self.x = dic.get("x")  # type: int
            ''' 方块x坐标 '''
            self.y = dic.get("y")  # type: int
            ''' 方块y坐标 '''
            self.z = dic.get("z")  # type: int
            ''' 方块z坐标 '''
            self.blockName = dic.get("blockName")  # type: str
            ''' 方块的identifier，包含命名空间及名称 '''
            self.auxValue = dic.get("auxValue")  # type: int
            ''' 方块附加值 '''
            self.cancel = dic.get("cancel")  # type: bool
            ''' 设为True可以取消剪刀破坏 '''

    class StepOffBlockClientEvent:
        ''' 触发时机：实体移动离开一个实心方块时触发 '''
        def __init__(self, dic):
            self.cancel = dic.get("cancel")  # type: bool
            ''' 是否允许触发，默认为False，若设为True，可阻止触发后续物理交互事件 '''
            self.blockX = dic.get("blockX")  # type: int
            ''' 方块x坐标 '''
            self.blockY = dic.get("blockY")  # type: int
            ''' 方块y坐标 '''
            self.blockZ = dic.get("blockZ")  # type: int
            ''' 方块z坐标 '''
            self.entityId = dic.get("entityId")  # type: str
            ''' 触发的entity的唯一ID '''
            self.blockName = dic.get("blockName")  # type: str
            ''' 方块的identifier，包含命名空间及名称 '''

    class PlayMusicClientEvent:
        ''' 播放背景音乐时触发 '''
        def __init__(self, dic):
            self.name = dic.get("name")  # type: str
            ''' 即资源包中sounds/music_definitions.json中的event_name，并且对应sounds/sound_definitions.json中的key '''
            self.cancel = dic.get("cancel")  # type: bool
            ''' 设为True可屏蔽该次音效播放 '''

    class PlaySoundClientEvent:
        ''' 播放场景音效或UI音效时触发 '''
        def __init__(self, dic):
            self.name = dic.get("name")  # type: str
            ''' 即资源包中sounds/sound_definitions.json中的key '''
            self.pos = dic.get("pos")  # type: tuple
            ''' 音效播放的位置。UI音效为(0,0,0) '''
            self.volume = dic.get("volume")  # type: float
            ''' 音量，范围为0-1 '''
            self.pitch = dic.get("pitch")  # type: float
            ''' 播放速度，正常速度为1 '''
            self.cancel = dic.get("cancel")  # type: bool
            ''' 设为True可屏蔽该次音效播放 '''

    class GyroSensorChangedClientEvent:
        ''' 触发时机：陀螺仪传感器姿态发生变化时 '''
        def __init__(self, dic):
            self.xDiff = dic.get("xDiff")  # type: float
            ''' x轴角速度，单位为弧度/s '''
            self.yDiff = dic.get("yDiff")  # type: float
            ''' y轴角速度，单位为弧度/s '''
            self.zDiff = dic.get("zDiff")  # type: float
            ''' z轴角速度，单位为弧度/s '''
            self.orientation = dic.get("orientation")  # type: int
            ''' 当前屏幕朝向,0竖屏正向 1横屏向左 2竖屏倒置 3横屏向右 '''
            self.timestamp = dic.get("timestamp")  # type: float
            ''' 触发时间戳,秒 '''

    class MouseWheelClientEvent:
        ''' 鼠标滚轮滚动时触发 '''
        def __init__(self, dic):
            self.direction = dic.get("direction")  # type: int
            ''' 1为向上滚动，0为向下滚动 '''

    class OnBackButtonReleaseClientEvent:
        ''' 返回按钮（目前特指安卓系统导航中的返回按钮）松开时触发 '''
        def __init__(self, dic):
            pass

    class OnGamepadControllerLayoutChangeClientEvent:
        ''' 游戏手柄按键映射改变事件 '''
        def __init__(self, dic):
            self.action = dic.get("action")  # type: str
            ''' 行为 '''
            self.newKey = dic.get("newKey")  # type: int
            ''' 修改后的键码，详见GamepadKeyType枚举 '''
            self.oldKey = dic.get("oldKey")  # type: int
            ''' 修改前的键码，详见GamepadKeyType枚举 '''

    class OnGamepadKeyPressClientEvent:
        ''' 游戏手柄按键事件 '''
        def __init__(self, dic):
            self.screenName = dic.get("screenName")  # type: str
            ''' 当前screenName '''
            self.key = dic.get("key")  # type: int
            ''' 键码，详见GamepadKeyType枚举 '''
            self.isDown = dic.get("isDown")  # type: str
            ''' 是否按下，按下为1，弹起为0 '''

    class OnGamepadStickClientEvent:
        ''' 游戏手柄摇杆事件 '''
        def __init__(self, dic):
            self.key = dic.get("key")  # type: int
            ''' 键码，详见GamepadKeyType枚举 '''
            self.x = dic.get("x")  # type: float
            ''' 摇杆水平方向的值，从左到右取值为 -1.0 ~ 1.0 '''
            self.y = dic.get("y")  # type: float
            ''' 摇杆竖直方向的值，从下到上取值为 -1.0 ~ 1.0 '''

    class OnGamepadTriggerClientEvent:
        ''' 游戏手柄扳机事件 '''
        def __init__(self, dic):
            self.key = dic.get("key")  # type: int
            ''' 键码，详见GamepadKeyType枚举 '''
            self.magnitude = dic.get("magnitude")  # type: float
            ''' 扣动扳机的力度，取值为 0 ~ 1.0 '''

    class OnKeyboardControllerLayoutChangeClientEvent:
        ''' 键盘按键映射改变事件 '''
        def __init__(self, dic):
            self.action = dic.get("action")  # type: str
            ''' 行为 '''
            self.newKey = dic.get("newKey")  # type: int
            ''' 修改后的键码，详见KeyBoardType枚举 '''
            self.oldKey = dic.get("oldKey")  # type: int
            ''' 修改前的键码，详见KeyBoardType枚举 '''

    class OnMouseMiddleDownClientEvent:
        ''' 鼠标按下中键时触发 '''
        def __init__(self, dic):
            self.isDown = dic.get("isDown")  # type: int
            ''' 1为按下，0为弹起 '''
            self.mousePositionX = dic.get("mousePositionX")  # type: float
            ''' 按下时的x坐标 '''
            self.mousePositionY = dic.get("mousePositionY")  # type: float
            ''' 按下时的y坐标 '''

    class AchievementButtonMovedClientEvent:
        ''' 触发时机：使用自定义成就系统的时，拖动成就入口结束时触发 '''
        def __init__(self, dic):
            self.oldPosition = dic.get("oldPosition")  # type: tuple
            ''' 移动前该控件相对父节点的坐标信息，第一项为横轴，第二项为纵轴 '''
            self.newPosition = dic.get("newPosition")  # type: tuple
            ''' 移动后该控件相对父节点的坐标信息，第一项为横轴，第二项为纵轴 '''

    class CloseNeteaseShopEvent:
        ''' 关闭商城界面时触发，包括脚本商城和Apollo插件商城 '''
        def __init__(self, dic):
            pass

    class HudButtonChangedClientEvent:
        ''' 当原生HUD按钮位置或大小发生改变时触发，例如玩家使用了自定义控件功能会触发，可在该事件中修改mod按钮的位置防止重叠 '''
        def __init__(self, dic):
            self.changedList = dic.get("changedList")  # type: tuple
            ''' 修改后的按钮列表 '''

    class PopScreenAfterClientEvent:
        ''' screen移除触发 '''
        def __init__(self, dic):
            self.screenName = dic.get("screenName")  # type: str
            ''' UI名字 '''
            self.screenDef = dic.get("screenDef")  # type: str
            ''' 包含命名空间的UI名字，格式为namespace.screenName '''

    class ScreenSizeChangedClientEvent:
        ''' 改变屏幕大小时会触发的事件 '''
        def __init__(self, dic):
            self.beforeX = dic.get("beforeX")  # type: float
            ''' 屏幕大小改变前的宽度 '''
            self.beforeY = dic.get("beforeY")  # type: float
            ''' 屏幕大小改变前的高度 '''
            self.afterX = dic.get("afterX")  # type: float
            ''' 屏幕大小改变后的宽度 '''
            self.afterY = dic.get("afterY")  # type: float
            ''' 屏幕大小改变后的高度 '''

    class EntityModelChangedClientEvent:
        ''' 实体模型改变事件 '''
        def __init__(self, dic):
            self.id = dic.get("id")  # type: str
            ''' 实体id '''

    class HealthChangeClientEvent:
        ''' 生命值改变事件 '''
        def __init__(self, dic):
            self.id = dic.get("id")  # type: str
            ''' 实体id '''
