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
    if retLevel: info = -1
    else: info = ''
    colorCode = ''
    if val != '' and key != '':
        val = float(val)
        if key in ('pm2.5','pm25'):
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
        elif key == 'pm1': #https://fotoacc.pl/normy-jakosci-powietrza-w-polsce/
            if   val <= 11 :
                colorCode = clr['VeryGood']
                if retLevel: info = 0
                else: info =  'Very good'
            elif val <= 31 :
                colorCode = clr['Good']
                if retLevel: info = 1
                else: info =  'Good'
            elif val <=51 :
                colorCode = clr['Moderate']
                if retLevel: info = 2
                else: info =  'Moderate'
            elif val <=71 :
                colorCode = clr['satisfactory']
                if retLevel: info = 3
                else: info =  'satisfactory'
            elif val <=101 :
                colorCode = clr['Bad']
                if retLevel: info = 4
                else: info =  'Bad'
            else:
                colorCode = clr['VeryBad']
                if retLevel: info = 5
                else: info =  'Very bad'
        elif key in ('o3', 'ozone'):
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
        elif key == 'co': #https://fotoacc.pl/normy-jakosci-powietrza-w-polsce/
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
    try:
        dirInt = int(iconName)
        dirInt = int(dirInt / 22.5)
    except Exception:
        dirInt = -1
        
    if iconName is None or iconName == '':
        return None
    elif iconName == 'N' or dirInt in (0,16): 
        return '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w000_polnoc.png'
    elif iconName in ('NE', 'ENE', 'NNE') or dirInt in (1,2): 
        return '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w045_polnocny_wschod.png'
    elif iconName == 'E' or dirInt in (3,4): 
        return '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w090_wschod.png'
    elif iconName in ('SE', 'SSE', 'ESE') or dirInt in (5,6): 
        return '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w135_poludniowy_wschod.png'
    elif iconName == 'S' or dirInt in (7,8): 
        return '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w180_poludnie.png'
    elif iconName in ('SW', 'WSW', 'SSW') or dirInt in (9,10): 
        return '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w225_poludniowy_zachod.png'
    elif iconName == 'W' or dirInt in (11,12): 
        return '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w270_zachod.png'
    elif iconName in ('NW', 'WNW', 'NNW') or dirInt in (13,15): 
        return '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/w315_polnocny_zachod.png'
    else:
        return None

def getWindSummary(windSpeed):
    WindInfo = ''
    try:
        windSpeed = int(windSpeed)
        if windSpeed < 1: WindInfo = 'Będzie bezwietrznie'
        elif windSpeed <= 5: WindInfo = 'Powiewy o prędkości %s km/h' % windSpeed
        elif windSpeed <= 11: WindInfo = 'Wiatr słaby o prędkości %s km/h' % windSpeed
        elif windSpeed <= 19: WindInfo = 'Wiatr łagodny o prędkości %s km/h' % windSpeed
        elif windSpeed <= 28: WindInfo = 'Wiatr umiarkowany o prędkości %s km/h' % windSpeed
        elif windSpeed <= 38: WindInfo = 'Wiatr dość silny o prędkości %s km/h' % windSpeed
        elif windSpeed <= 49: WindInfo = 'Wiatr silny o prędkości %s km/h' % windSpeed
        elif windSpeed <= 61: WindInfo = 'Wiatr bardzo silny o prędkości %s km/h' % windSpeed
        elif windSpeed <= 74: WindInfo = 'Wiatr gwałtowny o prędkości %s km/h' % windSpeed
        elif windSpeed <= 88: WindInfo = 'Wichura o prędkości %s km/h' % windSpeed
        elif windSpeed <= 102: WindInfo = 'Silna wichura o prędkości %s km/h' % windSpeed
        elif windSpeed <= 117: WindInfo = 'Gwałtowna wichura o prędkości %s km/h' % windSpeed
        else: WindInfo = 'Huragan o prędkości %s km/h'
    except Exception:
        pass
    return WindInfo

