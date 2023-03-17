# standard Picon.py modified by @j00zek to support any picon folder name and animations
# the name can be defined in xml by putting attrib picontype="<foldername>"
# e.g. picontype="zzpicon"
# new attrib implemented doAnimationanimation
#       doAnimationanimation="blink,<showTime>,<hideTime>"

from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3

import os, re, sys, unicodedata

PyMajorVersion = sys.version_info.major

if PyMajorVersion >= 3:
    import unicodedata
    import six
    

from Components.Renderer.Renderer import Renderer #ATV7.0,EGAMI10
from enigma import ePixmap, eTimer #, ePicLoad
from Tools.Alternatives import GetWithAlternative
from Tools.Directories import pathExists, SCOPE_SKIN_IMAGE, resolveFilename
try:
    from Tools.Directories import SCOPE_CURRENT_SKIN
except Exception:
    from Tools.Directories import SCOPE_ACTIVE_SKIN as SCOPE_CURRENT_SKIN


from Components.Harddisk import harddiskmanager
from ServiceReference import ServiceReference
from Components.config import config
from Components.j00zekComponents import isImageType, isINETworking

searchPaths = ['/usr/share/enigma2/']

lastPiconsDict = {}
#piconType = 'picon'

##### write log in /tmp folder #####
DBG = False
try:
    from Components.j00zekComponents import j00zekDEBUG
except Exception:
    DBG = False
#####

isVTI = isImageType('vti')

def initPiconPaths():
    for part in harddiskmanager.getMountedPartitions():
        if DBG: j00zekDEBUG('[j00zekPicons]:[initPiconPaths] MountedPartitions:' + part.mountpoint)
        addPiconPath(part.mountpoint)
    if pathExists("/proc/mounts"):
        with open("/proc/mounts", "r") as f:
            for line in f:
                if line.startswith('/dev/sd'):
                    mountpoint = line.split(' ')[1]
                    if DBG: j00zekDEBUG('[j00zekPicons]:[initPiconPaths] mounts:' + mountpoint)
                    addPiconPath(mountpoint)

def addPiconPath(mountpoint):
    if DBG: j00zekDEBUG('[j00zekPicons] mountpoint=' + mountpoint)
    if mountpoint == '/':
        return
    global searchPaths
    try:
        if config.plugins.j00zekCC.NoPiconsOnHDD.value and mountpoint in ['/hdd','/media/hdd']:
            print('Excluding /hdd, /media/hdd from picons searchPaths')
            return
        elif mountpoint not in searchPaths:
            if DBG: j00zekDEBUG('[j00zekPicons] mountpoint not in searchPaths')
            for pp in os.listdir(mountpoint):
                lpp = os.path.join(mountpoint, pp) + '/'
                if pp.find('picon') >= 0 and os.path.isdir(lpp): #any folder *picon*
                    for pf in os.listdir(lpp):
                        if pf.endswith('.png') and mountpoint not in searchPaths: #if containf *.png
                            if mountpoint.endswith('/'):
                                searchPaths.append(mountpoint)
                            else:
                                searchPaths.append(mountpoint + '/')
                            if DBG: j00zekDEBUG('[j00zekPicons] mountpoint appended to searchPaths')
                            break
                    else:
                        continue
                    break
    except Exception as e:
        if DBG: j00zekDEBUG('[j00zekPicons] Exception:' + str(e))

def onPartitionChange(why, part):
    if DBG: j00zekDEBUG('[j00zekPicons] onPartitionChange>>>')
    global searchPaths
    if why == 'add' and part.mountpoint not in searchPaths:
        addPiconPath(part.mountpoint)
    elif why == 'remove' and part.mountpoint in searchPaths:
        searchPaths.remove(part.mountpoint)

