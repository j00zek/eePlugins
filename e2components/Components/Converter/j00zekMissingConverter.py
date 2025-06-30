# -*- coding: utf-8 -*-
#
# j00zek: this file is just to avoid GS-es, when required component is not installed
# usage example: for file with name BlackHarmonyREQUIREDCOMPONENT
#try:
#    from Components.Converter.REQUIREDCOMPONENT import REQUIREDCOMPONENT as BlackHarmonyREQUIREDCOMPONENT
#except Exception:
#    from Components.Converter.j00zekMissingConverter import j00zekMissingConverter as BlackHarmonyREQUIREDCOMPONENT
#  
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.Converter.Converter import Converter
from Components.Element import cached

class j00zekMissingConverter(Converter, object):
	def __init__(self, type): Converter.__init__(self, type)
	def getIndex(self, key): return None
	def getText(self): return ""
	text = property(getText)
	def getIconFilename(self): return ""
	iconfilename = property(getIconFilename)
