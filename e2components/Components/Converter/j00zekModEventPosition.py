# j00zek: this file has changed name just to avoid errors using opkg (situation when file was installed by different pockage)
#
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.Converter.Converter import Converter
from Components.Converter.Poll import Poll
from Components.Element import cached
from time import time

class j00zekModEventPosition(Poll, Converter, object):

    def __init__(self, type):
        Poll.__init__(self)
        Converter.__init__(self, type)
        self.poll_interval = 30000
        self.poll_enabled = True

    @cached
    def getPosition(self):
        event = self.source.event
        if event is None:
            return
        else:
            now = int(time())
            start_time = event.getBeginTime()
            duration = event.getDuration()
            if start_time <= now <= start_time + duration and duration > 0:
                return now - start_time
            return 0
            return

    @cached
    def getLength(self):
        event = self.source.event
        if event is None:
            return
        else:
            return event.getDuration()

    @cached
    def getCutlist(self):
        return []

    position = property(getPosition)
    length = property(getLength)
    cutlist = property(getCutlist)

    def changed(self, what):
        if what[0] != self.CHANGED_CLEAR:
            self.downstream_elements.changed(what)
            if len(self.downstream_elements):
                if not self.source.event and self.downstream_elements[0].visible:
                    self.downstream_elements[0].visible = False
                elif self.source.event and not self.downstream_elements[0].visible:
                    self.downstream_elements[0].visible = True