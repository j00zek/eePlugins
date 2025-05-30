# -*- coding: utf-8 -*-

from xbmc import Monitor, Player, getInfoLabel

from resources.lib.proksy.proxy import Proxy
from emukodi import xbmc
from emukodi import xbmcaddon
addon = xbmcaddon.Addon('plugin.video.orangetvgo')
proxyport = addon.getSetting('proxyport')

try:
    # Python 3
    from urllib.parse import quote_plus
    #to_unicode = str
except:
    # Python 2.7
    from urllib import quote_plus


class BackgroundService(Monitor):
    """ Background service code """

    def __init__(self):
        Monitor.__init__(self)
        self._player = PlayerMonitor()
        self._proxy_thread = None

    def run(self):
        """ Background loop for maintenance tasks """

        addon.setSetting('proxyport', None)

        self._proxy_thread = Proxy.start()

        while not self.abortRequested():

            # Stop when abort requested
            if self.waitForAbort(10):
                break

        # Wait for the proxy thread to stop
        if self._proxy_thread and self._proxy_thread.is_alive():

            Proxy.stop()
            
class PlayerMonitor(Player):

    def __init__(self):
        """ Initialises a custom Player object """
        self.__listen = False

        self.__path = None

        Player.__init__(self)

    def onPlayBackStarted(self):  
        """ Will be called when Kodi player starts """
        self.__path = getInfoLabel('Player.FilenameAndPath')
        if not self.__path.startswith('plugin://plugin.video.orangetvgo/'):
            self.__listen = False
            return

        self.__listen = True

    def onPlayBackEnded(self):  
        """ Will be called when [Kodi] stops playing a file """
        if not self.__listen:
            return
        stream_url = str(self.__path).replace('playtv','resetSession')
        xbmc.executebuiltin('RunPlugin(' + stream_url + ')')

        
    def onPlayBackStopped(self):  
        """ Will be called when [user] stops Kodi playing a file """
        if not self.__listen:
            return
        stream_url = str(self.__path).replace('playtv','resetSession')
        xbmc.executebuiltin('RunPlugin(' + stream_url + ')')

def run():
    """ Run the BackgroundService """
    BackgroundService().run()
