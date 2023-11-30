from Components.Renderer.Renderer import Renderer
from enigma import ePixmap
from Tools.LoadPixmap import LoadPixmap
from Plugins.Extensions.DGWeather.components.utils import *

DBG = False

class dgWeatherAirlyPicon(Renderer):
    def __init__(self):
        if DBG: write_log('Renderer.dgWeatherAirlyPicon().__init__() >>>')
        Renderer.__init__(self)
        self.pngname = ''
        return

    GUI_WIDGET = ePixmap

    def changed(self, what):
        if DBG: write_log('Renderer.dgWeatherAirlyPicon().changed() >>>')
        if self.instance:
            if DBG: write_log('Renderer.dgWeatherAirlyPicon().changed() instance')
            pngname = self.source.iconfilename
            if DBG: write_log('Renderer.dgWeatherAirlyPicon().changed() pngname = "%s"' % pngname)
            if not pngname is None:
                if pngname and self.pngname != pngname:
                    self.instance.setScale(1)
                    self.instance.setPixmapFromFile(pngname)
                    self.instance.show()
                    self.pngname = pngname
