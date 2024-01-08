#/bin/bash
myPath=$(dirname $0)
myAbsPath=$(readlink -fn "$myPath")
SLpath=$myAbsPath/../StreamlinkConfig
#echo $myAbsPath

rm -rf ~/streamlink-master* 2 >/dev/null

wget -q https://github.com/streamlink/streamlink/archive/refs/heads/master.zip -O ~/streamlink-master.zip
[ $? -gt 0 ] && exit 0
unzip -q ~/streamlink-master.zip

mkdir -p $SLpath/plugins/streamlink/
rm -rf $SLpath/plugins/streamlink/*
cp -rf ~/streamlink-master/src/streamlink/* $SLpath/plugins/streamlink/

SL_version=`grep -m 1 '## streamlink ' < ~/streamlink-master/CHANGELOG.md | grep -o '[0-9]\.[0-9].*'`
sed -i "s/__version__ = _get_version()/__version__ = '$SL_version'/" $SLpath/plugins/streamlink/_version.py
echo "$SL_version" > $SLpath/plugins/streamlink/github_version


mkdir -p $SLpath/plugins/streamlink_cli/
rm -rf $SLpath/plugins/streamlink_cli/*
cp -rf ~/streamlink-master/src/streamlink_cli/* $SLpath/plugins/streamlink_cli/

#stary klient
if [ `grep -c '#j00zek_patch 2' < $SLpath/plugins/streamlink_cli/main.py` -eq 0 ];then
 sed -i 's/\(.*\)\(log\.info."Stream ended".*\)/\1\2\n\1if args.player_external_http and not "streamlinkProxy" in sys.argv[0]: sys.exit() #j00zek_patch 2/' $SLpath/plugins/streamlink_cli/main.py
fi
#nowy klient
if [ `grep -c '#j00zek_patch 2' < $SLpath/plugins/streamlink_cli/main.py` -eq 0 ];then
 sed -i 's/\(.*\)\(stream_runner\.run.prebuffer.*\)/\1\2\n\1if args.player_external_http and not "streamlinkProxy" in sys.argv[0]: sys.exit() #j00zek_patch 2/' $SLpath/plugins/streamlink_cli/main.py
fi

if [ `grep -c '#j00zek_patch 2' < $SLpath/plugins/streamlink_cli/main.py` -eq 0 ];then
  echo " COŚ ŹLE Z j00zek_patch 2 !!!!!!"
fi
rm -rf ~/streamlink-master*

wget -q https://raw.githubusercontent.com/openatv/enigma2/7.1/lib/python/Plugins/Extensions/StreamlinkWrapper/plugin.py -O $myAbsPath/../StreamlinkWrapper/plugin.py
wget -q https://raw.githubusercontent.com/openatv/enigma2/7.1/lib/python/Plugins/Extensions/YTDLPWrapper/plugin.py -O $myAbsPath/../YTDLPWrapper/plugin.py
wget -q https://raw.githubusercontent.com/openatv/enigma2/7.1/lib/python/Plugins/Extensions/YTDLWrapper/plugin.py -O $myAbsPath/../YTDLWrapper/plugin.py

#drm
rm -rf ~/streamlink-master* 2 >/dev/null
rm -rf ~/streamlink-drm-master* 2 >/dev/null

wget -q https://github.com/ImAleeexx/streamlink-drm/archive/refs/heads/master.zip -O ~/streamlink-master.zip
[ $? -gt 0 ] && exit 0
unzip -q ~/streamlink-master.zip

mkdir -p $SLpath/plugins/streamlink-drm/
rm -rf $SLpath/plugins/streamlink-drm/*
mkdir -p $SLpath/plugins/streamlink-drm/streamlink
cp -rf ~/streamlink-drm-master/src/streamlink/* $SLpath/plugins/streamlink-drm/streamlink
mkdir -p $SLpath/plugins/streamlink-drm/streamlink_cli
cp -rf ~/streamlink-drm-master/src/streamlink_cli/* $SLpath/plugins/streamlink-drm/streamlink_cli
