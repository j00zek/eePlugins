from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.Converter.Converter import Converter
from Components.Element import cached

class j00zekModBlinkingClock(Converter, object):

    def __init__(self, type):
        Converter.__init__(self, type)

    @cached
    def getBoolean(self):
        return True

    boolean = property(getBoolean)

    def changed(self, what):
        Converter.changed(self, what)