# -*- coding: utf-8 -*-
from __future__ import absolute_import #zmiana strategii ladowania modulow w py2 z relative na absolute jak w py3
from Plugins.Extensions.MyMemories.__init__ import mygettext as _
from Plugins.Extensions.MyMemories.version import Version
 
from Components.ActionMap import ActionMap, NumberActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile, NoSave, ConfigNothing, ConfigDirectory, ConfigSubsection, ConfigInteger, ConfigSelection, ConfigText, ConfigEnableDisable, KEY_LEFT, KEY_RIGHT, KEY_0, getConfigListEntry
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.FileList import FileList
from Components.Pixmap import Pixmap, MovingPixmap
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from datetime import datetime
from enigma import ePicLoad, eTimer, getDesktop, ePoint, eSize, gFont
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from skin import parseColor,parseFont 
from Tools.Directories import resolveFilename, pathExists, fileExists, SCOPE_MEDIA

import os
import Screens.Standby
import random

MyMemoriesWakeUpPicDialog = None
GenerateBootlogo = """
ffmpeg -i "PHOTO" -r 25 -b 20000 -s 1280x720 /tmp/mybootlogo.m1v
if [ -f /tmp/mybootlogo.m1v ];then
  if [ -e /usr/share/vuplus-bootlogo/ ];then 
    [ -f /usr/share/vuplus-bootlogo/bootlogo.mvi.org ] || mv -f /usr/share/vuplus-bootlogo/bootlogo.mvi /usr/share/vuplus-bootlogo/bootlogo.mvi.org
    cp -f /tmp/mybootlogo.m1v /usr/share/vuplus-bootlogo/bootlogo.mvi
  else
    cp -f /tmp/mybootlogo.m1v /etc/enigma2/bootlogo.mvi
  fi
  rm -f /tmp/mybootlogo.m1v
fi
""" # podaje sie pelna sciezka do jpg , orginalne bootlogo /usr/share/bootlogo.mvi

def getScale():
    return AVSwitch().getFramebufferScale()

config.mymemories = ConfigSubsection()

#DEBUG
config.mymemories.debug = ConfigEnableDisable(default = False)
if config.mymemories.debug.value:
    DBG=True
    def printDEBUG(myText, append2file=True):
        try:
            if append2file == False:
                f = open('/tmp/MyMemories.log', 'w')
            else:
                f = open('/tmp/MyMemories.log', 'a')
            f.write('%s %s\n' %(str(datetime.now()), myText))
            f.close
        except: pass
else:
    DBG=False

if DBG: printDEBUG("Loaded", False)

config.mymemories.picMargin = ConfigInteger(default=30, limits=(5, 99))
config.mymemories.slidetime = ConfigInteger(default=5, limits=(1, 60))
config.mymemories.resize = ConfigSelection(default="1", choices = [("0", _("simple")), ("1", _("better"))])
config.mymemories.cache = ConfigEnableDisable(default=False)
config.mymemories.lastDir = ConfigText(default=resolveFilename(SCOPE_MEDIA))
config.mymemories.infoline = ConfigEnableDisable(default=True)
config.mymemories.loop = ConfigEnableDisable(default=True)
config.mymemories.bgcolor = ConfigSelection(default="#00000000", choices = [("#00000000", _("black")),("#009eb9ff", _("blue")),("#00ff5a51", _("red")), ("#00ffe875", _("yellow")), ("#0038FF48", _("green"))])
config.mymemories.textcolor = ConfigSelection(default="#0038FF48", choices = [("#00000000", _("black")),("#009eb9ff", _("blue")),("#00ff5a51", _("red")), ("#00ffe875", _("yellow")), ("#0038FF48", _("green"))])
config.mymemories.textHeight = ConfigInteger(default=40, limits=(20, 60))
config.mymemories.textPositionH = ConfigInteger(default=60, limits=(0, getDesktop(0).size().width()))
config.mymemories.textPositionV = ConfigInteger(default= getDesktop(0).size().height() - 40 - 40, limits=(0, getDesktop(0).size().height()))

config.mymemories.stopService = ConfigEnableDisable(default=False)
config.mymemories.separator = NoSave(ConfigNothing())

config.mymemories.FrameSize = ConfigSelection(default="pic_frame_290x260x32.png", choices = [("pic_frame_190x200x8.png", "190x200"),("pic_frame_290x260x32.png", "290x260")])
                                              
#Auto display a pic
BingPicOfTheDay = '/usr/lib/enigma2/python/Plugins/Extensions/MyMemories/data/BingPicOfTheDay.jpg'
try:
    from Components.j00zekBING import getPicOfTheDay
    if not os.path.exists(BingPicOfTheDay):
        if DBG: printDEBUG("initial import of the BingPicOfTheDay")
        getPicOfTheDay(downloadPathAndFileName = BingPicOfTheDay)
except Exception as e:
    print(str(e))
    if DBG: printDEBUG("Exception: required components are missing!!!")

config.mymemories.autoMode =  ConfigSelection(default = "off",choices = [("off", _("off")),
                                                                            ("bing", _("show Bing pic of the day")),
                                                                            ("on", _("show my photos from folder")),
                                                                            ])
config.mymemories.autoDir = ConfigDirectory(default='/hdd/picture')
config.mymemories.autoWakeUp = ConfigEnableDisable(default = False)
config.mymemories.autoWakeUpTime = ConfigInteger(default=10, limits=(0, 30))
if os.path.exists('/usr/bin/ffmpeg'):
    config.mymemories.autoBoot = ConfigEnableDisable(default = False)
else:
    config.mymemories.autoBoot = NoSave(ConfigSelection(default="1", choices = [("1", _("Disabled, ffmpeg not installed:("))]))

config.mymemories.currWakeUpPic = NoSave(ConfigText(default=''))
config.mymemories.currWakeUpPicShowName = ConfigEnableDisable(default = False)

try:
    from PIL import Image, ExifTags
    config.mymemories.autoRotate = NoSave(ConfigEnableDisable(default=True))
except Exception:
    config.mymemories.autoRotate = NoSave(ConfigEnableDisable(default=False))
if DBG: printDEBUG("autoRotate=%s" % str(config.mymemories.autoRotate.value))

############################################### FUNCTIONS ######################################################################################

