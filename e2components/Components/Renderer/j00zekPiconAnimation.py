#######################################################################
#
#    Renderer for Enigma2
#    Coded by j00zek (c)2018-2020
#
#    Uszanuj moja prace i nie kasuj/zmieniaj informacji kto jest autorem renderera
#    Please respect my work and don't delete/change name of the renderer author
#
#    Nie zgadzam sie na wykorzystywanie tego skryptu w projektach platnych jak np. Graterlia!!!
#
#    Prosze NIE dystrybuowac tego skryptu w formie archwum zip, czy tar.gz
#    Zgadzam sie jedynie na dystrybucje z repozytorium opkg
#    
#    To use it do the following:
#       - download package of animated picons, for example from my opkg
#       - write them in the animatedPicons folder on mounted device or in /usr/share/enigma2/
#             NOTE:if you want to use any other folder, you need to specify it in widget definition. E.g. pixmaps="animatedPicons/Flara/"
#       - include J00zekPiconAnimation widget in the infobar skin definition.
#             E.g. <widget source="session.CurrentService" render="j00zekPiconAnimation" position="30,30" size="220,132" zPosition="5" transparent="1" alphatest="blend" />
#             NOTE:
#                   -  position="X,Y" should be the same like position of a picon in skin definition
#                   -  size="X,Y" should be the same like size of a picon in skin definition
#                   -  zPosition="Z" should be bigger than zPosition of a picon in skin definition, to display animation over the picon.
#
#             OTHER PARAMETERS:
#                   - pixmaps           : name of the directory, default 'animatedPicons'
#                   - pixalter          : name of the pic to display when pixmaps firectory not found
#                   - pixdelay          : delay between showing frames, minimum 40ms, default 50ms
#                   - lockpath="True"   : always use path defined in skin, default "False" - very usefull if skin author want to have many different animations
#                   - loop="True"       : run animation in a loop, default "False"
#                   - loopdelay         : delay between showing frames, minimum 40ms, default 5* pixdelay
#                   - initdelay         : delay before first loop, minimum 40ms, default 50ms
#                   - dontcache         : True|False switch to cache pics in memory, default False
#                   - chainid           : id of the animation in chain, default None
#                   - random            : True|False switch to cache pics in memory, default False
#
#    OPTIONAL animations control:
#       - to set speed put '.ctrl' file  in the pngs folder containing 'delay=TIME' where TIME is miliseconds to wait between frames
#       - to overwrite skin setting use config attributes from your own plugin or use UserSkin which has GUI to present them
#       - to disable user settings (see above) put lockpath="True" attribute in widget definition
#       - to randomize animations put all in the subfolders of main empy animations folder. If you want to disable any just put ".off" at the end of the folder name
#                 Example:
#                         create /usr/shareenigma2/animatedPicons/ EMPTY folder
#                         create /usr/shareenigma2/animatedPicons/Flara subfolder with animation png's
#                         create /usr/shareenigma2/animatedPicons/OldMovie subfolder with second animation png's
#
####################################################################### 
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.Renderer.Renderer import Renderer #ATV7.0,EGAMI10
from Components.config import config
from Components.Harddisk import harddiskmanager
from Components.Pixmap import Pixmap
from enigma import ePixmap, eTimer, iPlayableService
from random import randint
from Tools.Directories import resolveFilename
from Tools.LoadPixmap import LoadPixmap
import os

try:
    from Tools.Directories import SCOPE_CURRENT_SKIN
except Exception:
    from Tools.Directories import SCOPE_ACTIVE_SKIN as SCOPE_CURRENT_SKIN

DBG = False
try:
    if DBG: from Components.j00zekComponents import j00zekDEBUG
    def printDBG(myText = None, Append = True):
        if myText is None:
            return
        else:
            myText = str(myText)
            j00zekDEBUG(myText, Append, '/tmp/j00zekPiconAnimation.log')
    
except Exception: DBG = False 

