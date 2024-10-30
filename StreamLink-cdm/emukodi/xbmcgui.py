#import xbmcinit

import os, sys
import urllib
import emukodi.xbmcplugin as xbmcplugin
from emukodi import xbmcE2

def getCurrentWindowId():
    """Returns the id for the current 'active' window as an integer."""
    return 0

def getCurrentWindowDialogId():
    """Returns the id for the current 'active' dialog as an integer."""
    return 0

# xbmc/guilib/GUIListItem.h
ICON_OVERLAY_NONE = 0
ICON_OVERLAY_RAR = 1
ICON_OVERLAY_ZIP = 2
ICON_OVERLAY_LOCKED = 3
ICON_OVERLAY_HAS_TRAINER = 4
ICON_OVERLAY_TRAINED = 5
ICON_OVERLAY_UNWATCHED = 6
ICON_OVERLAY_WATCHED = 7
ICON_OVERLAY_HD = 8

NOTIFICATION_INFO    = "info"
NOTIFICATION_WARNING = "warning"
NOTIFICATION_ERROR   = "error" 


#https://github.com/romanvm/Kodistubs/blob/master/xbmcgui.py

class mock(object):
    '''
    A shapeless self-referring class that never raises
    an AttributeError, is always callable and will always
    evaluate as a string, int, float, bool, or container.
    '''
    # http://www.rafekettler.com/magicmethods.html
    def __new__(cls, *args): return object.__new__(cls)
    def __init__(self, *args): return None
    def __getattr__(self, name): return self
    def __call__(self, *args, **kwargs): return self
    def __int__(self): return 0
    def __float__(self): return 0
    def __str__(self): return '0'
    def __nonzero__(self): return False
    def __getitem__(self, key): return self
    def __setitem__(self, key,value): pass
    def __delitem__(self, key): pass
    def __len__(self): return 3
    def __iter__(self): return iter([self,self,self])
    def __mro_entries__(self, *args): return ()

#DialogProgress = mock()

Window = \
WindowDialog = \
WindowXML = \
WindowXMLDialog = mock()

Window.getResolution = lambda:5 # NTSC 16:9 (720x480)
Window.getWidth = lambda:720
Window.getHeight = lambda:480

Control = \
ControlButton = \
ControlCheckMark = \
ControlFadeLabel = \
ControlGroup = \
ControlImage = \
ControlList = \
ControlProgress = \
ControlRadioButton = mock()
#ControlTextBox = mock()     
#ControlLabel =

def Log(text):
              file = open("/tmp/xbmclog.txt", "a")
              text = text + "\n"
#              file.write(text)
              file.close()    
                       
# xbmc/interfaces/python/xbmcmodule/listitem.cpp
class ListItemX:
#def ListItem(name, iconImage, thumbnailImage):
#    def __init__(self, name, iconImage, thumbnailImage, path):

        def __init__(self, label=" ", label2=" ", iconImage=None, thumbnailImage="DefaultFolder.png", path="path"):
              
              self.__dict__['label'] = label
              self.__dict__['label2'] = label2
              self.__dict__['iconImage'] = iconImage
              self.__dict__['thumbnailImage'] = thumbnailImage
              self.__dict__['path'] = path
#              if os.path.exists("/etc/debugxb"):
##              try:
              
              
              pass#print("ListItem label =", label)
#                      Log("Blabel =%sthumbnailImage =%s" % (label, thumbnailImage))
              pass#print("ListItem label2 =", label2)
#                      Log("Clabel =%sthumbnailImage =%s" % (label, thumbnailImage))
              pass#print("ListItem iconImage =", iconImage)
#                      Log("Dlabel =%sthumbnailImage =%s" % (label, thumbnailImage))
              pass#print("ListItem thumbnailImage =", thumbnailImage)
#                      Log("Elabel =%sthumbnailImage =%s" % (label, thumbnailImage))
              pass#print("ListItem path =", path)
