#######################################################################
#
#    Converter for Enigma2
#    Coded by j00zek (c)2018-2023
#
#    Uszanuj moja prace i nie kasuj/zmieniaj informacji kto jest autorem konwertera
#    Please respect my work and don't delete/change name of the converter author
#
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version 2
#    of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#    Example to show current played time in your skin:
#        <widget source="session.CurrentService" render="Label" font="Roboto_HD; 50" position="10,260" size="460,50" halign="left" backgroundColor="black" transparent="1" >
#            <convert type="j00zekE2iPlayer">CurrentTime</convert>
#        </widget>
#
#######################################################################
from Components.Converter.Converter import Converter
from Components.Converter.Poll import Poll
from Components.Element import cached
from Components.config import config
from datetime import timedelta

class j00zekE2iPlayerSSS(Poll, Converter, object):

    def __init__(self, type):
        Converter.__init__(self, type)
        Poll.__init__(self)
        self.type = type
        self.poll_interval = 1000
        self.poll_enabled = True
        self.playback = None

    def importExtPlayer(self):
        if self.playback is None:
            try:
                from Plugins.Extensions.IPTVPlayer.components.extmovieplayer import ExtMoviePlayer
                self.playback = ExtMoviePlayer.playback
                print('j00zekE2iPlayerSSS.importExtPlayer() self.playback = ExtMoviePlayer.playback')
            except Exception as e:
                self.playback = False
                print('j00zekE2iPlayerSSS.importExtPlayer() Exception: %s' % str(e))

    @cached
    def getText(self):
        try:
            self.importExtPlayer()
            if self.type == 'AllTimes': return  '%s -%s %s' %(str(timedelta(seconds=self.playback['CurrentTime'])),
                                                                str(timedelta(seconds=self.playback['Length']-self.playback['CurrentTime']))[:-3],
                                                                str(timedelta(seconds=self.playback['Length']))[:-3])
            elif self.type == 'CurrentTimeHM': return str(timedelta(seconds=self.playback['CurrentTime']))[:-3]
            elif self.type == 'CurrentTimeHMS': return str(timedelta(seconds=self.playback['CurrentTime']))
            elif self.type == 'RemindedTimeHM': return str(timedelta(seconds=self.playback['Length']-self.playback['CurrentTime']))[:-3]
            elif self.type == 'RemindedTimeHMS': return str(timedelta(seconds=self.playback['Length']-self.playback['CurrentTime']))
            elif self.type == 'RemindedMinutes': 
                if self.playback['Length']-self.playback['CurrentTime'] > 60:
                    return '+%smin' % str(int(((self.playback['Length']-self.playback['CurrentTime'])/60)))
                else:
                    return '+%ss' % str(self.playback['Length']-self.playback['CurrentTime'])
            elif self.type == 'LengthHM': return str(timedelta(seconds=self.playback['Length']))[:-3]
            elif self.type == 'LengthHMS': return str(timedelta(seconds=self.playback['Length']))
        except Exception as e:
            print('j00zekE2iPlayerSSS.getText() Exception: %s' % str(e))
            return ' '
        return 'N/A'

    text = property(getText)

    @cached
    def getValue(self):
        try:
            self.importExtPlayer()
            if self.type == 'Progress': return int(float(self.playback['CurrentTime']) / float(self.playback['Length']) * 100)
        except Exception: return 0
        return 0

    value = property(getValue)
    range = 100
    
    def changed(self, what):
        try:
            if what[0] == self.CHANGED_POLL:
                self.downstream_elements.changed(what)
        except Exception: pass
                




