#
# j00zek: this file has changed name to avoid errors using opkg (situation when file was installed by different pockage)
#
# Usage example:
#  <!-- emuname info -->
#  <widget source="session.CurrentService" render="Label" position="1657,984" size="210,40" font="Roboto_HD;20" halign="right" valign="center" foregroundColor="light_yellow" backgroundColor="Background" transparent="1" noWrap="1"  valign="center" zPosition="3">
#      <convert type="j00zekModEmuName">camd</convert>
#  </widget-->  
#
# Copyright (c) 2boom & Taapat 2013-14, j00zek 2019-2020
# v.1.1
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from enigma import iServiceInformation
from Components.config import config, getConfigListEntry, ConfigText, ConfigPassword, ConfigClock, ConfigSelection, ConfigSubsection, ConfigYesNo, configfile, NoSave
from Components.ConfigList import ConfigListScreen
from Components.Converter.Converter import Converter
from Components.Converter.Poll import Poll
from Components.Element import cached
from Tools.Directories import fileExists
#from cStringIO import StringIO
import os

class j00zekModEmuName(Poll, Converter, object):
    def __init__(self, type):
        Converter.__init__(self, type)
        Poll.__init__(self)
        self.poll_interval = 2000
        self.poll_enabled = True
        
    @cached
    def getText(self):
        info = ""
        # Alternative SoftCam Manager 
        if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/AlternativeSoftCamManager/plugin.py"):
            if config.plugins.AltSoftcam.actcam.value != "none":
                info = config.plugins.AltSoftcam.actcam.value + ' & '

        # checking various files
        if 'oscam' not in info and fileExists('/tmp/.oscam'):
            info += 'oscam' + ' & '
        for infoFile in ("/tmp/.emu.info", #VTI
                         "/etc/startcam.sh", #TS-Panel
                         "/etc/init.d/cardserver", "/etc/init.d/softcam", #Pli
                         "/etc/CurrentBhCamName", #BlackHole
                         "/etc/.emustart",
                         "/tmp/cam.info",
                         "/etc/active_emu.list", #Domica
                         "/etc/clist.list"  # Merlin2
                         ):
            if fileExists(infoFile):
                fileContent = ''
                with open (infoFile, "r") as myfile:
                    fileContent = myfile.read().lower()
                    myfile.close()
                for softCamName in ('oscam','oscam','newcs','wicard','wicardd','cccam','mgcamd','camd3','evocamd','rqcamd','gbox','mpcs','sbox'):
                    if softCamName not in info and softCamName in fileContent:
                        info += softCamName + ' & '

        if info.endswith(' & '):
            info = info[:-3]
        return info

    text = property(getText)

    def changed(self, what):
        Converter.changed(self, (self.CHANGED_POLL,))
