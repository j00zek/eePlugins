echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
echo "            pakowanie rozszerzen"
echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
extensionsPath=/DuckboxDisk/github/eePlugins/E2KodiAddons
find "$extensionsPath" -maxdepth 1 -mindepth 1 -type d | 
while read F 
do
  if [ -e "$F/CONTROL/control" ];then
    #ewentualna korekta DestinationPath
    pkgPathFolderName=`echo "$F"|sed "s;$extensionsPath; /usr/lib/enigma2/python/Plugins/Extensions/E2Kodi/site-packages/emukodi/Plugins;"`
    echo $extensionsPath
    echo $pkgPathFolderName
    sed -i "s;DestinationPath:.*$;DestinationPath: $pkgPathFolderName;" "$F/CONTROL/control"
    
   
    #nazwa paczki
    pathName=`dirname "$F"`
    pkgFolderName=`basename "$F"`
    pkgName=`echo $pkgFolderName| tr '[:upper:]' '[:lower:]'|sed -r 's/[_\.]+/-/g'`
    pkgPathName=`basename $pathName| tr '[:upper:]' '[:lower:]'|sed -r 's/[_\.]+/-/g'`
    #sed -i "s;\(Package:\).*;\1 e2-j00zeks-bh-addon-$pkgPathName-$pkgName;" "$F/CONTROL/control"

  if [ -e $extensionsPath/$pkgFolderName/e2kodi__init__.py ];then
    echo "e2kodi__init__.py już dodany"
  elif [ -e $extensionsPath/$pkgFolderName/own_e2kodi__init__.py ];then
      ln -sf $extensionsPath/$pkgFolderName/own_e2kodi__init__.py $extensionsPath/$pkgFolderName/e2kodi__init__.py
  else
      echo "#to jest po to, zeby sciezki we wtyczkach sie zgadzaly
#dostosowane pod dodatek sciezki nalezy umiescic na github w own_e2kodi__init__.py
# w skrypcie dodatku dopisac na poczatku import e2kodi__init__ # aby zainicjowac sciezki i nie musiec zmieniac czegos w kodzie

import sys
for pTa in ['/usr/lib/enigma2/python/Plugins/Extensions/E2Kodi/site-packages/emukodi',
           ]:
  if pTa not in sys.path:
    sys.path.append(pTa)" > $extensionsPath/$pkgFolderName/e2kodi__init__.py
  fi

    #opis
    if [ `grep -c 'Description: $' < "$F/CONTROL/control"` -gt 0 ];then
      sed -i "s;\(Description:\).*;\1 $pkgPathName;" "$F/CONTROL/control"
    fi
    grep "Package:" < "$F/CONTROL/control"
    
    /DuckboxDisk/github/eePlugins/build_ipk.sh "$F" #> /dev/null
  fi
done
exit 0

