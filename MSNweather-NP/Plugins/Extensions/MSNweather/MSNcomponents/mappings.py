# -*- coding: utf-8 -*- 
"""
####################################################################### 
#
#   This script resolves issue with freezing E2 in case of network problems and speeds-up everything
#   Coded by j00zek (c)2020-2021
#
#    Uszanuj moja decyzje i prace i ...
#              - nie kasuj/zmieniaj informacji kto jest autorem skryptu
#
#    Please respect my decision and work and ...
#              - don't delete/change name of the script author
#     
####################################################################### 
"""

def Hex2strColor(rgb):
  out = ""
  for i in range(28, -1, -4):
    out += "%s" % chr(0x30 + (rgb >> i & 0x0F))
  return "\c%s" % out

clr={'Y':           Hex2strColor(0x00ffcc00), #yellow
     'R':           Hex2strColor(0x00FF3333), #red
     'G':           Hex2strColor(0x0066FF33), #green
     'B':           Hex2strColor(0x0033ccff), #blue
     'O':           Hex2strColor(0x00ffcc00), #orange
     'Gray':        Hex2strColor(0x00e6e6e6),
     'VeryGood':    Hex2strColor(0x00009900),
     'VERY_GOOD':   Hex2strColor(0x00009900),
     'Good':        Hex2strColor(0x0099FF33),
     'GOOD':        Hex2strColor(0x0099FF33),
     'Moderate':    Hex2strColor(0x00FFFF00),
     'MODERATE':    Hex2strColor(0x00FFFF00),
     'satisfactory':Hex2strColor(0x00FF6600),
     'ACCEPTABLE':  Hex2strColor(0x00FF6600),
     'Bad':         Hex2strColor(0x00FF0000),
     'BAD':         Hex2strColor(0x00FF0000),
     'VeryBad':     Hex2strColor(0x00990000),
     'VERY_BAD':    Hex2strColor(0x00990000),
     'Żółty':       Hex2strColor(0x00ffcc00),
     'Czerwony':    Hex2strColor(0x00FF3333),
     'Yellow':      Hex2strColor(0x00ffcc00),
     'Red':         Hex2strColor(0x00FF3333),
    }

def Temperature2strColor(temp):
    retVal = ''
    temp = int(temp)
    if temp < -20:
        retVal = Hex2strColor(0x009966ff)
    elif temp < -10:
        retVal = Hex2strColor(0x003366ff)
    elif temp < 0:
        retVal = Hex2strColor(0x000099ff)
    elif temp < 10:
        retVal = Hex2strColor(0x0000ffff)
    elif temp < 20:
        retVal = Hex2strColor(0x0000ff00)
    elif temp < 30:
        retVal = Hex2strColor(0x00ffff66)
    elif temp < 40:
        retVal = Hex2strColor(0x00ffcc66)
    elif temp < 50:
        retVal = Hex2strColor(0x00ff9999)
    else:
        retVal = Hex2strColor(0x00ff99cc)
    return retVal

