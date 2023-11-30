try:
    from Renderer import Renderer
except Exception:
    from Components.Renderer.Renderer import Renderer
from enigma import ePixmap
from Tools.LoadPixmap import LoadPixmap
# >>> musismy ladowac z pelnej sciezki bo konwerter jet uruchamany z innego kataouog mimo ze jest tutaj
from Plugins.Extensions.DGWeather.components.utils import *

class dgWeatherAirlyPicon(Renderer):

    def __init__(self):
        write_log('Renderer.dgWeatherAirlyPicon().__init__() >>>')
        Renderer.__init__(self)
        self.pngname = ''
        return

    GUI_WIDGET = ePixmap

    def changed(self, what):
        #write_log('Renderer.dgWeatherAirlyPicon().changed() >>>')
        if self.instance:
            pngname = self.source.text
            write_log('Renderer.dgWeatherAirlyPicon().changed() pngname = "%s"' % pngname)
            if not pngname is None:
                if pngname and self.pngname != pngname:
                    self.instance.setScale(1)
                    self.instance.setPixmapFromFile(pngname)
                    self.instance.show()
                    self.pngname = pngname