#                      Log("F label =%sthumbnailImage =%s" % (label, thumbnailImage))
##              except:    
##                      pass
              if thumbnailImage is None:
                      thumbnailImage = "DefaultFolder.png"

              if (".jpg" not in thumbnailImage) and (".png" not in thumbnailImage):
                      thumbnailImage = "DefaultFolder.png"
              
              if thumbnailImage is not None:
                      thumbnailImage = thumbnailImage.replace(" ", "-")
                      thumbnailImage = thumbnailImage.replace("&", "AxNxD")
                      thumbnailImage = thumbnailImage.replace("=", "ExQ")
              if label is not None:
                      label = label.replace(" ", "-")
                      label = label.replace("&", "AxNxD")
                      label = label.replace("=", "ExQ")
              if path is not None:
                      if '|' in path:
                          path,headers = path.split('|')
#                      path = path.replace(" ", "-")
                      path = path.replace("&", "AxNxD")
                      path = path.replace("=", "ExQ")
#              pass#print("path =", path)
#              pass#print("label =", label)
              i = 0
              col = ""
              while i < 4:
                     n1 = path.find("[COLOR", 0)
                     if n1 > -1:
                            n2 = path.find("]", n1)
                            col = path[n1:(n2+1)]
                            path = path.replace(col, "")
                            i = i+1
                     else:
                            i = i+1
                            continue 
              path = path.replace("[/COLOR]", "")
              path = path.replace("[B]", "")                
              path = path.replace("[/B]", "")
              path = path.replace(">", "")
                                                    
              i = 0
              col = ""
              while i < 4:
                     n1 = label.find("[COLOR", 0)
                     if n1 > -1:
                            n2 = label.find("]", n1)
                            col = label[n1:(n2+1)]
                            label = label.replace(col, "")
                            i = i+1
                     else:
                            i = i+1
                            continue 
              label = label.replace("[/COLOR]", "")
              label = label.replace("[B]", "")                
              label = label.replace("[/B]", "")
              label = label.replace(">", "")               
#              pass#print("path B=", path)
#              pass#print("label B=", label)
#              if "plugin://" in path:
              path = path.replace("plugin://", "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/plugins/")
              path = path.replace("?", "default.py?")  
              if label is None:
                      label = "Video"                                          
              if (path != "path"):
                      data = "name=" + str(label) + "&url=" + str(path) + "&thumbnailImage=" + str(thumbnailImage) + "&iconlImage=" + str(iconImage)
              else:
                      data = "name=" + str(label) + "&thumbnailImage=" + str(thumbnailImage) + "&iconImage=" + str(iconImage)
              i = 0
              col = ""

              data = data.replace("[/COLOR]", "")
              data = data.replace("[B]", "")                
              data = data.replace("[/B]", "")
              data = data.replace("\n", "")
              if os.path.exists("/etc/debugxb"):
                  try:
                      pass#print("In xbmcgui Kodi data =", data)
                      pass#print("<<<")
                  except:        
                      pass
#              file = open("/tmp/data.txt", "a")
#              file.write(data)
#              file.close()
              self.data = data
              return
              
class ListItem:
    def __init__(self, label=None, label2=None, iconImage=None, thumbnailImage=None, path=None):
        self.data = {}
        self.data['label'] = label
        self.data['label2'] = label2
        self.data['iconImage'] = iconImage
        self.data['thumbnailImage'] = thumbnailImage
        self.data['path'] = path
        self.data['type'] = 'VIDEO'
        self.data['streams'] = []
        return

    def getLabel(self):
        """Returns the listitem label."""
        return self.data['label']

    def getLabel2(self):
        """Returns the listitem's second label."""
        return self.data['label2']

    def setLabel(self, label):
        """Sets the listitem's label."""
        self.data['label'] = label

    def setLabel2(self, label2):
        """Sets the listitem's second label."""
        self.data['label2'] = label2

    def setIconImage(self, icon):
        """Sets the listitem's icon image."""
        self.data['iconImage'] = icon

    def setThumbnailImage(self, thumb):
        """Sets the listitem's thumbnail image."""
        self.data['thumbnailImage'] = thumb

    def select(self, selected):
        """Sets the listitem's selected status."""
        pass

    def isSelected(self):
        """Returns the listitem's selected status."""
        return False

    def setInfo(self, type, infoLabels):
        """Sets the listitem's infoLabels."""
        self.data['type'] = type
        self.data.update(infoLabels)

    def setMimeType(self, mimetype: str) -> None:
        """
        Sets the listitem's mimetype if known.

        :param mimetype: string or unicode - mimetype

        If known prehand, this can (but does not have to) avoid HEAD requests
        being sent to HTTP servers to figure out file type.
        """
        pass
        
    def setContentLookup(self, enable: bool) -> None:
        """
        Enable or disable content lookup for item.

        If disabled, HEAD requests to e.g determine mime type will not be sent.

        :param enable: bool to enable content lookup

        @python_v16 New function added.
        """
        pass

    def setSubtitles(self, subs):
            pass

    def setProperty(self, key, value):
        """Sets a listitem property, similar to an infolabel."""
        self.data[key] = value

    def getProperty(self, key):
        """Returns a listitem property as a string, similar to an infolabel."""
        return (self.data[key] if key in self.data else None)

    def addContextMenuItems(self, items, replaceItems=None):
        """Adds item to the context menu for media lists."""
        pass

    def setPath(self, path):
        """Sets the listitem's path."""
        self.data['path'] = path

    def addStreamInfo(self, type, values):
        """Add a stream with details."""
        pass

    def setArt(self, posters):
        pass

    def addStreamInfo(self, video, duration):
        pass
                


