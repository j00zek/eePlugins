# -*- coding: utf-8 -*-
#
# j00zek 2019/2020
# some images doesn't present title, some doesn't translate
# this converter is to manage over both situations
#
#      <!-- zamiast elabel - widget source="session.CurrentService" render="Label"-->
"""
    <widget source="session.CurrentService" render="Label" backgroundColor="black" font="Roboto_HD; 26" foregroundColor="light_yellow" position="65,210" size="210,32" transparent="1">
      <convert type="j00zekAlternateTitle">Plugin browser</convert>
    </widget>
"""

from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.j00zekSkinTranslatedLabels import translate
    
class j00zekAlternateTitle(Converter, object):
    def __init__(self, LabelText):
        Converter.__init__(self, LabelText)
        self.translatedLabel = translate(LabelText)

    @cached
    def getText(self):
        retText = ''
        try:
            retText = translate(str(self.source.text))
        except Exception as e:
            retText = self.translatedLabel
        if len(retText) < 5:
            retText = self.translatedLabel
        return retText
        
    text = property(getText)
