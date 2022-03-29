#######################################################################
#
#    Converter for Enigma2
#    Coded by shamann (c)2017
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
#######################################################################
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.config import config
from Components.Converter.Converter import Converter
from Components.Converter.Poll import Poll
from Components.Element import cached
from enigma import iServiceInformation, iPlayableService

class j00zekVideoResolution(Poll, Converter, object):
    VideoResolution = 0

    def __init__(self, type):
        Converter.__init__(self, type)
        Poll.__init__(self)
        self.type, self.interesting_events = {
            'VideoResolution': (self.VideoResolution, (iPlayableService.evVideoSizeChanged, iPlayableService.evUpdatedInfo)),
            }[type]
        self.poll_interval = 1000
        self.poll_enabled = True

    @cached
    def getText(self):
        service = self.source.service
        info = service and service.info()
        if not info:
            return ''
        if self.type == self.VideoResolution:
            x = info.getInfo(iServiceInformation.sVideoWidth)
            y = info.getInfo(iServiceInformation.sVideoHeight)
            if x == -1 or y == -1:
                return ' '
            m = ''
            try:
                f = open('/proc/stb/vmpeg/0/progressive', 'r').read()
                if f.find('0') != -1:
                    m = 'i'
                elif f.find('1') != -1:
                    m = 'p'
            except: pass
            if m == '':
                try:
                    m = ({False:'i', True:'p'}[info.getInfo(iServiceInformation.sProgressive) == 1])
                except: pass
            x = '%sx%s%s' % (x,y,m)
            if m == '':
                x = x.replace('x',' x ')
            return x
        return ' '

    text = property(getText)

    def changed(self, what):
        if what[0] != self.CHANGED_SPECIFIC or what[1] in self.interesting_events:
            Converter.changed(self, what)
        elif what[0] == self.CHANGED_POLL:
            self.downstream_elements.changed(what)




