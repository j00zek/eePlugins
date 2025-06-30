#/bin/bash
myPath=$(dirname $0)
myAbsPath=$(readlink -fn "$myPath")
SLpath=$myAbsPath/../StreamlinkConfig
SLoptionalPluginsPath=$myAbsPath/../../Streamlink-optionalPlugins/StreamlinkConfig/bin/site-packages/streamlink/plugins
#echo $myAbsPath

rm -rf ~/streamlink-master* 2 >/dev/null

wget -q https://github.com/streamlink/streamlink/archive/refs/heads/master.zip -O ~/streamlink-master.zip
[ $? -gt 0 ] && exit 0
unzip -q ~/streamlink-master.zip
#usuniecie gowna
rm -f ~/streamlink-master/src/streamlink/plugins/vtvgo.* 2 > /dev/null

mkdir -p $SLpath/bin/site-packages/streamlink/
rm -rf $SLpath/bin/site-packages/streamlink/*
cp -rf ~/streamlink-master/src/streamlink/* $SLpath/bin/site-packages/streamlink/

#tworzenie linkow w strukturze drzewa
echo "Dołączanie pakietów emukodi i streamlink_cli do pythona..."
cp -f $SLpath/bin/jtools.py $SLpath/bin/site-packages/streamlink/jtools.py
cp -f $SLpath/bin/e2config.py $SLpath/bin/site-packages/streamlink/e2config.py

echo "Dołączanie nieoficjalnych wtyczek j00zka do streamlinka..."
find $SLpath/plugins/unofficial/ -iname *.py|while read f; do
    #echo "$f"
    f2=`echo "$f"|sed "s;plugins/unofficial/;bin/site-packages/streamlink/;"`
    if [ -e "$f2" ];then
      mv -f "$f2" "$f2.org" #koopia oryginałów
    fi
    #echo "$f2"
    cp -f "$f" "$f2"
    #echo cp -f "$f" "$f2"
  done


SL_version=`grep -m 1 '## streamlink ' < ~/streamlink-master/CHANGELOG.md | grep -o '[0-9]\.[0-9].*'`
sed -i "s/__version__ = _get_version()/__version__ = '$SL_version'/" $SLpath/bin/site-packages/streamlink/_version.py
echo "$SL_version" > $SLpath/bin/site-packages/streamlink/github_version


mkdir -p $SLpath/bin/site-packages/streamlink_cli/
rm -rf $SLpath/bin/site-packages/streamlink_cli/*
cp -rf ~/streamlink-master/src/streamlink_cli/* $SLpath/bin/site-packages/streamlink_cli/


echo "Modyfikacje oryginalnych skryptów..."
#stary klient
if [ `grep -c '#j00zek_patch 2' < $SLpath/bin/site-packages/streamlink_cli/main.py` -eq 0 ];then
 echo "Modyfikuję streamlink_cli/main.py..."
 sed -i 's/\(.*\)\(log\.info."Stream ended".*\)/\1\2\n\1if args.player_external_http and not "streamlinkProxy" in sys.argv[0]: sys.exit() #j00zek_patch 2/' $SLpath/bin/site-packages/streamlink_cli/main.py
fi
#nowy klient
if [ `grep -c '#j00zek_patch 2' < $SLpath/bin/site-packages/streamlink_cli/main.py` -eq 0 ];then
 echo "Modyfikuję streamlink_cli/main.py..."
 sed -i 's/\(.*\)\(stream_runner\.run.prebuffer.*\)/\1\2\n\1if args.player_external_http and not "streamlinkProxy" in sys.argv[0]: sys.exit() #j00zek_patch 2/' $SLpath/bin/site-packages/streamlink_cli/main.py
fi


if [ `grep -c '#j00zek_patch 1' < "$SLpath/bin/site-packages/streamlink_cli/main.py"` -lt 1 ];then
  echo "Modyfikuję streamlink_cli/main.py ..."
  sed -i 's/\(from socks import __version__ as socks_version\)/\n#j00zek_patch 1\ntry: \1\nexcept Exception: from websocket import __version__ as socks_version\n/' $SLpath/bin/site-packages/streamlink_cli/main.py
fi

if [ `grep -c '#j00zek_patch 2' < $SLpath/bin/site-packages/streamlink_cli/main.py` -eq 0 ];then
  echo " COŚ ŹLE Z j00zek_patch 2 !!!!!!"
fi

rm -rf ~/streamlink-master*

#na chwile dla logowania
#wget -q https://raw.githubusercontent.com/openatv/enigma2/7.4/lib/python/Plugins/Extensions/StreamlinkWrapper/plugin.py -O $myAbsPath/../StreamlinkWrapper/plugin.CHANNEL_ZAP
#wget -q https://raw.githubusercontent.com/openatv/enigma2/7.4/lib/python/Plugins/Extensions/YTDLPWrapper/plugin.py -O $myAbsPath/../YTDLPWrapper/plugin.CHANNEL_ZAP
#wget -q https://raw.githubusercontent.com/openatv/enigma2/7.4/lib/python/Plugins/Extensions/YTDLWrapper/plugin.py -O $myAbsPath/../YTDLWrapper/plugin.CHANNEL_ZAP

#wget -q https://raw.githubusercontent.com/openatv/enigma2/master/lib/python/Plugins/Extensions/StreamlinkWrapper/plugin.py -O $myAbsPath/../StreamlinkWrapper/plugin.PLAYSERVICE
#wget -q https://raw.githubusercontent.com/openatv/enigma2/master/lib/python/Plugins/Extensions/YTDLPWrapper/plugin.py -O $myAbsPath/../YTDLPWrapper/plugin.PLAYSERVICE
#wget -q https://raw.githubusercontent.com/openatv/enigma2/master/lib/python/Plugins/Extensions/YTDLWrapper/plugin.py -O $myAbsPath/../YTDLWrapper/plugin.PLAYSERVICE

wget -q https://raw.githubusercontent.com/azman26/EPGazman/main/azman_channels_mappings.py -O $myAbsPath/../StreamlinkConfig/plugins/azman_channels_mappings.py

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


  if [ `grep -c '__version_date__' < "$SLpath/bin/site-packages/streamlink/__init__.py"` -lt 1 ];then
    echo "Modyfikuję streamlink/__init__.py ..."
    sed -i '/del get_versions/i __version_date__ = get_versions()["date"]' $SLpath/bin/site-packages/streamlink/__init__.py
  fi

  if [ `grep -c 'except ImportError as e:' < "$SLpath/bin/site-packages/streamlink/utils/l10n.py"` -lt 1 ];then
    echo "Modyfikuję streamlink/utils/l10n.py ..."
    sed -i 's/\(^except ImportError\)\(:.*\)/\1 as e\2\n    print(str(e))\n/' $SLpath/bin/site-packages/streamlink/utils/l10n.py
  fi

#fix for DRM
echo "Modyfikacje do obsługi DRM..."
sed -i 's/raise PluginError\(.*DRM"\)/log.debug\1/' $SLpath/bin/site-packages/streamlink/stream/dash/dash.py

sed -i '/start_at_zero = session.options.get.*/a\        deckey = session.options.get("decryption_key")\n        deckey2 = session.options.get("decryption_key_2") or deckey\n        log.debug(f"Decryption key parsed: {deckey}")\n        log.debug(f"Decryption key 2 parsed: {deckey2}")\n        cur_deckey = deckey' $SLpath/bin/site-packages/streamlink/stream/ffmpegmux.py
sed -i '/for np in self\.pipes:/a\            if cur_deckey:\n                self._cmd.extend(["-decryption_key", cur_deckey])\n                if cur_deckey == deckey:\n                    cur_deckey = deckey2\n                else:\n                    cur_deckey = deckey\n                #JDRM self._cmd.extend(['-thread_queue_size', '32768'])' $SLpath/bin/site-packages/streamlink/stream/ffmpegmux.py

