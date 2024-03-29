#
#  j00zek: this file has changed name just to avoid errors using opkg (situation when file was installed by different pockage)
#
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.Converter.Converter import Converter
from Components.Element import cached

class j00zekModEMCinfo(Converter):
    EMC_PATHINFO = 0
    EMC_VERSIONSINFO = 1
    EMC_NAME_PLUS_VERSION = 2

    def __init__(self, type):
        Converter.__init__(self, type)
        if type == 'emc_pathinfo':
            self.type = self.EMC_PATHINFO
        elif type == 'emc_versionsinfo':
            self.type = self.EMC_VERSIONSINFO
        elif type == 'emc_name_plus_version':
            self.type = self.EMC_NAME_PLUS_VERSION
        else:
            self.type = None
        return

    @cached
    def getText(self):
        text = self.source.getText()
        if self.type == self.EMC_PATHINFO:
            ts = text.split(' - ', 1)
            if len(ts) == 2 and 'emc git' in text.lower():
                return ts[1]
            else:
                return text
        elif self.type == self.EMC_VERSIONSINFO:
            ts = text.split(' ')
            if len(ts) > 1 and 'emc git' in text.lower():
                return ts[1]
            else:
                return text
        elif self.type == self.EMC_NAME_PLUS_VERSION:
            ts = text.split(' ')
            if len(ts) > 1 and 'emc git' in text.lower():
                return 'Enhanced Movie Center - ' + ts[1]
            else:
                return 'Enhanced Movie Center'
        else:
            return text

    text = property(getText)