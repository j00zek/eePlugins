# j00zek: this file has changed name just to avoid errors using opkg (situation when file was installed by different package)
#
#
# BlackHarmonyTypeLabel Renderer for Enigma2 Dreamboxes (TypeLabel.py)
# Coded by vlamo (c) 2011
#
# Version: 1.2 (07.07.2011 15:56)
# Support: http://dream.altmaster.net/
#
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.Renderer.Renderer import Renderer #ATV7.0,EGAMI10
from enigma import eLabel, eTimer

class j00zekModTypeLabel(Renderer):
	def __init__(self):
		Renderer.__init__(self)
		self.timer = None
		self.text = ""
		self.caret = "_"
		self.mark = False
		self.delay = self.repeat = self.maxrep = 0
		self.speed = 100

	GUI_WIDGET = eLabel

	def applySkin(self, desktop, parent):
		def getIntValue(val, limit, default):
			try:	x = max(limit, int(val))
			except:	x = default
			return x
		
		if self.skinAttributes is not None:
			attribs = [ ]
			for (attrib, value) in self.skinAttributes:
				if attrib == "typeCaret":
					val = value.lower()
					if val in ("0","none"):
						self.caret = ""
					elif val in ("1","underscore"):
						self.caret = "_"
					elif val in ("2","block"):
						self.caret = " "
					else:
						self.caret = str(value)
					self.mark = (self.caret == " ")
				elif attrib == "typeSpeed":
					x = getIntValue(value, 0, 600)
					if x > 0: self.speed = max(25, int(60000/x))
				elif attrib == "typeStartDelay":
					self.delay = getIntValue(value, 0, self.delay)
				elif attrib == "typeRepeats":
					self.maxrep = getIntValue(value, 0, self.maxrep)
				elif attrib == "noCaret":
					if not value.lower() in ("0","false","no","off"):
						self.caret = ""
				else:
					attribs.append((attrib,value))
			self.skinAttributes = attribs
		return Renderer.applySkin(self, desktop, parent)

	def postWidgetCreate(self, instance):
		self.timer = eTimer()
		self.timer.callback.append(self.__timerLoop)
	
	def preWidgetRemove(self, instance):
		self.timer.stop()
		self.timer = None

	def doSuspend(self, suspended):
		if suspended:
			self.changed((self.CHANGED_CLEAR,))
		else:
			self.repeat = 0
			self.changed((self.CHANGED_DEFAULT,))

	def connect(self, source):
		Renderer.connect(self, source)
		#self.changed((self.CHANGED_DEFAULT,))

	def changed(self, what):
		if self.timer is not None: self.timer.stop()
		if what[0] == self.CHANGED_CLEAR:
			self.text = ""
			if self.instance is not None:
				self.instance.setText(self.text)
		else:
			self.text = self.source.text
			if not self.instance is None:	# and not self.suspended:
				if self.timer is None or (self.maxrep and self.repeat >= self.maxrep):
					self.instance.setText(self.text)
				else:
					if self.maxrep: self.repeat += 1
					self.pos = 0
					if self.caret:
						if self.mark:
							self.instance.setMarkedPos(self.pos)
						self.instance.setText(self.caret)
					self.timer.start(self.delay, True)

	def __timerLoop(self):
		self.pos += 1
		if self.pos <= len(self.text):
			if self.mark:
				self.instance.setMarkedPos(self.pos)
			self.instance.setText(self.text[:self.pos] + self.caret)
			self.timer.start(self.speed, True)
		else:
			if self.mark:
				self.instance.setMarkedPos(-1)
			self.instance.setText(self.text)

