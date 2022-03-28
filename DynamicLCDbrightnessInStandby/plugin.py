# -*- coding: iso-8859-2 -*-

from . import mygettext as _
#no idea why importing scripts in the same directory doesn't work in ATV6.5
from Plugins.Extensions.DynamicLCDbrightnessInStandby.version import Version

from enigma import eTimer, eDBoxLCD
from Components.ActionMap import ActionMap
from Components.config import config, ConfigSubsection, ConfigEnableDisable, ConfigSlider, ConfigSelection, ConfigNothing, getConfigListEntry, NoSave, ConfigText
from Components.ConfigList import ConfigListScreen
from Components.Sources.StaticText import StaticText
from datetime import datetime
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.Setup import SetupSummary
from Tools import Notifications

import Screens.Standby
import time

config.plugins.dynamicLCD = ConfigSubsection()
if eDBoxLCD.getInstance().detected():
    config.plugins.dynamicLCD.enabled = ConfigEnableDisable(default = False)
    config.plugins.dynamicLCD.debug = ConfigEnableDisable(default = False)
    config.plugins.dynamicLCD.ConfigNothing = ConfigNothing()
    config.plugins.dynamicLCD.KODIsupport = ConfigSelection(default = "no",choices = [("no", _("No")),
                                                                            #("powerOn", _("LCD brighter when KODI is running")),
                                                                            #("isNOTidle", _("LCD brighter when KODI is running and not spleeping")),
                                                                            ("playingOn", _("LCD brighter when KODI is playing")),
                                                                            ])
    config.plugins.dynamicLCD.KODIstate = NoSave(ConfigText(default = ""))
    
    val = int(config.lcd.standby.value * 255 / 10)
    if val > 255:
        val = 255
    config.plugins.dynamicLCD.NightStandbyBrightness = ConfigSlider(default= val, limits=(0, 255))
    config.plugins.dynamicLCD.NightStandbyBrightness23 = ConfigSlider(default=config.lcd.standby.value, limits=(0, 255))
    config.plugins.dynamicLCD.NightStandbyBrightness00 = ConfigSlider(default=config.lcd.standby.value, limits=(0, 255))
    config.plugins.dynamicLCD.NightStandbyBrightness01 = ConfigSlider(default=config.lcd.standby.value, limits=(0, 255))
    config.plugins.dynamicLCD.NightStandbyBrightness02 = ConfigSlider(default=config.lcd.standby.value, limits=(0, 255))
    config.plugins.dynamicLCD.NightStandbyBrightness03 = ConfigSlider(default=config.lcd.standby.value, limits=(0, 255))

    config.plugins.dynamicLCD.SunRise30minsBefore = ConfigSlider(default=config.lcd.standby.value, limits=(0, 255))
    config.plugins.dynamicLCD.SunRise30minsAfter = ConfigSlider(default=config.lcd.standby.value, limits=(0, 255))

    config.plugins.dynamicLCD.NightStandbyBrightness04 = ConfigSlider(default=config.lcd.standby.value, limits=(0, 255))
    config.plugins.dynamicLCD.NightStandbyBrightness05 = ConfigSlider(default=config.lcd.standby.value, limits=(0, 255))
    config.plugins.dynamicLCD.NightStandbyBrightness06 = ConfigSlider(default=config.lcd.standby.value, limits=(0, 255))
    config.plugins.dynamicLCD.NightStandbyBrightness07 = ConfigSlider(default=config.lcd.standby.value, limits=(0, 255))
    
    config.plugins.dynamicLCD.NightStandbyBrightness08 = ConfigSlider(default=config.plugins.dynamicLCD.NightStandbyBrightness.value, limits=(0, 255))
    config.plugins.dynamicLCD.NightStandbyBrightness09 = ConfigSlider(default=config.plugins.dynamicLCD.NightStandbyBrightness.value, limits=(0, 255))
    config.plugins.dynamicLCD.NightStandbyBrightness10 = ConfigSlider(default=config.plugins.dynamicLCD.NightStandbyBrightness.value, limits=(0, 255))
    config.plugins.dynamicLCD.NightStandbyBrightness11 = ConfigSlider(default=config.plugins.dynamicLCD.NightStandbyBrightness.value, limits=(0, 255))
    config.plugins.dynamicLCD.NightStandbyBrightness12 = ConfigSlider(default=config.plugins.dynamicLCD.NightStandbyBrightness.value, limits=(0, 255))
    config.plugins.dynamicLCD.NightStandbyBrightness13 = ConfigSlider(default=config.plugins.dynamicLCD.NightStandbyBrightness.value, limits=(0, 255))
    config.plugins.dynamicLCD.NightStandbyBrightness14 = ConfigSlider(default=config.plugins.dynamicLCD.NightStandbyBrightness.value, limits=(0, 255))
    config.plugins.dynamicLCD.NightStandbyBrightness15 = ConfigSlider(default=config.plugins.dynamicLCD.NightStandbyBrightness.value, limits=(0, 255))
    config.plugins.dynamicLCD.NightStandbyBrightness16 = ConfigSlider(default=config.plugins.dynamicLCD.NightStandbyBrightness.value, limits=(0, 255))
    config.plugins.dynamicLCD.NightStandbyBrightness17 = ConfigSlider(default=config.plugins.dynamicLCD.NightStandbyBrightness.value, limits=(0, 255))
    config.plugins.dynamicLCD.NightStandbyBrightness18 = ConfigSlider(default=config.plugins.dynamicLCD.NightStandbyBrightness.value, limits=(0, 255))
    config.plugins.dynamicLCD.NightStandbyBrightness19 = ConfigSlider(default=config.plugins.dynamicLCD.NightStandbyBrightness.value, limits=(0, 255))
    config.plugins.dynamicLCD.NightStandbyBrightness20 = ConfigSlider(default=config.plugins.dynamicLCD.NightStandbyBrightness.value, limits=(0, 255))
    config.plugins.dynamicLCD.NightStandbyBrightness21 = ConfigSlider(default=config.plugins.dynamicLCD.NightStandbyBrightness.value, limits=(0, 255))
    config.plugins.dynamicLCD.NightStandbyBrightness22 = ConfigSlider(default=config.plugins.dynamicLCD.NightStandbyBrightness.value, limits=(0, 255))
