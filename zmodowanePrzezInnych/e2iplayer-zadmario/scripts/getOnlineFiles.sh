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
cp -rf ~/e2iplayer-master/IPTVPlayer $myAbsPath/../
sync
rm -rf ~/e2iplayer-master*
#infoversion
rm -rf ~/infoversion-master* 2 >/dev/null
wget -q https://gitlab.com/mosz_nowy/infoversion/-/archive/master/infoversion-master.zip -O ~/infoversion-master.zip
unzip -q infoversion-master.zip
cp -rf ~/infoversion-master/* $myAbsPath/../IPTVPlayer/
sync
rm -rf ~/infoversion-master*
#modifications of infoversion
sed -i 's/<>/!=/g' $myAbsPath/../IPTVPlayer/hosts/hostinfoversion.py
sed -i "/'Info o E2iPlayer - samsamsam'/d" $myAbsPath/../IPTVPlayer/hosts/hostinfoversion.py
sed -i "/'Info o E2iPlayer - fork maxbambi'/d" $myAbsPath/../IPTVPlayer/hosts/hostinfoversion.py
sed -i "/'Info o E2iPlayer - fork mosz_nowy'/d" $myAbsPath/../IPTVPlayer/hosts/hostinfoversion.py
sed -i "s/\([ ]*\)\(.*'---UPDATE---'.*\)/\1pass #\2/" $myAbsPath/../IPTVPlayer/hosts/hostinfoversion.py
sed -i 's/urllib2\.unquote/urllib_unquote/g' $myAbsPath/../IPTVPlayer/hosts/hostinfoversion.py
sed -i 's/, urllib2/\nfrom Plugins.Extensions.IPTVPlayer.p2p3.UrlLib import urllib_unquote/' $myAbsPath/../IPTVPlayer/hosts/hostinfoversion.py
exit 0
