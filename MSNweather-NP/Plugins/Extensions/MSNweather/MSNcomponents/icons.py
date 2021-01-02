# -*- coding: utf-8 -*- 

from Tools.LoadPixmap import LoadPixmap
import os

DBG = False

def DEBUG(myFUNC = '' , myText = '' ):
    if DBG:
        from debug import printDEBUG
        printDEBUG( myFUNC , myText, logFileName = 'MSNcomponents.log' )

def getWindIcon(iconName = None):
    retPNG = None
    DEBUG('icons.getWindIcon' , 'iconName: %s ' % iconName)
    if iconName is None or iconName == '':
        return None
    elif iconName == 'N': 
        retPNG = '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w000_polnoc.png'
    elif iconName in ('NE', 'ENE', 'NNE'): 
        retPNG = '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w045_polnocny_wschod.png'
    elif iconName == 'E': 
        retPNG = '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w090_wschod.png'
    elif iconName in ('SE', 'SSE', 'ESE'): 
        retPNG = '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w135_poludniowy_wschod.png'
    elif iconName == 'S': 
        retPNG = '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w180_poludnie.png'
    elif iconName in ('SW', 'WSW', 'SSW'): 
        retPNG = '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w225_poludniowy_zachod.png'
    elif iconName == 'W': 
        retPNG = '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w270_zachod.png'
    elif iconName in ('NW', 'WNW', 'NNW'): 
        retPNG = '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w315_polnocny_zachod.png'
    else:
        return None

    if not retPNG is None and os.path.exists(retPNG):
        DEBUG('icons.getWindIcon ' , 'retPNG: %s ' % retPNG)
        return LoadPixmap(cached=False, path=retPNG)
    else:
        return None
    
