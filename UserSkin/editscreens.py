# -*- coding: utf-8 -*-

# UserSkin, editscreens part
#
# maintainer: j00zek @2015
#
# Uszanuj czyj¹ pracê i NIE przyw³aszczaj sobie autorstwa!

#This plugin is free software, you are allowed to
#modify it (if you keep the license),
#but you are not allowed to distribute/publish
#it without source code (this version and your modifications).
#This means you also have to distribute
#source code of your modifications.
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3

from Plugins.Extensions.UserSkin.debug import printDEBUG
from Plugins.Extensions.UserSkin.inits import *

from Components.ActionMap import ActionMap
from Components.config import *
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from enigma import ePicLoad, eLabel, gFont, getDesktop, ePoint, eSize
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from skin import parseColor,parseFont
from Tools.Directories import *
from Tools.LoadPixmap import LoadPixmap
from Tools import Notifications
#system imports
from os import listdir, remove, rename, system, path, symlink, chdir, mkdir
#import re
import xml.etree.cElementTree as ET
#Translations part
from Plugins.Extensions.UserSkin.translate import _

class UserSkinEditScreens(Screen):
    skin = """
  <screen name="UserSkinEditScreens" position="0,0" size="1280,720" title="UserSkin EditScreens" backgroundColor="transparent" flags="wfNoBorder">
    <eLabel position="0,0" size="1280,720" zPosition="-15" backgroundColor="#20000000" />
    <widget source="Title" render="Label" position="70,47" size="1100,43" font="Regular;35" foregroundColor="#00ffffff" backgroundColor="#004e4e4e" transparent="1" />
    <!-- List -->
    <eLabel position="55,100" size="475,400" zPosition="-10" backgroundColor="#20606060" />
    <widget source="menu" render="Listbox" position="65,110" size="455,385" scrollbarMode="showOnDemand" transparent="1">
      <convert type="TemplatedMultiContent">
                                {"template":
                                        [
                                                MultiContentEntryPixmapAlphaTest(pos = (2, 2), size = (54, 54), png = 3),
                                                MultiContentEntryText(pos = (60, 2), size = (650, 24), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 1), # name
                                                MultiContentEntryText(pos = (65, 26),size = (600, 30), font=1, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 2), # info
                                        ],
                                        "fonts": [gFont("Regular", 22),gFont("Regular", 14)],
                                        "itemHeight": 56
                                }
                        </convert>
    </widget>
    <!-- Preview on Screen -->
    <eLabel position="535,100" size="695,400" zPosition="-10" backgroundColor="#20606060" />
    <!-- Below graphs TV area, size has to be 16/8 -->
    <widget name="ScreenPixMapPictureInScale" position="545,110" zPosition="-5" size="675,379" alphatest="blend" />
    <widget name="WigetPixMapPictureInScale" position="545,110" zPosition="1" size="675,379" alphatest="blend" />
    <widget name="WigetPixMapPictureInScale1" position="545,110" zPosition="-1" size="1,1" alphatest="on" />
    <widget name="WigetPixMapPictureInScale2" position="545,110" zPosition="-2" size="1,1" alphatest="on" />
    
    <!-- Preview -->
    <eLabel position="1035,505" size="195,115" zPosition="-10" backgroundColor="#20606060" />
    <widget name="SkinPicture" position="1040,510" size="185,105" backgroundColor="#004e4e4e" />

    <!-- Widget Details -->
    <eLabel position="55,505" size="585,115" zPosition="-10" backgroundColor="#20606060" />
    <widget name="widgetDetailsTXT" position="65,515" size="565,95" font="Regular;15" transparent="1"/>
    
    <!-- Preview text -->
    <eLabel position="645,505" size="385,115" zPosition="-10" backgroundColor="#20606060" />
    <widget name="PreviewFont" position="655,515" size="365,95" valign="center" font="Regular;20" transparent="1" foregroundColor="#00ffffff" />
    
    <!-- Preview pixmap -->
    <widget name="PixMapPreview" position="925,515" size="95,95" alphatest="on" />
    
    <!-- BUTTONS -->
    <eLabel position=" 55,625" size="290,55" zPosition="-10" backgroundColor="#20b81c46" />
    <eLabel position="350,625" size="290,55" zPosition="-10" backgroundColor="#20009f3c" />
    <eLabel position="645,625" size="290,55" zPosition="-10" backgroundColor="#209ca81b" />
    <eLabel position="940,625" size="290,55" zPosition="-10" backgroundColor="#202673ec" />
    <widget source="key_red" render="Label" position="70,640" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#20b81c46" transparent="1" />
    <widget source="key_green" render="Label" position="365,640" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#20009f3c" transparent="1" />
    <widget source="key_yellow" render="Label" position="655,640" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#20009f3c" transparent="1" />
    <widget source="key_blue" render="Label" position="950,640" zPosition="1" size="260,25" valign="center" halign="left" font="Regular;20" transparent="1" foregroundColor="#00ffffff" />
  </screen>
"""

    #init some variables
    EditedScreen = False
    myScreenName = None
    currentScreenID = 0
    NumberOfScreens = 1
    NumberOfChilds = 1
    
    blockActions = False
    
    doNothing = 0
    doDelete = 1
    doExport = 2
    doSave = 3
    doSaveAs = 4
    doImport = 5
    resizeFont = 6
    moveHorizontally = 7
    moveVertically = 8
    resizeHorizontally = 9
    resizeVertically = 10
    PermanentPreview1 = 11
    PermanentPreview2 = 12
    AdvancedAttribEdit = 13
    Preview2Background = 14
    
    WidgetPreviewX = 0
    WidgetPreviewY = 0
    WidgetPreviewScale = 0
    
    currAction = doNothing
    
    def __init__(self, session, ScreenFile = ''):
        Screen.__init__(self, session)
        self.session = session
        #valid ScreenFile is mandatory
        if ScreenFile == '':
            self.close()
            return
        elif not path.exists(ScreenFile):
            self.close()
            return

        self.ScreenFile = ScreenFile
        try:
            self.root = ET.parse(self.ScreenFile).getroot()
            self.myScreenName = self.root.find('screen').attrib['name']
            self.NumberOfScreens = len(self.root.findall('screen'))
            self.NumberOfChilds = len(self.root.findall('*'))
        except:
            printDEBUG("%s -Is NOT proper xml file - END!!!" % self.ScreenFile)
            self.close()
            return
        printDEBUG("%s has been loaded successfully. :)" % self.ScreenFile)
        if self.NumberOfChilds != self.NumberOfScreens:
            iindex = 0
            for child in self.root.findall('*'):
                if child.tag == 'screen':
                    break
                iindex+= 1
            self.currentScreenID = iindex
          
        if self.myScreenName == None:
            myTitle=_("UserSkin %s - EditScreens") %  UserSkinInfo
        else:
            if self.NumberOfScreens == 1:
                myTitle=_("UserSkin %s - Edit %s screen") %  (UserSkinInfo,self.myScreenName)
            else:
                myTitle=_("UserSkin %s - Edit %s screen (1/%d)") %  (UserSkinInfo,self.myScreenName,self.NumberOfScreens)
            
        self.setTitle(myTitle)
        
        self["key_red"] = StaticText(_("Exit"))
        self["key_green"] = StaticText("")
        if self.NumberOfScreens == 1:
            self["key_yellow"] = StaticText("")
        else:
            self["key_yellow"] = StaticText(_("Switch screen"))
        self['key_blue'] = StaticText(_('Actions'))
        self["PreviewFont"] = Label()
        self["widgetDetailsTXT"] = Label()
        
        self["PixMapPreview"] = Pixmap()
        self["SkinPicture"] = Pixmap()
        self["ScreenPixMapPictureInScale"] = Pixmap()
        self["WigetPixMapPictureInScale"] = Pixmap()
        self["WigetPixMapPictureInScale1"] = Pixmap()
        self["WigetPixMapPictureInScale2"] = Pixmap()
        
        menu_list = []
        self["menu"] = List(menu_list)
        
        self["shortcuts"] = ActionMap(["UserSkinEditActions"],
        {
            "ok": self.keyOK,
            "cancel": self.keyExit,
            "red": self.keyExit,
            "green": self.keyGreen,
            "yellow": self.keyYellow,
            "blue": self.keyBlue,
            "keyup": self.channelup,
            "keydown": self.channeldown,
        }, -2)
        
        self.skin_base_dir = SkinPath
        #self.screen_dir = "allScreens"
        self.allScreens_dir = "allScreens"
        #check if we have preview files
        isPreview=0
        for xpreview in listdir(SkinPath + "allPreviews/"):
            if len(xpreview) > 4 and  xpreview[-4:] == ".png":
                isPreview += 1
            if isPreview >= 2:
                break

        self.elabel_png = LoadPixmap(cached=True, path= self.getPicFileNameWithPath("elabel.png"))
        self.epixmap_png = LoadPixmap(cached=True, path= self.getPicFileNameWithPath("epixmap.png"))
        self.label_png = LoadPixmap(cached=True, path= self.getPicFileNameWithPath("label.png"))
        self.pixmap_png = LoadPixmap(cached=True, path= self.getPicFileNameWithPath("pixmap.png"))
        self.widget_png = LoadPixmap(cached=True, path= self.getPicFileNameWithPath("widget.png"))
        
        
        if not self.selectionChanged in self["menu"].onSelectionChanged:
            self["menu"].onSelectionChanged.append(self.selectionChanged)
        
        self.onLayoutFinish.append(self.LayoutFinished)

    def getPicFileNameWithPath(self, filename):
        if path.isfile("%sUserSkinpics/%s" % (SkinPath,filename) ):
            return "%sUserSkinpics/%s" % (SkinPath,filename)
        else:
            return "%spic/edit/%s" % (PluginPath,filename)
        
        
    def LayoutFinished(self):
        self.currentHeight= getDesktop(0).size().height()
        self.currentWidth = getDesktop(0).size().width()

        # first we initiate the TV preview screen
        self["SkinPicture"].hide()
        fileName = self.ScreenFile.replace('allScreens/','allPreviews/preview_')[:-4]
        if path.exists(fileName + '.png'):
            fileName = fileName + '.png'
        elif path.exists(fileName + '.jpg'):
            fileName = fileName + '.jpg'
        else:
            fileName = self.getPicFileNameWithPath('tvpreview.png')
            
        if path.exists(fileName):
            self["ScreenPixMapPictureInScale"].instance.setScale(1)
            self["ScreenPixMapPictureInScale"].instance.setPixmap(LoadPixmap(path=fileName))
            self["ScreenPixMapPictureInScale"].show()
        else:
            print("no preview file")
        self.WidgetPreviewX = self["ScreenPixMapPictureInScale"].instance.position().x()
        self.WidgetPreviewY = self["ScreenPixMapPictureInScale"].instance.position().y()
        self.WidgetPreviewScale = ( float(self["ScreenPixMapPictureInScale"].instance.size().width()) / float(getDesktop(0).size().width()) )

        self["widgetDetailsTXT"].setText('')
        self["PreviewFont"].setText('')
        self["PixMapPreview"].hide()
        
        self.createWidgetsList()
      
    def createWidgetsList(self):
        menu_list = []
        f_list = []
        for child in self.root[self.currentScreenID].findall('*'):
            childTitle = ''
            childDescr = ' '
            childTYPE = child.tag
            if childTYPE.lower() == 'widget':
                pic = self.widget_png
                if 'render' in child.attrib:
                  childTitle = _(child.attrib['render'])
                if 'name' in child.attrib and child.attrib['name'] == 'list':
                    if 'serviceNameFont' in child.attrib and 'serviceNumberFont' in child.attrib:
                        childTitle = _('ChannelList')
                    else:
                        childTitle = _('List')
            elif childTYPE.lower() == 'elabel':
                pic = self.elabel_png
                childDescr += _('Paint a square. ')
            elif childTYPE.lower() == 'epixmap':
                pic = self.epixmap_png
                childDescr += _('Display a picture. ')
                
            elif childTYPE.lower() == 'label':
                pic = self.label_png
                
            elif childTYPE.lower() == 'pixmap':
                pic = self.pixmap_png
                
            else:
                pic = None
            if 'text' in child.attrib:
                childDescr += _('Display %s. ') % child.attrib['text']
            if 'render' in child.attrib and 'source' in child.attrib:
                childDescr += _('Controlled through %s. ') % child.attrib['source']
            if 'name' in child.attrib:
                childDescr += _('Controlled by script or plugin. ')
            f_list.append((child, "%s %s" % (childTYPE, childTitle), childDescr, pic))
        if len(f_list) == 0:
            f_list.append(("dummy", _("No widgets found"), '', None))
            self.blockActions=True
        if self.blockActions == True:
            self['key_blue'].setText('')
        for entry in f_list:
            menu_list.append((entry[0], entry[1], entry[2], entry[3]))
        #print menu_list
        try:
            self["menu"].UpdateList(menu_list)
        except:
            print("Update asser error :(") #workarround to have it working on openpliPC
            myIndex=self["menu"].getIndex() #as an effect, index is cleared so we need to store it first
            self["menu"].setList(menu_list)
            self["menu"].setIndex(myIndex) #and restore
        self.selectionChanged()

