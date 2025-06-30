#
#  j00zek: this file has changed name just to avoid errors using opkg (situation when file was installed by different pockage)
#

from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.Converter.Converter import Converter
from enigma import eTimer

class j00zekModConditionalShowHide(Converter, object):
	def __init__(self, argstr):
		Converter.__init__(self, argstr)
		args = argstr.split(',')
		self.invert = "Invert" in args
		self.blink = "Blink" in args
		if self.blink:
			self.blinktime = len(args) == 2 and args[1].isdigit() and int(args[1]) or 500
			self.timer = eTimer()
			self.timer.callback.append(self.blinkFunc)
		else:
			self.timer = None

	def blinkFunc(self):
		if self.blinking:
			for x in self.downstream_elements:
				x.visible = not x.visible

	def startBlinking(self):
		self.blinking = True
		self.timer.start(self.blinktime)

	def stopBlinking(self):
		self.blinking = False
		for x in self.downstream_elements:
			if x.visible:
				x.hide()
		self.timer.stop()

	def calcVisibility(self):
		b = self.source.boolean
		if b is None:
			return True
		b ^= self.invert
		return b

	def changed(self, what):
		vis = self.calcVisibility()
		if self.blink:
			if vis:
				self.startBlinking()
			else:
				self.stopBlinking()
		else:
			for x in self.downstream_elements:
				x.visible = vis

	def connectDownstream(self, downstream):
		Converter.connectDownstream(self, downstream)
		vis = self.calcVisibility()
		if self.blink:
			if vis:
				self.startBlinking()
			else:
				self.stopBlinking()
		else:
			downstream.visible = self.calcVisibility()

	def destroy(self):
		if self.timer:
			self.timer.callback.remove(self.blinkFunc)
