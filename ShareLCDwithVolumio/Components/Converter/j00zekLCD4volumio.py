# -*- coding: utf-8 -*-
#######################################################################
#
#    Converter for Enigma2
#    Coded by j00zek (c)2021
#
#    Uszanuj moja prace i nie kasuj/zmieniaj informacji kto jest autorem konwertera
#    Please respect my work and don't delete/change name of the converter author
#
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version 2
#    of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#     
#######################################################################

from enigma import eTimer
from Components.config import config
from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.j00zekVolumioState import getJSON
from Components.Language import language
from datetime import datetime, timedelta
from time import localtime
import os

### DBG 
DBG = True
DebugFile = '/tmp/j00zekVolumioState.log'
if os.path.exists(DebugFile): os.remove(DebugFile)
def printDBG(myText = None):
    if not DBG: return
    if myText is None: return
    else:
        myText = str(myText)
        try:
            f = open(DebugFile, 'a')
            f.write('%s\t%s\n' % (str(datetime.now()),myText))
            f.close()
            if os.path.getsize(DebugFile) > 100000:
                os.system('sed -i -e 1,10d %s' % DebugFile)
        except Exception, e:
            os.system('echo "Exception:%s" >> %s' %( str(e), DebugFile )) 

try:
    from Plugins.Extensions.DynamicLCDbrightnessInStandby.plugin import setKODIbrightness as setLCDbrightness, calculateLCDbrightness
except Exception as e:
    if DBG: printDBG('Exception loading delayedStandbyActions as setLCDbrightness: %s' % str(e))
    def setLCDbrightness(stateTXT = ''):
        if DBG: printDBG('Fake setLCDbrightness(%s)' % str(stateTXT))
        
