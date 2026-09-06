# -*- coding=utf-8 -*-
import math

from Script_Lemon_Legend.QuModLibs.Client import *
from Script_Lemon_Legend.QuModLibs.Modules.Services.Client import BaseService, BaseBusiness
from Script_Lemon_Legend.client.utils.clientUtils import compFactory
from Script_Lemon_Legend.common.data.biomeData import BiomesEnum
from Script_Lemon_Legend.common.utils import commonUtils


# @singleton
# class BackgroundMusicManager:
#     def __init__(self):
#         self.lastTime = 0
#         self.musicName = ""
#         self.biomeName = ""
#         self.isTrying = False
#         self.musicMap = {
#             LegendBiomeEnum.shimmerForest: ["music.legend_forest.shimmer_forest_1",
#                                             "music.legend_forest.shimmer_forest_2"]
#         }
#
#     def StopTrying(self):
#         self.isTrying = False
#         UnListenForEvent("OnScriptTickClient", self, self.Ticking)
#
#     def SettingBiome(self, biomeType):
#         if biomeType in self.musicMap.keys() and self.biomeName != biomeType:
#             self.biomeName = biomeType
#             musicNameList = self.musicMap[biomeType]  # type: list
#             self.musicName = random.choice(musicNameList)
#
#             if not self.isTrying:
#                 self.isTrying = True
#                 ListenForEvent("OnScriptTickClient", self, self.Ticking)
#         else:
#             self.StopTrying()
#
#     def Ticking(self):
#         self.lastTime += 1
#         if self.lastTime >= (random.randint(10, 20) * 20 * 60):  # 10-20 minutes
#             self.PlayMusic()
#             self.lastTime = 0
#
#     def PlayMusic(self):
#         CallOTClient(playerId, "PlayMusic", {"musicName": self.musicName, "volume": 0.75, "loop": False})


@BaseService.Init  # 服务持久化工作
class BiomeChangeService(BaseService):

    def __init__(self):
        BaseService.__init__(self)
        self.lastBiome = ""
        self.biomeType = ""
        self.biomeComp = compFactory.CreateBiome(playerId)
        self.nowBusiness = None  # type: BaseBusiness | None

    def onCreate(self):
        # 实例化过程正常走完没有遇到报错时将会触发该方法
        BaseService.onCreate(self)

    def onServiceStop(self):
        # 游戏关闭时会强制停用所有服务
        BaseService.onServiceStop(self)

    def onServiceUpdate(self):
        # Update触发逻辑 默认每秒30次
        BaseService.onServiceUpdate(self)
        pos = commonUtils.getIntPos(Entity(playerId).FootPos)
        biomeName = self.biomeComp.GetBiomeName(pos)

        if biomeName != self.lastBiome and biomeName is not None:
            self.lastBiome = biomeName
            self.changeBiome(biomeName)
            # TODO: 完成切换群系的成就

    def changeBiome(self, biomeName):
        targetBiomeType = BiomesEnum.getBiomesType(biomeName)
        if targetBiomeType != self.biomeType:
            if self.nowBusiness is not None:
                self.removeBusiness(self.nowBusiness)

            if targetBiomeType == BiomesEnum.SHIMMER_BIOMES:
                self.nowBusiness = ForestParticleBusiness()
                self.addBusiness(self.nowBusiness)
            elif targetBiomeType == BiomesEnum.ABANDONED_BIOMES:
                self.nowBusiness = AbandonEffectBusiness()
                self.addBusiness(self.nowBusiness)

            self.biomeType = targetBiomeType


# 微光森林环境效果事务
class ForestParticleBusiness(BaseBusiness):
    def __init__(self):
        BaseBusiness.__init__(self)
        self.particleComp = compFactory.CreateParticleSystem(None)
        self.pIdList = []
        self.environmentParticle = "legend_forest:leaves_fall"
        self.particleCooldown = 0
        self.remainingChecks = 8
        self.playerPos = None

    def onCreate(self):
        BaseBusiness.onCreate(self)
        # TODO: 播放背景音乐
        self.listenForEvent("BlockAnimateRandomTickEvent", self.onBlockAnimateRandomTick)

    def onTick(self):
        self.remainingChecks = 8
        self.playerPos = None
        if self.particleCooldown > 0:
            self.particleCooldown -= 1

    def onStop(self):
        self.unListenForEvent("BlockAnimateRandomTickEvent", self.onBlockAnimateRandomTick)
        for pid in self.pIdList:
            if self.particleComp.Exist(pid):
                self.particleComp.Remove(pid)
        self.pIdList = []
        BaseBusiness.onStop(self)

    def onBlockAnimateRandomTick(self, args):
        # 高频回调先限流；冷却/预算耗尽时不读参数、不调用引擎接口。
        if self.particleCooldown > 0 or self.remainingChecks <= 0:
            return
        if args["blockName"] != "legend_forest:leaves_shimmer":
            return
        self.remainingChecks -= 1
        if self.playerPos is None:
            self.playerPos = Entity(playerId).FootPos
            if self.playerPos is None:
                self.remainingChecks = 0
                return
        x, y, z = args["blockPos"]
        dx = x + 0.5 - self.playerPos[0]
        dy = y - self.playerPos[1]
        dz = z + 0.5 - self.playerPos[2]
        if dy < -8 or dy > 64 or dx * dx + dz * dz > 1024:
            return
        # 水平32格、上方64格覆盖高树冠；每3个客户端Tick最多一片。
        self.particleCooldown = 3
        self.pIdList = [pid for pid in self.pIdList if self.particleComp.Exist(pid)]
        pid = self.particleComp.Create(self.environmentParticle, (x + 0.5, y - 0.05, z + 0.5), (0, 0, 0))
        if pid:
            self.pIdList.append(pid)


