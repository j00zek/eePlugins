# coding: utf-8 
import os, os.path, sys, re
import xml.etree.cElementTree 
from streamlink.e2config import getE2config

from emukodi import xbmcE2

# xbmc/interfaces/python/xbmcmodule/PythonAddon.cpp
# (with a little help from xbmcswift)

def getaddonpath_params(item=None):
    addon_id = os.path.basename(os.path.dirname(sys.argv[0]))
    xbmcE2.log('xbmcaddon.getaddonpath_params(%s) = plugin_path/scripts_path/addons_path = %s, addon_id = %s' % (item, xbmcE2.addons_path, addon_id))
    if item in ('plugin_path', 'addons_path', 'scripts_path'): return xbmcE2.addons_path
    elif item=="addon_id": return addon_id
    elif item is None: return xbmcE2.addons_path, xbmcE2.addons_path, xbmcE2.addons_path, addon_id
                       
                       
class Addon:
    def __init__(self, id=None):
        xbmcE2.log('!!!!! xbmcaddon.Addon.__init__(%s)' % id)
        self.callingID = id
        xbmcE2.log(sys.argv[0])
        if id is not None:## requested from addons or scripts
            if id.startswith("script"):
                self.id=id
                self.path=getaddonpath_params("scripts_path")+"/"+str(self.callingID)
            elif id.startswith("plugin"):   
                self.id=getaddonpath_params("addon_id")
                self.path=getaddonpath_params("addons_path")+"/"+str(self.callingID)
            else:
                self.id=getaddonpath_params("addon_id")
                self.path=getaddonpath_params("addons_path")+"/"+str(self.callingID)                          
        else: #either requested from addons not scripts 
            self.id = getaddonpath_params("addon_id")
            self.path = getaddonpath_params("addons_path") + "/" + str(self.callingID)
        self.pluginSetingsSLPath = '/etc/streamlink/%s' % self.callingID.replace('plugin.video.', '')
        xbmcE2.log('\t self.id = %s, self.path = %s, self.callingID = %s, self.pluginSetingsSLPath = %s' % (self.id, self.path, self.callingID, self.pluginSetingsSLPath))

    def getLocalizedString(self, idx=" "):
        if 0:
            pass#print("In xbmcaddon idx =", idx)
            xfile = self.path + "_strings.xml"
            ftxt = open(xfile, "r").read() 
            n1 = ftxt.find(str(idx), 0)
            if n1 < 0:
                    xtxt = str(idx)
                    return xtxt
            n2 = ftxt.find(">", n1)
            n3 = ftxt.find("<", n2)      
            xtxt = ftxt[(n2+1):n3]
            pass#print("In xbmcaddon xtxt B=", xtxt)
            return str(xtxt)
        else:
            return str(idx)

    def getSettingSL(self, settingName):
        if os.path.exists("%s/%s" % (self.pluginSetingsSLPath, settingName)):
            return open("%s/%s" % (self.pluginSetingsSLPath, settingName), "r").read().strip()
        else:
            return ''
           
    def getSetting(self,id=None):
        if not id is None:
            if os.path.exists("%s/%s" % (self.pluginSetingsSLPath, id)):
                return self.getSettingSL(id)
            
        item = '"' + str(id) + '"'
        
        checkDirs = [os.path.join(xbmcE2.addons_path, self.callingID), '/media/hdd/.kodi/addons/%s' % self.callingID, '/usr/share/kodi/addons/%s' % self.callingID]
        xfile = ''
        for CurDir in checkDirs:
            if os.path.exists(os.path.join(CurDir,'resources', 'settings.xml')):
                xfile = os.path.join(CurDir,'resources', 'settings.xml')
                break
        if  xfile == '':
            xbmcE2.log('xbmcaddon.getSetting(%s) missing file: %s' % (id,xfile))
            return ''
        
        f = open(xfile, 'r').read()
        f = f.replace('\n', '').replace('\t', '').replace('<setting', '\n<setting') #usuniecie formatowania
        if item not in f:
            xbmcE2.log('xbmcaddon.getSetting(%s) missing in %s' % (id, xfile))
            return ""
        
        #testj00zka= self.openSettings()
        lines = []
        lines = f.splitlines()
        for line in lines:
            #print("In xbmcaddon-py line =", line)
            if str(item) in line:
                #print("In xbmcaddon-py line =", line)
                if 'type="folder"' in line:
                    if 'source="working_dir"' in line or 'source="auto"':
                        xtxt = xbmcE2.working_dir
                        #print('source=',xtxt)
                        return str(xtxt)
                    else:
                        n2 = line.find(" source=", 0)
                elif re.findall('<default>[^<]*', line):
                    retDefault =  re.findall('<default>[^<]*', line)[0].split('>')[1]
                    if 'type="boolean"' in line and retDefault == 'false':
                        retDefault = False
                    elif 'type="boolean"' in line and retDefault == 'true':
                        retDefault = True
                    return retDefault
                else:
                    n2 = line.find(" default", 0)
                    n3 = line.find('"', n2)
                    n4 = line.find('"', (n3+1))
                    xtxt = line[(n3+1):n4]
                    #print("In xbmcaddon-py line B=", line, 'xtxt=', xtxt)
                break

        ##print("In xbmcaddon xtxt B=", xtxt)
        if xtxt.startswith("getE2config('"):
            #xtxt = xtxt.split("'")[1]
            xtxt = getE2config(xtxt.split("'")[1])
        return str(xtxt)

    def getSetting2(self,id=None):
        xbmcE2.log('xbmcaddon.getSetting2(%s)\n' % id)
        item = id
        xfile = self.path + "/resources/settings.xml" 
        if not os.path.exists(xfile):
            xfile = '/usr/lib/python2.7/site-packages/emukodi/PluginsSettings/%s.xml' % self.callingID
        if not os.path.exists(xfile):
            return ''
        f = open(xfile, 'r').read()
        if item not in f:
            return ""

        lines = []
        lines = f.splitlines()
        for line in lines:
            if str(id) in line:
                n2 = line.find("default", 0)
                n3 = line.find('"', n2)
                n4 = line.find('"', (n3+1))
                xtxt = line[(n3+1):n4]
                break

        pass#print("In xbmcaddon xtxt B=", xtxt)
        return xtxt


    def setSettingSL(self, settingName = "", settingValue = ""):
        if settingName is None or settingName.strip() == "":
            return False
        elif settingValue is None:
            return False
        open("%s/%s" % (self.pluginSetingsSLPath, settingName), "w").write('%s' % settingValue)

    def setSetting(self, id = " ", value = " "):
        if value is None:
            return False
        elif os.path.exists(self.pluginSetingsSLPath):
            return self.setSettingSL(id,value)
        
        item = id
        xfile = '/usr/lib/python3.12/site-packages/emukodi/PluginsSettings/%s.xml' % self.callingID
        f = open(xfile, 'r').read()
        if item not in f:
            nline = '<setting id="' + item + '" type="text" default="' + str(value) + '" visible="false" />\n'
            n1 = f.find("<setting id", 0)
            s1 = f[:n1]
            s2 = f[n1:]
            fnew = s1 + nline + s2
            f2 = open('/tmp/temp.xml', 'w')
            f2.write(fnew)
            f2.close()
        else:
            f2 = open('/tmp/temp.xml', 'w')
            lines = []
            lines = f.splitlines()
            for line in lines:
                if str(id) in line:
                    n2 = line.find("default", 0)
                    n3 = line.find('"', n2)
                    n4 = line.find('"', (n3+1))
                    s = line[n2:(n4+1)]
                    s2 = 'default="' + str(value) + '"'
                    line = line.replace(s, s2)
                line = line + "\n"
                f2.write(line)
        f2.close()
        cmd = "mv -f '/tmp/temp.xml' " + xfile
        os.system(cmd)  
        return True
             
    # sometimes called with an arg, e.g veehd
    def openSettings(self, arg=None):
        #print(self.path)
        """get all settings."""
        try:
            settings_xml= os.path.join(self.path, "resources/settings.xml")
            #print("283",settings_xml)
            tree = xml.etree.cElementTree.parse(settings_xml)
            root = tree.getroot()
                
            i=0
            list=[]
            for setting in root.iter('setting'):
                #print(setting.tag)
                list.append((i,setting.attrib))##add dict for all settings in the line,i=line number
                i=i+1
                #print("In openSettings list =",list)
            return list  
        #print("*** openSettings ***")
        except:
            list=[]
            return list
                
    def getAddonInfo(self, item):
        xbmcE2.log('xbmcaddon.getAddonInfo(%s)\n' % item)
        item = item.lower()
        if item == "path":
            return self.path
        #print("In xbmcaddon item =", item)
        profile = '/hdd/.kodi/userdata/addon_data/' + str(self.id)
        if not os.path.exists(profile):
            cmd = "mkdir -p " + profile
            os.system(cmd)
        if item == "profile":
            return profile        

        xfile = self.path + "/addon.xml"
        #print("get_version xfile =", xfile)
        if os.path.exists(xfile):
            tree = xml.etree.cElementTree.parse(xfile)
            root = tree.getroot()
            version = str(root.get('version'))
            #print("get_version version =", version)
            author = str(root.get('provider-name'))
            name = str(root.get('name'))
            id = str(root.get('id'))
            if item == "version":
                return version
            elif item == "author":
                return author
            elif item == "name":
                return name
            elif item == "id":
                return id
        else:
            return "UNKNOWN ADDON"