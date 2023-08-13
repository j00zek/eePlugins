from Plugins.Plugin import PluginDescriptor

def zap(session, service, **kwargs):
    errormsg = None
    if service: 
        try:
            serviceString = service.toString()
            if "EXT%3a" in serviceString:
                url = serviceString
                url = url.split(":")
                if len(url) > 9: #marker that we have something interesting at the end
                    url = url[10]
                    url = url.replace("EXT%3a", "")
                    url = url.replace("%3a", ":")
                    print("[ChannelSelection] zap > EXTwrapper result '%s'" % url)
        except Exception as e:
            print("[ChannelSelection] zap > EXTwrapper failed %s" % str(e))
    return (None, errormsg)


def Plugins(**kwargs):
    if 0:
        return [PluginDescriptor(name="EXTwrapper", description="EXTwrapper", where=PluginDescriptor.WHERE_CHANNEL_ZAP, needsRestart = False, fnc=zap)]
    else:
        return []
