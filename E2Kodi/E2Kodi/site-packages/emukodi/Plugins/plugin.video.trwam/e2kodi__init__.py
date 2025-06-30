#to jest po to, zeby sciezki we wtyczkach sie zgadzaly
#dostosowane pod dodatek sciezki nalezy umiescic na github w own_e2kodi__init__.py
# w skrypcie dodatku dopisac na poczatku import e2kodi__init__ # aby zainicjowac sciezki i nie musiec zmieniac czegos w kodzie

import sys
for pTa in ['/usr/lib/enigma2/python/Plugins/Extensions/E2Kodi/site-packages/emukodi',
           ]:
  if pTa not in sys.path:
    sys.path.append(pTa)
