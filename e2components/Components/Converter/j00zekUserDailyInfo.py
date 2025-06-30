# -*- coding: utf-8 -*-
#
# j00zek: na podstawie pomyslu kolegi kolibert z forum s4a
#       typy:
#               retInfo
#               retPic
#

from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from time import localtime, strftime
from Components.Converter.Converter import Converter
from Components.Element import cached
import os

class j00zekUserDailyInfo(Converter, object):
    def __init__(self, type):
        fileDict = '/etc/enigma2/BH-UserDailyInfo.txt'
        Converter.__init__(self, type)
        self.DailyInfoDict = {}
        if os.path.exists(fileDict):
            with open(fileDict, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('#') or line == '' or not '=' in line:
                        continue
                    else:
                        try:
                            cfg = line.split('=')
                            parms = cfg[1].split('|')
                            if type == "retInfo":
                                self.DailyInfoDict[cfg[0].strip()] = parms[0].strip()
                            elif type == "retPic":
                                self.DailyInfoDict[cfg[0].strip()] = parms[1].strip()
                        except Exception as e:
                            pass
                f.close()
        else:
            with open(fileDict, 'w') as f:
                f.write("# Każda linia zawiera datę, info dla daty oraz zdjęcie dla daty\n")
                f.write("# Format:\n")
                f.write("# MM-DD=info|pełna ścieżka do zdjęcia\n")
                f.write("# Przykłady:\n")
                f.write("12-24=Wigilia|/usr/share/enigma2/BlackHarmony/pixAnims/choinka/a0.png\n")
                MonthDay = strftime('%m-%d')
                f.write("%s=Każdy dzień ma swój aromat - Melchior Wańkowicz|/usr/share/enigma2/BlackHarmony/icons/BingPicOfTheDay.jpg\n" % MonthDay)
                f.close()

    @cached
    def getText(self):
        MonthDay = strftime('%m-%d')
        retVal = self.DailyInfoDict.get(MonthDay, '')
        return retVal

    text = property(getText)