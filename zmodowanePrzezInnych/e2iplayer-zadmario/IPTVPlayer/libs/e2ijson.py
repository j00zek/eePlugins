# -*- coding: utf-8 -*-

###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc, byteify
###################################################
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import isPY2
###################################################
# FOREIGN import
###################################################
try:
    import json
except Exception:
    import simplejson as json

if isPY2():
    e2icjson = None
else: #e2icjson is not stable on py3 images, disabling is the best option for now
    e2icjson = False

############################################


def loads(inputString, noneReplacement=None, baseTypesAsString=False, utf8=True):
    global e2icjson

    if not isPY2(): # PY3 works with utf8 so we can't use this flag with it
        utf8 = False

    if e2icjson == None:
        if isPY2():
            try:
                from Plugins.Extensions.IPTVPlayer.libs.e2icjson import e2icjson
                e2icjson = e2icjson
            except Exception:
                e2icjson = False
        else:
            try:
                import e2icjson  #p3 should have it installed in site-packages through opkg
                e2icjson = e2icjson
            except Exception:
                e2icjson = False

    if e2icjson:
        printDBG(">> cjson ACELERATION noneReplacement[%s] baseTypesAsString[%s]" % (noneReplacement, baseTypesAsString))
        try:
            outDict = e2icjson.decode(inputString, 2 if utf8 else 1)
        except Exception as e:
            # TEMPORARY: SHOULD BE DEEPLY INVESTIGATED why cjson sometimes fails but json not
            printDBG(">> cjson FAILED with EXCEPTION: %s" % str(e))
            printDBG("\t Problematic inputString = '%s'" % inputString)
            printDBG(">> Trying with regular json module")
            outDict = json.loads(inputString)
    else:
        outDict = json.loads(inputString)

    if utf8 or noneReplacement != None or baseTypesAsString != False:
        return byteify(outDict, noneReplacement, baseTypesAsString)
    else:
        return outDict


def dumps(inputString, *args, **kwargs):
    return json.dumps(inputString, *args, **kwargs)
