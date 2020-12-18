echo "Cleaning skin files"
if [ -z $1 ];then
  searchPath=/DuckboxDisk/github/eePlugins/BH/usr/share/enigma2
else
  searchPath="$1"
fi
if [ ! -e "$searchPath" ];then
  echo "$searchPath does NOT exist, exiting !!!!!!!"
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo
  exit 1
fi

find "$searchPath" -type f -name "*.xml" | 
while read F 
do
#zrodla
  if [ `grep -c '"session\.BlackHarmonyMSNWeather"' < "$F"` -gt 0 ];then #zeby niepotrzebnienie ustawiac daty modyfikacji
    sed -i 's/"session\.BlackHarmonyMSNWeather"/"session.j00zekMSNWeather"/g' "$F"
  fi
#renderery
    if [ `grep -c 'render="BlackHarmonyABTCAirlyPixmap"' < "$F"` -gt 0 ];then 
      sed -i 's/render="BlackHarmonyABTCAirlyPixmap"/render="j00zekABTCAirlyPixmap"/g' "$F"
    fi
    if [ `grep -c 'render="BlackHarmonyAnimatedPicsmap"' < "$F"` -gt 0 ];then 
      sed -i 's/render="BlackHarmonyAnimatedPicsmap"/render="j00zekModAnimatedPicsmap"/g' "$F"
    fi
    if [ `grep -c 'render="BlackHarmonyAudioIcon"' < "$F"` -gt 0 ];then
      sed -i 's/render="BlackHarmonyAudioIcon"/render="j00zekModAudioIcon"/g' "$F"
    fi
    if [ `grep -c 'render="BlackHarmonyCover"' < "$F"` -gt 0 ];then
      sed -i 's/render="BlackHarmonyCover"/render="j00zekModCover"/g' "$F"
    fi
    if [ `grep -c 'render="BlackHarmonyEGEpgListNobile"' < "$F"` -gt 0 ];then
      sed -i 's/render="BlackHarmonyEGEpgListNobile"/render="j00zekModEGEpgListNobile"/g' "$F"
    fi
    if [ `grep -c 'render="BlackHarmonyEGSingleEpgList"' < "$F"` -gt 0 ];then
      sed -i 's/render="BlackHarmonyEGSingleEpgList"/render="j00zekModEGSingleEpgList"/g' "$F"
    fi
    if [ `grep -c 'render="BlackHarmonyEventListDisplay"' < "$F"` -gt 0 ];then
      sed -i 's/render="BlackHarmonyEventListDisplay"/render="j00zekModEventListDisplay"/g' "$F"
    fi
    if [ `grep -c 'render="BlackHarmonyFlipClock"' < "$F"` -gt 0 ];then
      sed -i 's/render="BlackHarmonyFlipClock"/render="j00zekModFlipClock"/g' "$F"
    fi
    if [ `grep -c 'render="BlackHarmonyMSNWeatherPixmap"' < "$F"` -gt 0 ];then
      sed -i 's/render="BlackHarmonyMSNWeatherPixmap"/render="j00zekMSNWeatherPixmap"/g' "$F"
    fi
    if [ `grep -c 'render="BlackHarmonyPositionGauge"' < "$F"` -gt 0 ];then
      sed -i 's/render="BlackHarmonyPositionGauge"/render="j00zekModPositionGauge"/g' "$F"
    fi
    if [ `grep -c 'render="BlackHarmonySingleEpgListNobile"' < "$F"` -gt 0 ];then
      sed -i 's/render="BlackHarmonySingleEpgListNobile"/render="j00zekModSingleEpgListNobile"/g' "$F"
    fi
    if [ `grep -c 'render="BlackHarmonyTypeLabel"' < "$F"` -gt 0 ];then
      sed -i 's/render="BlackHarmonyTypeLabel"/render="j00zekModTypeLabel"/g' "$F"
    fi
    if [ `grep -c 'render="BlackHarmonyVVolumeText"' < "$F"` -gt 0 ];then
      sed -i 's/render="BlackHarmonyVVolumeText"/render="j00zekModVolumeText"/g' "$F"
    fi
    if [ `grep -c 'render="BlackHarmonyWatches"' < "$F"` -gt 0 ];then
      sed -i 's/render="BlackHarmonyWatches"/render="j00zekModWatches"/g' "$F"
    fi
