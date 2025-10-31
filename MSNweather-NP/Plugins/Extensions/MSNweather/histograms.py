# -*- coding: utf-8 -*- 
from . import _
from Plugins.Extensions.MSNweather.MSNcomponents.mappings import *

from Components.ActionMap import ActionMap
from datetime import datetime
from enigma import getDesktop, ePoint, eSize
from Components.config import config
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.StaticText import StaticText
from os import path
from Screens.Screen import Screen
from Tools.LoadPixmap import LoadPixmap
import os, time

class MSNweatherHistograms(Screen):

    def __init__(self, session, args = 0):
        self.session = session
        if getDesktop(0).size().width() < 1920:
            WindowWidth = 1200
            WindowHeight = 600
            FontSize = 24
            SpaceBetweenBars = 10
            fieldSize = 70
            offset = 80 + fieldSize
            self.scaleSize = 100
        else:
            WindowWidth = 1760
            WindowHeight = 700
            FontSize = 24
            SpaceBetweenBars = 10
            fieldSize = 70
            offset = 80 + fieldSize
            self.scaleSize = 100
        self.maxItems = int(WindowWidth / (fieldSize + SpaceBetweenBars))
        self.skin = '<screen name="MSNweatherHistograms" position="center,center" size="%s,%s" title="What happened in last 24 hours?">\n' % (WindowWidth,WindowHeight)
        
        self.PressureBarPosY = offset + self.scaleSize
        self.TempBarPosY = offset + self.scaleSize * 2 + 50 + 100
        self.windBarPosY = offset + self.scaleSize * 3 + 50 + 100
        
        self.skin += '<widget name="TitlePressure" position="0,%s" size="220,25" font="Regular;20" halign="left" foregroundColor="yellow" />\n' %(100)
        self.skin += '<widget name="TitleTemperature" position="0,%s" size="420,25" font="Regular;20" halign="left" foregroundColor="yellow" />\n' %(self.PressureBarPosY + 100)
        
        i = 0
        while i < self.maxItems:
            posX = i * (fieldSize + SpaceBetweenBars)
            #header
            self.skin += '<widget name="Header%s" position="%s,0" zPosition="5" size="%s,30" halign="center" font="Regular;24" transparent="1"/>\n' % (i, posX, fieldSize)
            self.skin += '<widget name="Icon%s" position="%s,30" zPosition="1" size="%s,%s" alphatest="blend"/>\n' % (i, posX, fieldSize, fieldSize)
            #pressure
            self.skin += '<widget name="bar%s" position="%s,%s" zPosition="1" size="%s,3" alphatest="blend"/>\n' % (i, posX, self.PressureBarPosY, fieldSize)
            self.skin += '<widget render="Label" source="name%s" position="%s,%s" zPosition="5" size="%s,30" foregroundColor="lemon" halign="center" font="Regular;24" transparent="1"/>\n' % (i, posX, self.PressureBarPosY + 10, fieldSize)
            #temperature
            self.skin += '<widget name="tempBar%s" position="%s,%s" zPosition="1" size="%s,3" alphatest="blend"/>\n' % (i, posX, self.TempBarPosY, fieldSize)
            self.skin += '<widget name="curTempBar%s" position="%s,%s" zPosition="2" size="%s,2" alphatest="blend"/>\n' % (i, posX, self.TempBarPosY, fieldSize)
            self.skin += '<widget render="j00zekLabel" source="tempName%s" position="%s,%s" zPosition="5" size="%s,30" foregroundColor="lemon" halign="center" font="Regular;20" transparent="1"/>\n' % (i, posX, self.TempBarPosY + 10, fieldSize)
            #wind
            self.skin += '<widget name="TitleWind" position="0,%s" size="420,25" font="Regular;20" halign="left" foregroundColor="yellow" />\n' %(self.windBarPosY)
            self.skin += '<widget render="j00zekLabel" source="windspeed%s" position="%s,%s" zPosition="5" size="%s,30" foregroundColor="white" halign="center" font="Regular;20" transparent="1"/>\n' % (i, posX, self.windBarPosY + 30, fieldSize)
            self.skin += '<widget name="windIcon%s" position="%s,%s" zPosition="2" size="%s,30" alphatest="blend"/>\n' % (i, posX + 20, self.windBarPosY + 65, fieldSize)
            
            i += 1
        self.skin += '</screen>\n'
        #self.DEBUG(self.skin)

        Screen.__init__(self, session)
        self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
            {
                "cancel": self.cancel,
                "ok": self.keyOk,
                "yellow": self.cancel,
            }, -2)
        
        self.setTitle(_("What happened in weather during last %s hours?") % ( self.maxItems))
        self['TitlePressure'] = Label(_('Pressure'))
        self['TitleTemperature'] = Label(clr['R'] + _('Temperature') + clr['Y'] + ' | ' + clr['B'] + _('Feeling temperature'))
        self['TitleWind'] = Label(_('Wind'))

        self.currTime = int(time.time())
        i = 0
        self.mapDict = {}
        while i < self.maxItems:
            dayANDhour = str(time.strftime("%d%H", time.localtime(self.currTime - (self.maxItems - 1 - i) * 3600)))
            hour = dayANDhour[2:]
            self.mapDict[dayANDhour] = i
            self.DEBUG('self.mapDict[%s] = %s' % (dayANDhour,i))
            self['Header%s' % i] = Label('%s:00' % hour)
            self['Icon%s' % i] = Pixmap()
            #pressure
            self['bar%s' % i] = Pixmap()
            self['name%s' % i] = StaticText()
            #temperature
            self['tempBar%s' % i] = Pixmap()
            self['curTempBar%s' % i] = Pixmap()
            self['tempName%s' % i] = StaticText()
            #wind
            self['windspeed%s' % i] = StaticText()
            self['windIcon%s' % i] = Pixmap()
            
            i += 1
            
        self.barBlue = LoadPixmap(cached=True, path= '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/barBlue.png')
        self.barRed = LoadPixmap(cached=True, path= '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/barRed.png')
       
        self.onLayoutFinish.append(self.startRun)
    
    def DEBUG(self, myFUNC = '' , myText = '' ):
        if config.plugins.MSNweatherNP.DebugEnabled.value:
            from Plugins.Extensions.MSNweather.debug import printDEBUG
            printDEBUG( myFUNC , myText, logFileName='histograms.log' )

    def getTemperature(self, record): #Temperatura odczuwalna=-7\xc2
        try:
            return int(record[2].split('=')[1].strip())
        except Exception:
            return None
    
    def getPressure(self, record): #Barometr=1012.00 mbar
        try:
            return int(record[4].split('=')[1].strip())
        except Exception:
            return None
    
    def getCurrTemperature(self, record): #currTemp=0
        try:
            return int(record[6].split('=')[1].strip())
        except Exception:
            return None
    
    def getIcon(self, record): #iconFilename=/usr/share/enigma2/BlackHarmony/weather_icons/13.png
        try:
            return record[9].split('=')[1].strip()
        except Exception:
            return 'ExceptionIcon'
    
    def getWind(self, record): #iconFilename=/usr/share/enigma2/BlackHarmony/weather_icons/13.png
        try:
            return record[3].split('=')[1].strip()
        except Exception:
            return None
    
    def getWindIcon(self, record): #iconFilename=/usr/share/enigma2/BlackHarmony/weather_icons/13.png
        try:
            retPNG = getWindIconName(str(record[10].split('=')[1].strip()))
            if not retPNG is None and os.path.exists(retPNG):
                self.DEBUG('icons.getWindIcon ' , 'retPNG: %s ' % retPNG)
                return LoadPixmap(cached=False, path=retPNG)
            else:
                return None
        except Exception:
            return None

    #EPOC|0115|Temp. odczuwalna=-5|Wiatr=7|Cisnienie=1010|Wilgotnosc0|currTemp=1|skyCode=27.png|observationtime=15:10:55|iconFilename=/usr/share/enigma2/BlackHarmony/weather_icons/27.png|winddir=S
    def startRun(self):
        self.DEBUG('MSNweatherHistograms(Screen).startRun >>>')
        minPressure = 1000
        maxPressure = 1020
        diffPressure = 0
        stepPressure = 1
        minTemp = 99
        maxTemp = -99
        diffTemp = 0
        stepTemp = 1
        myData = []
        myFile = '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/histograms.data'
        if path.exists(myFile):
            with open(myFile, 'r') as f:
                for line in f:
                    if len(line.strip()) > 0:
                        myData.append(line.strip())
                        record = line.strip().split('|')
                        if self.mapDict.get(str(record[1]), -1) > -1:
                            #pressure
                            pressure = self.getPressure(record)
                            if pressure is not None:
                                if minPressure > pressure:
                                    minPressure = pressure
                                    maxPressure = minPressure + 20
                                if maxPressure < pressure: maxPressure = pressure
                            #temperature
                            temp = self.getTemperature(record)
                            if temp is not None:
                                if minTemp > temp: minTemp = temp
                                if maxTemp < temp: maxTemp = temp
                            #current temperature
                            currtemp = self.getCurrTemperature(record)
                            if currtemp is not None:
                                if minTemp > currtemp: minTemp = currtemp
                                if maxTemp < currtemp: maxTemp = currtemp
                f.close()
        diffPressure = maxPressure - minPressure
        if diffPressure > 0:
            stepPressure = int(self.scaleSize / diffPressure)
        self.DEBUG('\t\t minPressure=%s, maxPressure=%s, diffPressure=%s, stepPressure%s' % (minPressure, maxPressure, diffPressure, stepPressure))
        diffTemp = maxTemp - minTemp
        if diffTemp > 0:
            stepTemp = int(self.scaleSize / diffTemp)
        self.DEBUG('\t\t minTemp=%s, maxTemp=%s, diffTemp=%s, stepTemp%s' % (minTemp, maxTemp, diffTemp, stepTemp))
        
        myDataCount = len(myData)
        if myDataCount > 0:
            i = 0
            while i < (myDataCount - 1):
                record = myData[i].split('|')
                #self.DEBUG('\t record="%s"' % (record))
                pressure = self.getPressure(record)
                temp = self.getTemperature(record)
                currtemp = self.getCurrTemperature(record)
                windspeed = self.getWind(record)
                windDirectionIcon = self.getWindIcon(record)

                dayANDhour = str(record[1])
                index = self.mapDict.get(dayANDhour, -1)
                self.DEBUG('\t dayANDhour="%s", index=%s, pressure="%s", temp="%s"' % (dayANDhour, index, pressure,temp))
                if index > -1:
                    #self.DEBUG('\t\t name%s="%s"' % (index, pressure))
                    self['Icon%s' % index].instance.setScale(1)
                    self['Icon%s' % index].instance.setPixmapFromFile(self.getIcon(record))
                    self['Icon%s' % index].show()
                    if pressure is not None:
                        self['name%s' % index].text = str(pressure)
                        barX = self['bar%s' % index].instance.position().x()
                        self.DEBUG('\t\t barX=%s, self.PressureBarPosY=%s, newY=%s' % (barX, self.PressureBarPosY, int(self.PressureBarPosY - (int(pressure) - minPressure) * stepPressure)))
                        self['bar%s' % index].instance.move(ePoint(int(barX), int(self.PressureBarPosY - (int(pressure) - minPressure) * stepPressure)))
                        self['bar%s' % index].instance.setPixmap(self.barBlue)
                        self['bar%s' % index].show()
                    if temp is not None and currtemp is not None:
                        self['tempName%s' % index].text = '%s%s%s|%s%s' % (clr['R'], str(currtemp), clr['Y'], clr['B'], str(temp))
                        barX = self['tempBar%s' % index].instance.position().x()
                        self.DEBUG('\t\t tempBar=%s, self.TempBarPosY=%s, newY=%s' % (barX, self.TempBarPosY, int(self.TempBarPosY - (int(temp) - minTemp) * stepTemp)))
                        self['tempBar%s' % index].instance.move(ePoint(int(barX), int(self.TempBarPosY - (int(temp) - minTemp) * stepTemp)))
                        self['tempBar%s' % index].instance.setPixmap(self.barBlue)
                        self['tempBar%s' % index].show()
                        barX = self['curTempBar%s' % index].instance.position().x()
                        self.DEBUG('\t\t curTempBar=%s, self.TempBarPosY=%s, newY=%s' % (barX, self.TempBarPosY, int(self.TempBarPosY - (int(currtemp) - minTemp) * stepTemp)))
                        self['curTempBar%s' % index].instance.move(ePoint(int(barX), int(self.TempBarPosY - (int(currtemp) - minTemp) * stepTemp)))
                        self['curTempBar%s' % index].instance.setPixmap(self.barRed)
                        self['curTempBar%s' % index].show()
                    if windspeed is not None:
                        self['windspeed%s' % index].text = '%skm/h' % str(windspeed)
                    if windDirectionIcon is not None:
                        self['windIcon%s' % index].instance.setPixmap(windDirectionIcon)
                        self['windIcon%s' % index].show()
                i += 1

    def keyOk(self):
        self.close()

    def cancel(self):
        self.close()
