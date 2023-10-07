--[[
 This program is free software; you can redistribute it and/or modify it. 
 copy it to ...\VideoLAN\VLC\lua\sd\ folder, configure and you should see it in vlc
 useful editor to check errors https://www.jdoodle.com/execute-lua-online/
--]]

-- tuner configuration
local tuner_IP = "192.168.33.5"
local username = ""
local password = ""

-- OpenWebif configuration
local OpenWebif_auth = 1
local OpenWebif_port = 80

local OpenWebif_auth_for_streaming = 0
local OpenWebif_streamport = 8001

local OpenWebif_https_auth = 0
local OpenWebif_https_enabled = 0
local OpenWebif_https_port = 443

-- script configuration
local bouquet_name = "userbouquet.iptv-tvp-azman.tv" -- userbouquet of the box to be retrieved, default favourites
local put_box_in_standby = 1
local buid_sections_tree = 1 --when section marker found, it will be used to build the tree
local max_Number_of_loaded_channels = 99
local add_debug_info = 0

------------------------------------------------------------------------------------------------
-- building static URLs
local mainURL = ""
if ( OpenWebif_https_enabled == 1 ) then
	mainURL = "https://"
	if ( OpenWebif_https_auth == 1 ) then
		mainURL = mainURL + username + ":" + password + "@"
	end
	mainURL = mainURL..tuner_IP
else
	mainURL = "http://"
	if ( OpenWebif_auth == 1 ) then
		mainURL = mainURL..username..":"..password.."@"
	end
	mainURL = mainURL..tuner_IP
end

local streamingURL = mainURL..":"..OpenWebif_streamport

local webURL = mainURL
if ( OpenWebif_https_enabled == 1 ) then
	if ( OpenWebif_https_port ~= 443 ) then 
		webURL = webURL..":"..OpenWebif_https_port
	end
else
	if ( OpenWebif_port ~= 80 ) then 
		webURL = webURL..":"..OpenWebif_port
	end
end

-- plugin descriptor
function descriptor()
    return { title="E-TV mod j00zek",
    version = "1.5",
    shortdesc = "Parsing Enigma2 TV favorites",
    description = "Outputs the list of channels with art file, current EPG for a given Egnima2 TV bouquet.",
    capabilities = { "playing-listener" } }
end

-- translate xml tags to text
function xml2string(value)
  	value = string.gsub(value, "&#x([%x]+)%;", function(h)  return string.char(tonumber(h,16))  end)
  	value = string.gsub(value, "&#([0-9]+)%;", function(h)  return string.char(tonumber(h,10))  end)
	value = string.gsub (value, "&quot;", "\"")
	value = string.gsub (value, "&apos;", "'")
	value = string.gsub (value, "&gt;", ">")
	value = string.gsub (value, "&lt;", "<")
	value = string.gsub (value, "&amp;", "&")
	return value
end

-- get current epg for channel description
function epgnow(ref)
    local epgdesc = ""
	local epgTime, e2eventstart, e2eventduration, e2eventcurrenttime
    -- fetch the EPG NOW from the BOX
	if string.find( ref, "http" ) then
		fdepg, msg = vlc.stream( ref )
	else
		fdepg, msg = vlc.stream( webURL.."/web/epgservicenow?sRef="..ref)
	end
    if not fdepg then
        vlc.msg.warn(msg)
        return epgdesc
    end
    local lineepg =  fdepg:readline()
    while ( lineepg ~= nil ) do
		if ( string.find( lineepg, "e2eventstart" ) ) then
			_, _, ref = string.find( lineepg, "<e2eventstart>(.+)</e2eventstart>" )
			if (ref) then e2eventstart = tonumber(ref) end
		elseif ( string.find( lineepg, "e2eventduration" ) ) then
			_, _, ref = string.find( lineepg, "<e2eventduration>(.+)</e2eventduration>" )
			if (ref) then e2eventduration = tonumber(ref) end
		elseif ( string.find( lineepg, "e2eventcurrenttime" ) ) then
			_, _, ref = string.find( lineepg, "<e2eventcurrenttime>(.+)</e2eventcurrenttime>" )
			if (ref) then e2eventcurrenttime = tonumber(ref) end
		elseif ( string.find( lineepg, "e2eventtitle" ) ) then
			_, _, ref = string.find( lineepg, "<e2eventtitle>(.+)</e2eventtitle>" )
			if (ref) then epgdesc = ref end
		elseif ( string.find( lineepg, "e2eventdescription" ) ) then
			_, _, ref = string.find( lineepg, "<e2eventdescription>(.+)</e2eventdescription>" )
			if (ref) then epgdesc = epgdesc .." - "..ref end
		elseif ( string.find( lineepg, "e2eventdescriptionextended" ) ) then
			_, _, ref = string.find( lineepg, "<e2eventdescriptionextended>(.+)</e2eventdescriptionextended>" )
			if (ref) then epgdesc = epgdesc .." - "..ref end
		end    	
   		lineepg = fdepg:readline()
    	if (line ~=  nil) then line = xml2string(line) end
    end
	if ( e2eventstart ~= nil and e2eventduration ~= nil and e2eventcurrenttime ~= nil ) then
		epgTime = e2eventstart + e2eventduration - e2eventcurrenttime
	end
	return epgTime, epgdesc
end