class j00zekLCD4volumio(Converter, object):
    UNKNOWN = 0
    CURRENTTIME = 1
    STATE = 2
    TITLE = 3
    DURATION = 4
    PROGRESS = 5
    STATEICON = 6
    PLAYEDTIME = 7
    LEFTTIME = 8
    LEFTMINS = 9
    ALBUMPIC = 10
    reqList = ['UNKNOWN','CURRENTTIME','STATE','TITLE','DURATION','PROGRESS','STATEICON',
               'PLAYEDTIME','LEFTTIME','LEFTMINS','LEFTMINS', 'ALBUMPIC']
    
    def __init__(self, arg):
        Converter.__init__(self, arg)
        if DBG: printDBG('__init__ >>>')
        self.checkingState = False
        self.isSuspended = False
        self.argZero = None
        args = arg.split(',')
        self.hideWhenNotplaying = "hideWhenNotplaying" in args 
        self.hideWhenPlaying = "hideWhenPlaying" in args 
        self.showWhenPlaying = "showWhenPlaying" in args 
        self.DoRefreshDict = "DoRefreshDict" in args
        self.getAlbumArt = "getAlbumArt" in args
        
        self.emptyText = None
        if 'NoneAsNA' in args:
            self.emptyText = ''
        elif 'NoneAsNA' in args:
            self.emptyText = _('N/A')

        if 'state' in args: self.requested = self.STATE
        elif 'title' in args: self.requested = self.TITLE
        elif 'duration' in args: self.requested = self.DURATION
        elif 'progress' in args: self.requested = self.PROGRESS
        elif 'stateicon' in args: self.requested = self.STATEICON
        elif 'playedtime' in args: self.requested = self.PLAYEDTIME
        elif 'lefttime' in args: self.requested = self.LEFTTIME
        elif 'leftmins' in args: self.requested = self.LEFTMINS
        elif 'currentTime' in args: self.requested = self.CURRENTTIME
        else:
            self.requested = self.UNKNOWN
            self.argZero = args[0]
        
        self.StatesDict = {}
        self.JSON = getJSON()
        self.timer_interval = 1000
        self.timer = eTimer()
        self.timer.callback.append(self.timerEvent)
        if DBG and self.DoRefreshDict: printDBG('\t DoRefreshDict enabled')
        
    def timerEvent(self):
        #if DBG: printDBG('timerEvent() >>>')
        self.timer.stop()
        if not self.isSuspended and not self.checkingState:
            if self.DoRefreshDict:
                IP = '%s.%s.%s.%s' % (config.plugins.ShareLCDwithVolumio.IP.value[0],
                                      config.plugins.ShareLCDwithVolumio.IP.value[1],
                                      config.plugins.ShareLCDwithVolumio.IP.value[2],
                                      config.plugins.ShareLCDwithVolumio.IP.value[3]
                                     )
                self.JSON.refreshState(IP,
                                       config.plugins.ShareLCDwithVolumio.PORT.value,
                                       config.plugins.ShareLCDwithVolumio.getAlbumArt.value)
            self.StatesDict = self.JSON.getState()
            #if DBG: printDBG("timerEvent() >>>  self.StatesDict=%s" % str(self.StatesDict))
            self.timer.start(self.timer_interval, True)
            self.changed([9898,])
            
    def doSuspend(self, suspended): 
        #if DBG: printDBG('doSuspend(%s) >>> ' % suspended)
        if suspended == 1: 
            self.timer.stop()
            self.isSuspended = True
        else: 
            self.timer.start(self.timer_interval, True)
            self.isSuspended = False

    def changed(self, what):
        if what[0] == 9898:
            #if DBG: printDBG("changed() what[0] == 9898")
            if self.hideWhenNotplaying and len(self.downstream_elements):
                if self.StatesDict.get('status', 'unknown') == 'play':
                    self.downstream_elements[0].visible = True
                else:
                    self.downstream_elements[0].visible = False
            #LCDbrightness
            
            if self.StatesDict.get('status', 'off') == 'play': stateTxT = 'isPlaying'
            else: stateTxT = 'powerOff'
            setLCDbrightness(stateTxT)
            #if DBG: printDBG("changed() setLCDbrightness='%s'" % stateTxT)
            self.downstream_elements.changed(what) 

    def getKeyValue(self, keyName):
        pass
    
    def isPlaying(self):
        if  self.StatesDict.get('status', '') == 'play' or \
            self.StatesDict.get(u'status', '') == 'play'or \
            self.StatesDict.get(u'status', '') == u'play':
            return True
        else:
            return False

    def cutZeroHours(self, text):
        texts = text.split(',')
        if len(texts) > 2:
            if texts[0] == '0' or texts[0] == '00':
                texts[0] = ''
            text = ':'.join(texts)
    @cached
    def getBoolean(self):
        if self.isPlaying:
            retBool = True
        else:
            retBool = False
        if self.requested == self.hideWhenPlaying:
            retBool = not retBool
        if DBG: printDBG("getBoolean() self.requested=%s, retBool='%s'" % (self.requested, retBool))
        return retBool

    boolean = property(getBoolean)
    
    @cached
    def getValue(self):
        val = 0
        if not self.isPlaying:
            val = 0
        elif self.requested == self.PROGRESS:
            total = self.StatesDict.get('duration',0)
            if total != 0:
              played = self.StatesDict.get('seek',0) /1000
              val = ( float(played) / total ) * 100
        if DBG: printDBG("getValue() self.requested=%s, val='%s'" % (self.requested, val))
        return int(val)

    value = property(getValue)
    range = 100 

    @cached
    def getText(self):
        if DBG: printDBG("getText() >>> self.requested=%s(%s)" % (self.reqList[self.requested], self.requested,))
        retTXT = ''
        try:
            PLAYSTATUS = self.StatesDict.get(u'status','off')
            if DBG: printDBG("\t PLAYSTATUS=%s" % PLAYSTATUS)
            if self.requested == self.STATEICON:
                if PLAYSTATUS == 'stop': retTXT = 'stop.png'
                elif PLAYSTATUS == 'pause': retTXT = 'pause.png'
                elif PLAYSTATUS == 'play': retTXT = 'play.png'
                elif PLAYSTATUS == 'ERROR': retTXT = 'error.png'
                else: retTXT = 'off.png'
            elif PLAYSTATUS == 'off' and isNOTexception:
                retTXT = ''
            elif PLAYSTATUS != 'play' and self.hideWhenNotplaying:
                retTXT = ''
            elif PLAYSTATUS == 'play' and self.hideWhenPlaying:
                retTXT = ''
            elif self.requested == self.TITLE:  
                retTXT = self.StatesDict.get('title', '')
            elif self.requested == self.DURATION:
                p = self.StatesDict['duration']
                retTXT = str(timedelta(seconds=p))
            elif self.requested == self.PLAYEDTIME:
                p = int(self.StatesDict['seek'] /1000)
                retTXT = str(timedelta(seconds=p))
            elif self.requested == self.LEFTTIME:
                if self.StatesDict['duration'] > 0:
                    p = int(self.StatesDict['duration'] - (self.StatesDict['seek'] /1000))
                    retTXT = str(timedelta(seconds=p))
            elif self.requested == self.LEFTMINS:
                if self.StatesDict['duration'] > 0:
                    p = int(self.StatesDict['duration'] - (self.StatesDict['seek'] /1000))
                    retTXT = '+%s min' % int(p/60)
            #elif self.requested == self.ALBUMPIC:
            #    retTXT = self.StatesDict['albumpic']
            elif self.requested == self.CURRENTTIME:
                time = self.source.time
                if not time is None:
                    t = localtime(time)
                    retTXT = "%2d:%02d" % (t.tm_hour, t.tm_min)
            elif not self.argZero is None:
                retTXT = self.StatesDict.get(self.argZero, '')
                if retTXT is None:
                    retTXT = ''
            else:
                retTXT = ''
            
        except Exception as e:
            if DBG: printDBG("getText() Exception='%s'" % str(e))
            retTXT = 'ERR'
        if DBG: printDBG("getText() self.requested=%s(%s), retTXT='%s'" % (self.reqList[self.requested], self.requested, str(retTXT).strip()))
        
        return str(retTXT).strip()

    text = property(getText)
