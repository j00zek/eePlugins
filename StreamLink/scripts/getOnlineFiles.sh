#/bin/bash
myPath=$(dirname $0)
myAbsPath=$(readlink -fn "$myPath")
SLpath=$myAbsPath/../StreamlinkConfig
#echo $myAbsPath

rm -rf ~/streamlink-master* 2 >/dev/null

wget -q https://github.com/streamlink/streamlink/archive/refs/heads/master.zip -O ~/streamlink-master.zip
[ $? -gt 0 ] && exit 0
unzip -q ~/streamlink-master.zip

mkdir -p $SLpath/bin/site-packages/streamlink/
rm -rf $SLpath/bin/site-packages/streamlink/*
cp -rf ~/streamlink-master/src/streamlink/* $SLpath/bin/site-packages/streamlink/

SL_version=`grep -m 1 '## streamlink ' < ~/streamlink-master/CHANGELOG.md | grep -o '[0-9]\.[0-9].*'`
sed -i "s/__version__ = _get_version()/__version__ = '$SL_version'/" $SLpath/bin/site-packages/streamlink/_version.py
echo "$SL_version" > $SLpath/bin/site-packages/streamlink/github_version


mkdir -p $SLpath/bin/site-packages/streamlink_cli/
rm -rf $SLpath/bin/site-packages/streamlink_cli/*
cp -rf ~/streamlink-master/src/streamlink_cli/* $SLpath/bin/site-packages/streamlink_cli/

#stary klient
if [ `grep -c '#j00zek_patch 2' < $SLpath/bin/site-packages/streamlink_cli/main.py` -eq 0 ];then
 sed -i 's/\(.*\)\(log\.info."Stream ended".*\)/\1\2\n\1if args.player_external_http and not "streamlinkProxy" in sys.argv[0]: sys.exit() #j00zek_patch 2/' $SLpath/bin/site-packages/streamlink_cli/main.py
fi
#nowy klient
if [ `grep -c '#j00zek_patch 2' < $SLpath/bin/site-packages/streamlink_cli/main.py` -eq 0 ];then
 sed -i 's/\(.*\)\(stream_runner\.run.prebuffer.*\)/\1\2\n\1if args.player_external_http and not "streamlinkProxy" in sys.argv[0]: sys.exit() #j00zek_patch 2/' $SLpath/bin/site-packages/streamlink_cli/main.py
fi

if [ `grep -c '#j00zek_patch 2' < $SLpath/bin/site-packages/streamlink_cli/main.py` -eq 0 ];then
  echo " COŚ ŹLE Z j00zek_patch 2 !!!!!!"
fi
rm -rf ~/streamlink-master*

wget -q https://raw.githubusercontent.com/openatv/enigma2/7.1/lib/python/Plugins/Extensions/StreamlinkWrapper/plugin.py -O $myAbsPath/../StreamlinkWrapper/plugin.py
wget -q https://raw.githubusercontent.com/openatv/enigma2/7.1/lib/python/Plugins/Extensions/YTDLPWrapper/plugin.py -O $myAbsPath/../YTDLPWrapper/plugin.py
wget -q https://raw.githubusercontent.com/openatv/enigma2/7.1/lib/python/Plugins/Extensions/YTDLWrapper/plugin.py -O $myAbsPath/../YTDLWrapper/plugin.py

#drm
rm -rf ~/streamlink-master* 2 >/dev/null
rm -rf ~/streamlink-drm-master* 2 >/dev/null

#wget -q https://github.com/ImAleeexx/streamlink-drm/archive/refs/heads/master.zip -O ~/streamlink-master.zip
#[ $? -gt 0 ] && exit 0
#unzip -q ~/streamlink-master.zip

#mkdir -p $SLpath/bin/site-packages/streamlink-drm/
#rm -rf $SLpath/bin/site-packages/streamlink-drm/*
#mkdir -p $SLpath/bin/site-packages/streamlink-drm/streamlink
#cp -rf ~/streamlink-drm-master/src/streamlink/* $SLpath/bin/site-packages/streamlink-drm/streamlink
#mkdir -p $SLpath/bin/site-packages/streamlink-drm/streamlink_cli
#cp -rf ~/streamlink-drm-master/src/streamlink_cli/* $SLpath/bin/site-packages/streamlink-drm/streamlink_cli

#fix for DRM
sed -i 's/raise PluginError\(.*DRM"\)/log.debug\1/' $SLpath/bin/site-packages/streamlink/stream/dash/dash.py

sed -i '/start_at_zero = session.options.get.*/a\        deckey = session.options.get("decryption_key")\n        deckey2 = session.options.get("decryption_key_2") or deckey\n        log.debug(f"Decryption key parsed: {deckey}")\n        log.debug(f"Decryption key 2 parsed: {deckey2}")\n        cur_deckey = deckey' $SLpath/bin/site-packages/streamlink/stream/ffmpegmux.py
sed -i '/for np in self\.pipes:/a\            if cur_deckey:\n                self._cmd.extend(["-decryption_key", cur_deckey])\n                if cur_deckey == deckey:\n                    cur_deckey = deckey2\n                else:\n                    cur_deckey = deckey\n            self._cmd.extend(['-thread_queue_size', '32768'])' $SLpath/bin/site-packages/streamlink/stream/ffmpegmux.py

sed -i '/transport.add_argument("--http-stream-timeout"/a\    transport_ffmpeg.add_argument(\n        "-decryption_key",\n        metavar="FILENAME",\n        help="""\n       Use a CENC decryption key to decrypt the media that ffmpeg receives as\n        an input from the DASH streaming that you play with streamlink.\n        Example: -decryption_key "<hex key>"\n        """\n    )\n    transport_ffmpeg.add_argument(\n        "-decryption_key_2",\n        metavar="FILENAME",\n        help="""\n        Use a CENC decryption key to decrypt the media that ffmpeg receives as\n        an input from the DASH streaming that you play with streamlink.\n        This key will be used for the second track only.\n        Example: -decryption_key_2 "<hex key>"\n        """\n    )' $SLpath/bin/site-packages/streamlink_cli/argparser.py
sed -i '/"hls_audio_select", "hls-audio-select", None),/a\    ("decryption_key", "decryption_key", None),\n    ("decryption_key_2", "decryption_key_2", None),' $SLpath/bin/site-packages/streamlink_cli/argparser.py

sed -i '/"ffmpeg-ffmpeg":.*/a\            "decryption_key": None,\n            "decryption_key_2": None,\n' $SLpath/bin/site-packages/streamlink/session/options.py