-- get piconurl for channel art
function picon(name)
    local piconurl = name
    if ( piconurl ~=  nil) then piconurl = string.lower(piconurl) end
    if ( piconurl ~=  nil) then piconurl = string.gsub(piconurl, "+", "plus") end
    if ( piconurl ~=  nil) then piconurl = string.gsub(piconurl, "&", "and") end
    if ( piconurl ~=  nil) then piconurl = string.gsub(piconurl, "-", "") end
    if ( piconurl ~=  nil) then piconurl = string.gsub(piconurl, "[.,;:'/ ]", "") end
    if ( piconurl ~=  nil) then piconurl = webURL.."/picon/"..piconurl..".png" end
    if ( piconurl ==  nil) then piconurl = "" end
	return piconurl
end

-- Main
function main()
    -- check if BOX responsive and eventually put BOX in standby
    currURL = webURL.."/web/powerstate"
	if ( put_box_in_standby == 1 ) then
		currURL = currURL.."?newstate=5"
	end 
	fd, msg = vlc.stream( currURL )
    if not fd then
        vlc.sd.add_item({title = "E-TV.lua script error, check tuner_IP config", path = currURL , description = msg..":  [Tuner does not respond, check tuner_IP configuration in plugin file 'E-TV.lua']" })
        return nil
    end
    -- fetch bouquet from the BOX
    currURL = webURL.."/web/getservices?sRef=1:7:1:0:0:0:0:0:0:0:FROM%20BOUQUET%20%22"..bouquet_name.."%22%20ORDER%20BY%20bouquet"
	fd, msg = vlc.stream( currURL )
    if not fd then
        vlc.sd.add_item({title = "E-TV.lua script error loading data for '"..bouquet_name.."'", path = currURL, description = msg.." [Check configuration in plugin file 'E-TV.lua']" })
        return nil
    end
   
    -- create playlist
    local ref, name, nodename, epgDescr, epgTimeInfo, epgURL, streamdef, streamingFullURL
    local nodeid
    local nb = 1
    local line =  fd:readline()
    while ( line ~= nil and nb <= max_Number_of_loaded_channels ) do
		if ( string.find( line, "<e2servicereference>") and string.find( line, ":64:") and string.find( line, ":0:0:0:0:0:0:0:") ) then --catches section marker
			line = xml2string(fd:readline()) -- next line has section name
			_, _, nodename = string.find( line, "<e2servicename>(.+)</e2servicename>" )
			if ( buid_sections_tree == 1  ) then
				nodeid = vlc.sd.add_node{title=nodename} --visible name on the list
			end
		elseif ( string.find( line, "<e2servicereference" ) ) then --catches always first in chain "<e2servicereference>1:0:1:3ADB:514:13E:820000:0:0:0::TVP 1 HD</e2servicereference>"
			streamdef = ""
			_, _, ref = string.find( line, "<e2servicereference>(.+)</e2servicereference>" )
			line = fd:readline() ; if (line ~=  nil) then line = xml2string(line) end -- next line has channel name
			_, _, name = string.find( line, "<e2servicename>(.+)</e2servicename>" ) --catches always second in chain "<e2servicename>TVP 1 HD</e2servicename>"
				
			--remove name from ref as it doesn't work well
			if ( string.find( ref, ":"..name ) ) then ref = ref:gsub(":"..name, "") end
				
			--support for streams
			if ( string.find( ref, "http" ) ) then
				if ( string.find( ref, ":http" ) ) then
					_, _, streamdef = string.find( ref, ":(http[^:]+)" )
				else
					_, _, streamdef = string.find( ref, ":([sy].*http[^:]+)" )
				end
				if ( string.find( streamdef, "%%3a" ) ) then streamdef = streamdef:gsub("%%3a", ":") end
				if ( string.find( streamdef, "127.0.0.1" ) ) then streamdef = streamdef:gsub("127.0.0.1", tuner_IP) end
				if ( string.find( streamdef, "streamlink://" ) ) then streamdef = streamdef:gsub("streamlink://", "http://"..tuner_IP..":8088/") end
				if ( string.find( streamdef, "yt-dlp://" ) ) then streamdef = streamdef:gsub("yt-dlp://", "http://"..tuner_IP..":8088/") end
				if ( string.find( streamdef, "yt-dl://" ) ) then streamdef = streamdef:gsub("yt-dl://", "http://"..tuner_IP..":8088/") end
				--_, _, streamdef = string.find( webRef, "[/:](http[^:]+)" )
				streamingFullURL = streamdef
			else
				streamingFullURL = streamingURL.."/"..ref
			end
			--calculate epgURL
			epgURL = webURL.."/web/epgservicenow?sRef="..ref
			epgTimeInfo, epgDescr = epgnow(epgURL)
			if (nodeid ~=  nil) then 
				nodeid:add_subitem({tracknum = string.format("%0003d",nb), path = streamingFullURL, title = name, arturl = picon(name), duration = epgTimeInfo, album = epgDescr, description = epgDescr })
			else
				vlc.sd.add_item({tracknum = string.format("%0003d",nb), path = streamingFullURL, title = name, arturl = picon(name), duration = epgTimeInfo, album = epgDescr, description = epgDescr })
			end
			nb = nb + 1
		end
		line = fd:readline()
    	if (line ~=  nil) then line = xml2string(line) end
    end
    
    if ( nb == 1 ) then
        vlc.sd.add_item({title = "E-TV.lua empty bouqet received", path = currURL, description = "Copy path and check in web browser" })
        return nil
	elseif ( add_debug_info == 1 ) then
		vlc.sd.add_item({title = "Bouquet URL for Debuging: "..currURL , path = currURL, description = "Copy path and check in web browser" })
    end
end