else:
    config.plugins.dynamicLCD.enabled = NoSave(ConfigSelection(default = "0",choices = [("0", _("no LCD"))]))

#DEBUG
if config.plugins.dynamicLCD.debug.value:
    DBG=True
    def printDEBUG(myText, append2file=True):
        try:
            if append2file == False:
                f = open('/tmp/dynamicLCDbrightness.log', 'w')
            else:
                f = open('/tmp/dynamicLCDbrightness.log', 'a')
            f.write('%s %s\n' %(str(datetime.now()), myText))
            f.close
        except: pass
else:
    DBG=False

if DBG: printDEBUG("Loaded", False)
try:
    from Components.j00zekSunCalculations import Sun, geo
    sunRiseAvailable = True
    SunPeriodsNames = {
        "sunrise-30": "from 30mins before sunrise time",
        "30-sunrise": "from sunrise time to 30 mins after",
        "8-sunrise":  "from sunrise time till 8:00",
        "sunrise-30,30-sunrise": "from 30mins before to 30 mins after sunrise",
        "sunrise-30,8-sunrise": "from 30mins before sunrise till 8:00"
    }
    config.plugins.dynamicLCD.useSunRiseTime = ConfigSelection(default = "no",choices = [("no", _("No")),("sunrise-30", _(SunPeriodsNames['sunrise-30'])),
                                                                                                          ("30-sunrise", _(SunPeriodsNames['30-sunrise'])),
                                                                                                          ("8-sunrise", _(SunPeriodsNames['8-sunrise'])),
                                                                                                          ("sunrise-30,30-sunrise", _(SunPeriodsNames['sunrise-30,30-sunrise'])),
                                                                                                          ("sunrise-30,8-sunrise", _(SunPeriodsNames['sunrise-30,8-sunrise']))
                                                                                                          ])

except Exception as e:
    sunRiseAvailable = False
    config.plugins.dynamicLCD.useSunRiseTime = ConfigSelection(default = "no",choices = [("no", _("Disabled - no required components found!!!"))])
    if DBG: printDEBUG('Exception importing j00zekSunCalculations: %s' % str(e))