class AbandonEffectBusiness(BaseBusiness):
    def __init__(self):
        BaseBusiness.__init__(self)
        self.particleComp = compFactory.CreateParticleSystem(None)
        self.molangComp = compFactory.CreateQueryVariable(playerId)
        self.pIdList = []
        self.environmentParticle = "legend_forest:abandon_environment"

        self.footprintParticle = None
        self.alive = False
        self.isStart = False  # 开始使用tick改变天空颜色

    def onCreate(self):
        BaseBusiness.onCreate(self)
        self.alive = True
        self.playParticle()
        # TODO: 播放背景音乐
        # 更改天空颜色以及雾效距离
        comp = compFactory.CreateTime(levelId)
        realTime = abs(math.fmod(comp.GetTime(), 24000) - 6000)
        skyLightColor = self.__smoothTransitionRGB((1, 1, 1), (0.05, 0.05, 0.05), realTime / 24000.0)
        skyColor = commonUtils.getRGBFloatByStr("#51170E")
        targetColor = (skyColor[0] * skyLightColor[0], skyColor[1] * skyLightColor[1], skyColor[2] * skyLightColor[2])
        self.lerpChangeSkyColor(targetColor, 3 * 30.0, isStart=True)

        comp = compFactory.CreateSkyRender(levelId)
        comp.SetStarBrightness(0.5)
        comp = compFactory.CreateFog(levelId)
        comp.SetFogLength(0.0, 256.0)

    def onStop(self):
        self.alive = False
        for pid in self.pIdList:
            if self.particleComp.Exist(pid):
                self.particleComp.Remove(pid)
        self.pIdList = []
        # 还原天空颜色以及雾效距离
        compFactory.CreateFog(playerId).ResetFogLength()
        compFactory.CreateSkyRender(playerId).ResetStarBrightness()
        compFactory.CreateSkyRender(playerId).ResetSkyColor()
        BaseBusiness.onStop(self)

    def onTick(self):
        # 更改天空颜色(时间)
        if self.isStart:
            comp = compFactory.CreateTime(levelId)
            realTime = abs(math.fmod(comp.GetTime(), 24000) - 6000)
            skyLightColor = self.__smoothTransitionRGB((1, 1, 1), (0.05, 0.05, 0.05), realTime / 24000.0)
            skyColor = commonUtils.getRGBFloatByStr("#51170E")
            targetColor = (
                skyColor[0] * skyLightColor[0],
                skyColor[1] * skyLightColor[1],
                skyColor[2] * skyLightColor[2],
            )
            self.lerpChangeSkyColor(targetColor, 1)

        isSprint = self.molangComp.EvalMolangExpression("q.is_sprinting")
        isOnGround = self.molangComp.EvalMolangExpression("q.is_on_ground")
        if isSprint and isOnGround:
            if isSprint["value"] and isOnGround["value"]:
                self.playFootprintParticle()
            else:
                self.stopFootprintParticle()
        else:
            self.stopFootprintParticle()

    def lerpChangeSkyColor(self, targetColor, tick, nowColor=(0, 0, 0, 0), nowTick=0, isStart=False):
        comp = compFactory.CreateSkyRender(playerId)
        if nowTick == 0:
            nowColor = comp.GetSkyColor()
        if nowTick <= tick and self.alive:
            r, g, b = self.__smoothTransitionRGB(nowColor[:3], targetColor[:3], nowTick / tick)
            comp.SetSkyColor((r, g, b, 1.0))
            (
                compFactory.CreateGame(levelId).AddTimer(
                    0.0, lambda: self.lerpChangeSkyColor(targetColor, tick, nowColor, nowTick + 1)
                )
            )
        elif self.alive and isStart:
            self.isStart = True

    def playParticle(self):
        pid = self.particleComp.CreateBindEntityNew(self.environmentParticle, playerId, bone_name="head")
        if self.particleComp.Exist(pid):
            self.pIdList.append(pid)
        else:
            compFactory.CreateGame(levelId).AddTimer(1, self.playParticle)

    def playFootprintParticle(self):
        if self.footprintParticle is None:
            pid = self.particleComp.CreateBindEntityNew(
                "legend_forest:abandon_footprint", playerId, bone_name="leftLeg", offset=(0, -0.5, 0)
            )
            self.pIdList.append(pid)
            self.footprintParticle = pid

    def stopFootprintParticle(self):
        def removeParticle(pid):
            if self.particleComp.Exist(pid):
                self.particleComp.Remove(pid)
                self.pIdList.remove(pid)

        if self.footprintParticle is not None:
            if self.particleComp.Exist(self.footprintParticle):
                self.addTimer(BaseBusiness.Timer(removeParticle, time=1, argsTuple=(self.footprintParticle,)))
            self.footprintParticle = None

    @staticmethod
    def __lerp(start, end, t):
        return start + t * (end - start)

    def __smoothTransitionRGB(self, startRGB, endRGB, t):
        r = self.__lerp(startRGB[0], endRGB[0], t)
        g = self.__lerp(startRGB[1], endRGB[1], t)
        b = self.__lerp(startRGB[2], endRGB[2], t)
        return r, g, b
