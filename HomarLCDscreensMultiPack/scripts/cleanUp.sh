#!/bin/sh
#
# NIE uruchamiać na tunerze !!!!
#

instDir='/usr/share/enigma2/HomarLCDskins'
myDir=`dirname $0`
myDir=`dirname $myDir` #pozbycie sie scripts z konca, czyli katalog wczesniej
echo $myDir

echo "zamiana skin_vfd na skin_LCD"
find $myDir -iname skin_vfd_*.xml|while read f; do
  #echo "$f"
  nf=`echo $f|sed 's/skin_vfd_/skin_LCD_/g'`
  mv -f "$f" "$nf"
done

echo "korekta nazw dla ULTIMO4K"
find $myDir -iname skin_LCD_*.xml|while read f; do
  #echo "$f"
  if [ `echo "$f"|grep -c 'model.ultimo4k'` -eq 1 ];then
    if [ `echo "$f"|grep -c 'LCD_HMR_ULTIMO4K_'` -eq 0 ];then
      nf=`echo "$f"|sed 's/LCD_/LCD_HMR_ULTIMO4K_/g'`
      mv -f "$f" "$nf"
    fi
  fi
done

echo "Homar Skins: modyfikacja komponentów wewnątrz xml-i"
find $myDir -iname skin_LCD_*.xml|while read f; do
  echo "$f"
  #używamy standardowych komponentów paczki e2components
  sed -i 's/jOOzek/j00zek/g' "$f" 
  sed -i 's;vfd_skin/Homar/BingPicOfTheDay.jpg;BlackHarmony/icons/BingPicOfTheDay.jpg;g' "$f" #wersja aktualizowana przez BH
  sed -i 's;convert type="ServiceName2";convert type="BlackHarmonyServiceName2";g' "$f"
  sed -i 's;convert type="CpuUsage";convert type="BlackHarmonyCpuUsage_BH";g' "$f"
  # zmieniamy wszystkie ścieżki na nowe
  sed -i 's;vfd_skin/;HomarLCDskins/;g' "$f"
  #poprawiamy ścieżki fontów
  sed -i 's;Homar/fonts/;fonts/;g' "$f"
  sed -i 's;fonts/";fonts/;g' "$f"
  sed -i 's;Homar/fonts/;fonts/;g' "$f"
  sed -i 's;HomarLCDskins/Homar/clock/;HomarLCDskins/clock/;g' "$f"
  sed -i 's;HomarLCDskins/Homar/common/;HomarLCDskins/common/;g' "$f"
  sed -i 's;HomarLCDskins/Homar/MoonPhase/;HomarLCDskins/MoonPhase/;g' "$f"
  sed -i 's;HomarLCDskins/Homar/tunertypes/;HomarLCDskins/tunertypes/;g' "$f"
  sed -i 's;HomarLCDskins/Homar/weather/;HomarLCDskins/weather/;g' "$f"
  sed -i 's;HomarLCDskins/Homar/Homar\.png;HomarLCDskins/Homar/Homar_Ultimo4K.png;g' "$f"
  sed -i 's;Homar_480x320/Homar_Solo4K\.png;Homar/Homar_Solo4K.png;g' "$f"
  sed -i 's;Homar_480x320/Homar_Duo4K\.png;Homar/Homar_Duo4K.png;g' "$f"
  sed -i 's;HomarLCDskins/Homar/Homar_Uno4KSE\.png;HomarLCDskins/Homar/Homar_Uno4KSE.png;g' "$f"
  #komponenty własne
  sed -i 's;convert type="AnalogClock";convert type="HomarAnalogClock";g' $f
  sed -i 's;convert type="ProgressDiskSpaceInfo";convert type="HomarProgressDiskSpaceInfo";g' "$f"
  sed -i 's;convert type="RdsInfo";convert type="HomarRdsInfo";g' "$f"
  sed -i 's;convert type="TempFanInfo";convert type="HomarTempFanInfo";g' "$f"
  sed -i 's;convert type="Timers";convert type="HomarTimers";g' "$f"
  sed -i 's;render="AnalogClockLCD";render="HomarAnalogClockLCD";g' "$f"
  sed -i 's;render="FlipClock";render="HomarFlipClock";g' "$f"
  sed -i 's;render="RollerCharLCDLong";render="HomarRollerCharLCDLong";g' "$f"
  sed -i 's;source="parent.RdsDecoder";source="parent.HomarRdsDecoder";g' "$f"
  sed -i 's;transparent="2";transparent="1";g' "$f"
done

echo "Homar Skins: modyfikacja komponentów wewnątrz xml-i zgodnie ze zmianami w BlackHarmony"
/DuckboxDisk/github/eePlugins/BH/scripts/cleanUp.sh /DuckboxDisk/github/eePlugins/HomarLCDscreensMultiPack