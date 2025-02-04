# j00zek: this file has changed name just to avoid errors using opkg (situation when file was installed by different package)
#
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.Renderer.Renderer import Renderer #ATV7.0,EGAMI10

from enigma import ePixmap
from Tools.Directories import fileExists, SCOPE_CURRENT_SKIN, resolveFilename
import os

class j00zekModAudioIcon(Renderer):
	searchPaths = (resolveFilename(SCOPE_CURRENT_SKIN), '/usr/share/enigma2/skin_default/')

	def __init__(self):
		Renderer.__init__(self)
		self.size = None
		self.nameAudioCache = { }
		self.pngname = ""
		self.path = ""

	def applySkin(self, desktop, parent):
		attribs = [ ]
		for (attrib, value) in self.skinAttributes:
			if attrib == "path":
				self.path = value
				if value.endswith("/"):
					self.path = value
				else:
					self.path = value + "/"
			else:
				attribs.append((attrib,value))
			if attrib == "size":
				value = value.split(',')
				if len(value) == 2:
					self.size = value[0] + "x" + value[1]
		self.skinAttributes = attribs
		return Renderer.applySkin(self, desktop, parent)

	GUI_WIDGET = ePixmap

	def changed(self, what):
		if self.instance:
			pngname = ""
			if what[0] != self.CHANGED_CLEAR:
				sname = self.source.text
				pngname = self.nameAudioCache.get(sname, "")
				if pngname == "":
					pngname = self.findAudioIcon(sname)
					if pngname != "":
						self.nameAudioCache[sname] = pngname
			if pngname == "":
				self.instance.hide()
			else:
				self.instance.show()
			if pngname != "" and self.pngname != pngname:
				self.instance.setPixmapFromFile(pngname)
				self.pngname = pngname

	def findAudioIcon(self, audioName):
		if self.path.startswith("/"):
			pngname = self.path + audioName + ".png"
			if os.path.exists(pngname):
				return pngname
		for path in self.searchPaths:
			pngname = path + self.path + audioName + ".png"
			if os.path.exists(pngname):
				return pngname
		return ""