def autorotate(path):
    clean()
    try:
        image = Image.open(path)
        exif = image._getexif()
        if exif:
            orientation_key = 274 # cf ExifTags
            if orientation_key in exif:
                orientation = exif[orientation_key]
                rotate_values = {3: 180,
                                 6: 270,
                                 8: 90
                                }
                if orientation in rotate_values:
                    open("/tmp/autorotate.log", "w").write('rotating %s by %s\n' % (path, rotate_values[orientation]))
                    # Rotate and save the picture
                    image = image.rotate(rotate_values[orientation])
                    image_size = image.size  # old_size[0] is in (width, height) format
                    image_ratio = image_size[0] / float(image_size[1])
                    if image_ratio < 1.4:
                        new_im = Image.new("RGB", (int(image_size[1] * 1.778), image_size[1]))
                        new_im.paste(image, ( (new_im.size[0] - image_size[0]) / 2 , 0))
                        new_im.save("/tmp/rotated.jpg", quality=95, exif=str(exif))
                    elif image_ratio > 1.8:
                        new_im = Image.new("RGB", (image_size[0], int(image_size[0] / 1.778)))
                        new_im.paste(image, ( 0, (new_im.size[1] - image_size[1]) / 2 ))
                        new_im.save("/tmp/rotated.jpg", quality=95, exif=str(exif))
                    else:
                        image.save("/tmp/rotated.jpg", quality=95, exif=str(exif))
                    os.symlink(path, "/tmp/rotated.jpg.lnk")
                    return True
    except Exception as e:
        open("/tmp/autorotate.log", "a").write('%s\n' % str(e))
        pass
    
    return False

def clean(path = "/tmp/rotated.jpg"):
    if os.path.exists(path):   
        try: os.remove(path)
        except Exception: pass
    if os.path.exists(path + '.lnk'):   
        try: os.remove(path + '.lnk')
        except Exception: pass

def selectPicture():
    if config.mymemories.autoMode.value == 'bing':
        if DBG: printDEBUG('selectPicture() autoMode = bing')
        config.mymemories.currWakeUpPic.value = BingPicOfTheDay
    elif config.mymemories.autoMode.value == 'on':
        MyPhotos = []
        for currentpath, dirs, files in os.walk(config.mymemories.autoDir.value):
            for file in files:
                if file.lower().endswith('.jpg') or file.lower().endswith('.png'):
                    MyPhotos.append(os.path.join(currentpath, file))
        PhotosNumber=len(MyPhotos)
        if DBG: printDEBUG('selectPicture() found %s photos in %s directory' % (PhotosNumber, config.mymemories.autoDir.value ))
        if PhotosNumber > 1:
            config.mymemories.currWakeUpPic.value = MyPhotos[random.randint(0,len(MyPhotos) - 1)]
            if config.mymemories.autoRotate.value and autorotate(config.mymemories.currWakeUpPic.value):
                config.mymemories.currWakeUpPic.value = '/tmp/rotated.jpg'
    else:
        config.mymemories.currWakeUpPic.value = 'FakeName'

def setAlpha( AlphaLevel ):
    if os.path.exists('/proc/stb/video/alpha'):
        try:
            if config.av.osd_alpha.value == 255:
                if DBG: printDEBUG('setAlpha() Alpha not used, nothing to do')
            else:
                currAlpha = int(open("/proc/stb/video/alpha", "r").read().strip())
                if currAlpha == AlphaLevel:
                    if DBG: printDEBUG('setAlpha() Alpha already set, nothing to do')
                else:
                    open("/proc/stb/video/alpha", "w").write( str(AlphaLevel) )
                    if DBG: printDEBUG('setAlpha() Alpha set to %s' % AlphaLevel)
        except Exception as e:
            if DBG: printDEBUG('setAlpha() Exception working with Alpha: %s' % str(e))
    else:
        if DBG: printDEBUG('setAlpha() This system does not support Alpha :(')
    
    
def leaveStandby():
    if config.mymemories.autoWakeUp.value:
        selectPicture()
        if os.path.exists(config.mymemories.currWakeUpPic.value):
            if DBG: printDEBUG('leaveStandby() initiate WakeUpPic for %s' % config.mymemories.currWakeUpPic.value)
            global MyMemoriesWakeUpPicDialog
            MyMemoriesWakeUpPicDialog.start_decode()
            setAlpha(255) #disable Alpha 
            MyMemoriesWakeUpPicDialog.show()
        else:
            if DBG: printDEBUG('leaveStandby() %s does not exists' %config.mymemories.currWakeUpPic.value )

def standbyCounterChanged(configElement):
    try:
        if leaveStandby not in Screens.Standby.inStandby.onClose:
            Screens.Standby.inStandby.onClose.append(leaveStandby) 
            if DBG: printDEBUG('standbyCounterChanged() leaveStandby appended to Screens.Standby.inStandby.onClose')
    except Exception as e:
        if DBG: printDEBUG('standbyCounterChanged() exception %s' % str(e))

def main(session, **kwargs):
    session.open(picshow)

def filescan_open(list, session, **kwargs):
    if DBG: printDEBUG("filescan_open()")
    # Recreate List as expected by PicView
    filelist = [((file.path), None) for file in list]
    session.open(Pic_Full_View, filelist, 0, file.path)

def filescan(**kwargs):
    from Components.Scanner import Scanner, ScanPath

    # Overwrite checkFile to only detect local
    class LocalScanner(Scanner):
        def checkFile(self, file):
            return fileExists(file.path)

    return \
        LocalScanner(mimetypes = ["image/jpeg", "image/png", "image/gif", "image/bmp"],
            paths_to_scan = 
                [
                    ScanPath(path = "DCIM", with_subdirs = True),
                    ScanPath(path = "", with_subdirs = False),
                ],
            name = "Pictures", 
            description = _("View Photos..."),
            openfnc = filescan_open,
        )

# sessionstart
def sessionstart(reason, session = None, **kwargs):
    if reason == 0:
        if config.mymemories.autoMode.value != 'off':
            if DBG: printDEBUG("sessionstart() reason == 0 and autoMode enabled")
            from Screens.Standby import inStandby
            config.misc.standbyCounter.addNotifier(standbyCounterChanged, initial_call=False)
            global MyMemoriesWakeUpPicDialog
            MyMemoriesWakeUpPicDialog = session.instantiateDialog(MyMemoriesWakeUpPic)
        else:
            if DBG: printDEBUG('sessionstart() reason = 0 and autoMode disabled')
    else:
        if DBG: printDEBUG("sessionstart() reason <> 0")
      
