# -*- coding: utf-8 -*-
#
# BlackHarmonyEventList - Converter
#
# Coded by Dr.Best (c) 2013
# Support: www.dreambox-tools.info
# E-Mail: dr.best@dreambox-tools.info
#
# This plugin is open source but it is NOT free software.
#
# This plugin may only be distributed to and executed on hardware which
# is licensed by Dream Multimedia GmbH.
# In other words:
# It's NOT allowed to distribute any parts of this plugin or its source code in ANY way
# to hardware which is NOT licensed by Dream Multimedia GmbH.
# It's NOT allowed to execute this plugin and its source code or even parts of it in ANY way
# on hardware which is NOT licensed by Dream Multimedia GmbH.
#
# If you want to use or modify the code or parts of it,
# you have to keep MY license and inform me about the modifications by mail.
#
# j00zek: this file has changed name just to avoid errors using opkg (situation when file was installed by different pockage)
#


from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.Converter.Converter import Converter

from Components.Element import cached

from enigma import eEPGCache, eServiceReference
from time import localtime, strftime, mktime, time
from datetime import datetime, timedelta

class j00zekModEventList(Converter, object):
    def __init__(self, type):
        Converter.__init__(self, type)
        self.epgcache = eEPGCache.getInstance()
        self.primetime = 0
        self.eventCount = 0
        self.eventNo = 0
        self.retTime = True
        self.retName = True
        self.retDuration = True
        self.retFormat = ''
        self.firstEventColor = ''
        
        if (len(type)):
            args = type.split(',')
            for arg in args:
                if '=' in arg:
                    type_c, value = arg.split('=')
                else:
                    type_c = arg
                    value = ''
                if type_c == "eventcount":
                    self.eventCount = int(value)
                    self.eventNo = 0
                elif type_c == "primetime" and value == "yes":
                    self.primetime = 1
                elif type_c == "eventNo":
                    self.eventNo = int(value)
                    self.eventCount = self.eventNo
                elif type_c == "noTime":
                    self.retTime = False
                elif type_c == "NoName":
                    self.retName = False
                elif type_c == "NoDuration":
                    self.retDuration = False
                elif type_c == "firstEventColor":
                    self.firstEventColor = value

    @cached
    def getContent(self):
        contentList = []
        ref = self.source.service
        info = ref and self.source.info
        if info is None:
            return []
        curEvent = self.source.getCurrentEvent()
        if curEvent:
            if not self.epgcache.startTimeQuery(eServiceReference(ref.toString()), curEvent.getBeginTime() + curEvent.getDuration()):
                i = 1
                while i <= (self.eventCount):
                    event = self.epgcache.getNextTimeEntry()
                    if self.eventNo == 0 or i == self.eventNo:
                        if event is not None:
                            contentList.append(self.getEventTuple(event),)
                    i +=1
                if self.primetime == 1:
                    now = localtime(time())
                    dt = datetime(now.tm_year, now.tm_mon, now.tm_mday, 20, 15)
                    if time() > mktime(dt.timetuple()):
                        dt += timedelta(days=1) # skip to next day...
                    primeTime = int(mktime(dt.timetuple()))
                    if not self.epgcache.startTimeQuery(eServiceReference(ref.toString()), primeTime):
                        event = self.epgcache.getNextTimeEntry()
                        if event and (event.getBeginTime() <= int(mktime(dt.timetuple()))):
                            contentList.append(self.getEventTuple(event),)
        return contentList

    def getEventTuple(self,event):
        time = ''
        title = ''
        duration = ''
        if self.retTime:
            time = "%s" % (strftime("%H:%M", localtime(event.getBeginTime())))
        if self.retName:
            title = event.getEventName()
        if self.retDuration:
            duration = "%d min" % int(event.getDuration() / 60)
        #print('j00zekModEventList.getEventTuple',time,title,duration)
        return (time,title,duration)

    def changed(self, what):
        if what[0] != self.CHANGED_SPECIFIC:
            Converter.changed(self, what)

    @cached
    def getText(self):
        contentList = self.getContent()
        for item in contentList:
            if self.retFormat == '':
                if self.retTime:
                    if self.retDuration and self.retName:
                        return '%s (%s) - %s\n' % (item[0], item[2], item[1])
                    elif self.retDuration and not self.retName:
                        return '%s (%s)' % (item[0], item[2])
                    elif not self.retDuration and self.retName:
                        return '%s - %s\n' % (item[0], item[1])
                    else:
                        return item[0]
                elif self.retDuration:
                    if self.retName:
                        return '%s (%s)' % (item[1], item[2])
                    else:
                        return item[2]
                elif self.retName:
                    return item[1]
                else:
                    return ''

    text = property(getText)
