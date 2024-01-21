import os, traceback

def printDBG(DBGtxt, writeMode = 'a'):
    print(DBGtxt)
    DBG = True
    if DBG:
        DBGfile = '/tmp/kodiLauncher.log'
        try:
            f = open(DBGfile, writeMode)
            f.write(str(DBGtxt) + '\n')
            f.close
        except Exception:
            print("======================EXC printDBG======================")
            print("printDBG(I): %s" % traceback.format_exc())
            print("========================================================")
            try:
                msg = '%s' % traceback.format_exc()
                f = open(DBGfile, writeMode)
                f.write(str(DBGtxt) + '\n')
                f.close
            except Exception:
                print("======================EXC printDBG======================")
                print("printDBG(II): %s" % traceback.format_exc())
                print("========================================================")


def printExc(msg='', WarnOnly = False):
    printDBG("===============================================")
    printDBG("                   EXCEPTION                   ")
    printDBG("===============================================")
    exc_formatted = traceback.format_exc()
    msg = msg + ': \n%s' % exc_formatted
    printDBG(msg)
    printDBG("===============================================")
    return