# autostart
def autostart(reason, session = None, **kwargs):
    if reason == 0: # Enigma start
        if DBG: printDEBUG("autostart() Enigma starts")
        #if config.mymemories.autoMode.value != 'off':
        #    if DBG: printDEBUG("autostart() starting Enigma, autoMode enabled")
        #    from Screens.Standby import inStandby
        #    config.misc.standbyCounter.addNotifier(standbyCounterChanged, initial_call=False)
        #    global MyMemoriesWakeUpPicDialog
        #    MyMemoriesWakeUpPicDialog = session.instantiateDialog(MyMemoriesWakeUpPic)
        #else:
        #    if DBG: printDEBUG('sessionstart() starting Enigma, autoMode disabled')
    elif reason == 1: # Enigma stop
        try:
            if config.mymemories.autoBoot.value:
                selectPicture()
                if DBG: printDEBUG("autostart() Generating bootlogo during stop of Enigma from %s" % config.mymemories.currWakeUpPic.value)
                os.system(GenerateBootlogo.replace('PHOTO', config.mymemories.currWakeUpPic.value) )
            else:
                if DBG: printDEBUG("autostart() Nothing to do during  stop of Enigma")
        except Exception:
            pass
      
def Plugins(**kwargs):
    return [PluginDescriptor(name=_("My Memories"), icon="MyMemories.png", where = PluginDescriptor.WHERE_PLUGINMENU, needsRestart = False, fnc=main),
            PluginDescriptor(name=_("My Memories"), where = PluginDescriptor.WHERE_FILESCAN, needsRestart = False, fnc = filescan),
            PluginDescriptor(name="My Memories", where = PluginDescriptor.WHERE_SESSIONSTART, fnc = sessionstart, needsRestart = False, weight = -1),
            PluginDescriptor(where = PluginDescriptor.WHERE_AUTOSTART, fnc = autostart )]

############################################### CLASSES ######################################################################################

