# -*- coding: utf-8 -*-

from .QuModLibs.QuMod import *

MyMod = EasyMod()

# server
MyMod.Server("portal.server.server")
MyMod.Server("items.server.server")
MyMod.Server("enchantment.server.server")
MyMod.Server("ores.server.server")
MyMod.Server("blocks.server.server")
MyMod.Server("terrain.server.server")

# client
MyMod.Client("items.client.client")
MyMod.Client("blocks.client.client")