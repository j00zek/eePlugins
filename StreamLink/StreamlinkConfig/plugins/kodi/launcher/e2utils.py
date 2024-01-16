# -*- coding: UTF-8 -*-
from __future__ import print_function
import base64
import os
from twisted.web.client import downloadPage

from Components.AVSwitch import AVSwitch
from Components.ActionMap import HelpableActionMap
from Components.GUIComponent import GUIComponent
from Components.Label import Label
from Components.ServiceEventTracker import ServiceEventTracker
from Components.Sources.StaticText import StaticText
from Screens.AudioSelection import AudioSelection
from Screens.ChoiceBox import ChoiceBox
from Screens.Screen import Screen
import six

from skin import parseColor
from enigma import iPlayableService, ePicLoad, ePixmap, eTimer, getDesktop


def toString(text):
    if text is None:
        return None
    if isinstance(text, six.string_types):
        if isinstance(text, six.text_type):
            return text.encode('utf-8')
        return text
    return str(text)

def getAspect():
    val = AVSwitch().getAspectRatioSetting()
    if val == 0 or val == 1:
        r = (5 * 576, 4 * 720)
    elif val == 2 or val == 3 or val == 6:
        r = (16 * 720, 9 * 1280)
    elif val == 4 or val == 5:
        r = (16 * 576, 10 * 720)
    return r

def getPlayPositionPts(session):
    service = session.nav.getCurrentService()
    seek = service and service.seek()
    position = seek and seek.getPlayPosition()
    position = position and not position[0] and position[1] or None
    return position

def getPlayPositionInSeconds(session):
    position = getPlayPositionPts(session)
    if position is not None:
        position = position / 90000
    return position

def getDurationPts(session):
    service = session.nav.getCurrentService()
    seek = service and service.seek()
    duration = seek and seek.getLength()
    duration = duration and not duration[0] and duration[1] or None
    return duration

def getDurationInSeconds(session):
    duration = getDurationPts(session)
    if duration is not None:
        duration = duration / 90000
    return duration

def seekToPts(session, pts):
    service = session.nav.getCurrentService()
    seek = service and service.seek()
    if seek and seek.isCurrentlySeekable():
        return seek.seekTo(pts)

class WebPixmap(GUIComponent):
    GUI_WIDGET = ePixmap

    def __init__(self, default=None, cachedir='/tmp/', caching=True):
        GUIComponent.__init__(self)
        self.caching = caching
        self.cachedir = cachedir
        self.default = default
        self.currentUrl = None
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.setPixmapCB)

    def applySkin(self, desktop, parent):
        attribs = [ ]
        if self.skinAttributes is not None:
            for (attrib, value) in self.skinAttributes:
                if attrib == "default":
                    self.default = value
                else:
                    attribs.append((attrib, value))

        self.skinAttributes = attribs
        res = GUIComponent.applySkin(self, desktop, parent)
        return res

    def onShow(self):
        sc = getAspect()
        resize = False
        background = "#00000000"
        self.picload.setPara((self.instance.size().width(), self.instance.size().height(), sc[0], sc[1], False, resize, background))
        if self.currentUrl is None:
            self.load(self.default)

    def loadFromFile(self, filePath):
        self.__currentUrl = filePath
        self.picload.startDecode(six.ensure_str(filePath))

    def loadFromUrl(self, url, destPath):
        def loadSuccess(callback=None):
            self.__currentUrl = destPath
            self.picload.startDecode(destPath)

        def loadFailed(failure):
            failure.printException()
            if self.instance:
                self.load(self.default)

        agent = "Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.0.2) Gecko/2008091620 Firefox/3.0.2"
        d = downloadPage(url, destPath, agent=agent)
        d.addCallback(loadSuccess)
        d.addErrback(loadFailed)

    def load(self, url):
        url = toString(url)
        if self.caching:
            self.currentUrl = None
        if url == self.currentUrl:
            print('[WebPixmap] load - already loaded')
            return
        if os.path.isfile(url):
            self.loadFromFile(url)
        elif url.startswith(b"http"):
            tmpPath = os.path.join(self.cachedir, base64.b64encode(url).decode())
            if self.caching:
                if os.path.isfile(tmpPath):
                    self.loadFromFile(tmpPath)
                    return
            self.loadFromUrl(url, tmpPath)
        else:
            print('[WebPixmap] load - file not found or unsupported url: "%s"' % (str(url)))

    def setPixmapCB(self, picInfo=None):
        ptr = self.picload.getData()
        if ptr and self.instance:
            self.currentUrl = self.__currentUrl
            del self.__currentUrl
            self.instance.setPixmap(ptr.__deref__())


