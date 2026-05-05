# -*- coding: utf-8 -*-

from Script_Lemon_Legend.QuModLibs.QuMod import *

MyMod = EasyMod()

# server
MyMod.Server("server.utils.customGoalPatch")
MyMod.Server("server.portal.server")
MyMod.Server("server.items.server")
MyMod.Server("server.enchantment.server")
MyMod.Server("server.blocks.server")
MyMod.Server("server.blocks.oreService")
MyMod.Server("server.terrain.server")
MyMod.Server("server.entity.malfurion.server")
MyMod.Server("server.entity.vine.server")
MyMod.Server("server.entity.goblinShaman.server")
MyMod.Server("server.entity.gozuki.server")

# client
MyMod.Client("client.items.client")
MyMod.Client("client.blocks.client")
MyMod.Client("client.terrain.client")
MyMod.Client("client.entity.client")