sed -i '/http = parser.add_argument_group."HTTP options"/i\    transport_ffmpeg.add_argument(\n        "-decryption_key",\n        metavar="FILENAME",\n        help="""\n       Use a CENC decryption key to decrypt the media that ffmpeg receives as\n        an input from the DASH streaming that you play with streamlink.\n        Example: -decryption_key "<hex key>"\n        """\n    )\n    transport_ffmpeg.add_argument(\n        "-decryption_key_2",\n        metavar="FILENAME",\n        help="""\n        Use a CENC decryption key to decrypt the media that ffmpeg receives as\n        an input from the DASH streaming that you play with streamlink.\n        This key will be used for the second track only.\n        Example: -decryption_key_2 "<hex key>"\n        """\n    )' $SLpath/bin/site-packages/streamlink_cli/argparser.py
sed -i '/"hls_audio_select", "hls-audio-select", None),/a\    ("decryption_key", "decryption_key", None),\n    ("decryption_key_2", "decryption_key_2", None),' $SLpath/bin/site-packages/streamlink_cli/argparser.py

sed -i '/"ffmpeg-ffmpeg":.*/a\            "decryption_key": None,\n            "decryption_key_2": None,\n' $SLpath/bin/site-packages/streamlink/session/options.py

sed -i 's/^\(import exceptiongroup.*\)/try: \1\nexcept Exception: pass\n/' $SLpath/bin/site-packages/streamlink/compat.py

#fix for exeplayer3
echo "Modyfikacje lepszej obsługi exeplayer3..."
stdin=subprocess.PIPE
sed -i 's/stdin=self\.stdin/stdin=subprocess.PIPE/' $SLpath/bin/site-packages/streamlink_cli/output/player.py
sed -i '/stderr=self\.stderr,/a\            universal_newlines=True' $SLpath/bin/site-packages/streamlink_cli/output/player.py
sed -i '/self\.http\.shutdown/i\            if self.player.poll() is None: self.player.communicate(input="q\\n")[0] # j00zek to flush dvb buffer' $SLpath/bin/site-packages/streamlink_cli/output/player.py