class BufferIndicatorDetailed(Screen):
    def __init__(self, session, updateIntervalInMs=500):
        desktopWidth = getDesktop(0).size().width()
        offset = 20
        screenWidth = desktopWidth - (2 * offset)
        widgetWidth = screenWidth / 3 - 5
        self.skin = """
            <screen position="%d,0" size="%d,60" zPosition="2" backgroundColor="transparent" flags="wfNoBorder">
                <widget source="bufferSize" render="Label" position="0,0" size="%d,70" valign="center" halign="left" font="Regular;22" transparent="1" foregroundColor="#ffffff" shadowColor="#40101010" shadowOffset="2,2" />
                <widget source="bufferLevel" render="Label" position="%d,0" size="%d,70" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="#ffffff" shadowColor="#40101010" shadowOffset="2,2" />
                <widget source="avgInRate" render="Label" position="%d,0" size="%d,70" valign="center" halign="right" font="Regular;22" transparent="1" foregroundColor="#ffffff" shadowColor="#40101010" shadowOffset="2,2" />
            </screen>""" % (offset, screenWidth, widgetWidth, widgetWidth + 5, widgetWidth, 2 * widgetWidth + 10, widgetWidth)
        Screen.__init__(self, session)
        self["avgInRate"] = StaticText()
        self["bufferSize"] = StaticText()
        self["bufferLevel"] = StaticText()
        self.updateIntervalInMs = updateIntervalInMs
        self.updateTimer = eTimer()
        self.updateTimer.callback.append(self.updateStatus)
        self.__event_tracker = ServiceEventTracker(screen=self, eventmap=
            {
                iPlayableService.evBuffering: self.__evBuffering,
                iPlayableService.evStart: self.__evStart,
                iPlayableService.evStopped: self.__evStopped,
            })
        self.onClose.append(self.updateTimer.stop)

    def __evBuffering(self):
        pass

    def __evStopped(self):
        self.updateTimer.stop()

    def __evStart(self):
        self.updateTimer.start(self.updateIntervalInMs)

    def updateStatus(self):
        if self.shown:
            service = self.session.nav.getCurrentService()
            iStreamed = service and service.streamed()
            if iStreamed:
                bufferInfo = iStreamed.getBufferCharge()
                bufferLevel, bufferSize, avgInRate = bufferInfo[0], bufferInfo[4], bufferInfo[1]
                self["bufferLevel"].text = "%s: %d%%" % (_("Buffering"), bufferLevel)
                if bufferSize > 0:
                    self["bufferSize"].text = "%s: (%.2fMB / %.2fMB)" % (_("Buffer Size"), bufferSize * bufferLevel / float(100 * 1024 * 1024), bufferSize / float(1024 * 1024))
                else:
                    self["bufferSize"].text = "N/A"
                if avgInRate / 1024 > 1024:
                    self["avgInRate"].text = "%s: %.2fMB" % (_("Average Input rate"), avgInRate / float(1024 * 1024))
                else:
                    self["avgInRate"].text = "%s: %dKB" % (_("Average Input rate"), avgInRate / 1024)


