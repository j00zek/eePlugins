#
# j00zek: this file has changed name just to avoid errors using opkg (situation when file was installed by different package)
#
import os
import time
import xml.etree.cElementTree

from Components.Converter.Converter import Converter
from Components.Element import cached

class HomarTimers(Converter, object):
    def __init__(self, type):
        Converter.__init__(self, type)
        self.Filename = "/etc/enigma2/timers.xml"

    @cached
    def getText(self):
        strTimers = ""

        file = open(self.Filename, 'r')
        doc = xml.etree.cElementTree.parse(file)
        file.close()

        root = doc.getroot()

        for timer in root.findall("timer"):
            begin = int(timer.get("begin"))

            if int(time.time()) < begin and 0 == int(timer.get("disabled")):
                strTimers += time.strftime('%d, %H:%M', time.localtime(begin)) + " " + timer.get("name").encode("utf-8") + '\n'

        if not strTimers:
            strTimers = "Brak timera"

        return strTimers

    text = property(getText)

    def changed(self, what):
        Converter.changed(self, what)