# -*- coding: utf-8 -*-
from Components.Converter.Converter import Converter
from Components.Element import cached
#from Components.Converter.Poll import Poll
# >>> musismy ladowac z pelnej sciezki bo konwerter jet uruchamany z innego kataouog mimo ze jest tutaj
from Plugins.Extensions.DGWeather.components.utils import *
from Plugins.Extensions.DGWeather.components.WeatherData import WeatherData
# <<<

WeatherDict = None

#class DGWeather2(Poll, Converter, object):
class DGWeather2(Converter, object):
    def __init__(self, type):
        write_log('Converter.DGWeather2().__init__() >>>')
        #Poll.__init__(self)
        Converter.__init__(self, type)
        self.type = type
        #self.poll_interval = 600000
        #self.poll_enabled = True
        if WeatherDict is None:
            write_log('\t init WeatherDict')
            self.reloadWeatherDict(True)
        return

    def reloadWeatherDict(self, doLoad = False):
        #write_log('Converter.DGWeather2().reloadWeatherDict() >>>')
        global WeatherDict
        if doLoad:
            write_log('Converter.DGWeather2().reloadWeatherDict() LoadJsonDict(WeatherInfoDict.json)')
            WeatherDict = LoadJsonDict('WeatherInfoDict.json')
        else:
            write_log('Converter.DGWeather2().reloadWeatherDict() reLoadJsonDict(WeatherInfoDict.json)')
            WeatherDict = reLoadJsonDict('WeatherInfoDict.json', WeatherDict)

    @cached
    def getText(self):
        self.reloadWeatherDict()
        global WeatherDict
        retVal = ' '
        try:
            if str(self.type) in WeatherDict:
                retVal = str(WeatherDict[self.type])
            elif str(self.type).startswith('['):
                retVal = str(WeatherDict(str(self.type)))
            write_log('Converter.DGWeather2().getText(%s) = "%s"' % (self.type, retVal))
            return retVal
        except Exception as ex:
            Exc_log()
            return ' '

    text = property(getText)

    def changed(self, what):
        if what[0] == self.CHANGED_POLL:
            Converter.changed(self, what)