def findPicon(sName, selfPiconType, serviceName):
    if sName is None or sName == '':
        return None
    pngname = None
    findPiconTypeName='%s%s' % (selfPiconType,serviceName)
    if findPiconTypeName in lastPiconsDict:
        pngname = lastPiconsDict[findPiconTypeName]
        if pathExists(pngname):
            if DBG: j00zekDEBUG('[j00zekPicons:findPicon] found in lastPiconsDict[%s] = %s' % (findPiconTypeName,pngname) )
        else:
            pngname = None
            if DBG: j00zekDEBUG('[j00zekPicons:findPicon] cleaning faulty record lastPiconsDict[%s]' % findPiconTypeName )
            del lastPiconsDict[findPiconTypeName] 
    if pngname is None:
        for path in searchPaths:
            sPath = path + selfPiconType + '/'
            if DBG: j00zekDEBUG('[j00zekPicons:findPicon] searching for %s%s.[png|gif]' % (sPath,sName) )
            if pathExists(sPath + sName + '.png'):
                pngname = sPath + sName + '.png'
                lastPiconsDict[findPiconTypeName] = pngname
                if DBG: j00zekDEBUG('[j00zekPicons:findPicon] lastPiconsDict[%s] = %s' % (findPiconTypeName, pngname) )
                break
            elif pathExists(sPath + sName + '.gif'):
                pngname = sPath + sName + '.gif'
                lastPiconsDict[findPiconTypeName] = pngname
                if DBG: j00zekDEBUG('[j00zekPicons:findPicon] lastPiconsDict[%s] = %s' % (findPiconTypeName, pngname) )
                break
    return pngname

def getPiconName(serviceName, selfPiconType):
  
    def getName(serName, iptvStream = False):
        gname = ServiceReference(serName).getServiceName().lower()
        if DBG: j00zekDEBUG('[j00zekPicons:getPiconName:getName] "%s" translates to "%s"' % (serName,gname))
        if iptvStream:
            gname = gname.replace(' fhd', ' hd').replace(' uhd', ' hd') #iptv streams names correction
        if PyMajorVersion >= 3:
            gname = six.ensure_str(unicodedata.normalize('NFKD', gname).encode('ASCII', 'ignore'))
        else:
            gname = unicodedata.normalize('NFKD', unicode(gname, 'utf_8', errors='ignore')).encode('ASCII', 'ignore')
        gname = re.sub('[^a-z0-9]', '', gname.replace('&', 'and').replace('+', 'plus').replace('*', 'star').replace(' hevc', ''))
        if DBG: j00zekDEBUG('[j00zekPicons:getPiconName:getName] gname modified "%s"' % gname)
        return gname
      
    if DBG: j00zekDEBUG('[j00zekPicons:getPiconName] >>>')
    name = None
    sname = None
    pngname = None
    
    if selfPiconType == 'piconProv':
        if DBG: j00zekDEBUG('[j00zekPicons:getPiconName] looking for piconProv')
        pngname = findPicon(serviceName.upper(), selfPiconType, serviceName)
    elif selfPiconType == 'piconSat':
        if DBG: j00zekDEBUG('[j00zekPicons:getPiconName] looking for piconSat')
        pngname = findPicon(serviceName.upper().replace('.', '').replace('\xc2\xb0', ''), selfPiconType, serviceName)
    elif selfPiconType == 'MoonPhase':
        if DBG: j00zekDEBUG('[j00zekPicons:getPiconName] looking for MoonPhase')
        pngname = findPicon(serviceName.upper(), selfPiconType, serviceName)
    else:
        if DBG: j00zekDEBUG('[j00zekPicons:getPiconName] selfPiconType = %s' % selfPiconType)
    if not pngname:
        name = 'unknown'
        fields = GetWithAlternative(serviceName)
        if fields:
            fields = fields.split(':', 10)[:10]
            if len(fields) >= 10:
                sname = '_'.join(fields)
                pngname = findPicon(sname, selfPiconType, serviceName)
                if not pngname and not fields[6].endswith("0000"):
                    #remove "sub-network" from namespace
                    fields[6] = fields[6][:-4] + "0000"
                    pngname = findPicon('_'.join(fields), selfPiconType, serviceName)
                if not pngname and fields[0] != '1':
                    #fallback to 1 for other reftypes
                    fields[0] = '1'
                    pngname = findPicon('_'.join(fields), selfPiconType, serviceName)
                if not pngname and fields[2] != '1':
                    #fallback to 1 for services with different service types
                    fields[2] = '1'
                    pngname = findPicon('_'.join(fields), selfPiconType, serviceName)
                if pngname and isVTI and os.path.islink(pngname): #to delete incorrect references
                    name = getName(serviceName)
                    cname = os.path.abspath(pngname)
                    cname = os.path.realpath(cname)
                    cname = os.path.basename(cname)
                    cname = os.path.splitext(cname)[0]
                    if cname != name:
                        if DBG: j00zekDEBUG('[j00zekPicons:getPiconName] %s != %s, deleting' % (cname,name))
                        try:
                            os.remove(pngname)
                            pngname = None
                        except Exception:
                            pass
    if not pngname:
        if DBG: j00zekDEBUG('[j00zekPicons:getPiconName] pngname not found by sname')
        fields = sname.split('_', 6)
        isChanged = False
        isStream = False
        if len(fields) > 2 and fields[2] != '2' and fields[2] != '1':
            fields[2] = '1'
            isChanged = True
        if len(fields) > 0 and (fields[0] == '4097' or fields[0] == '5001' or fields[0] == '5002'):
            fields[0] = '1'
            isChanged = True
            isStream = True
        if len(fields) >= 6:
            currSID = fields[4]
            currTR = fields[5]
        else:
            currSID = ''
            currTR = ''
        if isChanged == True:
            pngname = findPicon('_'.join(fields), selfPiconType, serviceName)
        if not pngname:
            if DBG: j00zekDEBUG('[j00zekPicons:getPiconName] pngname not found by reference, trying by service name')
            name = getName(serviceName, isStream)
            if len(name) > 0:
                pngname = findPicon(name, selfPiconType, serviceName)
                if pngname and isVTI and not '1_' in pngname:
                    try:
                        os.symlink(pngname, '%s/%s.png' % (os.path.dirname(pngname), sname) )
                    except Exception as e:
                        if DBG:  j00zekDEBUG('[j00zekPicons:getPiconName] Exception %s' % str(e))
                if not pngname:
                    if name.endswith('hd'):
                        pngname = findPicon(name[:-2].strip(), selfPiconType, serviceName)
                    elif name.endswith('hevc'):
                        pngname = findPicon(name[:-4], selfPiconType, serviceName)
                    else:
                        pngname = findPicon(name, selfPiconType, serviceName + 'hd')
            if not pngname:
                if DBG: j00zekDEBUG('[j00zekPicons:getPiconName] service name not found in lamedb, trying provided name')
                pngname = findPicon(serviceName, selfPiconType, serviceName)
                if not pngname:
                    pngname = findPicon(serviceName.upper(), selfPiconType, serviceName)
                    if not pngname:
                        pngname = findPicon(serviceName.lower(), selfPiconType, serviceName)
    if DBG:
        j00zekDEBUG('[j00zekPicons:getPiconName] serviceName=%s, picon=%s, %s, piconFile=%s, selfPiconType=%s' %(str(serviceName),
                                                                sname, name, str(pngname), selfPiconType) )
    return pngname


