# -*- coding: utf-8 -*-
from Script_Lemon_Legend.QuModLibs.Client import *
from Script_Lemon_Legend.QuModLibs.Modules.Services.Client import BaseService
from Script_Lemon_Legend.common.config.modConfig import SKILL_ANIMATE_MOLANG_NAME
from Script_Lemon_Legend.client.utils.clientUtils import compFactory

molangComp = compFactory.CreateQueryVariable(levelId)
molangComp.Register(SKILL_ANIMATE_MOLANG_NAME, 0.0)


@BaseService.Init
class ClientService(BaseService):
    def __init__(self):
        BaseService.__init__(self)

    @BaseService.REG_API("entity/client/skill/setSkillAnimate")
    def setSkillAnimate(self, entityId, molangValue):
        comp = compFactory.CreateQueryVariable(entityId)
        comp.Set(SKILL_ANIMATE_MOLANG_NAME, molangValue)