def leaveStandby():
    if DBG: printDEBUG('leaveStandby, stop timer')
    config.plugins.dynamicLCD.KODIstate.value = ''
    global MyTimer
    MyTimer.stop()

def standbyCounterChanged(configElement):
    if DBG: printDEBUG('standbyCounterChanged')
    config.plugins.dynamicLCD.KODIstate.value = ''
    global MyTimer
    try:
        if leaveStandby not in Screens.Standby.inStandby.onClose:
            Screens.Standby.inStandby.onClose.append(leaveStandby)
            MyTimer.start(1000,True)
    except Exception as e:
        if DBG: printDEBUG('standbyCounterChanged %s' % str(e))

def main(session, **kwargs):
    if DBG: printDEBUG("Open Config Screen")
    session.open(DynamicLCDbrightnessInStandbyConfiguration)


def calculateLCDbrightness(DBGtext = ''):
    #tutaj logika ktore wlaczyc
    currTime = time.localtime()
    hour = int(currTime[3])
    Minutes = int(currTime[4])
    hourAndMinutes = time.strftime('%H:%M', currTime)
    MinutesSinceMidnight = hour * 60 + Minutes
    
    if hour == 0:    val = config.plugins.dynamicLCD.NightStandbyBrightness00.value
    elif hour == 1:  val = config.plugins.dynamicLCD.NightStandbyBrightness01.value
    elif hour == 2:  val = config.plugins.dynamicLCD.NightStandbyBrightness02.value
    elif hour == 3:  val = config.plugins.dynamicLCD.NightStandbyBrightness03.value
    elif hour == 4:  val = config.plugins.dynamicLCD.NightStandbyBrightness04.value
    elif hour == 5:  val = config.plugins.dynamicLCD.NightStandbyBrightness05.value
    elif hour == 6:  val = config.plugins.dynamicLCD.NightStandbyBrightness06.value
    elif hour == 7:  val = config.plugins.dynamicLCD.NightStandbyBrightness07.value
    elif hour == 8:  val = config.plugins.dynamicLCD.NightStandbyBrightness08.value
    elif hour == 9:  val = config.plugins.dynamicLCD.NightStandbyBrightness09.value
    elif hour == 10: val = config.plugins.dynamicLCD.NightStandbyBrightness10.value
    elif hour == 11: val = config.plugins.dynamicLCD.NightStandbyBrightness11.value
    elif hour == 12: val = config.plugins.dynamicLCD.NightStandbyBrightness12.value
    elif hour == 13: val = config.plugins.dynamicLCD.NightStandbyBrightness13.value
    elif hour == 14: val = config.plugins.dynamicLCD.NightStandbyBrightness14.value
    elif hour == 15: val = config.plugins.dynamicLCD.NightStandbyBrightness15.value
    elif hour == 16: val = config.plugins.dynamicLCD.NightStandbyBrightness16.value
    elif hour == 17: val = config.plugins.dynamicLCD.NightStandbyBrightness17.value
    elif hour == 18: val = config.plugins.dynamicLCD.NightStandbyBrightness18.value
    elif hour == 19: val = config.plugins.dynamicLCD.NightStandbyBrightness19.value
    elif hour == 20: val = config.plugins.dynamicLCD.NightStandbyBrightness20.value
    elif hour == 21: val = config.plugins.dynamicLCD.NightStandbyBrightness21.value
    elif hour == 22: val = config.plugins.dynamicLCD.NightStandbyBrightness22.value
    elif hour == 23: val = config.plugins.dynamicLCD.NightStandbyBrightness23.value
    else: val = config.plugins.dynamicLCD.NightStandbyBrightness.value
    timerWaitingTime = (60 - Minutes)
    if sunRiseAvailable and config.plugins.dynamicLCD.useSunRiseTime.value != 'no' and hour < 8:
        try:
            latitude = geo().getLatitude()
            longitude = geo().getLongitude()
            sunriseTime = Sun().getSunriseTime(longitude, latitude)['TZtime'].split(':')
            sunriseMinutesSinceMidnight = (int(sunriseTime[0]) * 60 + int(sunriseTime[0]))
            MinutesToSunrise = MinutesSinceMidnight - sunriseMinutesSinceMidnight
            DBGtext += "\t\t\t\t MinutesToSunrise='%s', configured='%s'\n" % (str(MinutesToSunrise),SunPeriodsNames[config.plugins.dynamicLCD.useSunRiseTime.value])
            if MinutesToSunrise < 0:
                if config.plugins.dynamicLCD.useSunRiseTime.value.startswith('sunrise-30'):
                    if (abs(MinutesToSunrise) - 30) < timerWaitingTime and (abs(MinutesToSunrise) - 30) > 0:
                        timerWaitingTime = abs(MinutesToSunrise) - 30
                        DBGtext += "\t\t\t\t timerWaitingTime correction 1 to catch 30 minutes catch sunrise time\n"
                    elif MinutesToSunrise >= -60 and MinutesToSunrise < -30:
                        timerWaitingTime = abs(MinutesToSunrise) - 30
                        DBGtext += "\t\t\t\t timerWaitingTime correction 2 to catch 30 minutes catch sunrise time\n"
                    elif MinutesToSunrise >= -30 and MinutesToSunrise < 0:
                        val = config.plugins.dynamicLCD.SunRise30minsBefore.value
                        timerWaitingTime = abs(MinutesToSunrise)
                        DBGtext += "\t\t\t\t val=SunRise30minsBefore.value='%s'\n" % str(val)
            elif MinutesToSunrise >= 0:
                if config.plugins.dynamicLCD.useSunRiseTime.value.endswith('30-sunrise'):
                    if MinutesToSunrise >= 0 and MinutesToSunrise < 30:
                        val = config.plugins.dynamicLCD.SunRise30minsAfter.value
                        timerWaitingTime = 30 - MinutesToSunrise
                        if timerWaitingTime <= 0: timerWaitingTime = 1
                        DBGtext += "\t\t\t\t val=SunRise30minsAfter.value='%s'\n" % str(val)
                elif config.plugins.dynamicLCD.useSunRiseTime.value.endswith('8-sunrise'):
                    if MinutesToSunrise >= 0:
                        val = config.plugins.dynamicLCD.SunRise30minsAfter.value
                        if (8 - hour) > 1:
                            timerWaitingTime += (8 - hour) * 60
                        DBGtext += "\t\t\t\t val=SunRiseTill8=SunRise30minsAfter.value='%s'\n" % str(val)
        except Exception as e:
            DBGtext += "\t\t\t\t Exception getting MinutesToSunrise: %s" % str(e)
    DBGtext += "\t\t\t\t at %s sets LCD brightness to %s and waits %s minutes for next invoke\n" % (hourAndMinutes, val,timerWaitingTime)
    return DBGtext, val, timerWaitingTime

