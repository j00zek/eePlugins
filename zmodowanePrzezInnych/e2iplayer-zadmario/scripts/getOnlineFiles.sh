#/bin/bash
myPath=$(dirname $0)
myAbsPath=$(readlink -fn "$myPath")
#echo $myAbsPath

rm -rf ~/e2iplayer-master* 2 >/dev/null

wget -q https://gitlab.com/zadmario/e2iplayer/-/archive/master/e2iplayer-master.zip -O ~/e2iplayer-master.zip
if [ $? -gt 0 ];then
  echo blad pobierania
  exit 1
fi
unzip -q ~/e2iplayer-master.zip
mkdir -p $myAbsPath/../IPTVPlayerMario/
cp -prf ~/e2iplayer-master/IPTVPlayer/* $myAbsPath/../IPTVPlayerMario/
sync
rm -rf ~/e2iplayer-master*
#modyfikacja importow
echo modyfikacja importow
find $myAbsPath/../IPTVPlayerMario/ -iname "*.py" | 
  while read F 
  do
    sed 's/from Plugins\.Extensions\.IPTVPlayer\./from Plugins.Extensions.IPTVPlayerMario./g' -i "$F"
  done
#modyfikacja settings
echo modyfikacja settings
find $myAbsPath/../IPTVPlayerMario/ -iname "*.py" | 
  while read F 
  do
    sed 's/config\.plugins\.iptvplayer\./config.plugins.IPTVPlayerMario./g' -i "$F"

    sed "s/['\"]IPTVPlayer['\"]/'IPTVPlayerMario'/g" -i "$F"
    sed "s;Extensions/IPTVPlayer/;Extensions/IPTVPlayerMario/;g" -i "$F"

  done
#poprawa innych pierdół
sed "s/['\"]E2iPlayer['\"]/'E2iPlayerMario'/g" -i "$myAbsPath/../IPTVPlayerMario/plugin.py"
sed "s/['\"]iptv_config['\"]/'iptvMario_config'/g" -i "$myAbsPath/../IPTVPlayerMario/plugin.py"
sed "s/['\"]iptv_main['\"]/'iptvMario_main'/g" -i "$myAbsPath/../IPTVPlayerMario/plugin.py"

sed "s/config.plugins.iptvplayer =/config.plugins.IPTVPlayerMario =/g" -i "$myAbsPath/../IPTVPlayerMario/components/iptvconfigmenu.py"
#infoversion
#rm -rf ~/infoversion-master* 2 >/dev/null
#wget -q https://gitlab.com/mosz_nowy/infoversion/-/archive/master/infoversion-master.zip -O ~/infoversion-master.zip
#unzip -q infoversion-master.zip
#cp -rf ~/infoversion-master/* $myAbsPath/../IPTVPlayer/
sync
#rm -rf ~/infoversion-master*
#modifications of infoversion
#sed -i 's/<>/!=/g' $myAbsPath/../IPTVPlayer/hosts/hostinfoversion.py
#sed -i "/'Info o E2iPlayer - samsamsam'/d" $myAbsPath/../IPTVPlayer/hosts/hostinfoversion.py
#sed -i "/'Info o E2iPlayer - fork maxbambi'/d" $myAbsPath/../IPTVPlayer/hosts/hostinfoversion.py
#sed -i "/'Info o E2iPlayer - fork mosz_nowy'/d" $myAbsPath/../IPTVPlayer/hosts/hostinfoversion.py
#sed -i "s/\([ ]*\)\(.*'---UPDATE---'.*\)/\1pass #\2/" $myAbsPath/../IPTVPlayer/hosts/hostinfoversion.py
#sed -i 's/urllib2\.unquote/urllib_unquote/g' $myAbsPath/../IPTVPlayer/hosts/hostinfoversion.py
#sed -i 's/, urllib2/\nfrom Plugins.Extensions.IPTVPlayer.p2p3.UrlLib import urllib_unquote/' $myAbsPath/../IPTVPlayer/hosts/hostinfoversion.py
exit 0
