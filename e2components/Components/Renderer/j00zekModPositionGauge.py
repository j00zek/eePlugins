# j00zek: this file has changed name just to avoid errors using opkg (situation when file was installed by different package)
#
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.Renderer.Renderer import Renderer #ATV7.0,EGAMI10

from enigma import ePositionGauge

class j00zekModPositionGauge(Renderer):

    def __init__(self):
        Renderer.__init__(self)
        self.__position = 0
        self.__seek_position = 0
        self.__length = 0
        self.__seek_enable = 0
        self.__cutlist = []

    GUI_WIDGET = ePositionGauge

    def postWidgetCreate(self, instance):
        self.changed((self.CHANGED_DEFAULT,))
        self.cutlist_changed()
        instance.setInOutList(self.__cutlist)

    def changed(self, what):
        if what[0] == self.CHANGED_CLEAR:
            self.length, self.position = 0
        else:
            self.length, self.position = self.source.length or 0, self.source.position or 0

    def cutlist_changed(self):
        self.cutlist = self.source.cutlist or []

    def getPosition(self):
        return self.__position

    def setPosition(self, pos):
        self.__position = pos
        if self.instance is not None:
            self.instance.setPosition(pos)
        return

    position = property(getPosition, setPosition)

    def getLength(self):
        return self.__length

    def setLength(self, len):
        self.__length = len
        if self.instance is not None:
            try:
                self.instance.setLength(len)
            except Exception:
                print('EXCEPTION in self.instance.setLength(%s)' % str(len))
                pass
        return

    length = property(getLength, setLength)

    def getCutlist(self):
        return self.__cutlist

    def setCutlist(self, cutlist):
        if self.__cutlist != cutlist:
            self.__cutlist = cutlist
            if self.instance is not None:
                self.instance.setInOutList(cutlist)
        return

    cutlist = property(getCutlist, setCutlist)

    def getSeekEnable(self):
        return self.__seek_enable

    def setSeekEnable(self, val):
        self.__seek_enable = val
        if self.instance is not None:
            self.instance.enableSeekPointer(val)
        return

    seek_pointer_enabled = property(getSeekEnable, setSeekEnable)

    def getSeekPosition(self):
        return self.__seek_position

    def setSeekPosition(self, pos):
        self.__seek_position = pos
        if self.instance is not None:
            self.instance.setSeekPosition(pos)
        return

    seek_pointer_position = property(getSeekPosition, setSeekPosition)