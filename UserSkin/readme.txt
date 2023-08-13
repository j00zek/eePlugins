UserSkin gives you possibility to dynamically personalize skin using prepared templates.

The schema of folders is:
=>allBars:	contains graphics of selectors,
			type: subfolder with name schema: <optionname>.<folder where graphics have to be copied>
			sobfolders contain png graphics in the same size and dimension skin author desinged.

=>allColors: contains colors definitions (<colors>...</colors>)
			type: xml, with same schema normal skin.xml file uses
			name: colors_<skinName>_<anything without spaces>.xml

=>allWindows: contains windowstyle definitions (<windowstyle...</windowstyle>)
			type: xml, with same schema normal skin.xml file uses
			name: window_<skinName>_<anything without spaces>.xml
			
=>allFonts: contains fonts definition (<fonts>...</fonts>)
			type: xml, with same schema normal skin.xml file uses
			name: font_<skinName>_<anything without spaces>.xml
			
=>allInfos: contains short info about particular skin
			type: txt utf8
			name: info_<lang>_<the skinName as defined in allScreens>.xml
			
=>allPreviews:	contains screenshots showing modified screen/skin,
			type: png
			name: preview_<the skinName as defined in allScreens|allFonts|allColors>.png
			resolution 400x244x8bit
			
=>allScreens: screen(s) definition (<screen name=>...</screen>), can contain multiple screens. Other sections will be omitted
			type: skin, with same schema normal skin.xml file uses
			name: skin_<skinName>_<anything without spaces>.xml

NOTE: <SkinName> sections are not needed, when file is directly put into skin subfolder.(e.g. by author of the skin)