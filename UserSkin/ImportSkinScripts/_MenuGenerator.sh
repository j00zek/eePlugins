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
#ITEM|<Nazwa opcji>|Typ opcji [CONSOLE|MSG|RUN|SILENT|YESNO|APPLET]|<nazwa skryptu do uruchomienia>
#
#CONSOLE wyświetla okno konsoli i wszystko co się w nim dzieje
#MSG uruchamia w tle skrypt i wyświetla wiadomość zawierającą to co zwróci skrypt
#RUN uruchamia skrypt w tle i potwierdza jego wykonanie
#SILENT uruchamia skrypt w tle
#YESNO pyta sie czy uruchomic skrypt
#
###########################################################################################################
#curl -s --ftp-pasv $addons 1>/dev/null 2>%1
#[ $? -gt 0 ] && addons="$addons/"
DownloadableArchives=`curl -kLs https://github.com/j00zek/Converted-Skins|grep tar.gz|sed 's/^.*>\(.*.tar.gz\)<.*$/\1/g'|sort`

echo "MENU|Import foreign skin">/tmp/_Skins2Import
if [ -z "$DownloadableArchives" ];then
  echo "ITEM|No skins to import|DONOTHING|">>/tmp/_Skins2Import
  exit 0
fi


for ArchiveName in $DownloadableArchives
do
  addonName=`echo $ArchiveName|sed 's/\..*$//'`
  echo $addonName
  echo "ITEM|$addonName|CONSOLE|UnpackArchive.sh $ArchiveName $skinPath">>/tmp/_Skins2Import
done