# xbmc/interfaces/python/xbmcmodule/dialog.cpp
class Dialog:
    def notification(self, heading, message, icon=None, time=None, sound=None):
        print("Dialog().Notification: %s\n" % [heading, message, icon])
        
    def ok(self, heading, line1, line2=None, line3=None):
        """Show a dialog 'OK'."""
        pass#print("*** dialog OK ***\n%s" % [heading, line1, line2, line3])
        return True

    def browse(self, type, heading, shares, mask=None, useThumbs=None, treatAsFolder=None, default=None, enableMultiple=None):
        """Show a 'Browse' dialog."""
#        pass#print("*** dialog browse ***\n%s" % [heading, shares, default])
        return default

    def numeric(self, type, heading, default=0):
        """Show a 'Numeric' dialog."""
        return self.choose('numeric', heading, [], default)

    def yesno(self, heading, line1, line2=None, line3=None, nolabel='no', yeslabel='yes'):
        """Show a dialog 'YES/NO'."""
        query = '%s%s%s%s' % (heading or '', line1 or '', line2 or '', line3 or '')
        if 0:
            sel = self.choose('YES/NO', query, [yeslabel, nolabel])
            return (True if sel == 0 else False)
        elif 'YESNO=NO' in sys.argv:
            return False
        else:
            return True #always yes

    def select(self, heading, list, autoclose=None):
        """Show a select dialog."""
        return self.choose('select', heading, list)

    def chooseX(self, type, query, list, default=0):
        try: _dialogs
        except: xbmcinit.read_dialogs()
        dlg = '%s %s %s' % (repr(query), list, _mainid)
        sel = (_dialogs[dlg] if dlg in _dialogs else default)
#        pass#print("*** dialog %s ***\n%s <<< %s" % (type, sel, dlg))
        return sel

    def choose(self, type, query, list, default=0): #DO KOREKCJI!!!!
                pass#print("Here in xbmcgui.py sys.argv =", sys.argv)
                pass#print("xbmcgui.py choose list =", list)
                rfile = "/tmp/result.txt"

                if not os.path.exists(rfile):
                        pass#print("xbmcgui.py no result.txt =")
                        f = open("/tmp/arg1.txt", "w")
                        text1 = sys.argv[0]
                        text1 = text1.replace("plugin://", "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/plugins/")
                        text1 = text1 + "default.py"
                        text = text1 + " " + sys.argv[1] + " " + sys.argv[2] + " &\n"
                        pass#print("xbmcgui.py choose arg1.txt created text =", text)
                        f.write(text)
                        f.close()
                        params = parameters_string_to_dict(sys.argv[2])
                        mode =  str(params.get("mode", ""))
                        pic = " "
                        addDirectoryItem(query, {"name":query, "url":" ", "mode":mode, 'select':'true'}, pic)
                        i=0
                        for item in list:
                           pass#print("item =",item)
                           name=item
                           pic=''
                           addDirectoryItem(name, {"name":name, "url":str(i), "mode":mode, 'select':'true'}, pic)
                           i=i+1
                        sys.exit() 