defaultIconsData = {
                    1: "/usr/share/enigma2/BlackHarmony/weather_icons/32.png",
                    2: "/usr/share/enigma2/BlackHarmony/weather_icons/34.png",
                    3: "/usr/share/enigma2/BlackHarmony/weather_icons/30.png",
                    4: "/usr/share/enigma2/BlackHarmony/weather_icons/82.png",
                    19: "/usr/share/enigma2/BlackHarmony/weather_icons/9.png",
                    22: "/usr/share/enigma2/BlackHarmony/weather_icons/12.png",
                    23: "/usr/share/enigma2/BlackHarmony/weather_icons/11.png",
                    28: "/usr/share/enigma2/BlackHarmony/weather_icons/31.png",
                    29: "/usr/share/enigma2/BlackHarmony/weather_icons/31.png",
                    30: "/usr/share/enigma2/BlackHarmony/weather_icons/30.png",
                    31: "/usr/share/enigma2/BlackHarmony/weather_icons/82.png" 
                    }
iconsMap={
    #Mapowanie poprzez svg (foreca) https://svgtopng.com/
    'd0000.png' : '34.png', #slonecznie
    'd1000.png' : '34.png', #przewaznieslonecznie
    'd2000.png' : '30.png', #czesciowoslonecznie
    'd2100.png' : '9.png',
    'd2120.png' : '9.png',  #niewielkieopadysniegu
    'd2220.png' : '9.png',  #opadysniegu
    'd3000.png' : '82.png', #duzezachmurzenie
    'd3100.png' : '9.png',  #lekkieprzelotneopadydeszczu, slabeopadydeszczu
    'd3101.png' : '75.png', #lekkie przelotnie opady deszczu / wiatr
    'd3110.png' : '9.png',  #lekkieprzelotneopadydeszczuzesniegiem
    'd3120.png' : '9.png',  #niewielkieopadysniegu, lekkieprzelotneopadysniegu
    'd3121.png' : '9.png',  #lekkieprzelotneopadysniegu/wiatr 
    'd3200.png' : '9.png',
    'd3211.png' : '9.png',  #przelotneopadydeszczuzesniegiem/wiatr 
    'd3220.png' : '9.png',  #opadysniegu
    'd3400.png' : '35.png',
    'd4000.png' : '26.png',
    'd4100.png' : '9.png',  #slabeopadydeszczu
    'd4200.png' : '11.png', #opadydeszczu
    'd4201.png' : '9.png',  #deszcz/wiat
    'd4210.png' : '111.png',#deszczzesniegiem
    'd4211.png' : '111.png',#deszczzesniegiem
    'd4220.png' : '9.png',  #snieg
    'd4300.png' : '9.png',  #ulewnydeszcz
    'd4301.png' : '9.png',  #deszcz
    'd4311.png' : '111.png',#deszczzesniegiem
    'd4320.png' : '9.png',  #obfiteopadysniegu, snieg
    'd4400.png' : '37.png',
    'd2400.png' : '35.png',
    'd6000.png' : '19.png', #mgla

    'n0000.png' : '31.png', #bezchmurnie
    'n1000.png' : '31.png', #przewazniebezchmurnie
    'n2000.png' : '29.png', #zachmurzeniemale
    'n2001.png' : '29.png', #zachmurzeniemale/wiatr
    'n2120.png' : '13.png', #niewielkieopadysniegu
    'n3000.png' : '83.png', #duzezachmurzenie
    'n3100.png' : '9.png',  #niewielkieopadydeszczu
    'n3110.png' : '9.png',  #lekkideszczzesniegiem
    'n3120.png' : '13.png', #niewielkieopadysniegu
    'n3121.png' : '13.png', #niewielkieopadysniegu
    'n3200.png' : '11.png',
    'n4000.png' : '83.png', #zachmurzeniecalkowite
    'n4100.png' : '9.png',  #
    'n4121.png' : '13.png', #niewielkieopadysniegu
    'n4200.png' : '11.png', #deszcz
    'n4201.png' : '11.png', #deszcz/wiatr, deszcz
    'n4210.png' : '16.png', #deszczzesniegiem
    'n4220.png' : '16.png', #snieg
    'n4300.png' : '12.png', #deszcz
    'n4301.png' : '12.png', #deszcz
    'n4310.png' : '16.png', #deszczzesniegiem
    'n4320.png' : '16.png', #obfiteopadysniegu, snieg
    'n4321.png' : '16.png', #snieg

    'd000.png' : '32.png',
    'd100.png' : '34.png',
    'd200.png' : '28.png',  #Częściowe zachmurzenie
    'd210.png' : '72.png', 
    'd211.png' : '71.png',
    'd212.png' : '84.png',
    'd220.png' : '73.png', 
    'd221.png' : '86.png', #Częściowe zachmurzenie i przejściowe opady mokrego śniegu
    'd222.png' : '88.png',
    'd240.png' : '38.png', 
    'd300.png' : '82.png', #Zachmurzenie
    'd310.png' : '74.png', #Zachmurzenie i niewielkie opady deszczu
    'd311.png' : '90.png',
    'd312.png' : '92.png',
    'd320.png' : '75.png', #Zachmurzenie i przelotne opady deszczu
    'd321.png' : '94.png',
    'd322.png' : '96.png',
    'd340.png' : '37.png',
    'd400.png' : '26.png', #Pochmurnie
    'd410.png' : '9.png',
    'd411.png' : '98.png',
    'd412.png' : '13.png',
    'd420.png' : '80.png',
    'd421.png' : '99.png',
    'd422.png' : '14.png',
    'd430.png' : '81.png',
    'd431.png' : '100.png',
    'd432.png' : '16.png',
    'd440.png' : '17.png',
    'd500.png' : '101.png',
    'd600.png' : '20.png',
    
    'n000.png' : '31.png',
    'n100.png' : '33.png',
    'n200.png' : '27.png',
    'n210.png' : '76.png',
    'n211.png' : '70.png',
    'n212.png' : '85.png',
    'n220.png' : '77.png',
    'n221.png' : '87.png',
    'n222.png' : '89.png',
    'n240.png' : '48.png', 
    'n300.png' : '83.png',
    'n310.png' : '78.png',
    'n311.png' : '91.png',
    'n312.png' : '93.png',
    'n320.png' : '79.png',
    'n321.png' : '95.png',
    'n322.png' : '97.png',
    'n340.png' : '37.png',
    'n400.png' : '26.png',
    'n410.png' : '9.png',
    'n411.png' : '98.png',
    'n412.png' : '13.png',
    'n420.png' : '80.png',
    'n421.png' : '99.png',
    'n422.png' : '14.png',
    'n430.png' : '81.png',
    'n431.png' : '100.png',
    'n432.png' : '16.png',
    'n440.png' : '17.png',
    'n500.png' : '102.png',
    'n600.png' : '20.png',
    #Mapowanie poprzez img
    'AAehLNN.png'       : '82.png',
    'BB1kKUu.png'       : '',
    'BB1kKVy.png'       : '27.png',
    'BB1kMP0.png'       : '',
    'BB1kc8s.png'       : '26.png',
    'BB1kj0A.png'       : '',
    'BB1kvFq.png'       : '',
    'BB1kvzy.png'       : '28.png',
    'BBaBrK.png'        : '',
    'BBaGxJ.png'        : '26.png',
    'BBaLQW.png'        : '28.png',
    'BBaM7D.png'        : '27.png',
    'BBaRv1.png'        : '',
    'BBaWqy.png'        : '16.png',
    'BBaWvD.png'        : '',
    'BBaWwj.png'        : '',
    'BBaYXh.png'        : '41.png',
    'BBayJl.png'        : '',
    'BBb3WX.png'        : '',
    'BBb49j.png'        : '13.png',
    'BBb4eF.png'        : '',
    'BBb75E.png'        : '',
    'BBb9wG.png'        : '',
    'BBi9D1.png'        : '',
    'BBi9ul.png'        : '9.png',
    'BBiAZc.png'        : '',
    'BBih5H.png'        : '',
    'BBiwNf.png'        : '',
    #Mapowanie odwrotne
    "9.png"         :   'BBi9ul.png',
    '13.png'        :   'BBb49j.png',
    '16.png'        :   'BBaWqy.png',
    "26.png"        :   'BB1kc8s.png',
    '27.png'        :   'BB1kKVy.png',
    '28.png'        :   'BB1kvzy.png',
    }