searchPaths = ['/usr/share/enigma2/']

isGrabEnabled = False

chainsDict={}

def initPiconPaths():
    if DBG: printDBG('[j00zekPiconAnimation]:[initPiconPaths] >>>')
    for part in harddiskmanager.getMountedPartitions():
        addPiconPath(part.mountpoint)
    if os.path.exists("/proc/mounts"):
        with open("/proc/mounts", "r") as f:
            for line in f:
                if line.startswith('/dev/sd'):
                    mountpoint = line.split(' ')[1]
                    addPiconPath(mountpoint)

def addPiconPath(mountpoint):
    if DBG: printDBG('[j00zekPiconAnimation]:[addPiconPath] >>> mountpoint=' + mountpoint)
    if mountpoint == '/':
        return
    global searchPaths
    try:
        if mountpoint not in searchPaths:
            if DBG: printDBG('j00zekPiconAnimation]:[addPiconPath] mountpoint not in searchPaths')
            for pp in os.listdir(mountpoint):
                lpp = os.path.join(mountpoint, pp) + '/'
                if pp.find('picon') >= 0 and os.path.isdir(lpp): #any folder *picon*
                    for pf in os.listdir(lpp):
                        if pf.endswith('.png') and mountpoint not in searchPaths: #if containf *.png
                            if mountpoint.endswith('/'):
                                searchPaths.append(mountpoint)
                            else:
                                searchPaths.append(mountpoint + '/')
                            if DBG: printDBG('[j00zekPiconAnimation]:[addPiconPath] mountpoint appended to searchPaths')
                            break
                    else:
                        continue
                    break
    except Exception as e:
        if DBG: printDBG('[j00zekPiconAnimation]:[addPiconPath] Exception:' + str(e))

def onPartitionChange(why, part):
    if DBG: printDBG('[j00zekPiconAnimation]:[onPartitionChange] >>>')
    global searchPaths
    if why == 'add' and part.mountpoint not in searchPaths:
        addPiconPath(part.mountpoint)
    elif why == 'remove' and part.mountpoint in searchPaths:
        searchPaths.remove(part.mountpoint)