#                        return "false"

                elif os.path.exists(rfile):
                        pass#print("xbmcgui.py yes result.txt")
                        myfile = open("/tmp/result.txt","r")       
                        icount = 0
                        for line in myfile.readlines(): 
                               idx = line
                               pass#print("xbmcgui.py yes idx 1=", idx)
                               icount = icount+1
                               if icount > 0:
                                      break
                        myfile.close()
                        cmd = "rm " + rfile
                        os.system(cmd)
                        pass#print("xbmcgui.py yes int(idx) 2=", int(idx))
                        return int(idx)
                else:
                        sys.exit()
                        
    def chooseXX(self, type, query, list, default=0):
            rfile = "/tmp/sel.txt"
            if os.path.exists(rfile):
                        myfile = open(rfile,"r")       
                        icount = 0
                        for line in myfile.readlines(): 
                               idx = line
                               icount = icount+1
                               if icount > 0:
                                      break
                        myfile.close()
                        if idx < 3: 
                               rep = idx+1
                        else:       
                               os.remove(rfile)
                               return None
            else:        
                        rep = 0
                        f = open("/tmp/sel.txt", "w")
                        f.write(rep)
                        f.close()
                        
            pass#print("In xbmcgui rep =", rep)
            return int(rep)
            
def addDirectoryItem(name, parameters={},pic=""):
    li = ListItem(name,iconImage="DefaultFolder.png", thumbnailImage=pic)
    #print(parameters)
    url = sys.argv[0] + '?' + urllib.parse.urlencode(parameters)
    #print("In xbmcgui addDirectoryItem url =", url)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=True)
            
def parameters_string_to_dict(parameters):
    ''' Convert parameters encoded in a URL to a dict. '''
    paramDict = {}
    if parameters:
        if parameters.startswith("?"):
          parameters=parameters[1:]    
        paramPairs = parameters.split("&")
 
          
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


            
# mock everything else, mostly


class DialogProgress:
    def __init__(self): self.isClosed = True
        
    def create(self, heading, line1=None, line2=None, line3=None):
        """Create and show a progress dialog."""
        self.heading = heading
        self.msg = ''
        self.percent = 0
        self.isClosed = False
        if not line1 is None: self.msg += '\n' + line1
        if not line2 is None: self.msg += '\n' + line2
        if not line3 is None: self.msg += '\n' + line3
        #if 'YESNO=NO' in sys.argv:
        xbmcE2.writeState('xbmcgui', 'DialogProgress', 'create', '-------------%s ----------------------\n%s' %(self.heading, self.msg))

    def update(self, percent, line1=None, line2=None, line3=None):
        """Update's the progress dialog."""
        if percent != self.percent:
            self.percent = percent
            xbmcE2.writeState('xbmcgui', 'DialogProgress', 'update', '-------------%s (%s/100) -------------\n%s' %(self.heading, self.percent, self.msg))

    def iscanceled(self):
        """Returns True if the user pressed cancel."""
        return self.isClosed

    def close(self):
        """Close the progress dialog."""
        self.msg = ''
        self.heading = ''
        self.isClosed = True
        xbmcE2.writeState('xbmcgui', 'DialogProgress', 'close', '')

class DialogProgressBG:
    def create(self, heading, line1=None, line2=None, line3=None):
        """Create and show a progress dialog."""
        pass

    def update(self, percent, line1=None, line2=None, line3=None):
        """Update's the progress dialog."""
        pass

    def iscanceled(self):
        """Returns True if the user pressed cancel."""
        return False

    def close(self):
        """Close the progress dialog."""
        pass

class ControlLabel:
    def __init__(self):
        pass#print("In xbmcgui.py ControlLabel")

    def setLabel(self, label):
        pass#print("In xbmcgui.py ControlLabel label =", label)

