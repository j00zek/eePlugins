#!/bin/sh 
# @j00zek 2015 dla Graterlia
#
#Plik do generowania menu
#musi znajdować się w katalogu menu i jest zawsze uruchamiany przy wyborzez ikonki
#jeśli chcemy, aby menu było statyczne, to na początku wpisujemy exit 0
#Jeśli menu ma byc dynamiczne to tutaj je sobie tworzymy przed każdym wejściem do niego
#
#struktura prosta jak budowa cepa,
#pierwsza linia zawiera nazwę menu
#MENU|<NAZWA Menu>
#
#kolejne linie zawierają poszczególne pozycje według schematu:
#ITEM|<Nazwa opcji>|Typ opcji [CONSOLE|MSG|RUN|SILENT|YESNO|APPLET]|<nazwa skryptu do uruchomienia>|<link do obrazka>
#
#CONSOLE wyświetla okno konsoli i wszystko co się w nim dzieje
#MSG uruchamia w tle skrypt i wyświetla wiadomość zawierającą to co zwróci skrypt
#RUN uruchamia skrypt w tle i potwierdza jego wykonanie
#SILENT uruchamia skrypt w tle
#YESNO pyta sie czy uruchomic skrypt
#
curl --help 1>/dev/null 2>&1
if [ $? -gt 0 ]; then
  echo "MENU|Delete addons">/tmp/_Deleteaddons
  echo "ITEM|Required program 'curl' is not available. Please install it first manually.|DONOTHING|">>/tmp/_Deleteaddons
  echo "MENU|Download addons">/tmp/_Getaddons
  echo "ITEM|Required program 'curl' is not available. Please install it first manually.|DONOTHING|">>/tmp/_Getaddons
  echo "MENU|Download additional Components/plugins">/tmp/_Getcomponents
  echo "ITEM|Required program 'curl' is not available. Please install it first manually.|DONOTHING|">>/tmp/_Getcomponents
  exit 0
fi

if [ -z $2 ]; then
  echo "MENU|Delete addons">/tmp/_Deleteaddons
  echo "ITEM|No addons path configured|DONOTHING|">>/tmp/_Deleteaddons
  echo "MENU|Download addons">/tmp/_Getaddons
  echo "ITEM|No addons path configured|DONOTHING|">>/tmp/_Getaddons
  echo "MENU|Download additional Components/plugins">/tmp/_Getcomponents
  echo "ITEM|Components path not configured|DONOTHING|">>/tmp/_Getcomponents
  exit 0
else
  skinPath=$2
fi

cd $skinPath

skinParts=`find -path "*/all*/*.xml"|sort|sed 's;^./;;'`
skinPartsNo=`find -path "*/all*/*.xml"|grep -c ".xml"`
cd $skinPath/allBars/
skinBars=`find -name "*bar_*.menu" -type d 2>/dev/null|sort|sed 's;^./;;'`
skinBarsNo=`find -type d -name 'bar_*' |grep -c ".menu"`

echo "MENU|Delete addons">/tmp/_Deleteaddons
if [ $skinBarsNo -lt 1 ] && [ $skinPartsNo -lt 1 ];then
  echo "ITEM|No addons installed|DONOTHING|">>/tmp/_Deleteaddons
fi

for addon in $skinBars
do
  addonName=`echo $addon|sed 's/\..*$//'`
  echo $addonName
  echo "ITEM|$addonName|SILENT|/bin/rm -rf $skinPath/allBars/$addon">>/tmp/_Deleteaddons
done
for addon in $skinParts
do
  addonName=`echo $addon|sed 's/^.*\/\(.*\)\.xml/\1/'`
  #echo $addonName
  echo "ITEM|$addonName|SILENT|/bin/rm -rf $skinPath/$addon">>/tmp/_Deleteaddons
done

###########################################################################################################
echo "MENU|Download addons">/tmp/_Getaddons
if [ ! -f $skinPath/skin.config ];then
  echo "ITEM|Skin does not have downloadable addons|DONOTHING|">>/tmp/_Getaddons
fi
. $skinPath/skin.config
if [[ -z $addons && -z $addonsList ]];then
  echo "ITEM|Skin does not have downloadable addons|DONOTHING|">>/tmp/_Getaddons
elif [ ! -z "$addonsList" ];then
    # skin author made a script in skin.conf to properly download the list :)
    #e.g. addonsList="curl -kLs --ftp-pasv ftp://blackharmony.pl:55535/FTP/addons -o -|awk '{print \$9}'|sort"
    #e.g. addonsList="curl -kLs http://files.blackharmony.pl/addons/ -o -|grep -o 'href="[^\S]*"'|cut -d'"' -f2"
    DownloadableAddons=`eval $addonsList`
elif [ ! -z "$addons" ];then
    #curl -s --ftp-pasv $addons 1>/dev/null 2>%1
    #[ $? -gt 0 ] && addons="$addons/"
    DownloadableAddons=`curl -kLs --ftp-pasv $addons/ -o -|awk '{print $9}'|sort`
    [ -z "$allPreviews" ] ||  DownloadablePerviews=`curl -kLs --ftp-pasv $allPreviews/ -o -|awk '{print $9}'|sort`
fi
echo "$DownloadableAddons">/tmp/aqq
echo "$DownloadablePerviews">/tmp/aqqpr

for addon in $DownloadableAddons
do
    addonName=`echo $addon|sed 's/\..*$//'`
    if [ ! -z "$addonName" ];then
      if `echo "$DownloadablePerviews"|grep -q "$addonName"`; then
        PIC="$allPreviews/preview_$addonName.jpg"
      else
        PIC=''
      fi
      echo "ITEM|$addonName|CONSOLE|InstallAddon.sh $addon $skinPath|$PIC">>/tmp/_Getaddons
    fi
done
###########################################################################################################
DownloadableAddons=""
echo "MENU|Download additional Components/plugins">/tmp/_Getcomponents
if [ ! -f $skinPath/skin.config ];then
  echo "ITEM|Skin does not have downloadable components|DONOTHING|">>/tmp/_Getcomponents
fi
. $skinPath/skin.config
if [[ -z $components && -z $componentsList ]];then
    echo "ITEM|Skin does not have downloadable components|DONOTHING|">>/tmp/_Getcomponents
elif [ ! -z "$componentsList" ];then
    # skin author made a script in skin.conf to properly download the list :)
    #e.g. componentsList="curl -kLs --ftp-pasv ftp://blackharmony.pl:55535/FTP/components/ -o -|awk '{print \$9}'|sort"
    #e.g. componentsList="curl -kLs http://files.blackharmony.pl/components/ -o -|grep -o 'href="[^\S]*"'|cut -d'"' -f2"
    DownloadableAddons=`eval $componentsList`
    echo $componentsList
elif [ ! -z "$components" ];then
  DownloadableAddons=`curl -kLs --ftp-pasv $components/ -o -|awk '{print $9}'|sort`
fi

for addon in $DownloadableAddons
do
  addonName=`echo $addon|sed 's/\..*$//'`
  if [ ! -z "$addonName" ];then
    if `echo $DownloadablePerviews|grep -q $addonName`; then
      PIC="$allPreviews/$addonName.jpg"
    else
      PIC=''
    fi
    #echo $addonName
    echo "ITEM|$addonName|CONSOLE|InstallComponent.sh $addon $skinPath|$PIC">>/tmp/_Getcomponents
  fi
done
