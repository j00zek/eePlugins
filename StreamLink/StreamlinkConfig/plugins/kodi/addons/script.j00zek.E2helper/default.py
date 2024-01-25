# Ten plik jest uruchamiany przy starcie KODI
import os, xbmcaddon, xbmcvfs

if __name__ == '__main__':
    xbmc.log("[E2helper] default.py initiated", level=xbmc.LOGINFO)
    #if not os.path.exists(xbmcaddon.Addon('weather.MSNweatherNP').getSetting('config.pluginconfig.plugins.MSNweatherNP.MSN_defaultsPath')):
    #    xbmcaddon.Addon('weather.MSNweatherNP').setSetting('config.pluginconfig.plugins.MSNweatherNP.MSN_defaultsPath', xbmcvfs.translatePath('special://temp').decode('utf-8'))