class ControlTextBox:
    def __init__(self):
        pass#print("In xbmcgui.py ControlTextBox")
      
    def setText(self, text):
        pass#print("In xbmcgui.py ControlTextBox text =", text)
        rfile = "/tmp/show.txt"
        f = open("/tmp/show.txt", "w")
        f.write(text)
        f.close()
                        
        f2 = open("/tmp/arg1.txt", "w")
        text1 = sys.argv[0]
        text1 = text1.replace("plugin://", "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/plugins/")
        text1 = text1 + "default.py"
        text = text1 + " " + sys.argv[1] + " " + sys.argv[2] + " &\n"
        pass#print("xbmcgui.py choose arg1.txt created text =", text_
        f2.write(text)
        f2.close()
    
        params = parameters_string_to_dict(sys.argv[2])
        mode =  str(params.get("mode", ""))
        pic = " "
        addDirectoryItem("Information", {"name":"Information", "url":" ", "mode":mode, 'showtext':'true'}, pic)

class Window:
    def __init__(self, windowId):
        self.properties = {}
        self.properties['windowId'] = windowId;

#    def addControl(self, control):
#        """Add a Control to this window."""
#        pass

#    def addControls(self, controlList):
#        """Add a list of Controls to this window."""
#        pass

#    def clearProperties(self):
#        """Clears all window properties."""
#        self.properties = {}

    def clearProperty(self, key):
#        """Clears the specific window property."""
        self.properties[key] = None

#    def close(self):
#        """Closes this window."""
#        pass

#    def doModal(self):
#        """Display this window until close() is called."""
#        pass

    def getControl(self, controlId):
        """Get's the control from this window."""
        pass#print)"In xbmcgui.py getControl controlId =", controlId)
        if controlId == 1:
                return ControlLabel()
        elif controlId == 5:        
                return ControlTextBox()
        else:
                        return ControlTextBox()
                
                
#    def getFocus(self, control):
#        """returns the control which is focused."""
#        pass

#    def getFocusId(self):
#        """returns the id of the control which is focused."""
#        return 0

#    def getHeight(self):
#        """Returns the height of this screen."""
#        return 480

    def getProperty(self, key):
#        """Returns a window property as a string, similar to an infolabel."""
            try:
                myfile = file(r"/tmp/guiprop.txt")       
                icount = 0
                for line in myfile.readlines(): 
                      prop = line
                      icount = icount+1
                      if icount > 0:
                            break
                myfile.close()            
                items = prop.split(" ")
                pass#print("In xbmcgui items =", items)
                return items[1]
                
            except:
                return ""    
####        return self.properties[key] if key in self.properties else ''

#    def getResolution(self):
#        """Returns the resolution of the screen. The returned value is one of the following:"""
#        return 5 # NTSC 16:9 (720x480)

#    def getWidth(self):
#        """Returns the width of this screen."""
#        return 720

#    def onAction(self, action):
#        """onAction method."""
#        pass

#    def onClick(self, control):
#        """onClick method."""
#        pass

#    def onFocus(self, control):
#        """onFocus method."""
#        pass

#    def onInit(self):
#        """onInit method."""
#        pass

#    def removeControl(self, control):
#        """Removes the control from this window."""
#        pass

#    def removeControls(self, controlList):
#        """Removes a list of controls from this window."""
#        pass

#    def setCoordinateResolution(self, resolution):
#        """Sets the resolution"""
#        pass

#    def setFocus(self, control):
#        """Give the supplied control focus."""
#        pass

#    def setFocusId(self):
#        """Gives the control with the supplied focus."""
#        pass

    def setProperty(self, key, value):
#        """Sets a window property, similar to an infolabel."""
        f = open("/tmp/guiprop.txt", "w")
        txt = str(key) + " " + str(value) + "\n"
        f.write(txt)
        f.close()
        self.properties[key] = value;

#    def show(self):
#        """Show this window."""
#        pass

#class WindowDialog(Window):

#    def __init__(self):
#        Window.__init__(self, 0)
#        pass

#class WindowXML(Window):

#    def __init__(self, xmlFilename, scriptPath=None, defaultSkin=None, forceFallback=False):
#        Window.__init__(self, 0)

#    def addItem(item, position=None):
#        """addItem(item[, position]) -- Add a new item to this Window List."""
#        pass

#    def clearList():
#        """clearList() -- Clear the Window List."""
#        pass

