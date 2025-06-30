from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from . import PluginName, PluginInfo
from Plugins.Plugin import PluginDescriptor

def main(session, **kwargs):
    from Plugins.Extensions.AdvancedFreePlayer.AFPtreeSelector import AdvancedFreePlayerStart
    session.open(AdvancedFreePlayerStart)

def Plugins(path, **kwargs):
    return PluginDescriptor( name=PluginName, description=PluginInfo,
    where = [ PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU ],
    icon = "AdvancedFreePlayer.png", fnc = main)

