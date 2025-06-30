# -*- coding: utf-8 -*-
#
# j00zek 2018/2019/2020
# eLabel is simple to use but not translated
# this converter is to use instead and have texts localized
#
#      <!-- zamiast elabel - widget source="session.CurrentService" render="Label"-->
"""
    <widget source="session.CurrentService" render="Label" backgroundColor="black" font="Roboto_HD; 26" foregroundColor="light_yellow" position="65,210" size="210,32" transparent="1">
      <convert type="j00zekTranslator">Box Type:</convert>
    </widget>
"""

from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.j00zekSkinTranslatedLabels import translate

class j00zekTranslator(Converter, object):
    def __init__(self, LabelText):
        Converter.__init__(self, LabelText)
        self.translatedLabel  = translate(LabelText)

    @cached
    def getText(self):
        return self.translatedLabel
        
    text = property(getText)
