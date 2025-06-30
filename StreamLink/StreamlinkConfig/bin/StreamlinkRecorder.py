# -*- coding: utf-8 -*-
# ===============================================================================
# coded by j00zek
# Based on the:https://github.com/opendreambox/enigma2-plugin-partnerbox/blob/master/src/PartnerboxRemoteInstantRecord.py
# ===============================================================================
# Remote Timer Setup by Homey
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2, or (at your option) any later
# version.
#
# Copyright (C) 2009 by nixkoenner@newnigma2.to
# http://newnigma2.to
#
# Copyright (C) 2020 by Mr.Servo, jbleyel
#
# License: GPL
#
# $Id$
# ===============================================================================

from __future__ import print_function
from . import mygettext as _ , DBGlog

from Components.ActionMap import ActionMap
from Components.config import getConfigListEntry, config
from Components.Label import Label
from Components.Pixmap import Pixmap

from enigma import eEPGCache

from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen

from ServiceReference import ServiceReference

import io, os, time, traceback #traceback.format_exc()

try:
    import json
except Exception:
    import simplejson as json

DBG = True

def doInstantRecord():
    DBGlog("doInstantRecord() >>>")
    
class StreamlinkRecorderScreen(Screen):
    skin = """
                <screen position="center,center" size="585,410" title="StreamlinkRecorder" >
                        <widget name="InfoLine" position="0,10" zPosition="1" size="585,20" font="Regular;20" halign="center" valign="center" />
                        <widget name="timersList" position="5,40" size="560,275" scrollbarMode="showOnDemand" />
                        <ePixmap position="5,365" zPosition="4" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
                        <widget name="key_red" position="5,365" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
                        <ePixmap position="150,365" zPosition="4" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
                        <widget name="key_green" position="150,365" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
                        <ePixmap position="295,365" zPosition="4" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />
                        <widget name="key_yellow" position="295,365" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
                        <ePixmap position="440,365" zPosition="4" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />
                        <widget name="key_blue" position="440,365" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
                </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        DBGlog("StreamlinkRecorderScreen.__init__() >>>")
        self.setTitle(_("Streamlink Recorder"))
        DBGlog("StreamlinkRecorderScreen.__init__2() >>>")
        self["actions"] = ActionMap(["StreamlinkRecorderScreen"],
                                    {
                                        "green": self.AddTimer,
                                        "blue": self.cleanTimers,
                                        "yellow": self.DeleteTimer,
                                        "red": self.InstantRecord,
                                        "cancel": self.exit,
                                        "ok": self.keyOK,
                                    }, -2)
        DBGlog("StreamlinkRecorderScreen.__init__3() >>>")
        self["InfoLine"] = Label("")
        self["timersList"] = Label('')
        self["key_green"] = Label(_("Add"))
        self["key_blue"] = Label(_("Clean past timers"))
        self["key_yellow"] = Label(_("Delete timer"))
        self["key_red"] = Label(_("Instant Record"))
        
        self.RecordingsDict = {}
        self.RecordingsJsonPath = '/etc/enigma2/StreamlinkRecordings.json'

        self.onLayoutFinish.append(self.LayoutFinished)

    def LayoutFinished(self, *args):
        DBGlog("StreamlinkRecorderScreen.LayoutFinished() >>>")
        if not os.path.exists(self.RecordingsJsonPath):
            self["InfoLine"].setText(_('No Streamlink timers found'))
        else:
            self.RecordingsDict = self.readJson()
            self["InfoLine"].setText(_('No Streamlink timers defined'))
        
    def AddTimer(self):
        DBGlog("StreamlinkRecorderScreen.AddTimer() >>>")

    def cleanTimers(self):
        DBGlog("StreamlinkRecorderScreen.cleanTimers() >>>")

    def DeleteTimer(self):
        DBGlog("StreamlinkRecorderScreen.DeleteTimer() >>>")
        def deleteTimerConfirmed(val):
            pass
        #sel = self["timerlist"].getCurrent()
        #if not sel:
        #    return
        #self.session.openWithCallback( deleteTimerConfirmed, MessageBox, _("Do you really want to delete the timer \n%s ?") % sel.name)
        pass

    def exit(self):
        DBGlog("StreamlinkRecorderScreen.exit() >>>")
        if len(self.RecordingsDict) != 0:
            self.saveJsonDict()
        elif os.path.exists(self.RecordingsJsonPath):
            os.remove(self.RecordingsJsonPath)
        self.close(None)

    def keyOK(self):
        DBGlog("StreamlinkRecorderScreen.keyOK() >>>")

    def readJson(self):
        retDict = {}
        if os.path.exists(self.RecordingsJsonPath):
            with open(self.RecordingsJsonPath, 'r') as (json_file):
                data = json_file.read()
                json_file.close()
            try:
                retDict = json.loads(data)
            except Exception:
                os.remove(self.RecordingsJsonPath)
        #remove old records
        keysToDelete = []
        for key in retDict:
            if int(key) <= int(time.time()):
                if int(key) + int(retDict[key]['RecEventDuration']) <= int(time.time()):
                    keysToDelete.append(key)
        for key in keysToDelete:
            del retDict[key]
        return retDict

    def saveJsonDict(self, doSort=False):
        myKeys = list(self.RecordingsDict.keys())
        try:
            myKeys.sort()
        except Exception:
            DBGlog("Exception sorting '%s': %s" % (str(myKeys), str(traceback.format_exc())))

        try:
            with io.open(self.RecordingsJsonPath, 'w', encoding='utf8') as (outfile):
                json_data = json.dumps(self.RecordingsDict, indent=4, sort_keys=doSort, ensure_ascii=False)
                outfile.write(str(json_data))
        except Exception:
            DBGlog("Exception writing json file '%s': %s" % (str(myKeys), str(traceback.format_exc())))

    def doNothing(self, ret = False):
        DBGlog('StreamlinkRecorderScreen.doNothing >>>')
        
    def getEventInfo(self, whatInfo):
        if whatInfo == 'RecEventStartTime':     return self.RecCurrentEventData[1]
        elif whatInfo == 'RecEventDuration':    return self.RecCurrentEventData[2]
        elif whatInfo == 'RecCurrentTime':      return self.RecCurrentEventData[3]
        elif whatInfo == 'RecEventName':        return self.RecCurrentEventData[4]
        elif whatInfo == 'RecEventDescr':       return self.RecCurrentEventData[6]
        elif whatInfo == 'RecChannelReference': return self.RecCurrentEventData[7]
        elif whatInfo == 'RecChannelName':      return self.RecCurrentEventData[8]
    
    def doRecord(self, ret = False):
        DBGlog('StreamlinkRecorderScreen.doRecord(ret=%s) >>>' % str(ret))
        self.RecordingsDict = self.readJson()
        if ret and len(self.RecCurrentEventData) >= 8:
            if self.getEventInfo('RecEventStartTime') <= int(time.time()):
                DBGlog("\t Instant recording:")
                DBGlog("\t\t Program: %s" % self.getEventInfo('RecEventName'))
                DBGlog("\t\t duration: %s s" % (self.getEventInfo('RecEventDuration') - (self.getEventInfo('RecCurrentTime') - self.getEventInfo('RecEventStartTime'))))
                DBGlog("\t\t from: %s" % self.getEventInfo('RecChannelName'))
                DBGlog("\t\t Description: %s" % self.getEventInfo('RecEventDescr'))
            else:
                DBGlog("\t Scheduled recording:")
        self.RecordingsDict[str(self.getEventInfo('RecEventStartTime'))] = {'RecEventDuration': self.getEventInfo('RecEventDuration'),
                                                                       'RecEventName': self.getEventInfo('RecEventName'),
                                                                       'RecChannelReference': self.getEventInfo('RecChannelReference'),
                                                                       'RecChannelName': self.getEventInfo('RecChannelName'),
                                                                       'RecEventDescr': self.getEventInfo('RecEventDescr'),
                                                                      }
        self.saveJsonDict()

    def InstantRecord(self):
        DBGlog("StreamlinkRecorderScreen.InstantRecord() >>>")
        length = 120 * 60 #to have in seconds
        ChannelRef = self.session.nav.getCurrentlyPlayingServiceReference().toString()
        if 'http%3a//127.0.0.1' not in ChannelRef:
            self.session.openWithCallback(self.doNothing,MessageBox, _("This is NOT Streamlink service!"), MessageBox.TYPE_ERROR, timeout = 5)
            DBGlog("\t ChannelRef='%s' is not Streamlink service, end." % str(ChannelRef))
            return
        else:
            try:
                self.RecCurrentEventData = eEPGCache.getInstance().lookupEvent(['IBDCTSERNX', (ChannelRef, 0, -1)])[0]
                DBGlog("=========== currentEventData ==============\n%s" % str(self.RecCurrentEventData))
            except Exception:
                DBGlog(str(traceback.format_exc()))
            self.session.openWithCallback(self.doRecord,MessageBox, _("Do you want to record\n '%s'\n from %s?") % (self.getEventInfo('RecEventName'), 
                                                                                                                    self.getEventInfo('RecChannelName')
                                                                                                                    ), MessageBox.TYPE_YESNO, timeout = 15)
