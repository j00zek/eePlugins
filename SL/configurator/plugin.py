from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Plugins.Plugin import PluginDescriptor
from . import mygettext as _
import sys

if sys.version_info.major > 2: #PyMajorVersion
    from importlib import reload

def main(session, **kwargs):
    import Plugins.Extensions.StreamlinkConfig.StreamlinkConfiguration
    reload(Plugins.Extensions.StreamlinkConfig.StreamlinkConfiguration)
    session.open(Plugins.Extensions.StreamlinkConfig.StreamlinkConfiguration.StreamlinkConfiguration)

def Plugins(path, **kwargs):
    return [PluginDescriptor(name=_("Streamlink Configuration"), where = PluginDescriptor.WHERE_PLUGINMENU, fnc = main, needsRestart = False)]