#konwertery
  if [ `grep -c 'type="ServiceName2' < "$F"` -gt 0 ];then #zeby niepotrzebnienie ustawiac daty modyfikacji
    sed -i 's/type="ServiceName2"/type="j00zekModServiceName2"/g' "$F"
  fi
  if [ `grep -c 'type="EventName' < "$F"` -gt 0 ];then 
    sed -i 's/type="EventName"/type="j00zekModEventName"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonyABTCAirlyWidget"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonyABTCAirlyWidget"/type="j00zekModABTCAirlyWidget"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonyBoxInfo"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonyBoxInfo"/type="j00zekModBoxInfo"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonyCaidInfo2"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonyCaidInfo2"/type="j00zekModCaidInfo2"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonyCodecInfo"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonyCodecInfo"/type="j00zekModCodecInfo"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonyCodecInfoColors"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonyCodecInfoColors"/type="j00zekModCodecInfoColors"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonyConditionalShowHide"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonyConditionalShowHide"/type="j00zekModConditionalShowHide"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonyCpuUsage_BH"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonyCpuUsage_BH"/type="j00zekModCpuUsage"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonyEMCinfo"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonyEMCinfo"/type="j00zekModEMCinfo"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonyEventList"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonyEventList"/type="j00zekModEventList"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonyEventName2"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonyEventName2"/type="j00zekModEventName2"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonyEventPosition"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonyEventPosition"/type="j00zekModEventPosition"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonyExtraNumText"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonyExtraNumText"/type="j00zekModExtraNumText"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonyFanTempInfo"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonyFanTempInfo"/type="j00zekModFanTempInfo"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonyFrontendInfo_BH"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonyFrontendInfo_BH"/type="j00zekModFrontendInfo"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonyFrontendInfo2"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonyFrontendInfo2"/type="j00zekModFrontendInfo2"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonygExtraInfo"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonygExtraInfo"/type="j00zekModExtraInfo"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonygExtraTuner"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonygExtraTuner"/type="j00zekModExtraTuner"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonyHddTempInfo"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonyHddTempInfo"/type="j00zekModHddTempInfo"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonyimieniny"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonyimieniny"/type="j00zekModimieniny"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonymFlashInfo"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonymFlashInfo"/type="j00zekModFlashInfo"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonyMovieReference"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonyMovieReference"/type="j00zekModMovieReference"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonyMSNWeather"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonyMSNWeather"/type="j00zekMSNWeather"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonyMSNWeatherThingSpeak"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonyMSNWeatherThingSpeak"/type="j00zekMSNWeatherThingSpeak"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonyMSNWeatherWebCurrent"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonyMSNWeatherWebCurrent"/type="j00zekMSNWeatherWebCurrent"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonyMSNWeatherWebDaily"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonyMSNWeatherWebDaily"/type="j00zekMSNWeatherWebDaily"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonyMSNWeatherWebhourly"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonyMSNWeatherWebhourly"/type="j00zekMSNWeatherWebhourly"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonyPliExtraInfo"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonyPliExtraInfo"/type="j00zekModPliExtraInfo"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonypliLayoutInfo"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonypliLayoutInfo"/type="j00zekModpliLayoutInfo"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonyQuickEcmInfo"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonyQuickEcmInfo"/type="j00zekModQuickEcmInfo"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonyRouteInfo"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonyRouteInfo"/type="j00zekModRouteInfo"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonyTestConnection"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonyTestConnection"/type="j00zekModTestConnection"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonyTestConnectionOFF"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonyTestConnectionOFF"/type="j00zekModTestConnectionOFF"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonyTestConnectionON"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonyTestConnectionON"/type="j00zekModTestConnectionON"/g' "$F"
  fi
  if [ `grep -c 'type="BlackHarmonyVAudioInfo"' < "$F"` -gt 0 ];then
    sed -i 's/type="BlackHarmonyVAudioInfo"/type="j00zekModAudioInfo"/g' "$F"
  fi
