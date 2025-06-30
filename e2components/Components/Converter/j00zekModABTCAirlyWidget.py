from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.Converter.Converter import Converter
from Components.Element import cached
import time, json, os

class useMsnDict(Converter, object):
    def __init__(self, argsstr):
        Converter.__init__(self, argsstr)
        self.dictWeather = {}
        self.argsstr = argsstr
        self.lastEPOC = time.time()

    @cached
    def getText(self):
        retText = '?'
        if os.path.exists('/tmp/.MSNdata/dictWeather_0.json') == False:
            print('/tmp/.MSNdata/dictWeather_0.json does NOT exists')
        else:
            try:
                if len(self.dictWeather) == 0 or (time.time() - self.lastEPOC) >= 1800:
                    with open('/tmp/.MSNdata/dictWeather_0.json', 'r') as json_file:
                        self.dictWeather = json.load(json_file)['currentData']
                        json_file.close()
                        self.lastEPOC = time.time()
                if self.argsstr == 'temp':
                    retText = self.dictWeather['temperature']['valInfo']
                elif self.argsstr == 'caqi':
                    retText = self.dictWeather['airIndex']['val']
                elif self.argsstr == 'indexBackPNG':
                    retText = self.dictWeather['airIndex']['iconfilename']
                else:
                    print('getText(useMsnDict) ',' UNKNOWN ARG "%s"' % self.argsstr)
            except Exception as e:
                print('getText(useMsnDict) ','Exception for "%s": %s' % (self.argsstr, str(e)))
        
        return retText
    
    text = property(getText)
    
    @cached
    def getIconFilename(self):
        retVal = ''
        try:
            retVal = dictWeather['airIndex']['iconfilename']
            print('getIconFilename() retVal= "%s"' % str(e))
        except Exception as e:
            print('getIconFilename() Exception' % str(e))
        return retVal
            
    iconfilename = property(getIconFilename)


try:
    from Components.Converter.ABTCAirlyWidget import ABTCAirlyWidget as j00zekModABTCAirlyWidget #py2
    print('ABTCAirlyWidget loaded')
except Exception:
    try:
        from Components.Converter.Airly2Widget import Airly2Widget as j00zekModABTCAirlyWidget #py3
        print('Airly2Widget loaded')
    except Exception as e:
        print('Exceptioon loading Airly2Widget: %s' % str(e))
        j00zekModABTCAirlyWidget = useMsnDict