class picshow(Screen):
    skin = """
        <screen name="picshow" position="center,center" size="560,440" title="My Memories" >
            <ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
            <ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
            <ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
            <ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on" />
            <widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
            <widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
            <widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
            <widget source="key_blue" render="Label" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
            <widget source="label" render="Label" position="5,55" size="350,140" font="Regular;19" backgroundColor="#25062748" transparent="1"  />
            <widget name="thn" position="360,40" size="180,160" alphatest="on" />
            <widget name="filelist" position="5,205" zPosition="2" size="550,230" scrollbarMode="showOnDemand" />
        </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)

        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions"],
        {
            "cancel": self.KeyExit,
            "red": self.KeyExit,
            "green": self.KeyGreen,
            "yellow": self.KeyYellow,
            "blue": self.KeyBlue,
            "ok": self.KeyOk
        }, -1)

        self["key_red"] = StaticText(_("Close"))
        self["key_green"] = StaticText(_("Thumbnails"))
        self["key_yellow"] = StaticText("")
        self["key_blue"] = StaticText(_("Setup"))
        self["label"] = StaticText("")
        self["thn"] = Pixmap()

        currDir = config.mymemories.lastDir.value
        if not pathExists(currDir):
            currDir = "/"

        self.filelist = FileList(currDir, matchingPattern = "(?i)^.*\.(jpeg|jpg|jpe|png|bmp|gif)")
        self["filelist"] = self.filelist
        self["filelist"].onSelectionChanged.append(self.selectionChanged)

        self.ThumbTimer = eTimer()
        self.ThumbTimer.callback.append(self.showThumb)

        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.showPic)

        self.onLayoutFinish.append(self.setConf)
        if config.mymemories.stopService.value:
            self.LastPlayedService = self.session.nav.getCurrentlyPlayingServiceReference()
            self.session.nav.stopService()

        if DBG: printDEBUG("class picshow initiated")

    def showPic(self, picInfo=""):
        ptr = self.picload.getData()
        if ptr != None:
            self["thn"].instance.setPixmap(ptr.__deref__())
            self["thn"].show()

        text = picInfo.split('\n',1)
        self["label"].setText(text[1])
        self["key_yellow"].setText(_("Exif"))

    def showThumb(self):
        if not self.filelist.canDescent():
            if self.filelist.getCurrentDirectory() and self.filelist.getFilename():
                if config.mymemories.autoRotate.value and autorotate(self.filelist.getCurrentDirectory() + self.filelist.getFilename()):
                    if self.picload.getThumbnail('/tmp/rotated.jpg') == 1:
                        self.ThumbTimer.start(500, True)
                else:
                    if self.picload.getThumbnail(self.filelist.getCurrentDirectory() + self.filelist.getFilename()) == 1:
                        self.ThumbTimer.start(500, True)

    def selectionChanged(self):
        if not self.filelist.canDescent():
            self.ThumbTimer.start(500, True)
        else:
            self["label"].setText("")
            self["thn"].hide()
            self["key_yellow"].setText("")

    def KeyGreen(self):
        #if not self.filelist.canDescent():
        self.session.openWithCallback(self.callbackView, Pic_Thumb, self.filelist.getFileList(), self.filelist.getSelectionIndex(), self.filelist.getCurrentDirectory())

    def KeyYellow(self):
        if not self.filelist.canDescent():
            self.session.open(Pic_Exif, self.picload.getInfo(self.filelist.getCurrentDirectory() + self.filelist.getFilename()))

    def KeyBlue(self):
        self.session.openWithCallback(self.setConf ,MyMemoriesSetup)

    def KeyOk(self):
        if self.filelist.canDescent():
            self.filelist.descent()
        else:
            self.session.openWithCallback(self.callbackView, Pic_Full_View, self.filelist.getFileList(), self.filelist.getSelectionIndex(), self.filelist.getCurrentDirectory())

    def setConf(self):
        self.setTitle(_("My Memories"))
        sc = getScale()
        #0=Width 1=Height 2=Aspect 3=use_cache 4=resize_type 5=Background(#AARRGGBB)
        self.picload.setPara((self["thn"].instance.size().width(), self["thn"].instance.size().height(), sc[0], sc[1], config.mymemories.cache.value, int(config.mymemories.resize.value), "#00000000"))

    def callbackView(self, val=0):
        if val > 0:
            self.filelist.moveToIndex(val)

    def KeyExit(self):
        clean()
        del self.picload

        if self.filelist.getCurrentDirectory() is None:
            config.mymemories.lastDir.value = "/"
        else:
            config.mymemories.lastDir.value = self.filelist.getCurrentDirectory()

        if config.mymemories.stopService.value and self.LastPlayedService:
            self.session.nav.playService(self.LastPlayedService)

        config.mymemories.save()
        self.close()

#####################################################################################################################################

class MyMemoriesSetup(Screen, ConfigListScreen):
    def __init__(self, session):
        Screen.__init__(self, session)
        # for the skin: first try MediaPlayerSettings, then Setup, this allows individual skinning
        self.skinName = ["MyMemoriesSetup", "Setup" ]
        self.setup_title = _("My Memories Settings by j00zek v %s")  % Version
        self.onChangedEntry = [ ]
        self.session = session

        self["actions"] = ActionMap(["MyMemoriesSetupActions"],
            {
                "cancel": self.keyCancel,
                "save": self.keySave,
                "ok": self.selectFolder,
                "key_blue": self.TestWakeUpPicture,
            }, -2)

        self["key_red"] = StaticText(_("Cancel"))
        self["key_green"] = StaticText(_("OK"))

        self.list = []
        ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)
        self.createSetup()
        self.onLayoutFinish.append(self.layoutFinished)
        if DBG: printDEBUG("class MyMemoriesSetup initiated")

    def layoutFinished(self):
        self.setTitle(self.setup_title)

    def createSetup(self):
        self.list = []
        self.list.append(getConfigListEntry(_("Slideshow Interval (sec.)"), config.mymemories.slidetime))
        self.list.append(getConfigListEntry(_("Scaling Mode"), config.mymemories.resize))
        self.list.append(getConfigListEntry(_("Cache Thumbnails"), config.mymemories.cache))
        self.list.append(getConfigListEntry(_("Thumbnails size"), config.mymemories.FrameSize))
        self.list.append(getConfigListEntry(_("Photo margins in full view"), config.mymemories.picMargin))
        self.list.append(getConfigListEntry(_("slide picture in loop"), config.mymemories.loop))
        self.list.append(getConfigListEntry(_("Background color"), config.mymemories.bgcolor))
        self.list.append(getConfigListEntry(_("show Infoline"), config.mymemories.infoline))
        self.list.append(getConfigListEntry(_("Infoline color"), config.mymemories.textcolor))
        self.list.append(getConfigListEntry(_("Infoline height"), config.mymemories.textHeight))
        self.list.append(getConfigListEntry(_("Infoline horizontal position"), config.mymemories.textPositionH))
        self.list.append(getConfigListEntry(_("Infoline vertial position"), config.mymemories.textPositionV))
        
        self.list.append(getConfigListEntry(_("Stop playing service"), config.mymemories.stopService))
        #
        self.list.append(getConfigListEntry(" ", config.mymemories.separator))
        self.list.append(getConfigListEntry(_("Auto mode:"), config.mymemories.autoMode))
        if config.mymemories.autoMode.value != 'off':
            self.list.append(getConfigListEntry(_("Generate boot logo:"), config.mymemories.autoBoot))
            self.list.append(getConfigListEntry(_("Display photo on wakeup:"), config.mymemories.autoWakeUp))
            if config.mymemories.autoWakeUp.value:
                self.list.append(getConfigListEntry(_("Display time:"), config.mymemories.autoWakeUpTime))
                if config.mymemories.autoMode.value == 'on':
                    self.list.append(getConfigListEntry(_("Photos directory:"), config.mymemories.autoDir))

        self.list.append(getConfigListEntry(" ", config.mymemories.separator))
        self.list.append(getConfigListEntry(_("Debug:"), config.mymemories.debug))
        self.list.append(getConfigListEntry(" ", config.mymemories.separator))
        if config.mymemories.autoRotate.value:
            self.list.append(getConfigListEntry(_("PIL loaded, rotating pic enabled :)"), config.mymemories.separator))
        else:
            self.list.append(getConfigListEntry(_("PIL not loaded, rotating pic disabled :("), config.mymemories.separator))

        self["config"].list = self.list
        self["config"].l.setList(self.list)
        self.currIDX = self["config"].getCurrentIndex()
        if not self.selectionChanged in self["config"].onSelectionChanged:
            self["config"].onSelectionChanged.append(self.selectionChanged)

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)

    def keyRight(self):
        ConfigListScreen.keyRight(self)

    def selectionChanged(self):
        newIDX = self["config"].getCurrentIndex()
        #if DBG: printDEBUG("MyMemoriesSetup.selectionChanged() currIDX=%s, newIDX=%s" %  (self.currIDX , newIDX))
        if self["config"].getCurrent()[1] == config.mymemories.separator:
            if newIDX > self.currIDX:
                if newIDX < len(self.list) - 1: newIDX += 1
                self["config"].setCurrentIndex(newIDX)
            elif newIDX < self.currIDX:
                if newIDX > 0: newIDX -= 1
                self["config"].setCurrentIndex(newIDX)
        self.currIDX = newIDX
        
    # for summary:
    def changedEntry(self):
        if DBG: printDEBUG("MyMemoriesSetup.changedEntry() %s=%s" %(self.getCurrentEntry() , self.getCurrentValue() ))
        for x in self.onChangedEntry:
            x()
        self.createSetup()

    def getCurrentEntry(self):
        return self["config"].getCurrent()[0]

    def getCurrentValue(self):
        return str(self["config"].getCurrent()[1].getText())

    def createSummary(self):
        from Screens.Setup import SetupSummary
        return SetupSummary

    def keySave(self):
        for x in self["config"].list:
            x[1].save()
        configfile.save()
        self.close()

    def keyCancel(self):
        for x in self["config"].list:
            x[1].cancel()
        self.close()  

    def selectFolder(self):
        curIndex = self["config"].getCurrentIndex()
        currItem = self["config"].list[curIndex][1]
        if isinstance(currItem, ConfigDirectory):
            def SetDirPathCallBack(curIndex, newPath):
                if None != newPath: self["config"].list[curIndex][1].value = newPath
            from Tools.BoundFunction import boundFunction
            titletxt=_("Select directory with your photos")
            print(curIndex)
            print(DirectorySelectorWidget)
            print(currItem.value)
            print(titletxt)
            print(boundFunction)
            print(SetDirPathCallBack)
            if os.path.isdir(currItem.value):
                self.session.openWithCallback(boundFunction(SetDirPathCallBack, curIndex), DirectorySelectorWidget, currDir=currItem.value, title=titletxt)
            else:
                self.session.openWithCallback(boundFunction(SetDirPathCallBack, curIndex), DirectorySelectorWidget, currDir='/', title=titletxt)
    
    def TestWakeUpPicture(self):
        if DBG: printDEBUG('TestWakeUpPicture()')
        def retFromTestWakeUpPicture():
            pass
        if config.mymemories.autoMode.value != 'off':
            self.session.openWithCallback(retFromTestWakeUpPicture, MyMemoriesWakeUpPic)
      
#####################################################################################################################################

class Pic_Exif(Screen):
    skin = """
        <screen name="Pic_Exif" position="center,center" size="560,360" title="Info" >
            <ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
            <widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
            <widget source="menu" render="Listbox" position="5,50" size="550,310" scrollbarMode="showOnDemand" selectionDisabled="1" >
                <convert type="TemplatedMultiContent">
                {
                    "template": [  MultiContentEntryText(pos = (5, 5), size = (250, 30), flags = RT_HALIGN_LEFT, text = 0), MultiContentEntryText(pos = (260, 5), size = (290, 30), flags = RT_HALIGN_LEFT, text = 1)],
                    "fonts": [gFont("Regular", 20)],
                    "itemHeight": 30
                }
                </convert>
            </widget>
        </screen>"""

    def __init__(self, session, exiflist):
        Screen.__init__(self, session)

        self["actions"] = ActionMap(["Pic_ExifActions"],
        {
            "cancel": self.close
        }, -1)

        self["key_red"] = StaticText(_("Close"))

        exifdesc = [_("filename")+':', "EXIF-Version:", "Make:", "Camera:", "Date/Time:", "Width / Height:", "Flash used:", "Orientation:", "User Comments:", "Metering Mode:", "Exposure Program:", "Light Source:", "CompressedBitsPerPixel:", "ISO Speed Rating:", "X-Resolution:", "Y-Resolution:", "Resolution Unit:", "Brightness:", "Exposure Time:", "Exposure Bias:", "Distance:", "CCD-Width:", "ApertureFNumber:"]
        list = []

        for x in range(len(exiflist)):
            if x>0:
                list.append((exifdesc[x], exiflist[x]))
            else:
                name = exiflist[x].split('/')[-1]
                list.append((exifdesc[x], name))
        self["menu"] = List(list)
        self.onLayoutFinish.append(self.layoutFinished)
        if DBG: printDEBUG("class Pic_Exif initiated")

    def layoutFinished(self):
        self.setTitle(_("Info"))

#####################################################################################################################################

T_INDEX = 0
T_FRAME_POS = 1
T_PAGE = 2
T_NAME = 3
T_FULL = 4

class Pic_Thumb(Screen):
    def __init__(self, session, piclist, lastindex, path):

        self.textcolor = config.pic.textcolor.value
        self.color = config.pic.bgcolor.value
        if config.mymemories.FrameSize.value == "pic_frame_290x260x32.png":
            textsize = 52
            self.spaceX = 26
            self.picX = 290
            self.spaceY = 8
            self.picY = 260
            self.frameX = 290
            self.frameY = 290
        else:
            textsize = 20
            self.spaceX = 35
            self.picX = 190
            self.spaceY = 30
            self.picY = 200
            self.frameX = 190
            self.frameY = 200

        size_w = getDesktop(0).size().width()
        size_h = getDesktop(0).size().height()
        self.thumbsX = size_w / (self.spaceX + self.picX) # thumbnails in X
        self.thumbsY = size_h / (self.spaceY + self.picY) # thumbnails in Y
        self.thumbsC = self.thumbsX * self.thumbsY # all thumbnails

        self.positionlist = []
        skincontent = '<screen position="0,0" size="%s,%s" flags="wfNoBorder" >' % (str(size_w), str(size_h))
        skincontent += '<eLabel position="0,0" zPosition="0" size="%s,%s" backgroundColor="%s" />' % (str(size_w), str(size_h), self.color)
        skincontent += '<widget name="frame" position="35,30" size="%s,%s" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMemories/data/%s" zPosition="1" alphatest="on" />' % (self.frameX, self.frameY, config.mymemories.FrameSize.value)

        posX = -1
        for x in range(self.thumbsC):
            posY = x / self.thumbsX
            posX += 1
            if posX >= self.thumbsX:
                posX = 0

            absX = self.spaceX + (posX*(self.spaceX + self.picX))
            absY = self.spaceY + (posY*(self.spaceY + self.picY))
            self.positionlist.append((absX, absY))
            skincontent += '<widget source="label%s" render="Label" position="%s,%s" size="%s,%s" font="Regular;20" zPosition="2" transparent="1" noWrap="0" foregroundColor="%s" />' % (str(x),
                                                                                                                                      str(absX+5), str(absY+self.picY-textsize),
                                                                                                                                      str(self.picX ),str(textsize),
                                                                                                                                      self.textcolor)
                             
            skincontent += '<widget name="thumb%s" position="%s,%s" size="%s,%s" zPosition="2" transparent="1" alphatest="on" />' % (str(x), 
                                                                                                                                     str(absX+5), str(absY+5), 
                                                                                                                                     str(self.picX -10), str(self.picY - (textsize*2)))

        # Screen, backgroundlabel and MovingPixmap
        skincontent += '</screen>'
        self.skin = skincontent

        Screen.__init__(self, session)

        self["actions"] = ActionMap(["Pic_ThumbActions"],
        {
            "cancel": self.Exit,
            "ok": self.KeyOk,
            "left": self.key_left,
            "right": self.key_right,
            "up": self.key_up,
            "down": self.key_down,
            "showPic_Exif": self.StartExif,
        }, -1)

        self["frame"] = MovingPixmap()
        for x in range(self.thumbsC):
            self["label"+str(x)] = StaticText()
            self["thumb"+str(x)] = Pixmap()

        self.Thumbnaillist = []
        self.filelist = []
        self.currPage = -1
        self.dirlistcount = 0
        self.path = path

        index = 0
        framePos = 0
        Page = 0
        for x in piclist:
            if x[0][1] == False:
                self.filelist.append((index, framePos, Page, x[0][0],  path + x[0][0]))
                index += 1
                framePos += 1
                if framePos > (self.thumbsC -1):
                    framePos = 0
                    Page += 1
            else:
                self.dirlistcount += 1

        self.maxentry = len(self.filelist)-1
        self.index = lastindex - self.dirlistcount
        if self.index < 0:
            self.index = 0

        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.showPic)

        self.onLayoutFinish.append(self.setPicloadConf)

        self.ThumbTimer = eTimer()
        self.ThumbTimer.callback.append(self.showPic)
        if DBG: printDEBUG("class Pic_Thumb initiated")

    def setPicloadConf(self):
        sc = getScale()
        self.picload.setPara([self["thumb0"].instance.size().width(), self["thumb0"].instance.size().height(), sc[0], sc[1], config.mymemories.cache.value, int(config.mymemories.resize.value), self.color])
        self.paintFrame()

    def paintFrame(self):
        #vtilog("index=" + str(self.index))
        if self.maxentry < self.index or self.index < 0:
            return

        pos = self.positionlist[self.filelist[self.index][T_FRAME_POS]]
        self["frame"].moveTo( pos[0], pos[1], 1)
        self["frame"].startMoving()

        if self.currPage != self.filelist[self.index][T_PAGE]:
            self.currPage = self.filelist[self.index][T_PAGE]
            self.newPage()

    def newPage(self):
        self.Thumbnaillist = []
        #clear Labels and Thumbnail
        for x in range(self.thumbsC):
            self["label"+str(x)].setText("")
            self["thumb"+str(x)].hide()
        #paint Labels and fill Thumbnail-List
        for x in self.filelist:
            if x[T_PAGE] == self.currPage:
                self["label"+str(x[T_FRAME_POS])].setText("(" + str(x[T_INDEX]+1) + ") " + x[T_NAME])
                self.Thumbnaillist.append([0, x[T_FRAME_POS], x[T_FULL]])

        #paint Thumbnail start
        self.showPic()

    def showPic(self, picInfo=""):
        for x in range(len(self.Thumbnaillist)):
            if self.Thumbnaillist[x][0] == 0:
                if config.mymemories.autoRotate.value and autorotate(self.Thumbnaillist[x][2]):
                    if self.picload.getThumbnail('/tmp/rotated.jpg') == 1:
                        self.ThumbTimer.start(500, True)
                elif self.picload.getThumbnail(self.Thumbnaillist[x][2]) == 1: #do it again
                    self.ThumbTimer.start(500, True)
                else:
                    self.Thumbnaillist[x][0] = 1
                break
            elif self.Thumbnaillist[x][0] == 1:
                self.Thumbnaillist[x][0] = 2
                ptr = self.picload.getData()
                if ptr != None:
                    self["thumb" + str(self.Thumbnaillist[x][1])].instance.setPixmap(ptr.__deref__())
                    self["thumb" + str(self.Thumbnaillist[x][1])].show()

    def key_left(self):
        self.index -= 1
        if self.index < 0:
            self.index = self.maxentry
        self.paintFrame()

    def key_right(self):
        self.index += 1
        if self.index > self.maxentry:
            self.index = 0
        self.paintFrame()

    def key_up(self):
        self.index -= self.thumbsX
        if self.index < 0:
            self.index =self.maxentry
        self.paintFrame()

    def key_down(self):
        self.index += self.thumbsX
        if self.index > self.maxentry:
            self.index = 0
        self.paintFrame()

    def StartExif(self):
        if self.maxentry < 0:
            return
        self.session.open(Pic_Exif, self.picload.getInfo(self.filelist[self.index][T_FULL]))

    def KeyOk(self):
        if self.maxentry < 0:
            return
        self.old_index = self.index
        self.session.openWithCallback(self.callbackView, Pic_Full_View, self.filelist, self.index, self.path)

    def callbackView(self, val=0):
        self.index = val
        if self.old_index != self.index:
            self.paintFrame()
    def Exit(self):
        clean()
        del self.picload
        self.close(self.index + self.dirlistcount)

#####################################################################################################################################

class Pic_Full_View(Screen):
    def __init__(self, session, filelist, index, path):

        self.textcolor = config.mymemories.textcolor.value
        self.bgcolor = config.mymemories.bgcolor.value
        space = config.mymemories.picMargin.value
        size_w = getDesktop(0).size().width()
        size_h = getDesktop(0).size().height()

        self.skin = "<screen position=\"0,0\" size=\"" + str(size_w) + "," + str(size_h) + "\" flags=\"wfNoBorder\" > \
            <eLabel position=\"0,0\" zPosition=\"0\" size=\""+ str(size_w) + "," + str(size_h) + "\" backgroundColor=\""+ self.bgcolor +"\" /><widget name=\"pic\" position=\"" + str(space) + "," + str(space) + "\" size=\"" + str(size_w-(space*2)) + "," + str(size_h-(space*2)) + "\" zPosition=\"1\" alphatest=\"on\" /> \
            <widget name=\"point\" position=\""+ str(space+5) + "," + str(space+2) + "\" size=\"20,20\" zPosition=\"2\" pixmap=\"skin_default/icons/record.png\" alphatest=\"on\" /> \
            <widget name=\"play_icon\" position=\""+ str(space+25) + "," + str(space+2) + "\" size=\"20,20\" zPosition=\"2\" pixmap=\"skin_default/icons/ico_mp_play.png\"  alphatest=\"on\" /> \
            <widget source=\"file\" render=\"Label\" position=\""+ str(space+45) + "," + str(space) + "\" size=\""+ str(size_w-(space*2)-50) + ",25\" font=\"Regular;20\" halign=\"left\" foregroundColor=\"" + self.textcolor + "\" zPosition=\"2\" noWrap=\"1\" transparent=\"1\" /></screen>"

        Screen.__init__(self, session)

        self["actions"] = ActionMap(["Pic_Full_View_Actions"],
        {
            "cancel": self.Exit,
            "PlayPause": self.PlayPause,
            "PlayPause": self.PlayPause,
            "blue": self.nextPic,
            "red": self.prevPic,
            "left": self.prevPic,
            "right": self.nextPic,
            "showPic_Exif": self.StartExif,
        }, -1)

        self["point"] = Pixmap()
        self["pic"] = Pixmap()
        self["play_icon"] = Pixmap()
        self["file"] = StaticText(_("please wait, loading picture..."))

        self.old_index = 0
        self.filelist = []
        self.lastindex = index
        self.currPic = []
        self.shownow = True
        self.dirlistcount = 0

        for x in filelist:
            if len(filelist[0]) == 3: #orig. filelist
                if x[0][1] == False:
                    self.filelist.append(path + x[0][0])
                else:
                    self.dirlistcount += 1
            elif len(filelist[0]) == 2: #scanlist
                if x[0][1] == False:
                    self.filelist.append(x[0][0])
                else:
                    self.dirlistcount += 1
            else: # thumbnaillist
                self.filelist.append(x[T_FULL])

        self.maxentry = len(self.filelist)-1
        self.index = index - self.dirlistcount
        if self.index < 0:
            self.index = 0

        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.finish_decode)

        self.slideTimer = eTimer()
        self.slideTimer.callback.append(self.slidePic)

        if self.maxentry >= 0:
            self.onLayoutFinish.append(self.setPicloadConf)

        if config.mymemories.stopService.value:
            self.LastPlayedService = self.session.nav.getCurrentlyPlayingServiceReference()
            self.session.nav.stopService()
        if DBG: printDEBUG("class Pic_Full_View initiated, pictures=%s" % len(self.filelist))

    def setPicloadConf(self):
        sc = getScale()
        self.picload.setPara([self["pic"].instance.size().width(), self["pic"].instance.size().height(), sc[0], sc[1], 0, int(config.mymemories.resize.value), self.bgcolor])

        self["play_icon"].hide()
        if config.mymemories.infoline.value == False:
            self["file"].setText("")
        self.start_decode()

    def ShowPicture(self):
        if self.shownow and len(self.currPic):
            self.shownow = False
            self["file"].setText(self.currPic[0])
            self.lastindex = self.currPic[1]
            self["pic"].instance.setPixmap(self.currPic[2].__deref__())
            self.currPic = []

            self.next()
            self.start_decode()

    def finish_decode(self, picInfo=""):
        self["point"].hide()
        ptr = self.picload.getData()
        if ptr != None:
            text = ""
            try:
                text = picInfo.split('\n',1)
                text = text[0].split('/')[-1]
                if text == 'rotated.jpg':
                    text = self.filelist[self.index].split('/')[-1]
                text = "(" + str(self.index+1) + "/" + str(self.maxentry+1) + ") " + text
            except:
                pass
            self.currPic = []
            self.currPic.append(text)
            self.currPic.append(self.index)
            self.currPic.append(ptr)
            self.ShowPicture()

    def start_decode(self):
        if config.mymemories.autoRotate.value and autorotate(self.filelist[self.index]):
            self.picload.startDecode('/tmp/rotated.jpg')
        else:
            self.picload.startDecode(self.filelist[self.index])
        self["point"].show()

    def next(self):
        self.index += 1
        if self.index > self.maxentry:
            self.index = 0

    def prev(self):
        self.index -= 1
        if self.index < 0:
            self.index = self.maxentry

    def slidePic(self):
        vtilog("slide to next Picture index=" + str(self.lastindex))
        if config.mymemories.loop.value==False and self.lastindex == self.maxentry:
            self.PlayPause()
        self.shownow = True
        self.ShowPicture()

    def PlayPause(self):
        if self.slideTimer.isActive():
            self.slideTimer.stop()
            self["play_icon"].hide()
        else:
            self.slideTimer.start(config.mymemories.slidetime.value*1000)
            self["play_icon"].show()
            self.nextPic()

    def prevPic(self):
        self.currPic = []
        self.index = self.lastindex
        self.prev()
        self.start_decode()
        self.shownow = True

    def nextPic(self):
        self.shownow = True
        self.ShowPicture()

    def StartExif(self):
        if self.maxentry < 0:
            return
        self.session.open(Pic_Exif, self.picload.getInfo(self.filelist[self.lastindex]))

    def Exit(self):
        clean()
        if config.mymemories.stopService.value and self.LastPlayedService:
            self.session.nav.playService(self.LastPlayedService)
        del self.picload
        self.close(self.lastindex + self.dirlistcount)

#####################################################################################################################################
from Components.FileList import FileList
from Components.Label import Label 
from Components.Sources.StaticText import StaticText
#from Screens.HelpMenu import HelpableScreen
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Tools.BoundFunction import boundFunction

class DirectorySelectorWidget(Screen):
    skin = """
    <screen name="DirectorySelectorWidget" position="center,center" size="620,440" title="">
            <widget name="key_red"      position="10,10"  zPosition="2"  size="600,35" valign="center"  halign="left"   font="Regular;22" transparent="1" foregroundColor="red" />
            <widget name="key_blue"     position="10,10"  zPosition="2"  size="600,35" valign="center"  halign="center" font="Regular;22" transparent="1" foregroundColor="blue" />
            <widget name="key_green"    position="10,10"  zPosition="2"  size="600,35" valign="center"  halign="right"  font="Regular;22" transparent="1" foregroundColor="green" />
            <widget name="key_yellow"   position="10,10"  zPosition="2"  size="600,35" valign="center"  halign="right"  font="Regular;22" transparent="1" foregroundColor="green" />
            <widget name="curr_dir"     position="10,50"  zPosition="2"  size="600,35" valign="center"  halign="left"   font="Regular;18" transparent="1" foregroundColor="white" />
            <widget name="filelist"     position="10,85"  zPosition="1"  size="580,335" transparent="1" scrollbarMode="showOnDemand" />
    </screen>"""
    def __init__(self, session, currDir, title="Select directory"):
        print("DirectorySelectorWidget.__init__ -------------------------------")
        Screen.__init__(self, session)
        # for the skin: first try MediaPlayerDirectoryBrowser, then FileBrowser, this allows individual skinning
        #self.skinName = ["MediaPlayerDirectoryBrowser", "FileBrowser" ]
        self["key_red"]    = Label(_("Cancel"))
        #self["key_yellow"] = Label(_("Refresh"))
        self["key_blue"]   = Label(_("New directory"))
        self["key_green"]  = Label(_("Select"))
        self["curr_dir"]   = Label(_(" "))
        self.filelist      = FileList(directory=currDir, matchingPattern="", showFiles=False)
        self["filelist"]   = self.filelist
        self["FilelistActions"] = ActionMap(["SetupActions", "ColorActions"],
            {
                "green" : self.use,
                "red"   : self.exit,
                "yellow": self.refresh,
                "blue"  : self.newDir,
                "ok"    : self.ok,
                "cancel": self.exit
            })
        self.title = title
        self.onLayoutFinish.append(self.layoutFinished)
        self.onClose.append(self.__onClose)

    def mkdir(newdir):
        """ Wrapper for the os.mkdir function
            returns status instead of raising exception
        """
        try:
            os_mkdir(newdir)
            sts = True
            msg = _('Directory "%s" has been created.') % newdir
        except:
            sts = False
            msg = _('Error creating directory "%s".') % newdir
            printExc()
        return sts,msg
    
    def __del__(self):
        print("DirectorySelectorWidget.__del__ -------------------------------")

    def __onClose(self):
        print("DirectorySelectorWidget.__onClose -----------------------------")
        self.onClose.remove(self.__onClose)
        self.onLayoutFinish.remove(self.layoutFinished)

    def layoutFinished(self):
        print("DirectorySelectorWidget.layoutFinished -------------------------------")
        self.setTitle(_(self.title))
        self.currDirChanged()

    def currDirChanged(self):
        self["curr_dir"].setText(_(self.getCurrentDirectory()))
        
    def getCurrentDirectory(self):
        currDir = self["filelist"].getCurrentDirectory()
        if currDir and os.path.isdir( currDir ):
            return currDir
        else:
            return "/"

    def use(self):
        self.close( self.getCurrentDirectory() )

    def exit(self):
        self.close(None)

    def ok(self):
        if self.filelist.canDescent():
            self.filelist.descent()
        self.currDirChanged()

    def refresh(self):
        self["filelist"].refresh()

    def newDir(self):
        currDir = self["filelist"].getCurrentDirectory()
        if currDir and os.path.isdir( currDir ):
            self.session.openWithCallback(boundFunction(self.enterPatternCallBack, currDir), VirtualKeyBoard, title = (_("Enter name")), text = "")

    def IsValidFileName(name, NAME_MAX=255):
        prohibited_characters = ['/', "\000", '\\', ':', '*', '<', '>', '|', '"']
        if isinstance(name, basestring) and (1 <= len(name) <= NAME_MAX):
            for it in name:
                if it in prohibited_characters:
                    return False
            return True
        return False
    
    def enterPatternCallBack(self, currDir, newDirName=None):
        if None != currDir and newDirName != None:
            sts = False
            if self.IsValidFileName(newDirName):
                sts,msg = self.mkdir(os.path.join(currDir, newDirName))
            else:
                msg = _("Incorrect directory name.")
            if sts:
                self.refresh()
            else:
                self.session.open(MessageBox, msg, type = MessageBox.TYPE_INFO, timeout=5)

#####################################################################################################################################

class MyMemoriesWakeUpPic(Screen):
    def __init__(self, session):
        self.size_w = getDesktop(0).size().width()
        self.size_h = getDesktop(0).size().height()

        self.skin = """<screen position="0,0" size="%s,%s" flags="wfNoBorder" >
              <widget source="session.VideoPicture" render="Pig" position="%s,%s" zPosition="0" size="192,108" backgroundColor="transparent" />
              <widget name="pic" position="0,0" size="10,10" zPosition="1" alphatest="on" />
              <widget name="picDescr" position="0,0" size="10,10" font="Regular;10" halign="left" valign="center" zPosition="2" noWrap="1" transparent="0"/>
            </screen>""" % (self.size_w, self.size_h, self.size_w, self.size_h)

        Screen.__init__(self, session)

        self["actions"] = ActionMap(["MyMemoriesWakeUpPicActions"], { "cancel": self.Exit, }, -1)
        self["pic"] = Pixmap()
        self["picDescr"] = Label() 
        
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.finish_decode)

        self.closeTimer = eTimer()
        self.closeTimer.callback.append(self.Exit)

        self.onShown.append(self.start_decode)
        
        if DBG: printDEBUG("class MyMemoriesWakeUpPic initiated")

    def cleanFileNameForDisplay(self):
        cleanedName = config.mymemories.currWakeUpPic.value
        
        if not config.mymemories.infoline.value:
            return ''
        elif cleanedName == BingPicOfTheDay:
            return _('Bing picture of the day')
        elif cleanedName == '/tmp/rotated.jpg':
            if not os.path.exists("/tmp/rotated.jpg.lnk"):
                return _('No description for this photorotated by PIL')
            else:
                cleanedName = os.path.realpath("/tmp/rotated.jpg.lnk")
        
        if config.mymemories.currWakeUpPicShowName.value:
            cleanedName = cleanedName.replace(config.mymemories.autoDir.value,'')
            if cleanedName.startswith('/'):
                cleanedName = cleanedName[1:]
        else:
            cleanedName = os.path.dirname(cleanedName).replace(config.mymemories.autoDir.value,'').replace(os.path.realpath(config.mymemories.autoDir.value),'')
            if cleanedName.startswith('/'):
                cleanedName = cleanedName[1:]
            if cleanedName.endswith('/'):
                cleanedName = cleanedName[:-1]
        return cleanedName
    
    def start_decode(self):
        if DBG: printDEBUG("MyMemoriesWakeUpPic.start_decode()")
        if os.path.exists(config.mymemories.currWakeUpPic.value):
            #self.LastPlayedService = self.session.nav.getCurrentlyPlayingServiceReference()
            #self.session.nav.stopService()
            #if DBG: printDEBUG("\t LastPlayedService=%s" % str(self.LastPlayedService))
            self["pic"].instance.resize(eSize(self.size_w-(config.mymemories.picMargin.value * 2), self.size_h-(config.mymemories.picMargin.value * 2)) )
            self["pic"].instance.move(ePoint(config.mymemories.picMargin.value, config.mymemories.picMargin.value)) 
            sc = getScale()
            self.picload.setPara([self["pic"].instance.size().width(), self["pic"].instance.size().height(), sc[0], sc[1], 0, 1, config.mymemories.bgcolor.value])
            self.picload.startDecode(config.mymemories.currWakeUpPic.value)
        else:
            if DBG: printDEBUG("\t %s does nto exists, end" % config.mymemories.currWakeUpPic.value )
            self.LastPlayedService = None
            self.Exit()

    def finish_decode(self, picInfo=""):
        if DBG: printDEBUG("MyMemoriesWakeUpPic.finish_decode()")
        ptr = self.picload.getData()
        if ptr != None:
            text = self.cleanFileNameForDisplay()
            self["picDescr"].setText(text)
            textWidth = len(text) * int(config.mymemories.textHeight.value * 0.75) # The best would be to calculate real width, but don't know how to do it. :(
            self["picDescr"].instance.resize(eSize(textWidth, config.mymemories.textHeight.value + 4) )
            self["picDescr"].instance.setForegroundColor(parseColor(config.mymemories.textcolor.value))
            self["picDescr"].instance.setBackgroundColor(parseColor(config.mymemories.bgcolor.value))
            self["picDescr"].instance.move(ePoint(config.mymemories.textPositionH.value, config.mymemories.textPositionV.value))
            self["picDescr"].instance.setFont(gFont("Regular", config.mymemories.textHeight.value)) 
            textWidth = self["picDescr"].instance.calculateSize().width()
            self["picDescr"].instance.resize(eSize(textWidth, config.mymemories.textHeight.value + 4) )
            
            self["pic"].instance.setPixmap(ptr.__deref__())
            if config.mymemories.autoWakeUpTime.value > 0:
                self.closeTimer.start(config.mymemories.autoWakeUpTime.value * 1000)

    def Exit(self):
        if DBG: printDEBUG("MyMemoriesWakeUpPic.Exit()")
        self.closeTimer.stop()
        setAlpha(config.av.osd_alpha.value)
        clean()
        self.hide()
        #if self.LastPlayedService:
        #    self.session.nav.playService(self.LastPlayedService)
        self.close()
