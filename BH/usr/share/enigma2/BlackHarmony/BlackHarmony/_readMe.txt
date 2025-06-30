This folder is to workarround openATV issues with searching file in incorrect order.

Example for 'BlackHarmony/buttons/key_ok.png' definition in skin
searching for "/etc/enigma2/BlackHarmony/BlackHarmony/buttons/key_ok.png
searching for "/usr/share/enigma2/BlackHarmony/BlackHarmony/buttons/key_ok.png
searching for "/usr/share/enigma2/skin_fallback_1080/BlackHarmony/buttons/key_ok.png
searching for "/usr/share/enigma2/skin_default/BlackHarmony/buttons/key_ok.png
searching for "/usr/share/enigma2/BlackHarmony/buttons/key_ok.png
searching for "/etc/enigma2/BlackHarmony/buttons/key_ok.png


#below links should be automatically done during installation
ln -sf /usr/share/enigma2/BlackHarmony/buttons/ /usr/share/enigma2/BlackHarmony/BlackHarmony/buttons
ln -sf /usr/share/enigma2/BlackHarmony/icons/ /usr/share/enigma2/BlackHarmony/BlackHarmony/icons
