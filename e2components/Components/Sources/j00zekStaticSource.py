from __future__ import absolute_import #zmiana strategii ladowania modulow w py2 z relative na absolute jak w py3
from Components.Sources.Source import Source

class j00zekStaticSource(Source):
	# filter is a function which filters external, untrusted strings
	# this must be done to avoid XSS attacks!

	# (and is probably not done yet. For this reason, be careful when
	# using this on HTML pages. *DO* provide your filter function.)
	def __init__(self, text = "", filter = lambda x: x):
		Source.__init__(self)
		self.__text = text
		self.filter = filter

	def handleCommand(self, cmd):
		self.text = self.filter(cmd)

	def getText(self):
		return self.__text

	def setText(self, text):
		self.__text = text
		self.changed((self.CHANGED_ALL,))

	text = property(getText, setText)

	def getBoolean(self):
		return bool(self.__text)

	boolean = property(getBoolean)
