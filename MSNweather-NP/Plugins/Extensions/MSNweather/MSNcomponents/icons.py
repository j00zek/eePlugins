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
    'bezchmurnie'                       :   '31.png',
    'burze'                             :   '35.png',
    'czesciowoslonecznie'               :   '30.png',
    'deszcz'                            :   '12.png',
    'deszczzesniegiem'                  :   '7.png',
    'lekkideszczzesniegiem'             :   '6.png',
    'mgla'                              :   '19.png',
    "niewielkieopadysniegu"             :   '13.png', 
    'opadydeszczu'                      :   '11.png',
    "opadysniegu"                       :   '14.png', 
    'przelotneopadysniegu'              :   '41.png',
    'przelotneopadydeszczuzesniegiem'   :   '41.png',
    'przewazniebezchmurnie'             :   '31.png',
    'przewaznieslonecznie'              :   '34.png',
    'silneburze'                        :   '37.png',
    "slabeopadydeszczu"                 :   '9.png',
    'slonecznie'                        :   '32.png',
    'snieg'                             :   '16.png',
    "zachmurzeniecalkowite"             :   '26.png',
    'zachmurzenieduze'                  :   ['28.png', '27.png'],
    'zachmurzeniemale'                  :   ['30.png', '29.png'],
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
    'BB1kKUu.png'	: '',
    'BB1kKVy.png'	: '27.png',
    'BB1kMP0.png'	: '',
    'BB1kc8s.png'	: '26.png',
    'BB1kj0A.png'	: '',
    'BB1kvFq.png'	: '',
    'BB1kvzy.png'	: '28.png',
    'BBaBrK.png'	: '',
    'BBaGxJ.png'	: '26.png',
    'BBaLQW.png'	: '28.png',
    'BBaM7D.png'	: '27.png',
    'BBaRv1.png'	: '',
    'BBaWqy.png'	: '16.png',
    'BBaWvD.png'	: '',
    'BBaWwj.png'	: '',
    'BBaYXh.png'	: '41.png',
    'BBayJl.png'	: '',
    'BBb3WX.png'	: '',
    'BBb49j.png'	: '13.png',
    'BBb4eF.png'	: '',
    'BBb75E.png'	: '',
    'BBb9wG.png'	: '',
    'BBi9D1.png'	: '',
    'BBi9ul.png'	: '9.png',
    'BBiAZc.png'	: '',
    'BBih5H.png'	: '',
    'BBiwNf.png'	: '',
    #Mapowanie odwrotne
    "9.png"         :   'BBi9ul.png',
    "26.png"        :   'BB1kc8s.png',
    '27.png'        :   'BB1kKVy.png',
    '28.png'        :   'BB1kvzy.png',
    }