#    def getCurrentListPosition():
#        """getCurrentListPosition() -- Gets the current position in the Window List."""
#        return 0

#    def getListItem(position):
#        """getListItem(position) -- Returns a given ListItem in this Window List."""
#        return None

#    def getListSize():
#        """getListSize() -- Returns the number of items in this Window List."""
#        return 0

#    def removeItem(position):
#        """removeItem(position) -- Removes a specified item based on position, from the Window List."""
#        pass

#    def setCurrentListPosition(position):
#        """setCurrentListPosition(position) -- Set the current position in the Window List."""
#        return 0

## xbmc/interfaces/python/xbmcmodule/winxmldialog.cpp
#class WindowXMLDialog(WindowXML):

#    def __init__(self, xmlFilename, scriptPath=None, defaultSkin=None, defaultRes=None):
#        """Create a new WindowXMLDialog script."""
#        WindowXML.__init__(self, xmlFilename, scriptPath, defaultSkin)

class ControlSlider(Control):

    """
    ControlSlider class.
    Creates a slider.
    """

    def __init__(self, x, y, width, height, textureback=None, texture=None, texturefocus=None):
        """
        x: integer - x coordinate of control.
        y: integer - y coordinate of control.
        width: integer - width of control.
        height: integer - height of control.
        textureback: string - image filename.
        texture: string - image filename.
        texturefocus: string - image filename.

        Note:
            After you create the control, you need to add it to the window with addControl().

        Example:
            self.slider = xbmcgui.ControlSlider(100, 250, 350, 40)
        """
        pass

    def getPercent(self):
        """Returns a float of the percent of the slider."""
        return float

    def setPercent(self, percent):
        """Sets the percent of the slider."""
        pass

#noinspection PyUnusedLocal
class ControlGroup(Control):

    """ControlGroup class."""

    def __init__(self, x, y, width, height):
        """
        x: integer - x coordinate of control.
        y: integer - y coordinate of control.
        width: integer - width of control.
        height: integer - height of control.

        Example:
        self.group = xbmcgui.ControlGroup(100, 250, 125, 75)
        """
        pass



#noinspection PyUnusedLocal
class ControlEdit(Control):

    """
    ControlEdit class.
    ControlEdit(x, y, width, height, label[, font, textColor,
                                                    disabledColor, alignment, focusTexture, noFocusTexture])
    """

    def __init__(self, x, y, width, height, label, font=None, textColor=None, disabledColor=None, alignment=None,
                                                                            focusTexture=None, noFocusTexture=None):
        """
        x              : integer - x coordinate of control.
        y              : integer - y coordinate of control.
        width          : integer - width of control.
        height         : integer - height of control.
        label          : string or unicode - text string.
        font           : [opt] string - font used for label text. (e.g. 'font13')
        textColor      : [opt] hexstring - color of enabled label's label. (e.g. '0xFFFFFFFF')
        disabledColor  : [opt] hexstring - color of disabled label's label. (e.g. '0xFFFF3300')
        _alignment      : [opt] integer - alignment of label - *Note, see xbfont.h
        focusTexture   : [opt] string - filename for focus texture.
        noFocusTexture : [opt] string - filename for no focus texture.
        isPassword     : [opt] bool - if true, mask text value.

        *Note, You can use the above as keywords for arguments and skip certain optional arguments.
        Once you use a keyword, all following arguments require the keyword.
        After you create the control, you need to add it to the window with addControl().

        example:
        - self.edit = xbmcgui.ControlEdit(100, 250, 125, 75, 'Status')
        """
        pass

    def getLabel(self):
        """
        getLabel() -- Returns the text heading for this edit control.

        example:
        - label = self.edit.getLabel()
        """
        return unicode

    def getText(self):
        """
        getText() -- Returns the text value for this edit control.

        example:
        - value = self.edit.getText()
        """
        return unicode

    def setLabel(self, label):
        """
        setLabel(label) -- Set's text heading for this edit control.

        label          : string or unicode - text string.
        example:
        - self.edit.setLabel('Status')
        """
        pass

    def setText(self, value):
        """
        setText(value) -- Set's text value for this edit control.

        value          : string or unicode - text string.
        example:
        - self.edit.setText('online')
        """
        pass