class j00zekPiconAnimation(Renderer):
    __module__ = __name__

    def __init__(self):
        Renderer.__init__(self)
        self.pixmaps = 'animatedPicons'
        self.pixalter = None
        self.animName = self.pixmaps
        self.initialPic = False
        self.initialDelay = 50
        self.delayBetweenFrames = 50
        self.delayBetweenLoops = self.delayBetweenFrames * 5
        self.doAnim = False
        self.doLockPath = False
        self.doInLoop = False
        self.inChain = None
        self.chainID = None
        self.animCounter = 0
        self.FramesCount = 0
        self.slideFrame = 0
        self.FramesList = []
        self.animationsFoldersList = []
        self.isSuspended = True
        self.dontcache = False
        self.random = False
        self.animTimer = eTimer()
        self.animTimer.callback.append(self.timerEvent)
        self.what = ['CHANGED_DEFAULT', 'CHANGED_ALL', 'CHANGED_CLEAR', 'CHANGED_SPECIFIC', 'CHANGED_POLL']
        self.whatDescr = ['# initial "pull" state ', '# really everything changed ',
                    '# we are expecting a real update soon. do not bother polling NOW, but clear data. ',
                    '# second tuple will specify what exactly changed ', '# a timer expired ']
        self.CH_SP_ev = ['evStart', 'evEnd', 'evTunedIn', 'evTuneFailed', 'evUpdatedEventInfo', 'evUpdatedInfo', 'evSeekableStatusChanged',
                        'evEOF', 'evSOF', 'evCuesheetChanged','evUpdatedRadioText', 'evUpdatedRtpText', 'evUpdatedRassSlidePic',
                        'evUpdatedRassInteractivePicMask', 'evVideoSizeChanged', 'evVideoFramerateChanged', 'evVideoProgressiveChanged',
                        'evBuffering', 'evStopped', 'evHBBTVInfo', 'evFccFailed', 'evUser']

    def applySkin(self, desktop, parent):
        if DBG: printDBG('[j00zekPiconAnimation]:[applySkin] >>>')
        #Load attribs
        attribs = []
        for attrib, value in self.skinAttributes:
            if attrib == 'pixmaps':
                self.pixmaps = value
                if DBG: printDBG('[j00zekPiconAnimation]:[applySkin] self.pixmaps=%s' % value)
            elif attrib == 'pixalter':
                self.pixalter = value
                if DBG: printDBG('[j00zekPiconAnimation]:[applySkin] self.pixalter=%s' % value)
            elif attrib == 'pixdelay':
                self.delayBetweenFrames = int(value)
                if self.delayBetweenFrames < 40: self.delayBetweenFrames = 40
                if DBG: printDBG('[j00zekPiconAnimation]:[applySkin] self.delayBetweenFrames=%s' % self.delayBetweenFrames)
            elif attrib == 'random':
                if value == 'True': self.random = True
                if DBG: printDBG('[j00zekPiconAnimation]:[applySkin] self.random=%s' % self.random)
            elif attrib == 'dontcache':
                if value == 'True': self.dontcache = True
                if DBG: printDBG('[j00zekPiconAnimation]:[applySkin] self.dontcache=%s' % self.dontcache)
            elif attrib == 'lockpath':
                if value == 'True': self.doLockPath = True
                if DBG: printDBG('[j00zekPiconAnimation]:[applySkin] self.doLockPath=%s' % self.doLockPath)
            elif attrib == 'loop':
                if value == 'True': self.doInLoop = True
                if DBG: printDBG('[j00zekPiconAnimation]:[applySkin] self.doInLoop=%s' % self.doInLoop)
            elif attrib == 'loopdelay':
                self.delayBetweenLoops = int(value)
                if self.delayBetweenLoops < 40: self.delayBetweenLoops = 40
                if DBG: printDBG('[j00zekPiconAnimation]:[applySkin] self.delayBetweenLoops=%s' % self.delayBetweenLoops)
            elif attrib == 'initdelay':
                self.initialDelay = int(value)
                if self.initialDelay < 40: self.initialDelay = 40
                if DBG: printDBG('[j00zekPiconAnimation]:[applySkin] self.delayBetweenLoops=%s' % self.delayBetweenLoops)
            elif attrib == 'chainid':
                if ',' in value:
                    value = value.split(',')
                    self.inChain = value[0]
                    self.chainID = value[1]
                    self.initialPic = True
                    global chainsDict
                    if chainsDict.get(self.inChain, None) is None:
                        chainsDict[self.inChain] = []
                    if not self.chainID in chainsDict[self.inChain]:
                        chainsDict[self.inChain].append(self.chainID)
                    if DBG: printDBG('[j00zekPiconAnimation]:[applySkin] chainsDict=%s' % str(chainsDict))
            else:
                attribs.append((attrib, value))
                if attrib not in ('unknown','size','position','zPosition','alphatest'):
                    if DBG: printDBG('[j00zekPiconAnimation]:[applySkin] unknown %s=%s' % (attrib,value))

        self.skinAttributes = attribs
        #Load animation into memory
        try:
            if self.doLockPath == False and os.path.exists(config.plugins.j00zekCC.PiconAnimation_UserPath.value):
                if DBG: printDBG('UserPath exists and self.doLockPath == False')
                self.loadPNGsAnim(config.plugins.j00zekCC.PiconAnimation_UserPath.value)
                self.loadPNGsSubFolders(config.plugins.j00zekCC.PiconAnimation_UserPath.value)
            elif self.pixmaps.startswith('/'):
                if DBG: printDBG("self.pixmaps starts with '/'")
                self.loadPNGsAnim(self.pixmaps)
            else:
                if DBG: printDBG('self.doLockPath == True or UserPath does not exist:')
                for path in searchPaths:
                    if self.loadPNGsAnim(os.path.join(path, self.pixmaps)) == True:
                        break
                self.loadPNGsSubFolders(os.path.join(path, self.pixmaps))
        except Exception as e:
            if DBG: printDBG('[j00zekPiconAnimation]:[applySkin] Exception %s' % str(e))
        return Renderer.applySkin(self, desktop, parent)

    GUI_WIDGET = ePixmap

    def postWidgetCreate(self, instance):
        if DBG: printDBG('[j00zekPiconAnimation]:[postWidgetCreate] >>>')
