# -*- coding: utf-8 -*-
#
# j00zek: this file is just to avoid GS-es, when weather plugin not installed
#

from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.Renderer.Renderer import Renderer #ATV7.0,EGAMI10

from enigma import ePixmap
from Components.AVSwitch import AVSwitch
from enigma import eEnv, ePicLoad, eRect, eSize, gPixmapPtr

class fakePixmap(Renderer):
	def __init__(self): Renderer.__init__(self)
	GUI_WIDGET = ePixmap

try:
    from Components.Renderer.ABTCAirlyPixmap import ABTCAirlyPixmap as j00zekABTCAirlyPixmap
except Exception:
    j00zekABTCAirlyPixmap = fakePixmap  