# -*- coding: utf-8 -*-
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
try:
    from Plugins.Extensions.UserSkin.inits import myDEBUG, myDEBUGfile, PluginName
except Exception:
    PluginName = 'UserSkinDebug'
    myDEBUG=True
    myDEBUGfile = '/tmp/%s.log' % PluginName

from datetime import datetime

append2file=False
def printDEBUG( myText  , myFUNC = '' ):
    global append2file
    if myDEBUG or 'exception' in myText.lower() or 'exception' in myFUNC.lower():
        try:
            print ("[%s%s] %s" % (PluginName,myFUNC,myText))
            if append2file == False:
                append2file = True
                f = open(myDEBUGfile, 'w')
            else:
                f = open(myDEBUGfile, 'a')
                f.write('%s\t%s\n' % (str(datetime.now()), myText))
            f.close
        except Exception:
            pass

printDBG=printDEBUG
str(datetime.now())
