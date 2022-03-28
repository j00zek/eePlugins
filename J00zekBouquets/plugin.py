from Plugins.Plugin import PluginDescriptor

def main(session, **kwargs):
    from j00zekBouquets import j00zekBouquets
    session.open(j00zekBouquets)

def menu(menuid, **kwargs):
    if menuid == 'scan':
        return [('j00zekBouquets', main, 'j00zekBouquets', None)]
    else:
        return []


def Plugins(**kwargs):
    return [PluginDescriptor(name='j00zekBouquets', where=PluginDescriptor.WHERE_MENU, fnc=menu)]