#### Selection changed - display widgets

    def selectionChanged(self):
        #print("> self.selectionChanged")
        myIndex=self["menu"].getIndex()
        # widget details
        self["widgetDetailsTXT"].setText( ET.tostring(self.root[self.currentScreenID][myIndex]) )
        self.setPixMapPreview(myIndex)
        self.setPreviewFont(myIndex)
        self.setWigetPixMapPictureInScale(myIndex)

    def setWigetPixMapPictureInScale(self, myIndex, myWidget = "WigetPixMapPictureInScale", myWidgetFile = 'widgetmarker.png' ):
        if not 'position' in self.root[self.currentScreenID][myIndex].attrib:
            self[myWidget].hide()
            return
        elif not 'size' in self.root[self.currentScreenID][myIndex].attrib:
            self[myWidget].hide()
            return
        elif not 'pixmap' in self.root[self.currentScreenID][myIndex].attrib:
            if path.exists("%sUserSkinpics/%s" % (SkinPath, myWidgetFile) ):
                pic = "%sUserSkinpics/%s" % (SkinPath, myWidgetFile) 
            else:
                pic = "%spic/edit/%s" % (PluginPath, myWidgetFile)
        else:
            pic = resolveFilename(SCOPE_SKIN, self.root[self.currentScreenID][myIndex].attrib['pixmap'] )
        #position="x,y" size="x,y"
        printDEBUG("setWigetPixMapPictureInScale, pic=%s" % pic)
        
        WidgetPosition=self.root[self.currentScreenID][myIndex].attrib['position'].split(',')
        WidgetSize=self.root[self.currentScreenID][myIndex].attrib['size'].split(',')
        if WidgetPosition[0] == 'center':
            WidgetPosition[0] = self.currentWidth/2 - int(WidgetSize[0])/2
        if WidgetPosition[1] == 'center':
            WidgetPosition[1] = self.currentHeight/2 - int(WidgetSize[1])/2
        if path.exists(pic):
            self[myWidget].instance.resize(eSize(int(int(WidgetSize[0])*self.WidgetPreviewScale) , int(int(WidgetSize[1])*self.WidgetPreviewScale) ))
            self[myWidget].instance.setScale(1)
            self[myWidget].instance.setPixmapFromFile(pic)
            self[myWidget].show()
            
            self[myWidget].instance.move(ePoint(int(int(WidgetPosition[0])*self.WidgetPreviewScale) + self.WidgetPreviewX , \
                                                                                    int(int(WidgetPosition[1])*self.WidgetPreviewScale + self.WidgetPreviewY)))
        else:
            self[myWidget].hide()
            
    def setPixMapPreview(self, myIndex):
        if not 'pixmap' in self.root[self.currentScreenID][myIndex].attrib:
            self["PixMapPreview"].hide()
            return
        pic = self.root[self.currentScreenID][myIndex].attrib['pixmap']
        if path.exists(resolveFilename(SCOPE_SKIN, pic)):
            self["PixMapPreview"].instance.setScale(1)
            self["PixMapPreview"].instance.setPixmapFromFile(resolveFilename(SCOPE_SKIN, pic))
            self["PixMapPreview"].show()
        else:
            self["PixMapPreview"].hide()
            
    def setPreviewFont(self, myIndex):
        if not 'font' in self.root[self.currentScreenID][myIndex].attrib:
            self["PreviewFont"].setText('')
            return
        #### Now we know we have font, so we can preview it :)
        myfont = self.root[self.currentScreenID][myIndex].attrib['font']
        #print myfont
        try:
            self["PreviewFont"].instance.setFont(gFont(myfont.split(';')[0], int(myfont.split(';')[1])))
        except Exception:
            printDEBUG("Missing font '%s' definition in skin.xml" % self.root[self.currentScreenID][myIndex].attrib['font'])
        try:
            if 'text' in self.root[self.currentScreenID][myIndex].attrib:
                self["PreviewFont"].setText('%s' % self.root[self.currentScreenID][myIndex].attrib['text'])
            else:
                self["PreviewFont"].setText(_('Sample Text'))
        except Exception as e:
            printDEBUG("Exception occured: %s" % str(e))
        if 'foregroundColor' in self.root[self.currentScreenID][myIndex].attrib:
            try:
                self["PreviewFont"].instance.setForegroundColor(parseColor(self.root[self.currentScreenID][myIndex].attrib['foregroundColor']))            
            except:
                printDEBUG("Missing color '%s' definition in skin.xml" % self.root[self.currentScreenID][myIndex].attrib['foregroundColor'])
        else:
            self["PreviewFont"].instance.setForegroundColor(parseColor("#00ffffff"))            
        if 'backgroundColor' in self.root[self.currentScreenID][myIndex].attrib:
            try:
                self["PreviewFont"].instance.setBackgroundColor(parseColor(self.root[self.currentScreenID][myIndex].attrib['backgroundColor']))            
            except:
                printDEBUG("Missing color '%s' definition in skin.xml" % self.root[self.currentScreenID][myIndex].attrib['backgroundColor'])
  
