from Plugins.Plugin import PluginDescriptor

zapIPTVExtMoviePlayer = None

def zap(session, service, **kwargs):
    def leaveMoviePlayer(answer=None, lastPosition=None, clipLength=None, *args, **kwargs):
        pass
    
    errormsg = None
    if service:
        try:
            serviceString = service.toString()
            url = serviceString.split(":")[10]
            #print("[ChannelSelection] zap > IPTVExtMoviePlayerWrapper serviceString url = '%s'" % url)
            if url != '':
                global zapIPTVExtMoviePlayer
                url = url.replace("%3a", ":")
                urlPartfound = False
                if url.startswith("IPTVExtMoviePlayer://"):
                    #print("[ChannelSelection] zap > IPTVExtMoviePlayerWrapper url starts with 'IPTVExtMoviePlayer://'")
                    urlPartfound = True
                    url = url[21:]
                else:
                    from Components.config import config
                    urlsParts = config.plugins.streamlinkSRV.IPTVExtMoviePlayer.value
                    if urlsParts != '':
                        if not ';' in urlsParts:
                            #print("[ChannelSelection] zap > IPTVExtMoviePlayerWrapper checking '%s' urlPart" % urlsParts)
                            if urlsParts.strip() in url:
                                urlPartfound = True
                        else:
                            for checkPart in urlsParts.split(';'):
                                #print("[ChannelSelection] zap > IPTVExtMoviePlayerWrapper checking '%s' urlPart" % checkPart)
                                if checkPart.strip() in url:
                                    urlPartfound = True
                                    break
                #print("[ChannelSelection] zap > IPTVExtMoviePlayerWrapper urlPartfound = '%s'" % urlPartfound)
                if urlPartfound:
                    if zapIPTVExtMoviePlayer is None:
                        try:
                            from Plugins.Extensions.IPTVPlayer.components.iptvextmovieplayer import IPTVExtMoviePlayer
                            zapIPTVExtMoviePlayer = True
                        except ImportError as e:
                            print("[ChannelSelection] zap > IPTVExtMoviePlayerWrapper importing IPTVPlayer component error '%s'" % str(e))
                    if zapIPTVExtMoviePlayer:
                        print("[ChannelSelection] zap > IPTVExtMoviePlayerWrapper result '%s'" % url)
                        try:
                            titleOfMovie = serviceString.split(":")[11]
                        except Exception:
                            titleOfMovie = url
                        playerVal = 'eplayer' # extgstplayer
                        gstAdditionalParams = {}
                        if 1:
                            session.openWithCallback(leaveMoviePlayer, IPTVExtMoviePlayer, url, titleOfMovie, None, playerVal, gstAdditionalParams)
                        else:
                            #from Components.config import config
                            bufferingPath = config.plugins.iptvplayer.bufferingPath.value
                            downloadingPath = config.plugins.iptvplayer.NaszaSciezka.value
                            bufferSize = config.plugins.iptvplayer.requestedBuffSize.value * 1024 * 1024 * 2
                            from Plugins.Extensions.IPTVPlayer.iptvdm.iptvbuffui import E2iPlayerBufferingWidget
                            session.openWithCallback(leaveMoviePlayer, E2iPlayerBufferingWidget, url, bufferingPath, downloadingPath, titleOfMovie, playerVal, bufferSize, gstAdditionalParams)
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
