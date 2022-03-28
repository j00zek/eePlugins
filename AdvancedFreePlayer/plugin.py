from . import PluginName, PluginInfo
from Plugins.Plugin import PluginDescriptor

def main(session, **kwargs):
    from AFPtreeSelector import AdvancedFreePlayerStart
    session.open(AdvancedFreePlayerStart)

def Plugins(path, **kwargs):
    return PluginDescriptor( name=PluginName, description=PluginInfo,
    where = [ PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU ],
    icon = "AdvancedFreePlayer.png", fnc = main)

