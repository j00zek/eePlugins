#j00zek, name changed to assure no conflicts
from Plugins.Plugin import PluginDescriptor

def sessionstart(session, **kwargs):
    try:
        from Components.Sources.j00zekMSNWeather import j00zekMSNWeather
        session.screen['j00zekMSNWeather'] = j00zekMSNWeather()
    except Exception as e:
        print("Exception: %s" % str(e))


def Plugins(**kwargs):
    return [PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=sessionstart)]