#klawisze kolorow
  if [ `grep -c 'buttons/green.png' < "$F"` -gt 0 ];then
    sed -i 's;buttons/green.png;buttons/key_green.png;g' "$F"
  fi
  if [ `grep -c 'buttons/yellow.png' < "$F"` -gt 0 ];then
    sed -i 's;buttons/yellow.png;buttons/key_yellow.png;g' "$F"
  fi
  if [ `grep -c 'buttons/red.png' < "$F"` -gt 0 ];then
    sed -i 's;buttons/red.png;buttons/key_red.png;g' "$F"
  fi
  if [ `grep -c 'buttons/blue.png' < "$F"` -gt 0 ];then
    sed -i 's;buttons/blue.png;buttons/key_blue.png;g' "$F"
  fi
#wtyczka pogodowa
#  if [ `grep -c 'type="j00zekMSNWeatherWebDaily">Record' < "$F"` -gt 0 ];then
#    sed -i 's;type="j00zekMSNWeatherWebDaily">Record;type="j00zekMSNWeather">DailyRecord;g' "$F"
#  fi
#  if [ `grep -c 'type="j00zekMSNWeatherWebhourly">Record' < "$F"` -gt 0 ];then
#    sed -i 's;type="j00zekMSNWeatherWebhourly">Record;type="j00zekMSNWeather">HourlyRecord;g' "$F"
#  fi
#  if [ `grep -c 'type="j00zekMSNWeatherWebhourly">title<' < "$F"` -gt 0 ];then
#    sed -i "s;type=\"j00zekMSNWeatherWebhourly\">title<;type=\"j00zekMSNWeather\">RUN|['hourlyData']['title']<;g" "$F"
#  fi
#  if [ `grep -c 'type="j00zekMSNWeatherWebCurrent">barometrValue' < "$F"` -gt 0 ];then
#    sed -i "s;type=\"j00zekMSNWeatherWebCurrent\">barometrValue;type=\"j00zekMSNWeather\">RUN|['currentData']['pressure']['val']|hPa;g" "$F"
#  fi
#  if [ `grep -c 'type="j00zekMSNWeatherWebhourly">Record' < "$F"` -gt 0 ];then
#    sed -i 's;type="j00zekMSNWeatherWebhourly">Record;type="j00zekMSNWeather">RUN|[\'currentData\'][\'pressure\'][\'val\'];g' "$F"
#  fi
  if [ `grep -c 'type="j00zekMSNWeather">temperature_current' < "$F"` -gt 0 ];then
    sed -i "s;type=\"j00zekMSNWeather\">temperature_current;type=\"j00zekMSNWeather\">GET|['currentData']['temperature']['valInfo'];g" "$F"
  fi
  if [ `grep -c 'type="j00zekMSNWeather">temperature_high,day1' < "$F"` -gt 0 ];then
    sed -i "s;type=\"j00zekMSNWeather\">temperature_high,day1;type=\"j00zekMSNWeather\">RUN|['dailyData']['Record=0']['temp_high']|C;g" "$F"
  fi
  if [ `grep -c 'type="j00zekMSNWeather">temperature_low,day1' < "$F"` -gt 0 ];then
    sed -i "s;type=\"j00zekMSNWeather\">temperature_low,day1;type=\"j00zekMSNWeather\">RUN|['dailyData']['Record=0']['temp_low']|C;g" "$F"
  fi

done
exit 0