#self.changed((self.CHANGED_DEFAULT,))
        return

    def preWidgetRemove(self, instance):
        if DBG: printDBG('[j00zekPiconAnimation]:[preWidgetRemove] >>>')
        if not self.animTimer is None:
            self.animTimer.stop()
            self.animTimer.callback.remove(self.timerEvent)
            self.animTimer = None

    def connect(self, source):
        Renderer.connect(self, source)

    def doSuspend(self, suspended):
        if suspended:
                self.isSuspended = True
                #if DBG: printDBG('[j00zekPiconAnimation]:[doSuspend] >>> suspended=%s' % str(self.isSuspended))
                self.changed((self.CHANGED_CLEAR,))
        else:
                self.isSuspended = False
                #if DBG: printDBG('[j00zekPiconAnimation]:[doSuspend] >>> suspended=%s' % str(self.isSuspended))
                self.changed((self.CHANGED_DEFAULT,))
            
    def loadPNGsSubFolders(self, animPath):
        self.animName = os.path.basename(os.path.normpath(animPath))
        self.animationsFoldersList = []
        if len(self.FramesList) == 0 and os.path.exists(animPath):
            picsFolder = [f for f in os.listdir(animPath) if (os.path.isdir(os.path.join(animPath, f)) and not f.endswith(".off"))]
            for x in picsFolder:
                for f in os.listdir(os.path.join(animPath, x)):
                    if f.endswith(".png"):
                        self.animationsFoldersList.append(os.path.join(animPath, x))
                        if DBG: printDBG('[j00zekPiconAnimation]]:[loadPNGsSubFolders] found *.png in subfolder "%s"' % os.path.join(animPath, x))
                        break
                    
    def loadPNGsAnim(self, animPath):
        if animPath == self.pixmaps and not self.pixmaps.startswith('/'): return False
        if os.path.exists(animPath):
            self.pixmaps = animPath
            pngfiles = [f for f in os.listdir(self.pixmaps) if (os.path.isfile(os.path.join(self.pixmaps, f)) and f.endswith(".png"))]
            pngfiles.sort()
            self.FramesList = []
            self.doAnim = False
            for x in pngfiles:
                if self.dontcache:
                    if DBG: printDBG('[j00zekPiconAnimation]:[loadPNGsAnim] appended image %s' % os.path.join(self.pixmaps, x))
                    self.FramesList.append(os.path.join(self.pixmaps, x))
                else:
                    if DBG: printDBG('[j00zekPiconAnimation]:[loadPNGsAnim] pixmap loaded from %s' % os.path.join(self.pixmaps, x))
                    self.FramesList.append(LoadPixmap(os.path.join(self.pixmaps, x)))
            if len(self.FramesList) > 0:
                self.FramesCount = len(self.FramesList)
                self.doAnim = True
                if os.path.exists(os.path.join(animPath,'.ctrl')):
                    with open(os.path.join(animPath,'.ctrl')) as cf:
                        try:
                            myDelay=cf.readline().strip()
                            cf.close()
                            self.delayBetweenFrames = int(myDelay.split('=')[1])
                            if self.delayBetweenFrames < 40: self.delayBetweenFrames = 40
                        except Exception as e:
                            if DBG: printDBG('[j00zekPiconAnimation]:[loadPNGsAnim] Exception "%s" loading .ctrl' % str(e))
                if DBG: printDBG('[j00zekPiconAnimation]:[loadPNGsAnim] Loaded from path=%s, pics=%s, pixdelay=%s' % (self.pixmaps,self.FramesCount,self.delayBetweenFrames))
                return True
            else:
                if DBG: printDBG('[j00zekPiconAnimation]:[loadPNGsAnim] No *.png in given path "%s".' % (animPath))
        elif not self.pixalter is None and self.pixalter.endswith('.png'):
            if self.pixalter.startswith('/'):
                if DBG: printDBG('[j00zekPiconAnimation]:[loadPNGsAnim] read pixalter %s' % self.pixalter)
                self.FramesList = []
                self.FramesList.append(LoadPixmap(self.pixalter))
                self.FramesCount = len(self.FramesList)
                return True
            else:
                for path in searchPaths:
                    fullpath = os.path.join(path, self.pixalter)
                    if os.path.exists(fullpath):
                        if DBG: printDBG('[j00zekPiconAnimation]:[loadPNGsAnim] read pixalter %s' % fullpath)
                        self.FramesList = []
                        self.FramesList.append(LoadPixmap(fullpath))
                        self.FramesCount = len(self.FramesList)
                        return True
        else:
            if DBG: printDBG('[j00zekPiconAnimation]:[loadPNGsAnim] Path "%s" does NOT exist.' % (animPath))
        return False
         
      
    def changed(self, what):
        if self.instance:
            self.instance.setScale(1) 
            if DBG: 
                try:
                    if what[0] == self.CHANGED_SPECIFIC:
                        printDBG('[j00zekPiconAnimation]:[changed] > what(%s,%s)=%s:%s, self.doAnim=%s' % (what[0],
                                                                                                        what[1],
                                                                                                        self.what[int(what[0])],
                                                                                                        self.CH_SP_ev[int(what[1])],
                                                                                                        self.doAnim)
                                                                                                        )
                    else: 
                        printDBG('[j00zekPiconAnimation]:[changed] > what(%s)=%s %s, self.doAnim=%s' % (what[0],
                                                                                                        self.what[int(what[0])],
                                                                                                        self.whatDescr[int(what[0])],
                                                                                                        self.doAnim)
                                                                                                        )
                except Exception as e:
                    printDBG('[j00zekPiconAnimation]:[changed]  exception %s' % str(e))
            if self.FramesCount == 0:
                self.instance.hide()
            elif what[0] == self.CHANGED_CLEAR: #we are expecting a real update soon. do not bother polling NOW, but clear data
                if not self.animTimer is None: self.animTimer.stop()
                self.instance.hide()
                self.slideFrame = 0
                self.doAnim = True
            elif what[0] == self.CHANGED_SPECIFIC and what[1] not in (iPlayableService.evStart,): #Do nothing for some CHANGED_SPECIFIC codes
                    if DBG: printDBG('CHANGED_SPECIFIC is not iPlayableService.evStart')
                    pass
            elif self.FramesCount == 1: #static alternate picon
                self.instance.show()
                self.instance.setPixmap(self.FramesList[0])
            elif self.doAnim == True and self.isSuspended == False:
                self.doAnim = False
                self.slideFrame = 0
                self.instance.show()
                self.animTimer.start(self.initialDelay, True)

    def doGrabPICs(self):
        try:
            if isGrabEnabled:
                if not os.path.exists('/tmp/PreviewAnim'):
                    os.mkdir('/tmp/PreviewAnim')
                if not os.path.exists('/tmp/PreviewAnim/.ctrl'):
                    open('/tmp/PreviewAnim/.ctrl', 'w').write('%sDelay=%s\n' % (self.animName,self.delayBetweenFrames))
                if self.slideFrame < 10:
                    myChar = '0'
                else:
                    myChar = ''
                #os.system('grab -dqp /tmp/PreviewAnim/%s-%s_%s%s.png' % (self.animName, self.delayBetweenFrames, myChar, self.slideFrame))
                os.system('grab -dqj 85 /tmp/PreviewAnim/%s-%s_%s%s.jpg' % (self.animName, self.delayBetweenFrames, myChar, self.slideFrame))
        except Exception:
            pass
    
    def timerEvent(self):
        if DBG: printDBG('[j00zekPiconAnimation]:[timerEvent] >>> self.slideFrame=%s' % self.slideFrame)
        global isGrabEnabled, chainsDict
        self.animTimer.stop()
        
        self.doGrabPICs()
        
        if self.slideFrame < self.FramesCount:
            if not self.inChain is None:
                if self.chainID != chainsDict.get(self.inChain, ['',])[0]:
                    if self.initialPic == True:
                        self.initialPic = False
                        if self.dontcache:
                            self.instance.setPixmap(LoadPixmap(self.FramesList[0]))
                        else:
                            self.instance.setPixmap(self.FramesList[0])
                    self.animTimer.start(self.delayBetweenFrames, True)
                    return
            if self.dontcache:
                self.instance.setPixmap(LoadPixmap(self.FramesList[self.slideFrame]))
            else:
                self.instance.setPixmap(self.FramesList[self.slideFrame])
            self.slideFrame += 1
            if self.slideFrame >= self.FramesCount:
                self.slideFrame = self.FramesCount
                if isGrabEnabled:
                    isGrabEnabled = False
                    
                if self.doInLoop == True:
                    self.slideFrame = 0
                    if self.inChain is None:
                        if DBG: printDBG('\t\t\t loop animation')
                    else:
                        if self.chainID == chainsDict.get(self.inChain, ['',])[0]:
                            if self.random:
                                tmpID = randint(1, len(chainsDict[self.inChain])-1)
                                tmpchainID = chainsDict[self.inChain][tmpID]
                                chainsDict[self.inChain].pop(tmpID)
                                chainsDict[self.inChain].insert(0, tmpchainID)
                            else:
                                chainsDict[self.inChain].pop(0)
                                chainsDict[self.inChain].append(self.chainID)
                        if DBG: printDBG('[j00zekPiconAnimation]:[applySkin] chainsDict=%s' % str(chainsDict))
                    self.animTimer.start(self.delayBetweenLoops, True)
                else:
                    if DBG: printDBG('\t\t\t Finished stop animation')
                    self.instance.hide()
                    self.doAnim = True
                    self.animCounter = self.animCounter + 1
                    if len(self.animationsFoldersList) > 1: #loading next animation to load after screen unhide
                        if DBG: printDBG('[j00zekPiconAnimation]:[timerEvent] change animation')
                        self.loadPNGsAnim(self.animationsFoldersList[randint(0, len(self.animationsFoldersList)-1)])
            else:
                self.animTimer.start(self.delayBetweenFrames, True)
        #elif self.slideFrame == self.FramesCount: #Note last frame does NOT exists
        #    if self.doInLoop == True:
        #        self.slideFrame = 0
        #        self.animTimer.start(self.delayBetweenLoops, True)
        #        if DBG: printDBG('\t\t\t loop animation')
        #    else:
        #        if DBG: printDBG('\t\t\t Finished stop animation')
        #        self.instance.hide()
        #        self.doAnim = True
        #        self.animCounter = self.animCounter + 1
        #        if len(self.animationsFoldersList) > 1:
        #            if DBG: printDBG('[j00zekPiconAnimation]:[timerEvent] change animation')
        #            self.loadPNGsAnim(self.animationsFoldersList[randint(0, len(self.animationsFoldersList)-1)])
        #if DBG: j00zekDEBUG('[j00zekPiconAnimation]:[timerEvent] <<<')

harddiskmanager.on_partition_list_change.append(onPartitionChange)
initPiconPaths()
