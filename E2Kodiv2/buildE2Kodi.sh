echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
echo "            pakowanie rozszerzen"
echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"

/DuckboxDisk/github/eePlugins/build_ipk.sh /DuckboxDisk/github/eePlugins/E2Kodiv2/python39/
/DuckboxDisk/github/eePlugins/build_ipk.sh /DuckboxDisk/github/eePlugins/E2Kodiv2/python312/
/DuckboxDisk/github/eePlugins/build_ipk.sh /DuckboxDisk/github/eePlugins/E2Kodiv2/python313/

extensionsPath=/DuckboxDisk/github/eePlugins/E2Kodiv2/Addons
find "$extensionsPath" -maxdepth 1 -mindepth 1 -type d | 
while read F 
do
  if [ -e "$F/CONTROL/control" ];then
    #ewentualna korekta DestinationPath
    #pkgPathFolderName=`echo "$F"|sed "s;$extensionsPath; /usr/lib/enigma2/python/Plugins/Extensions/E2Kodi/site-packages/emukodi/Plugins;"`
    #echo $extensionsPath
    #echo $pkgPathFolderName
    #sed -i "s;DestinationPath:.*$;DestinationPath: $pkgPathFolderName;" "$F/CONTROL/control"
    
   
    #nazwa paczki
    pathName=`dirname "$F"`
    pkgFolderName=`basename "$F"`
    pkgName=`echo $pkgFolderName| tr '[:upper:]' '[:lower:]'|sed -r 's/[_\.]+/-/g'`
    pkgPathName=`basename $pathName| tr '[:upper:]' '[:lower:]'|sed -r 's/[_\.]+/-/g'`
    #sed -i "s;\(Package:\).*;\1 e2-j00zeks-bh-addon-$pkgPathName-$pkgName;" "$F/CONTROL/control"


    #opis
    if [ `grep -c 'Description: $' < "$F/CONTROL/control"` -gt 0 ];then
      sed -i "s;\(Description:\).*;\1 $pkgPathName;" "$F/CONTROL/control"
    fi
    grep "Package:" < "$F/CONTROL/control"
    
    /DuckboxDisk/github/eePlugins/build_ipk.sh "$F" #> /dev/null
  fi
done

