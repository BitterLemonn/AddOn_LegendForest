from Script_Lemon_Legend.QuModLibs.Modules.Services.Server import BaseService
from Script_Lemon_Legend.QuModLibs.Server import *
import common

importlib = common.__builtins__["__import__"]("importlib")
modModuleUtil = importlib.import_module("common.utils.moduleUtil")
game = importlib.import_module("common.game")
customGoalMgr = importlib.import_module("server.gamePlay.AI.customGoalMgr")


class CustomGoalMgr(object):
    def __init__(self):
        self.mGoalClsCache = {}

    def Init(self):
        self.mGoalClsCache = {}
        serverApi.serverlevel.register_goal_creator(self.CreateCustomGoalFromEngine)

    def OnQuitLevel(self):
        self.mGoalClsCache = {}
        serverApi.serverlevel.unregister_goal_creator(self.CreateCustomGoalFromEngine)

    def CreateCustomGoalFromEngine(self, entityId, argsJson, modulePath, clsName):
        key = (modulePath, clsName)
        if key in self.mGoalClsCache:
            return self.mGoalClsCache[key](entityId, argsJson)

        module = modModuleUtil.GetModuleByName(modulePath)

        if module is None:
            return None

        cls = getattr(module, clsName, None)

        if cls is None:
            return None

        self.mGoalClsCache[key] = cls

        return cls(entityId, argsJson)


@BaseService.Init
class CustomGoalService(BaseService):

    def __init__(self):
        BaseService.__init__(self)
        self.mCustomGoalMgr = CustomGoalMgr()

    @BaseService.Listen("LoadServerAddonScriptsAfter")
    def LoadServerAddonScriptsAfter(self, args):
        server = game.GetServer()

        if server.mCustomGoalMgr is not None:
            server.mCustomGoalMgr.OnQuitLevel()
        server.mCustomGoalMgr = self.mCustomGoalMgr
        self.mCustomGoalMgr.Init()

    def onServiceStop(self):
        game.GetServer().mCustomGoalMgr = customGoalMgr.CustomGoalMgr()
        self.mCustomGoalMgr.OnQuitLevel()
        return BaseService.onServiceStop(self)
