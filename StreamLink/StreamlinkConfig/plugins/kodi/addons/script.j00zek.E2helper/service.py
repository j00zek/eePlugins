#https://xbmc.github.io/docs.kodi.tv/master/kodi-dev-kit/group__python__xbmc.html
import os
import xbmc
#from resources.MyService import MonitorService

# run the program
xbmc.log("[E2helper] service.py starting updater for Kodi ....", level=xbmc.LOGINFO)
#xbmc.executebuiltin("PlayMedia(" + "plugin://plugin.video.pgobox/?mode=playtvs&&url=1456452%7Ctv&&page=0&&moviescount=0&&movie=True&&name=POLSAT+SPORT+HD" + ")")

class MyPlayer(xbmc.Player):
    def __init__(self, *args):
        xbmc.log("[E2helper] __init__", level=xbmc.LOGINFO)
        xbmc.Player.__init__(self, *args)

    def onPlayBackStarted(self):
        xbmc.log("[E2helper] onPlayBackStarted", level=xbmc.LOGINFO)

    def onPlayBackEnded(self):
        # This works
        xbmc.log("[E2helper] onPlayBackEnded", level=xbmc.LOGINFO)

    def onPlayBackStopped(self):
        # This works
        xbmc.log("[E2helper] onPlayBackStopped", level=xbmc.LOGINFO)
        #xbmc.shutdown() #nie wyłącza tylko minimalizuje na windzie
        xbmc.executebuiltin('Quit')

    def onPlayBackPaused(self):
        xbmc.log("[E2helper] onPlayBackPaused", level=xbmc.LOGINFO)

    def onPlayBackResumed(self):
        xbmc.log("[E2helper] onPlayBackResumed", level=xbmc.LOGINFO)

player=MyPlayer()
if os.path.exists('/tmp/playInKodi.url'):
    xbmc.log("[E2helper] /tmp/playInKodi.url exists :)", level=xbmc.LOGINFO)
    with open('/tmp/playInKodi.url','r') as f:
        myURL=f.read()
        f.close()
        xbmc.log("[E2helper] xontent to play '%s'" % myURL, level=xbmc.LOGINFO)
        if myURL.startswith('plugin'):
            player.play(myURL)

    while(1):
        if xbmc.Player().isPlayingVideo():
            VIDEO = 1
        else:
            VIDEO = 0

        xbmc.sleep(500) #in ms

#MonitorService().runLoop()
#xbmc.log("[MSNweather] service.py ends", level=xbmc.LOGINFO)

#xbmc.executebuiltin("PlayMedia(" + self.startupPlaylistPath + ")")

#https://kodi.wiki/view/HOW-TO:Modify_the_video_cache#Example_4

#def executeJSONRPC(jsonStr):
#    import json

#    response = json.loads(xbmc.executeJSONRPC(jsonStr))
#    response = response['result'] if 'result' in response else response

#    return response

#executeJSONRPC('{{"jsonrpc": "2.0", "method": "Application.SetVolume", "params": {{ "volume": {0}}}, "id": 1}}'.format(self.volumeLevelPartyMode))


#The script can also be triggered manually using kodi-send:
#kodi-send -a "RunScript(/storage/.kodi/userdata/autoexec.py)"

