# -*- coding: utf-8 -*- 
from . import _
from Components.j00zekModHex2strColor import Hex2strColor as h2c, clr
from Components.j00zekAccellPixmap import j00zekAccellPixmap

from Components.ActionMap import ActionMap
from datetime import datetime
from enigma import getDesktop, ePoint, eSize, eTimer, ePicLoad
from Components.config import config
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from MSNcomponents.GetAsyncWebDataNP import IMGtoICON
from os import path
from Screens.Screen import Screen
from Tools.LoadPixmap import LoadPixmap

import os, time

DBG = True

class MSNweatherDailyDetails(Screen):

    def __init__(self, session, weatherItems):
        self.session = session
        self.item = weatherItems
        self.skin = open("/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/skins/skin_MSNweatherDailyDetails.xml",'r').read()
        Screen.__init__(self, session)
        self["setupActions"] = ActionMap(["MSNweatherDailyDetails"],
            {
                "keyCancel":  self.cancel,
                "keyNextDay": self.NextDay,
                "keyPreviousDay": self.PreviousDay,
                "keyHourLeft": self.HourLeft,
                "keyHourRight": self.HourRight,
            }, -2)
        
        self.DEBUG('INIT' ,'MSNweatherDailyDetails(Screen).__init__ >>>')

        self.dayIDX = 0
        self.Days = 0
        self.hourIDX = 0
        self.Hours = 0
        self.MaxHours = 6
        
        #TOP LEFT
        self["day_icon"] = j00zekAccellPixmap()
        self["day_skytext"] = StaticText()
        self["day_infoList"] = List([])
        
        #<!-- TOP MIDDLE-->
        self["Day_Forecast"] = StaticText()
        self["details_List"] = List([])
        
        self["hourlyData_title"] = StaticText()
        
        self["h0_infoList"] = List([])
        self["h1_infoList"] = List([])
        self["h2_infoList"] = List([])
        self["h3_infoList"] = List([])
        self["h4_infoList"] = List([])
        self["h5_infoList"] = List([])
        
        #self[""] = List([])
        #self[""] = StaticText()
        #self[""] = j00zekAccellPixmap()
        
        self["key_red"] = Label(_('Cancel'))
        self["key_green"] = Label('')
        self["key_yellow"] = Label('')
        self["key_blue"] = Label('')
       
        self.CurrentSkinPath = '/usr/share/enigma2/%s/weather_icons/' % config.skin.primary_skin.value.replace('skin.xml', '').replace('/', '')
        #self.onLayoutFinish.append(self.startRun)
        self.onShown.append(self.__onShown)
    
    def DEBUG(self, myFUNC = '' , myText = '' ):
        if DBG:
            from Plugins.Extensions.MSNweather.debug import printDEBUG
            printDEBUG( myFUNC , myText, logFileName = 'MSNweatherDailyDetails.log' )

    def __onShown(self):
        self.DEBUG('__onShown', ' >>>')
        self.setTitle(_("Detailed forecast") )
        self.title = _("Detailed forecast")
        self.Days = len(self.item.dictWeather['dailyData']) - 1 #nie liczymy title
        self.DEBUG('__onShown', 'self.Days = %s' % self.Days)
        self.startDelay = eTimer()
        self.startDelay.callback.append(self.startRun)
        self.startDelay.start(30, True)
        
    def startRun(self):
        self.startDelay.stop()
        self.humidity_icon = LoadPixmap(cached=False, path='/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/humidity_icon.png')
        self.temperature_icon = LoadPixmap(cached=False, path='/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/temperature_icon.png')
        self.tempHigh_icon = LoadPixmap(cached=False, path='/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/temp+.png')
        self.tempLow_icon = LoadPixmap(cached=False, path='/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/temp-.png')
        self.rain = LoadPixmap(cached=False, path='/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/rain_icon.png')
        self.uv = LoadPixmap(cached=False, path='/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/uv_icon.png')
        
        self.updateInfo()

    def NextDay(self):
        self.dayIDX += 1
        if self.dayIDX >= self.Days:
            self.dayIDX = 0
        self.hourIDX = 0
        self.updateInfo()
        
    def PreviousDay(self):
        self.dayIDX -= 1
        if self.dayIDX < 0:
            self.dayIDX = self.Days - 1
        self.hourIDX = 0
        self.updateInfo()

    def HourLeft(self):
        if self.hourIDX > 0:
            self.hourIDX -= 1
        self.DEBUG('HourLeft() ', 'self.Hours = %s/%s' % (self.hourIDX,self.Hours))
        self.updateInfo()

    def HourRight(self):
        if self.hourIDX < self.Hours - 1:
            self.hourIDX += 1
        self.DEBUG('HourRight() ', 'self.Hours = %s/%s' % (self.hourIDX,self.Hours))
        self.updateInfo()
        
    def loadIcon(self, iconName = None, dayDetails = {}, hourlyIDX = 0):
        retPNG = None
        if iconName is None or iconName == '' or dayDetails == {}:
            return retPNG
        if iconName == 'dailyIcon':
            if config.plugins.MSNweatherNP.IconsType.value == "serviceIcons":
                iconsList = (str(dayDetails['imgfilename']),str(dayDetails['iconfilename']))
            else:
                iconsList = (str(dayDetails['iconfilename']),str(dayDetails['imgfilename']))
            for tmpIcon in iconsList:
                if tmpIcon.endswith('.png') and os.path.exists(tmpIcon):
                    retPNG = tmpIcon
                    break
        self.DEBUG('loadIcon' , 'retPNG: %s ' % str(retPNG))
        #retPNG = LoadPixmap(cached=True, path=iconfilename)
        return retPNG
        
    def loadWindIcon(self, iconName = None):
        retPNG = None
        self.DEBUG('loadWindIcon' , 'iconName: %s ' % iconName)
        if iconName is None or iconName == '':
            return None
        elif iconName == 'N': 
            retPNG = '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w000_polnoc.png'
        elif iconName == 'NE': 
            retPNG = '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w045_polnocny_wschod.png'
        elif iconName == 'E': 
            retPNG = '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w090_wschod.png'
        elif iconName in ('SE', 'SSE'): 
            retPNG = '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w135_poludniowy_wschod.png'
        elif iconName == 'S': 
            retPNG = '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w180_poludnie.png'
        elif iconName == 'SW': 
            retPNG = '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w225_poludniowy_zachod.png'
        elif iconName == 'W': 
            retPNG = '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w270_zachod.png'
        elif iconName == 'NW': 
            retPNG = '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w315_polnocny_zachod.png'
        else:
            return None

        if not retPNG is None and os.path.exists(retPNG):
            self.DEBUG('loadWindIcon ' , 'retPNG: %s ' % retPNG)
            return LoadPixmap(cached=False, path=retPNG)
        else:
            return None
    
    def updateInfo(self):
        try:
            dayDetails = self.item.dictWeather['dailyData']['Record=%s' % self.dayIDX]
            #self.DEBUG('loadIcon' , 'retPNG: %s ' % str(dayDetails))
            dictdetails = dayDetails['dictdetalis']
            #self.DEBUG('loadIcon' , 'retPNG: %s ' % str(dictdetails))
            #top left
            self["day_icon"].updateIcon(self.loadIcon('dailyIcon' , dayDetails))
            self["day_skytext"].text = str(dictdetails.get('skytext','?'))
            
            windIcon = self.loadWindIcon(str(dictdetails.get('windDir','')))
            self["day_infoList"].list = [(  
                                            self.tempHigh_icon, str(dayDetails.get('temp_high','?')),
                                            self.tempLow_icon,  str(dayDetails.get('temp_low','?')),
                                            self.rain,  str(dayDetails.get('rainprecip','?')),
                                            self.uv,  str(dictdetails.get('uvindex','?')),
                                            windIcon,  str(dictdetails.get('windSpeed','?')),
                                        ),]
            #top middle
            self.DEBUG('updateInfo ' ,'top middle...')
            self["Day_Forecast"].text = str(dayDetails.get('forecast',''))
            sunrise = str(dictdetails['sunrise'])
            sunriseMins = int(sunrise[:2]) * 60 + int(sunrise[-2:])
            sunset = str(dictdetails['sunset'])
            sunsetMins = int(sunset[:2]) * 60 + int(sunset[-2:])
            dayLenghtMins = sunsetMins - sunriseMins
            self["details_List"].list = [(
                                        'Średnia temperatura maksymalna',   clr['R'] + str(dictdetails['avgHi']),
                                        'Najwyższa zanotowana',             "%s%s %s(%s)" % (clr['R'], str(dictdetails['recHi']), clr['Gray'], str(dictdetails['recHiYr']) ),
                                        
                                        'Średnia temperatura minimalna',    clr['B'] + str(dictdetails['avgLo']),
                                        'Najniższa zanotowana',             "%s%s %s(%s)" % (clr['B'], str(dictdetails['recLo']), clr['Gray'], str(dictdetails['recLoYr']) ),
                                        
                                        'Średnie opady deszczu',            str(dictdetails['avgRain']),
                                        'Najwyższe zanotowane',             "%s (%s)" % (str(dictdetails['recRain']), str(dictdetails['recRainYr']) ),

                                        'Wschód słońca',                    sunrise,
                                        'Zachód słońca',                    sunset,
                                        'Dzień będzie trwał %s godzin i %s minut' % (int(dayLenghtMins/60), (dayLenghtMins - int(dayLenghtMins/60)*60)),
                                        
                                        'Wschód księżyca',                  str(dictdetails['moonrise']),
                                        'Zachód księżyca',                  str(dictdetails['moonset']),
                                        str(dictdetails['moon']),
                                        )]
        except Exception as e:
            self.DEBUG('updateInfo Exception: ' ,str(e))

        #hourly
        dicthourly = dayDetails['dicthourly']
        self.Hours = len(dicthourly['times'])
        precipitationsList = dicthourly.get('precipitations', [])
        skyCodesList = dicthourly.get('skyCodes', [])
        skyImagesList = dicthourly.get('skyImages', [])
        skyTextsList = dicthourly.get('skyTexts', [])
        temperaturesList = dicthourly.get('temperatures', [])
        timesList = dicthourly.get('times', [])
        windList = dicthourly.get('wind', [])
        windDirList = dicthourly.get('windDir', [])
        try:
            self.DEBUG('updateInfo ' ,'cleaning hourly data...')
            hIDX = 0
            while hIDX < self.Hours:
                listName = "h%s_infoList" % hIDX
                self[listName].list = []
                hIDX += 1
        except Exception as e:
            self.DEBUG('updateInfo Exception cleaning hourly data: ' ,str(e))
        try:
            self.DEBUG('updateInfo ' ,'updating hourly data...')
            hIDX = 0
            while hIDX < self.Hours:
                listName = "h%s_infoList" % hIDX
                hourIDX = self.hourIDX + hIDX
                skytext = str(skyTextsList[hourIDX])
                weatherIcon =  str(skyImagesList[hourIDX]).split('entityid/')[1].split('.img?')[0]
                imgWeather = '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/%s.png' % weatherIcon
                iconWeather = self.CurrentSkinPath + IMGtoICON('%s.png' % weatherIcon, skytext, int(timesList[hourIDX]), 6, 21)
                self.DEBUG('updateInfo ' ,iconWeather)
                if config.plugins.MSNweatherNP.IconsType.value != "serviceIcons" and os.path.exists(iconWeather):
                    weatherIcon = LoadPixmap(cached=False, path=iconWeather)
                elif os.path.exists(imgWeather):
                    weatherIcon = LoadPixmap(cached=False, path=imgWeather)
                else:
                    weatherIcon = None
                windIcon = self.loadWindIcon(str(windDirList[hourIDX]))
                self[listName].list = [(
                                        str(timesList[hourIDX]) + ':00',
                                        weatherIcon,
                                        self.temperature_icon, str(temperaturesList[hourIDX]) + '°C',
                                        self.rain,  str(precipitationsList[hourIDX]) + '%',
                                        windIcon,  str(windList[hourIDX]) + 'km/h',
                                        skytext,
                                        )]
                hIDX += 1
        except Exception as e:
            self.DEBUG('updateInfo Exception updating hourly data: ' ,str(e))
        
    def keyOk(self):
        self.close()

    def cancel(self):
        self.close()