def airQualityInfo(key, val, retLevel = False):
    info = ''
    colorCode = ''
    if val != '' and key != '':
        val = float(val)
        if key in ('pm25','pm25'):
            if   val <= 12 :
                colorCode = clr['VeryGood']
                if retLevel: info = 0
                else: info = 'Very good'
            elif val <= 36 :
                colorCode = clr['Good']
                if retLevel: info = 1
                else: info =  'Good'
            elif val <= 60 :
                colorCode = clr['Moderate'] 
                if retLevel: info = 2
                else: info =  'Moderate'
            elif val <= 84 :
                colorCode = clr['satisfactory']
                if retLevel: info = 3
                else: info =  'satisfactory'
            elif val <=120 :
                colorCode = clr['Bad']
                if retLevel: info = 4
                else: info =  'Bad'
            else:
                colorCode = clr['VeryBad']
                if retLevel: info = 5
                else: info =  'Very bad'
        elif key == 'pm10':
            if   val <= 20 :
                colorCode = clr['VeryGood']
                if retLevel: info = 0
                else: info =  'Very good'
            elif val <= 60 :
                colorCode = clr['Good']
                if retLevel: info = 1
                else: info =  'Good'
            elif val <=100 :
                colorCode = clr['Moderate']
                if retLevel: info = 2
                else: info =  'Moderate'
            elif val <=140 :
                colorCode = clr['Bad']
                if retLevel: info = 3
                else: info =  'satisfactory'
            elif val <=200 :
                colorCode = clr['Gray']
                if retLevel: info = 4
                else: info =  'Bad'
            else:
                colorCode = clr['VeryBad']
                if retLevel: info = 5
                else: info =  'Very bad'
        elif key == 'pm1off':
            if   val <= 20 :
                colorCode = clr['VeryGood']
                if retLevel: info = 0
                else: info =  'Very good'
            elif val <= 60 :
                colorCode = clr['Good']
                if retLevel: info = 1
                else: info =  'Good'
            elif val <=100 :
                colorCode = clr['Moderate']
                if retLevel: info = 2
                else: info =  'Moderate'
            elif val <=140 :
                colorCode = clr['satisfactory']
                if retLevel: info = 3
                else: info =  'satisfactory'
            elif val <=200 :
                colorCode = clr['Bad']
                if retLevel: info = 4
                else: info =  'Bad'
            else:
                colorCode = clr['VeryBad']
                if retLevel: info = 5
                else: info =  'Very bad'
        elif key == 'o3':
            if   val <= 79 :
                colorCode = clr['VeryGood']
                if retLevel: info = 0
                else: info =  'Very good'
            elif val <=120 :
                colorCode = clr['Good']
                if retLevel: info = 1
                else: info =  'Good'
            elif val <=150 :
                colorCode = clr['Moderate']
                if retLevel: info = 2
                else: info =  'Moderate'
            elif val <=180 :
                colorCode = clr['satisfactory']
                if retLevel: info = 3
                else: info =  'satisfactory'
            elif val <=240 :
                colorCode = clr['Bad']
                if retLevel: info = 4
                else: info =  'Bad'
            else:
                colorCode = clr['VeryBad']
                if retLevel: info = 5
                else: info =  'Very bad'
        elif key == 'no2':
            if   val <= 40 :
                colorCode = clr['VeryGood']
                if retLevel: info = 0
                else: info =  'Very good'
            elif val <=100 : 
                colorCode = clr['Good']
                if retLevel: info = 1
                else: info =  'Good'
            elif val <=150 :
                colorCode = clr['Moderate']
                if retLevel: info = 2
                else: info =  'Moderate'
            elif val <=200 : 
                colorCode = clr['satisfactory']
                if retLevel: info = 3
                else: info =  'satisfactory'
            elif val <=400 :
                if retLevel: info = 4
                else: colorCode = clr['Bad']
                info =  'Bad'
            else:
                if retLevel: info = 5
                else: colorCode = clr['VeryBad']
                info =  'Very bad'
        elif key == 'so2':
            if   val <= 50 :
                colorCode = clr['VeryGood']
                if retLevel: info = 0
                else: info =  'Very good'
            elif val <=100 :
                colorCode = clr['Good']
                if retLevel: info = 1
                else: info =  'Good'
            elif val <=200 :
                colorCode = clr['Moderate']
                if retLevel: info = 2
                else: info =  'Moderate'
            elif val <=350 :
                colorCode = clr['satisfactory']
                if retLevel: info = 3
                else: info =  'satisfactory'
            elif val <=500 :
                colorCode = clr['Bad']
                if retLevel: info = 4
                else: info =  'Bad'
            else:
                colorCode = clr['VeryBad']
                if retLevel: info = 5
                else: info =  'Very bad'
        elif key == 'c6h6':
            if   val <=  6 :
                colorCode = clr['VeryGood']
                if retLevel: info = 0
                else: info =  'Very good'
            elif val <= 11 :
                colorCode = clr['Good']
                if retLevel: info = 1
                else: info =  'Good'
            elif val <= 16 :
                colorCode = clr['Moderate']
                if retLevel: info = 2
                else: info =  'Moderate'
            elif val <= 21 :
                colorCode = clr['satisfactory']
                if retLevel: info = 3
                else: info =  'satisfactory'
            elif val <= 51 :
                colorCode = clr['Bad']
                if retLevel: info = 4
                else: info =  'Bad'
            else:
                colorCode = clr['VeryBad']
                if retLevel: info = 5
                else: info =  'Very bad'
        elif key == 'co':
            if   val <=  3 :
                colorCode = clr['VeryGood']
                if retLevel: info = 0
                else: info =  'Very good'
            elif val <=  7 :
                colorCode = clr['Good']
                if retLevel: info = 1
                else: info =  'Good'
            elif val <= 11 :
                colorCode = clr['Moderate']
                if retLevel: info = 2
                else: info =  'Moderate'
            elif val <= 15 :
                colorCode = clr['satisfactory']
                if retLevel: info = 3
                else: info =  'satisfactory'
            elif val <= 21 :
                colorCode = clr['Bad']
                if retLevel: info = 4
                else: info =  'Bad'
            else:
                colorCode = clr['VeryBad']
                if retLevel: info = 5
                else: info =  'Very bad'

    return colorCode, info

def getWindIconName(iconName = None):
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
    'gestamgla'                         :   '19.png',
    'lekkideszczzesniegiem'             :   '6.png',
    'mgla'                              :   '19.png',
    "niewielkieopadysniegu"             :   '13.png', 
    'opadydeszczu'                      :   '11.png',
    "opadysniegu"                       :   '14.png', 
    'przelotneopadysniegu'              :   '41.png',
    'przelotneopadydeszczuzesniegiem'   :   '71.png',
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

paramsNames={
        'NO2'   : 'dwutlenek azotu',
        'no2'   : 'dwutlenek azotu',
        'PM1'   : 'pył zawieszony PM1',
        'pm1'   : 'pył zawieszony PM1',
        'PM10'  : 'pył zawieszony PM10',
        'pm10'  : 'pył zawieszony PM10',
        'PM2.5' : 'pył zawieszony PM2.5',
        'pm2.5' : 'pył zawieszony PM2.5',
        'PM25'  : 'pył zawieszony PM2.5',
        'pm25'  : 'pył zawieszony PM2.5',
        'O3'    : 'ozon',
        'o3'    : 'ozon',
        'C6H6'  : 'benzen',
        'c6h6'  : 'benzen',
    }