# -*- coding: utf-8 -*-
# ===============================================================================
# coded by j00zek
# Based on the:
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
from requests import get
from xml.etree.cElementTree import fromstring
from six.moves.urllib.parse import quote

from enigma import eEPGCache
from boxbranding import getImageDistro

from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.config import getConfigListEntry, config
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.TimerList import TimerList
from Plugins.Plugin import PluginDescriptor
from RecordTimer import AFTEREVENT
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.TimerEntry import TimerEntry
from Screens.ChoiceBox import ChoiceBox
from ServiceReference import ServiceReference
from Tools.BoundFunction import boundFunction

# ------------------------------------------------------------------------------------------

class RemoteService:
    def __init__(self, sref, sname):
        self.sref = sref
        self.sname = sname

    def getServiceName(self): return self.sname


class StreamlinkRecorderScreen(Screen):
    skin = """
                <screen position="center,center" size="585,410" title="StreamlinkRecorder" >
                        <widget name="text" position="0,10" zPosition="1" size="585,20" font="Regular;20" halign="center" valign="center" />
                        <widget name="timerlist" position="5,40" size="560,275" scrollbarMode="showOnDemand" />
                        <ePixmap name="key_red" position="5,365" zPosition="4" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
                        <widget name="key_red" position="5,365" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
                        <ePixmap name="key_green" position="150,365" zPosition="4" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
                        <widget name="key_green" position="150,365" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
                        <ePixmap name="key_yellow" position="295,365" zPosition="4" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />
                        <widget name="key_yellow" position="295,365" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
                        <ePixmap name="key_blue" position="440,365" zPosition="4" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />
                        <widget name="key_blue" position="440,365" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
                </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)

        self.setTitle(_("Streamlink Recorder"))

        self["actions"] = ActionMap(["SetupActions", "ColorActions"],
                                    {
            "green": self.settings,
            "blue": self.clean,
            "yellow": self.delete,
            "cancel": self.close,
        }, -1)

        self["timerlist"] = TimerList([])
        self["key_green"] = Button(_("Settings"))
        self["key_blue"] = Button(_("Cleanup"))
        self["key_yellow"] = Button(_("Delete"))
        self["key_red"] = Button(_("Cancel"))
        self["text"] = Label("")

        self.onLayoutFinish.append(self.getInfo)

    def getInfo(self, *args):
        info = _("not configured yet. please do so in the settings.")
        self["text"].setText(info)

    def clean(self):
        pass

    def delete(self):
        sel = self["timerlist"].getCurrent()
        if not sel:
            return
        self.session.openWithCallback(
            self.deleteTimerConfirmed,
            MessageBox,
            _("Do you really want to delete the timer \n%s ?") % sel.name
        )

    def deleteTimerConfirmed(self, val):
        pass

    def settings(self):
        pass

    def generateTimerE2(self, data):
        try:
            root = fromstring(data)
        except Exception as e:
            print("[RemoteTimer] error: %s", e)
            self["text"].setText(_("error parsing incoming data."))
        else:
            return [
                (
                    E2Timer(
                        sref=str(timer.findtext("e2servicereference", '')),
                        sname=str(timer.findtext("e2servicename", 'n/a')),
                        name=str(timer.findtext("e2name", '')),
                        disabled=int(timer.findtext("e2disabled", 0)),
                        failed=int(timer.findtext("e2failed", 0)),
                        timebegin=int(timer.findtext("e2timebegin", 0)),
                        timeend=int(timer.findtext("e2timeend", 0)),
                        duration=int(timer.findtext("e2duration", 0)),
                        startprepare=int(timer.findtext("e2startprepare", 0)),
                        state=int(timer.findtext("e2state", 0)),
                        repeated=int(timer.findtext("e2repeated", 0)),
                        justplay=int(timer.findtext("e2justplay", 0)),
                        eventId=int(timer.findtext("e2eit", -1)),
                        afterevent=int(timer.findtext("e2afterevent", 0)),
                        dirname=str(timer.findtext("e2dirname", '')),
                        description=str(timer.findtext("e2description", ''))
                    ),
                    False
                )
                for timer in root.findall("e2timer")
            ]


class E2Timer:
    def __init__(self, sref="", sname="", name="", disabled=0, failed=0,
                 timebegin=0, timeend=0, duration=0, startprepare=0,
                 state=0, repeated=0, justplay=0, eventId=0, afterevent=0,
                 dirname="", description="", isAutoTimer=0, ice_timer_id=None):
        self.service_ref = RemoteService(sref, sname)
        self.name = name
        self.disabled = disabled
        self.failed = failed
        self.begin = timebegin
        self.end = timeend
        self.duration = duration
        self.startprepare = startprepare
        self.state = state
        self.repeated = repeated
        self.justplay = justplay
        self.eventId = eventId
        self.afterevent = afterevent
        self.dirname = dirname
        self.description = description
        self.isAutoTimer = isAutoTimer
        self.ice_timer_id = ice_timer_id


baseTimerEntrySetup = None
baseTimerEntryGo = None


def timerInit(): #initiated during e2 start
    global baseTimerEntrySetup, baseTimerEntryGo
    if baseTimerEntrySetup is None:
        baseTimerEntrySetup = TimerEntry.createSetup
    if baseTimerEntryGo is None:
        baseTimerEntryGo = TimerEntry.keyGo
    TimerEntry.createSetup = createNewnigma2Setup
    TimerEntry.keyGo = newnigma2KeyGo


def createNewnigma2Setup(self, widget="config"):
    # print("[RemoteTimer] createNewnigma2Setup widget: %s" % widget)
    try:
        baseTimerEntrySetup(self, widget)
    except TypeError:  # for distros that do not use the "widget" argument in Setup.createSetup
        # print("[RemoteTimer] createNewnigma2Setup no widget")
        baseTimerEntrySetup(self)
    self.timerentry_remote = False
    self.list.insert(0, getConfigListEntry(_("Remote Timer"), self.timerentry_remote))

    # force re-reading the list
    self[widget].list = self.list


def newnigma2SubserviceSelected(self, service):
    print("[RemoteTimer] newnigma2SubserviceSelected entered service: %s" % service)
    if service is not None:
        # ouch, this hurts a little
        service_ref = self.timerentry_service_ref
        self.timerentry_service_ref = ServiceReference(service[1])
        eit = self.timer.eit
        self.timer.eit = None
        newnigma2KeyGo(self)
        self.timerentry_service_ref = service_ref
        self.timer.eit = eit


def newnigma2KeyGo(self):
    print("[RemoteTimer] newnigma2KeyGo entered self.timerentry_remote.value: %s" % self.timerentry_remote.value)
    if not self.timerentry_remote.value:
        baseTimerEntryGo(self)
    else:
        service_ref = self.timerentry_service_ref
        if self.timer.eit is not None:
            event = eEPGCache.getInstance().lookupEventId(service_ref.ref, self.timer.eit)
            if event:
                n = event.getNumOfLinkageServices()
                if n > 1:
                    tlist = []
                    ref = self.session.nav.getCurrentlyPlayingServiceReference()
                    parent = service_ref.ref
                    selection = 0
                    for x in range(n):
                        i = event.getLinkageService(parent, x)
                        if i.toString() == ref.toString():
                            selection = x
                        tlist.append((i.getName(), i))
                    self.session.openWithCallback(boundFunction(newnigma2SubserviceSelected, self), ChoiceBox, title=_("Please select a subservice to record..."), list=tlist, selection=selection)
                    return
                elif n > 0:
                    parent = service_ref.ref
                    service_ref = ServiceReference(event.getLinkageService(parent, 0))

        # unify the service ref
        service_ref = str(service_ref)
        clean_ref = ""
        colon_counter = 0

        for char in service_ref:
            if char == ':':
                colon_counter += 1
            if colon_counter < 10:
                clean_ref += char

        service_ref = clean_ref

        # XXX: this will - without any hassle - ignore the value of repeated
        begin, end = self.getBeginEnd()

        # when a timer end is set before the start, add 1 day
        if end < begin:
            end += 86400

        rt_name = quote(self.timerentry_name.value.encode('utf8', 'ignore'))
        rt_description = quote(self.timerentry_description.value.encode('utf8', 'ignore'))
        rt_disabled = 0  # XXX: do we really want to hardcode this? why do we offer this option then?
        rt_repeated = 0  # XXX: same here

        rt_dirname = "None"

        if self.timerentry_justplay.value == "zap":
            rt_justplay = 1
        else:
            rt_justplay = 0

        # XXX: this one is tricky since we do not know if the remote box offers afterEventAuto so lets just keep it simple for now
        rt_afterEvent = {
            "deepstandby": AFTEREVENT.DEEPSTANDBY,
            "standby": AFTEREVENT.STANDBY,
        }.get(self.timerentry_afterevent.value, AFTEREVENT.NONE)

        # Add Timer on RemoteBox via WebIf Command
        # http://192.168.178.20/web/timeradd?sRef=&begin=&end=&name=&description=&disabled=&justplay=&afterevent=&repeated=
        remoteurl = "http://127.0.0.1:80/web/timeradd?sRef=%s&begin=%s&end=%s&name=%s&description=%s&disabled=%s&justplay=%s&afterevent=%s&repeated=%s&dirname=%s" % (
            service_ref,
            begin,
            end,
            rt_name,
            rt_description,
            rt_disabled,
            rt_justplay,
            rt_afterEvent,
            rt_repeated,
            rt_dirname
        )
