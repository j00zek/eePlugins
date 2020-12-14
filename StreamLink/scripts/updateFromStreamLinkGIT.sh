echo "refreshing streamlink git"
SRCpath=/DuckboxDisk/github/streamlink-27-BILLY2011-SOURCE
cd $SRCpath
git pull
echo $?
#cd /DuckboxDisk/github/
#rm -rf /DuckboxDisk/github/streamlink-27-BILLY2011-SOURCE
#git clone https://github.com/Billy2011/streamlink-27.git $SRCpath
echo "copying..."

src=$SRCpath/src
dst=/DuckboxDisk/github/eePlugins/StreamLink/usr/lib/python2.7/site-packages

rm -f /DuckboxDisk/github/eePlugins/StreamLink/usr/lib/python2.7/site-packages/streamlink/plugins/*.py
cp -ru $src/streamlink/* $dst/streamlink/
cp -ru $src/streamlink_cli/* $dst/streamlink_cli/
cp -rf $dst/../../../../scripts/unofficial/* $dst/streamlink/

if [ `cat $dst/streamlink/__init__.py|grep -c '__version_date__'` -lt 1 ];then
  echo "patching __init__.py ..."
  sed -i '/del get_versions/i __version_date__ = get_versions()["date"]' $dst/streamlink/__init__.py
fi

if [ `cat $dst/streamlink/utils/l10n.py|grep -c 'except ImportError as e:'` -lt 1 ];then
  echo "patching l10n.py ..."
  sed -i 's/\(^except ImportError\)\(:.*\)/\1 as e\2\n    print str(e)\n/' $dst/streamlink/utils/l10n.py
fi


if [ `cat $dst/streamlink_cli/main.py|grep -c '#j00zek_patch 1'` -lt 1 ];then
  echo "patching streamlink_cli/main.py ..."
  sed -i 's/\(from socks import __version__ as socks_version\)/\n#j00zek_patch 1\ntry: \1\nexcept Exception: from websocket import __version__ as socks_version\n/' $dst/streamlink_cli/main.py
fi

#chwilowo
#rm -f /DuckboxDisk/github/eePlugins/StreamLink/usr/lib/python2.7/site-packages/streamlink/plugins/funimationnow*
#rm -f /DuckboxDisk/github/eePlugins/StreamLink/usr/lib/python2.7/site-packages/streamlink/plugins/pluzz*
#rm -f /DuckboxDisk/github/eePlugins/StreamLink/usr/lib/python2.7/site-packages/streamlink/plugins/svtplay*
#rm -f /DuckboxDisk/github/eePlugins/StreamLink/usr/lib/python2.7/site-packages/streamlink/plugins/vimeo*
#rm -f /DuckboxDisk/github/eePlugins/StreamLink/usr/lib/python2.7/site-packages/streamlink/plugins/rtve*