#### KEYS ####

#CHANNEL UP
    def channelup(self):
        self.EditedScreen = True
        myIndex=self["menu"].getIndex()
        if self.currAction == self.resizeFont and 'font' in self.root[self.currentScreenID][myIndex].attrib:
            myfont = self.root[self.currentScreenID][myIndex].attrib['font']
            mySize = int(myfont.split(';')[1]) + 1
            if mySize > 80:
                mySize = 80
            self.root[self.currentScreenID][myIndex].set('font',myfont.split(';')[0] + ';%d' % mySize)
        elif self.currAction == self.moveHorizontally and 'position' in self.root[self.currentScreenID][myIndex].attrib:
            myAttrib = self.root[self.currentScreenID][myIndex].attrib['position']
            try:
                myX= int(myAttrib.split(',')[0]) + 1
            except: #center
                myX=getDesktop(0).size().width()/2
                
            myY= int(myAttrib.split(',')[1])
            if myX > 1920:
                myX = 1920
            self.root[self.currentScreenID][myIndex].set('position','%d,%s' % (myX,str(myY)))
        elif self.currAction == self.moveVertically and 'position' in self.root[self.currentScreenID][myIndex].attrib:
            myAttrib = self.root[self.currentScreenID][myIndex].attrib['position']
            myX=myAttrib.split(',')[0]
            
            try:
                myY=int(myAttrib.split(',')[1]) + 1
            except: #center
                myY=getDesktop(0).size().height()/2
            if myY > 720:
                myY = 720
            self.root[self.currentScreenID][myIndex].set('position','%s,%d' % (str(myX),myY))
        elif self.currAction == self.resizeVertically and 'size' in self.root[self.currentScreenID][myIndex].attrib:
            myAttrib = self.root[self.currentScreenID][myIndex].attrib['size']
            myX=int(myAttrib.split(',')[0])
            myY=int(myAttrib.split(',')[1]) + 1
            if myY > 720:
                myY = 720
            self.root[self.currentScreenID][myIndex].set('size','%d,%d' % (myX,myY))
        elif self.currAction == self.resizeHorizontally and 'size' in self.root[self.currentScreenID][myIndex].attrib:
            myAttrib = self.root[self.currentScreenID][myIndex].attrib['size']
            myX=int(myAttrib.split(',')[0]) + 1
            myY=int(myAttrib.split(',')[1])
            if myX > 1920:
                myX = 1920
            self.root[self.currentScreenID][myIndex].set('size','%d,%d' % (myX,myY))
          
        self.selectionChanged()
        
