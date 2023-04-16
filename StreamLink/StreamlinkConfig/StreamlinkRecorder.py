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

import io, os, traceback #traceback.format_exc()

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
        
        if DBG and len(self.RecordingsDict) == 0:
            self.RecordingsDict[1672531200] = {'lenInMin': 120, 'chName':'channel Name', 'info':'info', 'descr':'description'}

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
        return retDict

    def saveJsonDict(self, doSort=True):
        myKeys = list(self.RecordingsDict.keys())
        myKeys.sort()
        
        with io.open(self.RecordingsJsonPath, 'w', encoding='utf8') as (outfile):
            json_data = json.dumps(self.RecordingsDict, indent=4, sort_keys=True, ensure_ascii=False)
            outfile.write(str(json_data))

    def doNothing(self, ret = False):
        DBGlog('StreamlinkRecorderScreen.doNothing >>>')
        return
        
    def InstantRecord(self):
        DBGlog("StreamlinkRecorderScreen.InstantRecord() >>>")
        length = 120 * 60 #to have in seconds
        ChannelName = self.session.nav.getCurrentlyPlayingServiceReference().toString()
        if 'http%3a//127.0.0.1' not in ChannelName:
            self.session.openWithCallback(self.doNothing,MessageBox, _("This is NOT Streamlink service!"), MessageBox.TYPE_INFO, timeout = 5)
            DBGlog("\t ChannelName='%s' is not Streamlink service, end." % str(ChannelName))
            return
        else:
            EventName =  ''
            EventDescr = ''
            DBGlog("\t ChannelName='%s'" % str(ChannelName))
