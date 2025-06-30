#/usr/bin/bash
timePeriod=1

currSkin=`cat /etc/enigma2/settings|grep 'config.skin.primary_skin='|cut -d '=' -f2|cut -d '/' -f1`
SkinModsPath="/usr/share/enigma2/$currSkin/mySkin"

echo "Safe mode script analyzes restart reason just before dvbapp" > /tmp/safeMode.log
if [ -e '/etc/enigma2/skinModified' ];then
    echo "dvbapp restarted after skin parts modification - hung/bootloop detector created"
    echo "dvbapp restarted after skin parts modification - hung/bootloop detector created" >> /tmp/safeMode.log
    mv -f /etc/enigma2/skinModified /etc/enigma2/dvbappHungMarker
elif [ -e '/etc/enigma2/dvbappHungMarker' ];then
    echo "It seems dvbapp hung during restart after $currSkin skin parts modification :("
    echo "Removing skin parts cmodifications"
    [ -e $SkinModsPath ] && rm -f $SkinModsPath/*.xml
    echo "It seems dvbapp hung during restart after $currSkin skin parts modification. All modifications has been deleted :(" >> /tmp/safeMode.log
else
    echo "dvbapp restart not connected to skin parts modification"
    echo "dvbapp restart not connected to skin parts modification" >> /tmp/safeMode.log
    echo "initiating reportGS script"
    echo "initiating reportGS script" >> /tmp/safeMode.log
    /usr/lib/enigma2/python/Plugins/Extensions/UserSkin/scripts/reportGS.sh &
fi
exit 0