class InfoBarBuffer(object):
    def __init__(self):
        self.bufferScreen = self.session.instantiateDialog(BufferIndicatorDetailed)
        self.bufferScreen.hide()
        self.onClose.append(self.bufferScreen.hide)
        self.onClose.append(self.bufferScreen.doClose)

class InfoBarAspectChange(object):
    """
    Simple aspect ratio changer
    """
    V_DICT = {
        '16_9_letterbox':{'aspect':'16:9', 'policy2':'letterbox', 'title':'16:9 ' + _("Letterbox")},
        '16_9_panscan':{'aspect':'16:9', 'policy2':'panscan', 'title':'16:9 ' + _("Pan&scan")},
        '16_9_nonlinear':{'aspect':'16:9', 'policy2':'panscan', 'title':'16:9 ' + _("Nonlinear")},
        '16_9_bestfit':{'aspect':'16:9', 'policy2':'bestfit', 'title':'16:9 ' + _("Just scale")},
        '16_9_4_3_pillarbox':{'aspect':'16:9', 'policy':'pillarbox', 'title':'4:3 ' + _("PillarBox")},
        '16_9_4_3_panscan':{'aspect':'16:9', 'policy':'panscan', 'title':'4:3 ' + _("Pan&scan")},
        '16_9_4_3_nonlinear':{'aspect':'16:9', 'policy':'nonlinear', 'title':'4:3 ' + _("Nonlinear")},
        '16_9_4_3_bestfit':{'aspect':'16:9', 'policy':'bestfit', 'title':_("Just scale")},
        '4_3_letterbox':{'aspect':'4:3', 'policy':'letterbox', 'policy2':'policy', 'title':_("Letterbox")},
        '4_3_panscan':{'aspect':'4:3', 'policy':'panscan', 'policy2':'policy', 'title':_("Pan&scan")},
        '4_3_bestfit':{'aspect':'4:3', 'policy':'bestfit', 'policy2':'policy', 'title':_("Just scale")}
    }

    V_MODES = ['16_9_letterbox', '16_9_panscan', '16_9_nonlinear', '16_9_bestfit',
        '16_9_4_3_pillarbox', '16_9_4_3_panscan', '16_9_4_3_nonlinear', '16_9_4_3_bestfit',
        '4_3_letterbox', '4_3_panscan', '4_3_bestfit'
    ]


    def __init__(self):
        self.postAspectChange = []
        self.aspectChanged = False
        try:
            self.defaultAspect = open("/proc/stb/video/aspect", "r").read().strip()
        except IOError:
            self.defaultAspect = None
        try:
            self.defaultPolicy = open("/proc/stb/video/policy", "r").read().strip()
        except IOError:
            self.defaultPolicy = None
        try:
            self.defaultPolicy2 = open("/proc/stb/video/policy2", "r").read().strip()
        except IOError:
            self.defaultPolicy2 = None
        self.currentAVMode = self.V_MODES[0]

        self["aspectChangeActions"] = HelpableActionMap(self, "KodiInfoBarAspectChangeActions",
            {
             "aspectChange":(self.toggleAspectRatio, _("Change aspect ratio"))
              }, -3)

        self.onClose.append(self.__onClose)

    def getAspectStr(self):
        mode = self.V_DICT[self.currentAVMode]
        aspectStr = mode['aspect']
        policyStr = mode['title']
        return "%s: %s\n%s: %s" % (_("Aspect"), aspectStr, _("Policy"), policyStr)

    def setAspect(self, aspect, policy, policy2):
        print('aspect: %s policy: %s policy2: %s' % (str(aspect), str(policy), str(policy2)))
        if aspect:
            try:
                open("/proc/stb/video/aspect", "w").write(aspect)
            except IOError as e:
                print(e)
        if policy:
            try:
                open("/proc/stb/video/policy", "w").write(policy)
            except IOError as e:
                print(e)
        if policy2:
            try:
                open("/proc/stb/video/policy2", "w").write(policy2)
            except IOError as e:
                print(e)
        for f in self.postAspectChange:
            f()

    def toggleAspectRatio(self):
        self.aspectChanged = True
        modeIdx = self.V_MODES.index(self.currentAVMode)
        if modeIdx + 1 == len(self.V_MODES):
            modeIdx = 0
        else:
            modeIdx += 1
        self.currentAVMode = self.V_MODES[modeIdx]
        mode = self.V_DICT[self.currentAVMode]
        aspect = mode['aspect']
        policy = 'policy' in mode and mode['policy'] or None
        policy2 = 'policy2' in mode and mode['policy2'] or None
        self.setAspect(aspect, policy, policy2)

    def __onClose(self):
        if self.aspectChanged:
            self.setAspect(self.defaultAspect, self.defaultPolicy, self.defaultPolicy2)


