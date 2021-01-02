# -*- coding: utf-8 -*- 

import os

DBG = False

def DEBUG(myFUNC = '' , myText = '' ):
    if DBG:
        from debug import printDEBUG
        printDEBUG( myFUNC , myText, logFileName = 'MSNcomponents.log' )


def getWindIconName(iconName = None):
    DEBUG('icons.getWindIconName' , 'iconName: %s ' % iconName)
    if iconName is None or iconName == '':
        return None
    elif iconName == 'N': 
        return '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w000_polnoc.png'
    elif iconName in ('NE', 'ENE', 'NNE'): 
        return '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w045_polnocny_wschod.png'
    elif iconName == 'E': 
        return '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w090_wschod.png'
    elif iconName in ('SE', 'SSE', 'ESE'): 
        return '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w135_poludniowy_wschod.png'
    elif iconName == 'S': 
        return '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w180_poludnie.png'
    elif iconName in ('SW', 'WSW', 'SSW'): 
        return '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w225_poludniowy_zachod.png'
    elif iconName == 'W': 
        return '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w270_zachod.png'
    elif iconName in ('NW', 'WNW', 'NNW'): 
        return '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w315_polnocny_zachod.png'
    else:
        return None

iconsMap={
#                                            dzien  ,   noc                        
    'lekkideszczzesniegiem'             :   '6.png',
    'deszczzesniegiem'                  :   '7.png',
    "slabeopadydeszczu"                 :   '9.png',
    'opadydeszczu'                      :   '11.png',
    'deszcz'                            :   '12.png',
    "niewielkieopadysniegu"             :   '13.png', 
    "opadysniegu"                       :   '14.png', 
    'snieg'                             :   '16.png',
    'mgla'                              :   '19.png',
    "zachmurzeniecalkowite"             :   '26.png',
    'zachmurzenieduze'                  :   ['28.png', '27.png'],
    'zachmurzeniemale'                  :   ['30.png', '29.png'],
    'czesciowoslonecznie'               :   '30.png',
    'bezchmurnie'                       :   '31.png',
    'przewazniebezchmurnie'             :   '31.png',
    'slonecznie'                        :   '32.png',
    'przewaznieslonecznie'              :   '34.png',
    'burze'                             :   '35.png',
    'silneburze'                        :   '37.png',
    'przelotneopadydeszczuzesniegiem'   :   '41.png',
    #EN
    "rainshowers"                       :   '9.png',
    'lightrain'                         :   '11.png',
    'rain'                              :   '12.png',
    'cloudy'                            :   '26.png',
    'sunny'                             :   '32.png',
    'mostlysunny'                       :   '34.png',
    #DE
    'leichterregenundschnee'            :   '6.png',
    'leichterregen'                     :   '9.png',
    'regenschauer'                      :   '11.png',
    'regen'                             :   '12.png',
    'schnee'                            :   '16.png',
    "bewoelkt"                          :   '26.png',
    "meistbewoelkt"                     :   '28.png',
    "teilweisebewoelkt"                 :   '29.png',
    'teilweisesonnig'                   :   '30.png',
    'sonnig'                            :   '32.png',
    'ueberwiegendsonnig'                :   '34.png',
    'gewitter'                          :   '35.png',
    #Mapowanie poprzez img
    '1'             :   '6.png',
    "BBi9ul.png"                        :   '9.png',
    '3'                      :   '11.png',
    '4'                            :   '12.png',
    "5"             :   '13.png', 
    "6"                       :   '14.png', 
    '7'                             :   '16.png',
    "BB1kc8s.png"                       :   '26.png',
    'BB1kKVy.png'                       :   '27.png',
    'BB1kvzy.png'                       :   '28.png',
    '0'                  :   '29.png',
    '-'               :   '30.png',
    'q'                       :   '31.png',
    'w'                        :   '32.png',
    'e'              :   '34.png',
    'r'                             :   '35.png',
    't'                        :   '37.png',
    'y'   :   '41.png',
    #Mapowanie odwrotne
    "9.png"                             :   'BBi9ul.png',
    "26.png"                            :   'BB1kc8s.png',
    '27.png'                            :   'BB1kKVy.png',
    '28.png'                            :   'BB1kvzy.png',
    }
