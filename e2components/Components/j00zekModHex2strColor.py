#
# j00zek: this file has changed name just to avoid errors using opkg (situation when file was installed by different pockage)
# and make it available for images whic doesn't have it e.g. VTI
#
# Converts hex colors to formatted strings,
# suitable for embedding in python code.
#
# hex:
# 0 1 2 3 4 5 6 7 8 9 a b c d e f
# converts to:
# 0 1 2 3 4 5 6 7 8 9 : ; < = > ?

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
  }