#CHANNEL DOWN
    def channeldown(self):
        myIndex=self["menu"].getIndex()
        self.EditedScreen = True
        if self.currAction == self.resizeFont and 'font' in self.root[self.currentScreenID][myIndex].attrib:
            myfont = self.root[self.currentScreenID][myIndex].attrib['font']
            mySize = int(myfont.split(';')[1]) - 1
            if mySize < 8:
                mySize = 8
            self.root[self.currentScreenID][myIndex].set('font',myfont.split(';')[0] + ';%d' % mySize)
        elif self.currAction == self.moveHorizontally and 'position' in self.root[self.currentScreenID][myIndex].attrib:
            myAttrib = self.root[self.currentScreenID][myIndex].attrib['position']
            myX= int(myAttrib.split(',')[0]) - 1
            myY= int(myAttrib.split(',')[1])
            if myX < 0:
                myX = 0
            self.root[self.currentScreenID][myIndex].set('position','%d,%d' % (myX,myY))
        elif self.currAction == self.moveVertically and 'position' in self.root[self.currentScreenID][myIndex].attrib:
            myAttrib = self.root[self.currentScreenID][myIndex].attrib['position']
            myX=int(myAttrib.split(',')[0])
            myY=int(myAttrib.split(',')[1]) - 1
            if myY < 0:
                myY = 0
            self.root[self.currentScreenID][myIndex].set('position','%d,%d' % (myX,myY))
        elif self.currAction == self.resizeVertically and 'size' in self.root[self.currentScreenID][myIndex].attrib:
            myAttrib = self.root[self.currentScreenID][myIndex].attrib['size']
            myX=int(myAttrib.split(',')[0])
            myY=int(myAttrib.split(',')[1]) - 1
            if myY < 0:
                myY = 0
            self.root[self.currentScreenID][myIndex].set('size','%d,%d' % (myX,myY))
        elif self.currAction == self.resizeHorizontally and 'size' in self.root[self.currentScreenID][myIndex].attrib:
            myAttrib = self.root[self.currentScreenID][myIndex].attrib['size']
            myX=int(myAttrib.split(',')[0]) - 1
            myY=int(myAttrib.split(',')[1])
            if myX < 0:
                myX = 0
            self.root[self.currentScreenID][myIndex].set('size','%d,%d' % (myX,myY))

        self.selectionChanged()
        
