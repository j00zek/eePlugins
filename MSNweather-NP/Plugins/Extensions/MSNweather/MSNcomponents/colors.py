#!/usr/bin/python
# -*- coding: utf-8 -*- 
"""
####################################################################### 
#
#   This script resolves issue with freezing E2 in case of network problems and speeds-up everything
#   Coded by j00zek (c)2020
#
#    Uszanuj moja decyzje i prace i ...
#              - nie kasuj/zmieniaj informacji kto jest autorem skryptu
#
#    Please respect my decision and work and ...
#              - don't delete/change name of the script author
#     
####################################################################### 
"""
from debug import printDEBUG

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
     'Good':        Hex2strColor(0x0099FF33),
     'Moderate':    Hex2strColor(0x00FFFF00),
     'satisfactory':Hex2strColor(0x00FF6600),
     'Bad':         Hex2strColor(0x00FF0000),
     'VeryBad':     Hex2strColor(0x00990000),
     '¯ó³ty':       Hex2strColor(0x00ffcc00),
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

def airQualityInfo(key, val):
    info = ''
    colorCode = ''
    val = float(val)
    if key in ('pm25','pm25'):
        if   val <= 12 :
            colorCode = clr['VeryGood']
            info = 'Very good'
        elif val <= 36 :
            colorCode = clr['Good']
            info =  'Good'
        elif val <= 60 :
            colorCode = clr['Moderate'] 
            info =  'Moderate'
        elif val <= 84 :
            colorCode = clr['satisfactory']
            info =  'satisfactory'
        elif val <=120 :
            colorCode = clr['Bad']
            info =  'Bad'
        else:
            colorCode = clr['VeryBad']
            info =  'Very bad'
    elif key == 'pm10':
        if   val <= 20 :
            colorCode = clr['VeryGood']
            info =  'Very good'
        elif val <= 60 :
            colorCode = clr['Good']
            info =  'Good'
        elif val <=100 :
            colorCode = clr['Moderate']
            info =  'Moderate'
        elif val <=140 :
            colorCode = clr['Bad']
            info =  'satisfactory'
        elif val <=200 :
            colorCode = clr['']
            info =  'Bad'
        else:
            colorCode = clr['VeryBad']
            info =  'Very bad'
    elif key == 'pm1off':
        if   val <= 20 :
            colorCode = clr['VeryGood']
            info =  'Very good'
        elif val <= 60 :
            colorCode = clr['Good']
            info =  'Good'
        elif val <=100 :
            colorCode = clr['Moderate']
            info =  'Moderate'
        elif val <=140 :
            colorCode = clr['satisfactory']
            info =  'satisfactory'
        elif val <=200 :
            colorCode = clr['Bad']
            info =  'Bad'
        else:
            colorCode = clr['VeryBad']
            info =  'Very bad'
    elif key == 'o3':
        if   val <= 79 :
            colorCode = clr['VeryGood']
            info =  'Very good'
        elif val <=120 :
            colorCode = clr['Good']
            info =  'Good'
        elif val <=150 :
            colorCode = clr['Moderate']
            info =  'Moderate'
        elif val <=180 :
            colorCode = clr['satisfactory']
            info =  'satisfactory'
        elif val <=240 :
            colorCode = clr['Bad']
            info =  'Bad'
        else:
            colorCode = clr['VeryBad']
            info =  'Very bad'
    elif key == 'no2':
        if   val <= 40 :
            colorCode = clr['VeryGood']
            info =  'Very good'
        elif val <=100 : 
            colorCode = clr['Good']
            info =  'Good'
        elif val <=150 :
            colorCode = clr['Moderate']
            info =  'Moderate'
        elif val <=200 : 
            colorCode = clr['satisfactory']
            info =  'satisfactory'
        elif val <=400 :
            colorCode = clr['Bad']
            info =  'Bad'
        else:
            colorCode = clr['VeryBad']
            info =  'Very bad'
    elif key == 'so2':
        if   val <= 50 :
            colorCode = clr['VeryGood']
            info =  'Very good'
        elif val <=100 :
            colorCode = clr['Good']
            info =  'Good'
        elif val <=200 :
            colorCode = clr['Moderate']
            info =  'Moderate'
        elif val <=350 :
            colorCode = clr['satisfactory']
            info =  'satisfactory'
        elif val <=500 :
            colorCode = clr['Bad']
            info =  'Bad'
        else:
            colorCode = clr['VeryBad']
            info =  'Very bad'
    elif key == 'c6h6':
        if   val <=  6 :
            colorCode = clr['VeryGood']
            info =  'Very good'
        elif val <= 11 :
            colorCode = clr['Good']
            info =  'Good'
        elif val <= 16 :
            colorCode = clr['Moderate']
            info =  'Moderate'
        elif val <= 21 :
            colorCode = clr['satisfactory']
            info =  'satisfactory'
        elif val <= 51 :
            colorCode = clr['Bad']
            info =  'Bad'
        else:
            colorCode = clr['VeryBad']
            info =  'Very bad'
    elif key == 'co':
        if   val <=  3 :
            colorCode = clr['VeryGood']
            info =  'Very good'
        elif val <=  7 :
            colorCode = clr['Good']
            info =  'Good'
        elif val <= 11 :
            colorCode = clr['Moderate']
            info =  'Moderate'
        elif val <= 15 :
            colorCode = clr['satisfactory']
            info =  'satisfactory'
        elif val <= 21 :
            colorCode = clr['Bad']
            info =  'Bad'
        else:
            colorCode = clr['VeryBad']
            info =  'Very bad'

    return colorCode, info
