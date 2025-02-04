 # -*- coding: utf-8 -*-
#
# j00zek: this file has changed name just to avoid errors using opkg (situation when file was installed by different pockage)
#
from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.Converter.Poll import Poll
from Tools.Directories import fileExists
from os import popen
import re

smartctlApprovedHDD = ('WD-WX31A96NAH24',)

class j00zekModHddTempInfo(Poll, Converter, object):
    def __init__(self, type):
        Converter.__init__(self, type)
        Poll.__init__(self)
        self.type = type
        self.poll_interval = 2000
        self.poll_enabled = True
        self.use_smartctl = False
        self.currentTemp = '?'
        tmp = popen("smartctl -i /dev/sda").read()
        for hdd in smartctlApprovedHDD:
            if hdd in tmp:
                self.use_smartctl = True
    
    @cached
    def getText(self):
        if fileExists("/usr/sbin/hddtemp") and fileExists("/dev/sda"):
            temp = popen("hddtemp -n -q /dev/sda").read().strip()
            if temp == '0' or temp == '' and self.use_smartctl:
                for line in popen("smartctl -A /dev/sda").readlines():
                    if line.startswith('194'):
                        line = re.sub(r" [ ]*"," ",line) #remove multiple spaces
                        #examples
                        #'194 Temperature_Celsius 0x0002 064 059 000 Old_age Always - 36 (Min/Max 20/53)'
                        #'194 Temperature_Celsius 0x0022 105 092 000 Old_age Always - 42'
                        temp = re.findall(' -[ ]*([0-9]*)', line, re.S)
                        if len(temp) > 0:
                            temp = temp[0]
                        else: #if not found by regex take 10th field from left
                            temp = line.strip().split(' ')
                            if len(temp) > 9:
                                temp = temp[9]
                            else:
                                temp = ''
                        
            if temp != '0' and temp != '':
                self.currentTemp = "%s%sC" % (temp, chr(176))
        return self.currentTemp
    
    text = property(getText)
    
    def changed(self, what):
        if what[0] == self.CHANGED_POLL:
            self.downstream_elements.changed(what)