# Yellow
    def keyYellow(self):
        if self.NumberOfScreens >= 1:
            self.currentScreenID += 1
            if self.currentScreenID >= self.NumberOfScreens:
                self.currentScreenID = 0
            while self.root[self.currentScreenID].tag != 'screen':
                self.currentScreenID += 1
                
            try:
                self.myScreenName = self.root[self.currentScreenID].attrib['name']
            except:
                self.myScreenName = _('UnknownName')
            myTitle=_("UserSkin %s - Edit %s screen (1/%d)") %  (UserSkinInfo,self.myScreenName,self.NumberOfScreens)
            print(myTitle)
            
            self.setTitle(myTitle)
            self["menu"].setIndex(0)
        #try:
            #self["Title"]=StaticText(myTitle)
        #except:
        #    pass
            self.createWidgetsList()

        if self.NumberOfChilds != self.NumberOfScreens:
            iindex = 0
            for child in self.root.findall('*'):
                if child.tag == screen:
                    break
                iindex+= 1
            self.currentScreenID = iindex
            
# RED, CANCEL
    def keyExit(self): 
        if self.EditedScreen == True:
            self.session.openWithCallback(self.keyExitRet, ChoiceBox, title = _("Exit options"), list = [(_("Exit without saving"),"exit"),(_("Save as & Exit"),"saveas"),(_("Save & Exit"),"save"),])
        else:
            self.close()

    def keyExitRet(self, ret):
        if ret:
            if ret[1] == 'exit':
                self.close()
            if ret[1] == 'save':
                self.keyExitRetSave()
            if ret[1] == 'saveas':
                self.keyExitRetSaveAs()
        else:
            self.close()
            
    def keyExitRetSaveAs(self):
        from Screens.VirtualKeyBoard import VirtualKeyBoard
        self.session.openWithCallback(self.keyExitRetSaveAsHasName, VirtualKeyBoard, title=(_("Enter filename")), text = path.basename(self.ScreenFile.replace('.xml','_new.xml')))
        
    def keyExitRetSaveAsHasName(self, callback = None):
        if callback is not None:
            self.ScreenFile = self.ScreenFile.replace(path.basename(self.ScreenFile), callback)
            if not self.ScreenFile.endswith('.xml'):
                self.ScreenFile += '.xml'
            self.keyExitRetSave()
        self.close()
        
    def keyExitRetSave(self):
        printDEBUG("Writing %s" % self.ScreenFile)
        with open(self.ScreenFile, "w") as f:
            f.write(ET.tostring(self.root, encoding='utf-8'))
        self.close()

