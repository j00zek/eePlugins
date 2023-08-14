from Plugins.Plugin import PluginDescriptor
try:
    from Plugins.Extensions.IPTVPlayer.components.iptvextmovieplayer import IPTVExtMoviePlayer
except ImportError as e:
    IPTVExtMoviePlayer = None
    print("[ChannelSelection] zap > IPTVExtMoviePlayerWrapper failed %s" % str(e))

def zap(session, service, **kwargs):
    def leaveMoviePlayer(answer=None, lastPosition=None, clipLength=None, *args, **kwargs):
        pass
    
    errormsg = None
    if IPTVExtMoviePlayer is not None and service:
        try:
            serviceString = service.toString()
            #print("[ChannelSelection] zap > IPTVExtMoviePlayerWrapper serviceString = '%s'" % serviceString)
            if "IPTVExtMoviePlayer%3a" in serviceString:
                url = serviceString.split(":")[10]
                url = url.replace("IPTVExtMoviePlayer%3a//", "")
                url = url.replace("%3a", ":")
                print("[ChannelSelection] zap > IPTVExtMoviePlayerWrapper result '%s'" % url)
                titleOfMovie = 'AQQ'
                playerVal = 'eplayer' # extgstplayer
                gstAdditionalParams = {}
                session.openWithCallback(leaveMoviePlayer, IPTVExtMoviePlayer, url, titleOfMovie, None, playerVal, gstAdditionalParams)
        except Exception as e:
            print("[ChannelSelection] zap > IPTVExtMoviePlayerWrapper failed %s" % str(e))
    return (None, errormsg)


def Plugins(**kwargs):
    try:
        if 1:
            return [PluginDescriptor(name="IPTVExtMoviePlayerWrapper", description="IPTVExtMoviePlayerWrapper", where=PluginDescriptor.WHERE_CHANNEL_ZAP, needsRestart = False, fnc=zap)]
        else:
            return []
    except Exception:
        pass