class j00zekPicons(Renderer):

    def __init__(self):
        Renderer.__init__(self)
        #self.PicLoad = ePicLoad()
        #self.PicLoad.PictureData.get().append(self.updatePicon)
        self.piconsize = (0, 0)
        self.pngname = ''
        self.piconType = 'picon'
        self.GifsPath = 'animatedGIFpicons'
        self.ShowDefault = True
        self.GIFsupport = False
        self.isVisible = True
        self.animationType = None
        self.animTimer = None
        return

    def addPath(self, value):
        if DBG: j00zekDEBUG('[j00zekPicons:addPath] %s' % value)
        global searchPaths
        if not value.endswith('/'):
            value += '/'
        if value not in searchPaths:
            searchPaths.append(value)

    def applySkin(self, desktop, parent):
        attribs = self.skinAttributes[:]
        for attrib, value in self.skinAttributes:
            if attrib == 'path':
                self.addPath(value)
                attribs.remove((attrib, value))
            elif attrib == 'size':
                self.piconsize = value
            elif attrib == 'picontype':
                self.piconType = value
                attribs.remove((attrib, value))
            elif attrib == 'showdefaultpic':
                if value in ('False','no'): self.ShowDefault = False
                attribs.remove((attrib, value))
            elif attrib == 'gifsupport':
                if value in ('True','yes'): self.GIFsupport = True
                attribs.remove((attrib, value))
            elif attrib == 'doAnimation':
                try:
                    animVals = value.split(',') # doAnimationanimation="<'blink'|>,<fadeInTime>,<showTime>,<fadeOutTime>,<hideTime>"
                    self.animationType = animVals[0]
                    
                    self.animTimer = eTimer()
                    if self.animationType == 'blink': #doAnimationanimation="blink,<showTime>,<hideTime>"
                        self.animTimer.callback.append(self.doBlink)
                        self.showTime = int(animVals[1])
                        self.hideTime = int(animVals[2])
                    else:                    
                        self.fadeInTime = int(animVals[1])
                        self.showTime = int(animVals[2])
                        self.fadeOutTime = int(animVals[3])
                        self.hideTime = int(animVals[4])

                    self.animTimerInitCall = False
                    attribs.remove((attrib, value))
                except Exception as e:
                    self.animationType = None
                    if DBG: j00zekDEBUG('[j00zekPicons:applySkin] Exception=%s' % str(e))

        self.skinAttributes = attribs
        if DBG: j00zekDEBUG('[j00zekPicons:applySkin] self.piconType=%s, self.ShowDefault=%s' % (self.piconType,self.ShowDefault))
        return Renderer.applySkin(self, desktop, parent)

    GUI_WIDGET = ePixmap

    def postWidgetCreate(self, instance):
        self.changed((self.CHANGED_DEFAULT,))

    def preWidgetRemove(self, instance):
        if DBG: j00zekDEBUG('[j00zekPicons]:[preWidgetRemove] >>>')
        if not self.animTimer is None:
            self.animTimer.stop()
            self.animTimer.callback.clear()
            self.animTimer = None

    def changed(self, what):
        if not self.animTimer is None:
            self.animTimer.stop()
        if self.instance:
            pngname = None
            gifname = None
            try:
                if what[0] == self.CHANGED_CLEAR: #we are expecting a real update soon. do not bother polling NOW, but clear data
                    pass
                else:
                    if self.source.text is not None and self.source.text != '':
                        if self.GIFsupport == True: gifname = getPiconName(self.source.text, self.GifsPath)
                        pngname = getPiconName(self.source.text, self.piconType)
                        if DBG: j00zekDEBUG('[j00zekPicons]:[changed(%s)] gifname=%s, pngname=%s' %(self.source.text, gifname,pngname))
                    if pngname is None and self.ShowDefault == True:
                        pngname = findPicon('picon_default', self.piconType, 'picon_default')
                        if pngname is None and pathExists(resolveFilename(SCOPE_CURRENT_SKIN, 'picon_default.png')):
                            pngname = resolveFilename(SCOPE_CURRENT_SKIN, 'picon_default.png')
                    if pngname is None:
                        self.updatePicon() #  hide it
                    else:
                        if self.pngname != pngname:
                            self.updatePicon(pngname) # show picon
                        self.initAnim()
                        
                    if DBG: j00zekDEBUG('[j00zekPicons]:[changed] piconType=' + self.piconType + ', pngname=' + str(pngname))
            except Exception as e:
                j00zekDEBUG('[j00zekPicons]:[changed] Exception:' + str(e))

    def doSuspend(self, suspended):
        if DBG: j00zekDEBUG('[j00zekPicons]:[doSuspend] >>> suspended=%s' % suspended)
        if suspended:
            self.changed((self.CHANGED_CLEAR,))
        else:
            self.changed((self.CHANGED_DEFAULT,))
            
    def updatePicon(self, pngname = None):
        if pngname:
            self.instance.setScale(1)
            self.instance.setPixmapFromFile(pngname)
            self.instance.show()
            self.isVisible = True
        else:
            self.instance.hide()
            self.isVisible = False
        self.pngname = pngname
        
    def initAnim(self):
        if not self.animTimer is None:
            self.animTimerInitCall = True
            self.animTimer.start(100, True)
        
    def doBlink(self):
        if not self.animTimer is None:
            if DBG: j00zekDEBUG('[j00zekPicons]:[doBlink] >>> self.animTimerInitCall=%s, self.isVisible=%s' % (self.animTimerInitCall, self.isVisible))
            self.animTimer.stop()
            if self.isVisible:
                if self.animTimerInitCall:
                    self.animTimerInitCall = False
                else:
                    self.instance.hide()
                    self.isVisible = False
                self.animTimer.start(self.hideTime, True)
            else:
                self.instance.show()
                self.isVisible = True
                self.animTimer.start(self.showTime, True)

harddiskmanager.on_partition_list_change.append(onPartitionChange)
initPiconPaths()
