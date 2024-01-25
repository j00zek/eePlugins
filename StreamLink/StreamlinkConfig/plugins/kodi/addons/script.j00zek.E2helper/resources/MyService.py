import xbmc, xbmcaddon

class MonitorService:
    AbortWaitTime = 15 # initial wait to give kodi time to run everything
    FirstRun = True

    def __init__(self):
        pass

    def runLoop(self):
        monitor = xbmc.Monitor()
        # run until abort requested
        while not monitor.abortRequested():
            # Sleep/wait for abort
            xbmc.log("[E2helper:MonitorService] self.AbortWaitTime = %s" % self.AbortWaitTime, level=xbmc.LOGINFO)
            if monitor.waitForAbort(self.AbortWaitTime):
                # Abort was requested while waiting. We should exit
                break
            if self.FirstRun:
                self.AbortWaitTime = 1200 #20 minutes
                self.FirstRun = False
#            if xbmcaddon.Addon('weather.MSNweatherNP').getSettingBool("config.plugins.MSNweatherNP.DebugGetWeatherBasic"):
#                xbmc.log("[MSNweather] Updater initiates update of default location", level=xbmc.LOGINFO)
#            getWeather().getDefaultWeatherData() 
