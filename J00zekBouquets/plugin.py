from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Plugins.Plugin import PluginDescriptor

def main(session, **kwargs):
    from Plugins.Extensions.J00zekBouquets.j00zekBouquets import j00zekBouquets
    session.open(j00zekBouquets)

def menu(menuid, **kwargs):
    if menuid == 'scan':
        return [('j00zekBouquets', main, 'j00zekBouquets', None)]
    else:
        return []


def Plugins(**kwargs):
    return [PluginDescriptor(name='j00zekBouquets', where=PluginDescriptor.WHERE_MENU, fnc=menu)]
