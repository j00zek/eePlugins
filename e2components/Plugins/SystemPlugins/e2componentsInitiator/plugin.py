#######################################################################
#
#  Coded by j00zek (c)2020-2021
#
#  Uszanuj moja prace i nie kasuj/zmieniaj informacji kto jest autorem renderera
#  Please respect my work and don't delete/change name of the renderer author
#
#  Nie zgadzam sie na wykorzystywanie tego skryptu w projektach platnych jak np. Graterlia!!!
#
#  Prosze NIE dystrybuowac tego skryptu w formie archwum zip, czy tar.gz
#  Zgadzam sie jedynie na dystrybucje z repozytorium opkg
#
################################################################################
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
######################################################################################
def sessionstart(session, **kwargs):
    try:
        from Components.Sources.j00zekStaticSource import j00zekStaticSource
        session.screen['j00zekStaticSource'] = j00zekStaticSource()
        print("e2components config initiated")
        #open("/tmp/j00zekStaticSource.log", "w").write('j00zekStaticSource initiated')
    except Exception as e:
        print("Exception for e2components: %s" % str(e))
        open("/tmp/j00zekStaticSource.exception", "w").write('Exception for e2components: %s' % str(e))

def Plugins(**kwargs):
    return [PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=sessionstart)]
