from Plugins.Plugin import PluginDescriptor

IPTVExtMoviePlayer = None
KodiLauncher = None

def zap(session, service, **kwargs):
    def leaveIPTVExtMoviePlayer(answer=None, lastPosition=None, clipLength=None, *args, **kwargs):
        pass
    
    def leaveKodiLauncher(answer=None, lastPosition=None, clipLength=None, *args, **kwargs):
        pass
    
    errormsg = None
    if service:
        try:
            serviceString = service.toString()
            url = serviceString.split(":")[10]
            #print("[ChannelSelection] zap > StreamlinkExtWrapper serviceString url = '%s'" % url)
            if url != '':
                global IPTVExtMoviePlayer
                url = url.replace("%3a", ":")
                if url.startswith("IPTVExtMoviePlayer://"):
                    url = url[21:]
                    if IPTVExtMoviePlayer is None:
                        try:
                            from Plugins.Extensions.IPTVPlayer.components.iptvextmovieplayer import IPTVExtMoviePlayer
                            IPTVExtMoviePlayer = IPTVExtMoviePlayer
                        except ImportError as e:
                            print("[ChannelSelection] zap > StreamlinkExtWrapper importing IPTVPlayer component error '%s'" % str(e))
                    if IPTVExtMoviePlayer:
                        print("[ChannelSelection] zap > StreamlinkExtWrapper:IPTVExtMoviePlayer url '%s'" % url)
                        try:
                            titleOfMovie = serviceString.split(":")[11]
                        except Exception:
                            titleOfMovie = url
                        playerVal = 'eplayer' # extgstplayer
                        gstAdditionalParams = {}
                        if 1:
                            session.openWithCallback(leaveIPTVExtMoviePlayer, IPTVExtMoviePlayer, url, titleOfMovie, None, playerVal, gstAdditionalParams)
                        else:
                            #from Components.config import config
                            bufferingPath = config.plugins.iptvplayer.bufferingPath.value
                            downloadingPath = config.plugins.iptvplayer.NaszaSciezka.value
                            bufferSize = config.plugins.iptvplayer.requestedBuffSize.value * 1024 * 1024
                            from Plugins.Extensions.IPTVPlayer.iptvdm.iptvbuffui import E2iPlayerBufferingWidget
                            session.openWithCallback(leaveIPTVExtMoviePlayer, E2iPlayerBufferingWidget, url, bufferingPath, downloadingPath, titleOfMovie, playerVal, bufferSize, gstAdditionalParams)
                elif url.startswith("kodi://"):
                    url = url[7:]
                    print("[ChannelSelection] zap > StreamlinkExtWrapper:kodi url='%s'" % url)
                    global KodiLauncher
                    try:
                        from Plugins.Extensions.Kodi.plugin import startLauncher
                        KodiLauncher = startLauncher
                        session.openWithCallback(leaveKodiLauncher, startLauncher)
                    except ImportError as e:
                        print("[ChannelSelection] zap > StreamlinkExtWrapper importing IPTVPlayer component error '%s'" % str(e))
                elif url.startswith("chrome://"):
                    url = url[9:]
                    print("[ChannelSelection] zap > StreamlinkExtWrapper:chrome url='%s'" % url)
                    try:
                        from Plugins.Extensions.Chromium.plugin import main
                        from base64 import b64decode
                        from Components.config import config
                        oldVal = config.plugins.Chromium.presets[0].portal.value
                        config.plugins.Chromium.presets[0].portal.value = b64decode(url) #'https://player.pl/live/tvn-w-domu-online,8759889'
                        main(session)
                        config.plugins.Chromium.presets[0].portal.value = oldVal
                    except ImportError as e:
                        print("[ChannelSelection] zap > StreamlinkExtWrapper importing IPTVPlayer component error '%s'" % str(e))
        except Exception as e:
            print("[ChannelSelection] zap > StreamlinkExtWrapper failed %s" % str(e))
    return (None, errormsg)


def Plugins(**kwargs):
    try:
        if 1:
            return [PluginDescriptor(name="StreamlinkExtWrapper", description="StreamlinkExtWrapper", where=PluginDescriptor.WHERE_CHANNEL_ZAP, needsRestart = False, fnc=zap)]
        else:
            return []
    except Exception:
        pass
