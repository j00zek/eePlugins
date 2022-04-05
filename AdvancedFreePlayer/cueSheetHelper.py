from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Plugins.Extensions.AdvancedFreePlayer.__init__ import printDEBUG
from os import path as os_path
import struct
cutsParser = struct.Struct('>QI') # big-endian, 64-bit PTS and 32-bit type
CUT_TYPE_LAST = 3
CUT_TYPE_LENGTH = 5

DBG = False

def setCut(cutsFileName, LastPosition, Movielength):
    if LastPosition is None or LastPosition == 0 or Movielength is None or Movielength == 0:
        printDEBUG('setCut>LastPosition or Movielength not provided, end')
        return
    printDEBUG('setCut(%s, LastPosition=%d, Movielength=%d):' % (cutsFileName,LastPosition, Movielength))
    CUT_LAST_VALUE = struct.pack('>QI', LastPosition, CUT_TYPE_LAST)
    CUT_LENG_VALUE = struct.pack('>QI', Movielength, CUT_TYPE_LENGTH)
    resetMoviePlayState(cutsFileName,CUT_LAST_VALUE, CUT_LENG_VALUE)
    return

def getCut(cutsFileName):
    if DBG: printDEBUG('getCut(%s):' % cutsFileName)
    data = ''
    currpts=0
    currLength=0
    if os_path.exists(cutsFileName):
        try:
            f = open(cutsFileName, 'rb')
            data = f.read()
            f.close()
        except Exception:
            pass
        if data:
            pos = 0
            while pos + 12 <= len(data):
                pts, what = struct.unpack('>QI', data[pos:pos + 12])
                if what == CUT_TYPE_LAST and pts > currpts:
                    currpts = int(pts/90/1000/60) #in mins
                elif what == CUT_TYPE_LENGTH and pts > currLength:
                    currLength = int(pts/90/1000/60)
                if DBG: printDEBUG("getCuts found: what=%d, pts=%d (%d mins)" %(what, pts, currpts))
                pos += 12
    return currpts,currLength

def resetMoviePlayState(cutsFileName, CUT_LAST_VALUE = None, CUT_LENG_VALUE = None):
    if CUT_LAST_VALUE is None or CUT_LENG_VALUE is None:
        printDEBUG('resetMoviePlayState(%s, CUT_LAST_VALUE=None, CUT_LENG_VALUE=None) >>> exiting!!!' % (cutsFileName))
        return
    else:
        printDEBUG('resetMoviePlayState(%s, CUT_LAST_VALUE=%s, CUT_LENG_VALUE=%s):' % (cutsFileName, ':'.join(x.encode('hex') for x in CUT_LAST_VALUE), ':'.join(x.encode('hex') for x in CUT_LENG_VALUE) ))
    cutlist = []
    if os_path.exists(cutsFileName):
        try:
            f = open(cutsFileName, 'rb')
            while 1:
                data = f.read(cutsParser.size)
                if len(data) < cutsParser.size:
                    break
                cut, cutType = cutsParser.unpack(data)
                if cutType not in [CUT_TYPE_LAST, CUT_TYPE_LENGTH]:
                    cutlist.append(data)
            f.close()
        except Exception as e:
            printDEBUG('resetMoviePlayState exception reading cuts file %s' % str(e))
    cutlist.append(CUT_LAST_VALUE)
    cutlist.append(CUT_LENG_VALUE)
    try:
        if len(cutlist) > 0:
            f = open(cutsFileName, 'wb')
            f.write(''.join(cutlist))
            f.close()
            printDEBUG('resetMoviePlayState has written cutsFileName len(cutlist)=%d, cutlist=%s' % ( len(cutlist), ':'.join(x.encode('hex') for x in ''.join(cutlist))))
            printDEBUG(''.join(cutlist))
    except Exception as e:
        printDEBUG('resetMoviePlayState exception writing cuts file %s' % str(e))

def clearLastPosition(cutsFileName):
    cutlist = []
    if os_path.exists(cutsFileName):
        try:
            f = open(cutsFileName, 'rb')
            while 1:
                data = f.read(cutsParser.size)
                if len(data) < cutsParser.size:
                    break
                cut, cutType = cutsParser.unpack(data)
                if cutType not in [CUT_TYPE_LAST]:
                    cutlist.append(data)
            f.close()
        except Exception as e:
            printDEBUG('clearLastPosition exception reading cuts file %s' % str(e))
        try:
            if len(cutlist) > 0:
                f = open(cutsFileName, 'wb')
                f.write(''.join(cutlist))
                f.close()
                printDEBUG('clearLastPosition has written cutsFileName len(cutlist)=%d, cutlist=%s' % ( len(cutlist), ':'.join(x.encode('hex') for x in ''.join(cutlist))))
                printDEBUG(''.join(cutlist))
        except Exception as e:
            printDEBUG('clearLastPosition exception writing cuts file %s' % str(e))
        