from Components.Pixmap import Pixmap
from enigma import ePicLoad

DBG = False
try:
    if DBG: from Components.j00zekComponents import j00zekDEBUG
except Exception:
    DBG = False 
    
class j00zekAccellPixmap(Pixmap):
    visible = 0

    def __init__(self):
        Pixmap.__init__(self)
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.paintIconPixmapCB)
        self.decoding = None
        self.decodeNext = None

    def doShow(self):
        if not self.visible:
            self.visible = True
            if DBG: j00zekDEBUG("[j00zekAccellPixmap:doShow] cover visible %s self.show" % self.visible)
            self.show()

    def doHide(self):
        if self.visible:
            self.visible = False
            if DBG: j00zekDEBUG("[j00zekAccellPixmap:doHide] cover visible %s self.hide" % self.visible)
            self.hide()

    def onShow(self):
        Pixmap.onShow(self)
        picWidth = self.instance.size().width()
        picHeight = self.instance.size().height()
        self.picload.setPara((picWidth, picHeight, 1, 1, False, 1, "#FF000000"))

    def paintIconPixmapCB(self, picInfo=None):
        ptr = self.picload.getData()
        if ptr != None:
            self.instance.setPixmap(ptr.__deref__())
            if self.visible:
                self.doShow()
        if self.decodeNext is not None:
            self.decoding = self.decodeNext
            self.decodeNext = None
            if self.picload.startDecode(self.decoding) != 0:
                if DBG: j00zekDEBUG("[j00zekAccellPixmap:paintIconPixmapCB] Failed to start decoding next image")
                self.decoding = None
        else:
            self.decoding = None

    def updateIcon(self, filename):
        #if DBG: j00zekDEBUG("[j00zekAccellPixmap:updateIcon] filename='%s'" % filename)
        if self.decoding is not None:
            self.decodeNext = filename
        else:
            if self.picload.startDecode(filename) == 0:
                self.decoding = filename
            else:
                if DBG: j00zekDEBUG("[j00zekAccellPixmap:updateIcon] Failed to start decoding image")
                self.decoding = None
