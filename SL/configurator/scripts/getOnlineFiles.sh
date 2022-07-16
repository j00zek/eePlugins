#/bin/bash
myPath=$(dirname $0)
myAbsPath=$(readlink -fn "$myPath")
#echo $myAbsPath

rm -rf ~/streamlink-master* 2 >/dev/null

wget -q https://github.com/streamlink/streamlink/archive/refs/heads/master.zip -O ~/streamlink-master.zip
[ $? -gt 0 ] && exit 0
unzip -q ~/streamlink-master.zip
#cp -rf ~/streamlink-master/src/streamlink/* $myAbsPath/../../streamlink/
#cp -rf ~/streamlink-master/src/streamlink_cli/* $myAbsPath/../../streamlink_cli/
cp -rf ~/streamlink-master/src/streamlink_cli/* $myAbsPath/../plugins/streamlink_cli/
if [ `grep -c '#j00zek_patch 2' < $myAbsPath/../plugins/streamlink_cli/main.py` -eq 0 ];then
 sed -i 's/\(.*\)\(log\.info."Stream ended".*\)/\1\2\n\1if args.player_external_http and not "streamlinkProxy" in sys.argv[0]: sys.exit() #j00zek_patch 2/' $myAbsPath/../plugins/streamlink_cli/main.py
fi
rm -rf ~/streamlink-master*