def delayedStandbyActions():
    global MyTimer
    MyTimer.stop()
    if eDBoxLCD.getInstance().detected():
        DBGtext, val, timerWaitingTime = calculateLCDbrightness()
        if config.plugins.dynamicLCD.KODIstate.value == 'isPlaying' and config.plugins.dynamicLCD.KODIsupport.value != 'no':
            DBGtext = 'delayedStandbyActions() >>>\n KODI is playing, LCD controlled through setKODIbrightness function, next wakeup in %smin' % timerWaitingTime
        else:
            DBGtext = 'delayedStandbyActions() >>>\n' + DBGtext
            try:
                eDBoxLCD.getInstance().setLCDBrightness(int(val))
            except Exception as e:
                DBGtext += "\t\t\t\t Exception: %s\n" % str(e)

        timestamp = int("%s%s%s" % (datetime.now().year,datetime.now().month,datetime.now().day))
        if timestamp < 20191204:
            DBGtext += 'system time seems to be not set yet. Next refresh after 10 seconds'
            timerWaitingTime = 10 * 1000
        else:
            timerWaitingTime = timerWaitingTime * 60 * 1000
          
        if DBG: printDEBUG(DBGtext.strip())
        MyTimer.start(timerWaitingTime, True)
        

def setKODIbrightness( stateTXT = '' ):
    def setLCD(val):
        myDBGtext = '\t\t\t\t setLCD(%s)' % val
        try:
            eDBoxLCD.getInstance().setLCDBrightness(int(val))
        except Exception as e:
            myDBGtext += "\t\t\t\t Exception: %s\n" % str(e)
        return myDBGtext
    
    if config.plugins.dynamicLCD.enabled.value and stateTXT != config.plugins.dynamicLCD.KODIstate.value and config.plugins.dynamicLCD.KODIsupport.value != 'no':
        DBGtext = "setKODIbrightness('%s') >>>\n" % str(stateTXT)
        config.plugins.dynamicLCD.KODIstate.value = stateTXT
        if eDBoxLCD.getInstance().detected():
            if MyTimer.isActive():
                if stateTXT == 'isPlaying' and config.plugins.dynamicLCD.KODIsupport.value in ('playingOn'):
                    try:
                        val = int(config.lcd.standby.value) * 255 / 10
                        if val > 255: val = 255
                        DBGtext = DBGtext + setLCD(val)
                    except Exception as e:
                        DBGtext += "\t\t\t\t E2 in standby and KODI is playing, Exception setting normal LCD brightness: %s\n" % str(e)
                else:
                    DBGtext += "\t\t\t\t E2 in standby and KODI is NOT playing, setting standby LCD brightness\n"
                    tmpTtext, val, timerWaitingTime = calculateLCDbrightness()
                    DBGtext += tmpTtext
                    DBGtext = DBGtext + setLCD(val)
            else:
                DBGtext += "\t\t\t\t E2 in operation, nothing to do"
        else:
            DBGtext += "\t\t\t\t eDBoxLCD instance NOT detected :("
        if DBG: printDEBUG(DBGtext.strip())