class MyAudioSelection(AudioSelection):
    def __init__(self, session, infobar=None, page='audio'):
        try:
            AudioSelection.__init__(self, session, infobar, page)
        except Exception:
            # really old AudioSelection
            AudioSelection.__init__(self, session)
        self.skinName = 'AudioSelection'

#    def getSubtitleList(self):
#        return []


class StatusScreen(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.stand_alone = True
        self.delayTimer = eTimer()
        self.delayTimer.callback.append(self.hideStatus)
        self.delayTimerDelay = 1500
        desktopSize = getDesktop(0).size()
        statusPositionX = 50
        statusPositionY = 100
        self.skin = """
            <screen name="StatusScreen" position="%s,%s" size="%s,90" zPosition="0" backgroundColor="transparent" flags="wfNoBorder">
                    <widget name="status" position="0,0" size="%s,70" valign="center" halign="left" font="Regular;22" transparent="1" shadowColor="#40101010" shadowOffset="3,3" />
            </screen>""" % (str(statusPositionX), str(statusPositionY), str(desktopSize.width()), str(desktopSize.height()))
        self["status"] = Label()
        self.onClose.append(self.delayTimer.stop)

    def setStatus(self, text, color="yellow"):
        self['status'].setText(text)
        self['status'].instance.setForegroundColor(parseColor(color))
        self.show()
        self.delayTimer.start(self.delayTimerDelay, True)

    def hideStatus(self):
        self.hide()
        self['status'].setText("")

# pretty much openpli's one but simplified
class InfoBarSubservicesSupport(object):
    def __init__(self):
        self["InfoBarSubservicesActions"] = HelpableActionMap(self,
                "ColorActions", { "green": (self.showSubservices, _("Show subservices"))}, -2)
        self.__timer = eTimer()
        self.__timer.callback.append(self.__seekToCurrentPosition)
        self.onClose.append(self.__timer.stop)

    def showSubservices(self):
        service = self.session.nav.getCurrentService()
        service_ref = self.session.nav.getCurrentlyPlayingServiceReference()
        subservices = service and service.subServices()
        numsubservices = subservices and subservices.getNumberOfSubservices() or 0

        selection = 0
        choice_list = []
        for idx in range(0, numsubservices):
            subservice_ref = subservices.getSubservice(idx)
            if service_ref.toString() == subservice_ref.toString():
                selection = idx
            choice_list.append((subservice_ref.getName(), subservice_ref))
        if numsubservices > 1:
            self.session.openWithCallback(self.subserviceSelected, ChoiceBox,
                title = _("Please select subservice..."), list = choice_list,
                selection = selection, skin_name="SubserviceSelection")

    def subserviceSelected(self, service_ref):
        if service_ref:
            self.__timer.stop()
            self.__playpos = getPlayPositionPts(self.session) or 0
            duration = getDurationPts(self.session) or 0
            if (self.__playpos > 0 and duration > 0
                    and self.__playpos < duration):
                self.__timer.start(500, True)
            self.session.nav.playService(service_ref[1])

    def __seekToCurrentPosition(self):
        if getPlayPositionPts(self.session) is None:
            self.__timer.start(500, True)
        else:
            seekToPts(self.session, self.__playpos)
            del self.__playpos