# Blue
    def keyBlue(self):
        if self.blockActions == False:
            keyBlueActionsList=[
                (_("No action"), self.doNothing),
                (_("Move left/right"), self.moveHorizontally),
                (_("Move Up/Down"), self.moveVertically),
                (_("Resize left/right"), self.resizeHorizontally),
                (_("Resize Up/Down"), self.resizeVertically),
                (_("Change font size"), self.resizeFont),
                (_("Advanced attributes edit"), self.AdvancedAttribEdit),
                ("---", self.doNothing),
                (_("Delete"), self.doDelete),
                (_("Export"), self.doExport),
                (_("Import"), self.doImport),
                ("---", self.doNothing),
                (_("Permanent preview 1"), self.PermanentPreview1),
                (_("Permanent preview 2"), self.PermanentPreview2),
                (_("Set standard background"), self.Preview2Background),
                ("---", self.doNothing),
                (_("Save"), self.doSave),
                (_("Save as"), self.doSaveAs),
            ]
            self.session.openWithCallback(self.keyBlueEnd, ChoiceBox, title = _("Select Action:"), list = keyBlueActionsList)
        return

    def keyBlueEnd(self, ret):
        if ret:
            self.currAction = ret[1]
        else:
            self.currAction = self.doNothing
            
        if self.currAction == self.doNothing:
            self['key_green'].setText('')
        #saving
        elif self.currAction == self.doSaveAs:
            self.keyExitRetSaveAs()
            return
        elif self.currAction == self.doSave:
            self.keyExitRetSave()
            return
        elif self.currAction == self.PermanentPreview1:
            self.setWigetPixMapPictureInScale(myIndex = self["menu"].getIndex(), myWidget = "WigetPixMapPictureInScale1", myWidgetFile = 'permanentwidget1.png' )
            return
        elif self.currAction == self.PermanentPreview2:
            self.setWigetPixMapPictureInScale(myIndex = self["menu"].getIndex(), myWidget = "WigetPixMapPictureInScale2", myWidgetFile = 'permanentwidget2.png' )
            return
        elif self.currAction == self.Preview2Background:
            fileName = self.ScreenFile.replace('allScreens/','allPreviews/preview_').replace('.xml','.png')
            if path.exists(fileName):
                self["SkinPicture"].instance.setScale(1)
                self["SkinPicture"].instance.setPixmapFromFile(fileName)
                self["SkinPicture"].show()
            if path.isfile( self.getPicFileNameWithPath('tvpreview.png') ):
                self["ScreenPixMapPictureInScale"].instance.setScale(1)
                self["ScreenPixMapPictureInScale"].instance.setPixmap(LoadPixmap(path=self.getPicFileNameWithPath('tvpreview.png')) )
                self["ScreenPixMapPictureInScale"].show()
            return
        #manipulation
        elif self.currAction == self.doDelete:
            self['key_green'].setText(_('Delete'))
        elif self.currAction == self.doExport:
            self['key_green'].setText(_('Export'))
        elif self.currAction == self.doImport:
            self['key_green'].setText(_('Import'))
        elif self.currAction == self.resizeFont:
            self['key_green'].setText(_('Change font size'))
        elif self.currAction == self.moveHorizontally:
            self['key_green'].setText(_('Move left/right'))
        elif self.currAction == self.moveVertically:
            self['key_green'].setText(_('Move Up/Down'))
        elif self.currAction == self.resizeHorizontally:
            self['key_green'].setText(_('Resize left/right'))
        elif self.currAction == self.resizeVertically:
            self['key_green'].setText(_('Resize Up/Down'))
        elif self.currAction == self.AdvancedAttribEdit:
            self['key_green'].setText(_('Advanced attributes edit'))
        return