MyTimer = eTimer()
MyTimer.callback.append(delayedStandbyActions)

# sessionstart
def sessionstart(reason, session = None):
    if DBG: printDEBUG("autostart")
    from Screens.Standby import inStandby
    if reason == 0 and eDBoxLCD.getInstance().detected() and config.plugins.dynamicLCD.enabled.value:
        if DBG: printDEBUG('reason == 0 and dynamicLCD.enabled')
        config.misc.standbyCounter.addNotifier(standbyCounterChanged, initial_call=False)
        #MyTimer.start(10000,True)

def Plugins(path, **kwargs):
    return [PluginDescriptor(name=_("Dynamic LCD brightness"), where = PluginDescriptor.WHERE_PLUGINMENU, fnc = main, needsRestart = False),
            PluginDescriptor(name="DynamicLCDbrightness", where = PluginDescriptor.WHERE_SESSIONSTART, fnc = sessionstart, needsRestart = False, weight = -1)]

class DynamicLCDbrightnessInStandbyConfiguration(Screen, ConfigListScreen):
    skin = """
    <screen name="DynamicLCDbrightnessInStandbyConfiguration" position="center,center" size="640,500" title="DynamicLCDbrightnessInStandby Config" backgroundColor="#20606060" >

            <widget name="config" position="10,10" size="620,450" zPosition="1" transparent="0" scrollbarMode="showOnDemand" />
            <widget name="key_red" position="0,465" zPosition="2" size="200,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="red" />
            <widget name="key_green" position="220,465" zPosition="2" size="200,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="green" />
            <widget name="key_blue" position="440,465" zPosition="2" size="200,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="#202673ec" />

    </screen>"""
    def __init__(self, session):
        Screen.__init__(self, session)
        #self.skinName = [ "Setup", ]

        # Summary
        self.setup_title = _("DynamicLCDbrightness v %s Configuration") % Version
        self.onChangedEntry = []

        # Buttons
        self["key_red"] = StaticText(_("Cancel"))
        self["key_green"] = StaticText(_("OK"))

        # Define Actions
        self["actions"] = ActionMap(["SetupActions"],
            {
                "cancel": self.keyCancel,
                "save": self.keySave,
            }
        )

        ConfigList = self.buildConfigList()
        
        ConfigListScreen.__init__(self, ConfigList, session = session, on_change = self.changedValue)

        if not self.selectionChanged in self["config"].onSelectionChanged:
            self["config"].onSelectionChanged.append(self.selectionChanged)
        self.onLayoutFinish.append(self.__layoutFinished)
        self.onClose.append(self.__onClose)

    def buildConfigList(self):
        ConfigList = [getConfigListEntry(_("Control LCD brightness in Standby:"), config.plugins.dynamicLCD.enabled)]
        if eDBoxLCD.getInstance().detected():
            if config.plugins.dynamicLCD.enabled.value:
                ConfigList.append(getConfigListEntry(_("Night hours..."), config.plugins.dynamicLCD.ConfigNothing))
                ConfigList.append(getConfigListEntry(_("from %s (%s)") % ('23:00',config.plugins.dynamicLCD.NightStandbyBrightness23.value), config.plugins.dynamicLCD.NightStandbyBrightness23))
                ConfigList.append(getConfigListEntry(_("from %s (%s)") % ('00:00',config.plugins.dynamicLCD.NightStandbyBrightness00.value), config.plugins.dynamicLCD.NightStandbyBrightness00))
                ConfigList.append(getConfigListEntry(_("from %s (%s)") % ('01:00',config.plugins.dynamicLCD.NightStandbyBrightness01.value), config.plugins.dynamicLCD.NightStandbyBrightness01))
                ConfigList.append(getConfigListEntry(_("from %s (%s)") % ('02:00',config.plugins.dynamicLCD.NightStandbyBrightness02.value), config.plugins.dynamicLCD.NightStandbyBrightness02))
                ConfigList.append(getConfigListEntry(_("from %s (%s)") % ('03:00',config.plugins.dynamicLCD.NightStandbyBrightness03.value), config.plugins.dynamicLCD.NightStandbyBrightness03))
                ConfigList.append(getConfigListEntry(_("from %s (%s)") % ('04:00',config.plugins.dynamicLCD.NightStandbyBrightness04.value), config.plugins.dynamicLCD.NightStandbyBrightness04))
                ConfigList.append(getConfigListEntry(_("from %s (%s)") % ('05:00',config.plugins.dynamicLCD.NightStandbyBrightness05.value), config.plugins.dynamicLCD.NightStandbyBrightness05))
                ConfigList.append(getConfigListEntry(_("from %s (%s)") % ('06:00',config.plugins.dynamicLCD.NightStandbyBrightness06.value), config.plugins.dynamicLCD.NightStandbyBrightness06))
                ConfigList.append(getConfigListEntry(_("from %s (%s)") % ('07:00',config.plugins.dynamicLCD.NightStandbyBrightness07.value), config.plugins.dynamicLCD.NightStandbyBrightness07))
                ConfigList.append(getConfigListEntry(_("Sunrise time..."), config.plugins.dynamicLCD.ConfigNothing))
                ConfigList.append(getConfigListEntry(_("Use sunrise time"), config.plugins.dynamicLCD.useSunRiseTime))
                if sunRiseAvailable:
                    if config.plugins.dynamicLCD.useSunRiseTime.value.startswith('sunrise-30'):
                        ConfigList.append(getConfigListEntry(_("from %s (%s)") % ('-30m',config.plugins.dynamicLCD.SunRise30minsBefore.value), config.plugins.dynamicLCD.SunRise30minsBefore))
                    if config.plugins.dynamicLCD.useSunRiseTime.value.endswith('30-sunrise'):
                        ConfigList.append(getConfigListEntry(_("to %s (%s)") % ('+30m',config.plugins.dynamicLCD.SunRise30minsAfter.value), config.plugins.dynamicLCD.SunRise30minsAfter))
                    elif config.plugins.dynamicLCD.useSunRiseTime.value.endswith('8-sunrise'):
                        ConfigList.append(getConfigListEntry(_("to %s (%s)") % ('8:00',config.plugins.dynamicLCD.SunRise30minsAfter.value), config.plugins.dynamicLCD.SunRise30minsAfter))
                ConfigList.append(getConfigListEntry(_("Day hours..."), config.plugins.dynamicLCD.ConfigNothing))
                ConfigList.append(getConfigListEntry(_("08:00-23:00 (%s)") % config.plugins.dynamicLCD.NightStandbyBrightness.value, config.plugins.dynamicLCD.NightStandbyBrightness))
                ConfigList.append(getConfigListEntry(_("from %s (%s)") % ('08:00',config.plugins.dynamicLCD.NightStandbyBrightness08.value), config.plugins.dynamicLCD.NightStandbyBrightness08))
                ConfigList.append(getConfigListEntry(_("from %s (%s)") % ('09:00',config.plugins.dynamicLCD.NightStandbyBrightness09.value), config.plugins.dynamicLCD.NightStandbyBrightness09))
                ConfigList.append(getConfigListEntry(_("from %s (%s)") % ('10:00',config.plugins.dynamicLCD.NightStandbyBrightness10.value), config.plugins.dynamicLCD.NightStandbyBrightness10))
                ConfigList.append(getConfigListEntry(_("from %s (%s)") % ('11:00',config.plugins.dynamicLCD.NightStandbyBrightness11.value), config.plugins.dynamicLCD.NightStandbyBrightness11))
                ConfigList.append(getConfigListEntry(_("from %s (%s)") % ('12:00',config.plugins.dynamicLCD.NightStandbyBrightness12.value), config.plugins.dynamicLCD.NightStandbyBrightness12))
                ConfigList.append(getConfigListEntry(_("from %s (%s)") % ('13:00',config.plugins.dynamicLCD.NightStandbyBrightness13.value), config.plugins.dynamicLCD.NightStandbyBrightness13))
                ConfigList.append(getConfigListEntry(_("from %s (%s)") % ('14:00',config.plugins.dynamicLCD.NightStandbyBrightness14.value), config.plugins.dynamicLCD.NightStandbyBrightness14))
                ConfigList.append(getConfigListEntry(_("from %s (%s)") % ('15:00',config.plugins.dynamicLCD.NightStandbyBrightness15.value), config.plugins.dynamicLCD.NightStandbyBrightness15))
                ConfigList.append(getConfigListEntry(_("from %s (%s)") % ('16:00',config.plugins.dynamicLCD.NightStandbyBrightness16.value), config.plugins.dynamicLCD.NightStandbyBrightness16))
                ConfigList.append(getConfigListEntry(_("from %s (%s)") % ('17:00',config.plugins.dynamicLCD.NightStandbyBrightness17.value), config.plugins.dynamicLCD.NightStandbyBrightness17))
                ConfigList.append(getConfigListEntry(_("from %s (%s)") % ('18:00',config.plugins.dynamicLCD.NightStandbyBrightness18.value), config.plugins.dynamicLCD.NightStandbyBrightness18))
                ConfigList.append(getConfigListEntry(_("from %s (%s)") % ('19:00',config.plugins.dynamicLCD.NightStandbyBrightness19.value), config.plugins.dynamicLCD.NightStandbyBrightness19))
                ConfigList.append(getConfigListEntry(_("from %s (%s)") % ('20:00',config.plugins.dynamicLCD.NightStandbyBrightness20.value), config.plugins.dynamicLCD.NightStandbyBrightness20))
                ConfigList.append(getConfigListEntry(_("from %s (%s)") % ('21:00',config.plugins.dynamicLCD.NightStandbyBrightness21.value), config.plugins.dynamicLCD.NightStandbyBrightness21))
                ConfigList.append(getConfigListEntry(_("from %s (%s)") % ('22:00',config.plugins.dynamicLCD.NightStandbyBrightness22.value), config.plugins.dynamicLCD.NightStandbyBrightness22))
                
                ConfigList.append(getConfigListEntry(_("Other settings..."), config.plugins.dynamicLCD.ConfigNothing))
                ConfigList.append(getConfigListEntry(_("Support 'Share LCD with KODI' plugin:"), config.plugins.dynamicLCD.KODIsupport))
                ConfigList.append(getConfigListEntry(_("Log to file"), config.plugins.dynamicLCD.debug))
        return ConfigList
        
    def __layoutFinished(self):
        self.setTitle(self.setup_title)
        try:
            self["title"]=StaticText(self.setup_title)
        except Exception:
            pass

    def __onClose(self):
        try:
            val = int(config.lcd.bright.value * 255 / 10)
            if val > 255:
                val = 255
            eDBoxLCD.getInstance().setLCDBrightness(val)
        except Exception:
            pass
    
    def setLCDBrightness(self):
        if self.getCurrentEntryConfig() != config.plugins.dynamicLCD.enabled and \
                self.getCurrentEntryConfig() != config.plugins.dynamicLCD.debug and \
                self.getCurrentEntryConfig() != config.plugins.dynamicLCD.ConfigNothing and \
                self.getCurrentEntryConfig() != config.plugins.dynamicLCD.KODIsupport and \
                self.getCurrentEntryConfig() != config.plugins.dynamicLCD.useSunRiseTime:
            try:
                currValue = self.getCurrentValue()
                currValue = int(currValue.split('/')[0].strip())
                eDBoxLCD.getInstance().setLCDBrightness(currValue)
            except Exception as e:
                if DBG: printDEBUG("Exception: %s" % str(e), True)
            if DBG: printDEBUG("%s > %s" % (self.getCurrentEntry(), currValue), True)
    
    def selectionChanged(self):
        self.setLCDBrightness()

    def changedValue(self):
        for x in self.onChangedEntry:
            x()
        self.setLCDBrightness()
        if self.getCurrentEntryConfig() == config.plugins.dynamicLCD.NightStandbyBrightness:
            config.plugins.dynamicLCD.NightStandbyBrightness08.value = config.plugins.dynamicLCD.NightStandbyBrightness.value
            config.plugins.dynamicLCD.NightStandbyBrightness09.value = config.plugins.dynamicLCD.NightStandbyBrightness.value
            config.plugins.dynamicLCD.NightStandbyBrightness10.value = config.plugins.dynamicLCD.NightStandbyBrightness.value
            config.plugins.dynamicLCD.NightStandbyBrightness11.value = config.plugins.dynamicLCD.NightStandbyBrightness.value
            config.plugins.dynamicLCD.NightStandbyBrightness12.value = config.plugins.dynamicLCD.NightStandbyBrightness.value
            config.plugins.dynamicLCD.NightStandbyBrightness13.value = config.plugins.dynamicLCD.NightStandbyBrightness.value
            config.plugins.dynamicLCD.NightStandbyBrightness14.value = config.plugins.dynamicLCD.NightStandbyBrightness.value
            config.plugins.dynamicLCD.NightStandbyBrightness15.value = config.plugins.dynamicLCD.NightStandbyBrightness.value
            config.plugins.dynamicLCD.NightStandbyBrightness16.value = config.plugins.dynamicLCD.NightStandbyBrightness.value
            config.plugins.dynamicLCD.NightStandbyBrightness17.value = config.plugins.dynamicLCD.NightStandbyBrightness.value
            config.plugins.dynamicLCD.NightStandbyBrightness18.value = config.plugins.dynamicLCD.NightStandbyBrightness.value
            config.plugins.dynamicLCD.NightStandbyBrightness19.value = config.plugins.dynamicLCD.NightStandbyBrightness.value
            config.plugins.dynamicLCD.NightStandbyBrightness20.value = config.plugins.dynamicLCD.NightStandbyBrightness.value
            config.plugins.dynamicLCD.NightStandbyBrightness21.value = config.plugins.dynamicLCD.NightStandbyBrightness.value
            config.plugins.dynamicLCD.NightStandbyBrightness22.value = config.plugins.dynamicLCD.NightStandbyBrightness.value
        self["config"].list = self.buildConfigList()

    def getCurrentEntry(self):
        return self["config"].getCurrent()[0]

    def getCurrentEntryConfig(self):
        return self["config"].getCurrent()[1]

    def getCurrentValue(self):
        return str(self["config"].getCurrent()[1].getText())

    def createSummary(self):
        return dynamicLCDsummary

##################################################################### LCD Screen <<<<<<<<<<<<<<<<<<<<<<<<<<<<<
class dynamicLCDsummary(Screen):
    def __init__(self, session, parent):
        Screen.__init__(self, session)
        self.skinName = [ "StandbySummary", ]
##################################################################### CLASS ENDS <<<<<<<<<<<<<<<<<<<<<<<<<<<<<         