# OK
    def keyOK(self):
        pass

#### Green
    def keyGreen(self):
        print('self.keyGreen')
        myIndex=self["menu"].getIndex()
        if self.currAction == self.doNothing:
            return
        elif self.currAction == self.doDelete:
            self.doDeleteAction(myIndex)
        elif self.currAction == self.doExport:
            self.doExportAction(myIndex)
        elif self.currAction == self.doImport:
            self.doImportFunc()
        elif self.currAction == self.AdvancedAttribEdit:
            self.doAttribEditFunc()
        self.EditedScreen = True

#### Green subprocedures

    def doDeleteAction(self, what):
        childAttributes=''
        for key, value in self.root[0][what].items():
            childAttributes += key + '=' + value + ' '
        printDEBUG('doDeleteAction <%s %s>\n' % (self.root[0][what].tag,childAttributes))
        self.root[0].remove(self.root[0][what])
            
        self.createWidgetsList()
        
    def doExportAction(self, what):
      
        printDEBUG('doExportAction')
        
        def SaveWidget(WidgetFile = None):
            if WidgetFile is not None:
                if not WidgetFile.endswith('.xml'):
                    WidgetFile += '.xml'
                WidgetPathName = path.dirname(self.ScreenFile).replace('allScreens','allWidgets')
                if not path.exists(WidgetPathName):
                    mkdir(WidgetPathName)
                printDEBUG("Writing %s/%s" % (WidgetPathName,WidgetFile))
                with open("%s/%s" % (WidgetPathName, WidgetFile), "w") as f:
                    f.write(ET.tostring(self.root[0][self["menu"].getIndex()]))

        myText=self.root[0][what].tag
        if 'name' in self.root[0][what].attrib:
            myText += '_' + self.root[0][what].attrib['name']
        if 'text' in self.root[0][what].attrib:
            myText += '_' + self.root[0][what].attrib['text']
        if 'render' in self.root[0][what].attrib:
            myText += '_' + self.root[0][what].attrib['render']
        if 'source' in self.root[0][what].attrib:
            myText += '_' + self.root[0][what].attrib['source']

        from Screens.VirtualKeyBoard import VirtualKeyBoard
        self.session.openWithCallback(SaveWidget, VirtualKeyBoard, title=(_("Enter filename")), text = myText.replace('.','-'))
        
    def doImportFunc(self):
        widgetlist = []
        for f in sorted(listdir(self.skin_base_dir + "allWidgets/"), key=str.lower):
            if f.endswith('.xml') and f.startswith('widget_'):
                friendly_name = f.replace("widget_", "")
                friendly_name = friendly_name.replace(".xml", "")
                friendly_name = friendly_name.replace("_", " ")
                widgetlist.append((friendly_name, f))
        if len(widgetlist) > 0:
            self.session.openWithCallback(self.doImportFuncRet, ChoiceBox, title = _("Select Widget:"), list = widgetlist)
            
    def doImportFuncRet(self, ret):
        if ret:
            if path.exists(self.skin_base_dir + "allWidgets/"+ret[1]):
                widgetRoot = ET.parse(self.skin_base_dir + "allWidgets/"+ret[1]).getroot()
                self.root[self.currentScreenID].insert(self["menu"].getIndex(),widgetRoot)
            self.createWidgetsList()

    def doAttribEditFunc(self):
        attriblist = []
        myIndex=self["menu"].getIndex()
        for name, value in self.root[self.currentScreenID][myIndex].attrib.items():
            attriblist.append((name,value))
        if len(attriblist) > 0:
            self.session.openWithCallback(self.doAttribEditFuncRet, ChoiceBox, title = _("Select attribute to edit:"), list = attriblist)

    def doAttribEditFuncRet(self, ret):
        if ret:
            self.AttributeToEdit = ret[0]
            self.OldAttributeValue = ret[1]
            from Screens.VirtualKeyBoard import VirtualKeyBoard
            self.session.openWithCallback(self.doAttribEditedFuncRet, VirtualKeyBoard, title=(_("Advanced %s attribute edit")), text = self.OldAttributeValue)

    def doAttribEditedFuncRet(self, ret):
        if ret:
            self.NewAttributeValue = ret
            self.session.openWithCallback(self.doAttribEditedFuncFinal, MessageBox, _("Are you sure you want to change: '%s' to '%s'?") % (self.OldAttributeValue,self.NewAttributeValue), MessageBox.TYPE_YESNO, default = False)
            
    def doAttribEditedFuncFinal(self, ret):
        if ret is None or ret is False:
            return
        else:
            myIndex=self["menu"].getIndex()
            self.root[self.currentScreenID][myIndex].set(self.AttributeToEdit,self.NewAttributeValue)
            self.selectionChanged()
