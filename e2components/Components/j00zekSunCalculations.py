#
# j00zek 2018  
# based on:
#    https://stackoverflow.com/questions/19615350/calculate-sunrise-and-sunset-times-for-a-given-gps-coordinate-within-postgresql
# plus automatically recognizes the coordinates

from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3

from decimal import Decimal as dec

import math
import datetime
import json
import time

class Sun:
    def getSunriseTime( self, longitude, latitude, year = None, month = None, day = None ):
        return self.calcSunTime( longitude, latitude, True, 90.8, year, month, day )
    
    def getSunsetTime( self, longitude, latitude, year = None, month = None, day = None ): 
        return self.calcSunTime( longitude, latitude, False, 90.8, year, month, day )
    
    def getDayDiffTimes( self, longitude, latitude, year = None, month = None, day = None ): 
        if year is None or month is None or day is None:
            now = datetime.datetime.now()
            day = now.day
            month = now.month
            year = now.year
        
        DayLengthDec = self.getDayLength(longitude, latitude, year, month, day )['DayLengthDec']
        sDayLengthDec = self.getShortestDayLength(longitude, latitude, year )['ShortestDayLengthDec']
        lDayLengthDec = self.getLongestDayLength(longitude, latitude, year )['LongestDayLengthDec']
        diffToShortestDec = DayLengthDec - sDayLengthDec
        diffToLongestDec = lDayLengthDec - DayLengthDec
        diffHourS = int(diffToShortestDec)
        diffMinsS = int((diffToShortestDec - diffHourS) * float(60))
        diffSecsS = int(diffToShortestDec * 3600) - diffHourS * 3600 - diffMinsS * 60
        diffToShortest = ''
        if diffHourS != 0: diffToShortest = '%s:' % diffHourS
        if diffMinsS < 10 and diffHourS != 0: diffToShortest += '0'
        diffToShortest += '%s:' % diffMinsS
        if diffSecsS < 10: diffToShortest += '0'
        diffToShortest += '%s' % diffSecsS
        
        diffHourL = int(diffToLongestDec)
        diffMinsL = int((diffToLongestDec - diffHourL)*float(60))
        diffSecsL = int(diffToLongestDec * 3600) - diffHourL * 3600 - diffMinsL * 60
        diffToLongest = ''
        if diffHourL != 0: diffToLongest = '%s:' % diffHourL
        if diffMinsL < 10 and diffHourL != 0: diffToLongest += '0'
        diffToLongest += '%s:' % diffMinsL
        if diffSecsL < 10: diffToLongest += '0'
        diffToLongest += '%s' % diffSecsL
        
        return {'diffToShortestDec': diffToShortestDec,
                'diffToShortest':    diffToShortest,
                'diffToShortesttHours':  diffHourS,
                'diffToShortestMinutes': diffMinsS,
                'diffToShortestSeconds': diffSecsS,
                'diffToLongestDec': diffToLongestDec,
                'diffToLongest':    diffToLongest,
                'diffToLongestHours':   diffHourL,
                'diffToLongestMinutes': diffMinsL,
                'diffToLongestSeconds': diffSecsL,
                }
    
    def getDayLength( self, longitude, latitude, year = None, month = None, day = None ):
        daySunriseDec = self.calcSunTime( longitude, latitude, True, 90.8, year, month, day )['UTCtimeDec']
        daySunsetDec = self.calcSunTime( longitude, latitude, False, 90.8, year, month, day )['UTCtimeDec']
        DayLengthDec = daySunsetDec - daySunriseDec
        dayLengthHour = int(DayLengthDec)
        dayLengthMinute = int((DayLengthDec - dayLengthHour)*60.0)
        if dayLengthMinute >=10:
            dayLength = "%s:%s" % (dayLengthHour,dayLengthMinute)
        else:
            dayLength = "%s:0%s" % (dayLengthHour,dayLengthMinute)
        return {'DayLengthDec': DayLengthDec,
                'dayLength': dayLength,
                }
    
    def getShortestDayLength( self, longitude, latitude, year = None ):
        if year is None:
            year = datetime.datetime.now().year
        DayLengthDec = 99
        dayLength = ''
        for day in (21, 22):
            daySunriseDec = self.calcSunTime( longitude, latitude, True, zenith = 90.8, year = year, month = 12, day = day )['UTCtimeDec']
            daySunsetDec = self.calcSunTime( longitude, latitude, False, zenith = 90.8, year = year, month = 12, day = day )['UTCtimeDec']
            if DayLengthDec > daySunsetDec - daySunriseDec:
                DayLengthDec = daySunsetDec - daySunriseDec
                dayLengthHour = int(DayLengthDec)
                dayLengthMinute = int((DayLengthDec - dayLengthHour)*60.0)
                if dayLengthMinute >=10:
                    dayLength = "%s:%s" % (dayLengthHour,dayLengthMinute)
                else:
                    dayLength = "%s:0%s" % (dayLengthHour,dayLengthMinute)
                
        return {'ShortestDayLengthDec': DayLengthDec,
                'ShortestdayLength': dayLength,
                }
    def getLongestDayLength( self, longitude, latitude, year = None ):
        if year is None:
            year = datetime.datetime.now().year
        DayLengthDec = 99
        dayLength = ''
        for day in (20, 21):
            daySunriseDec = self.calcSunTime( longitude, latitude, True, zenith = 90.8, year = year, month = 6, day = day )['UTCtimeDec']
            daySunsetDec = self.calcSunTime( longitude, latitude, False, zenith = 90.8, year = year, month = 6, day = day )['UTCtimeDec']
            if DayLengthDec > daySunsetDec - daySunriseDec:
                DayLengthDec = daySunsetDec - daySunriseDec
                dayLengthHour = int(DayLengthDec)
                dayLengthMinute = int((DayLengthDec - dayLengthHour)*60.0)
                if dayLengthMinute >=10:
                    dayLength = "%s:%s" % (dayLengthHour,dayLengthMinute)
                else:
                    dayLength = "%s:0%s" % (dayLengthHour,dayLengthMinute)
                
        return {'LongestDayLengthDec': DayLengthDec,
                'LongestdayLength': dayLength,
                }
    def calcSunTime( self, longitude, latitude, isRiseTime, zenith = 90.8, year = None, month = None, day = None ):
        # isRiseTime == False, returns sunsetTime
        longitude = float(longitude)
        latitude = float(latitude)

        if year is None or month is None or day is None:
            now = datetime.datetime.now()
            day = now.day
            month = now.month
            year = now.year

        TO_RAD = math.pi/180

        #1. first calculate the day of the year
        N1 = math.floor(275 * month / 9)
        N2 = math.floor((month + 9) / 12)
        N3 = (1 + math.floor((year - 4 * math.floor(year / 4) + 2) / 3))
        N = N1 - (N2 * N3) + day - 30

        #2. convert the longitude to hour value and calculate an approximate time
        lngHour = longitude / 15

        if isRiseTime:
            t = N + ((6 - lngHour) / 24)
        else: #sunset
            t = N + ((18 - lngHour) / 24)

        #3. calculate the Sun's mean anomaly
        M = (0.9856 * t) - 3.289

        #4. calculate the Sun's true longitude
        L = M + (1.916 * math.sin(TO_RAD*M)) + (0.020 * math.sin(TO_RAD * 2 * M)) + 282.634
        L = self.forceRange( L, 360 ) #NOTE: L adjusted into the range [0,360)

        #5a. calculate the Sun's right ascension

        RA = (1/TO_RAD) * math.atan(0.91764 * math.tan(TO_RAD*L))
        RA = self.forceRange( RA, 360 ) #NOTE: RA adjusted into the range [0,360)

        #5b. right ascension value needs to be in the same quadrant as L
        Lquadrant  = (math.floor( L/90)) * 90
        RAquadrant = (math.floor(RA/90)) * 90
        RA = RA + (Lquadrant - RAquadrant)

        #5c. right ascension value needs to be converted into hours
        RA = RA / 15

        #6. calculate the Sun's declination
        sinDec = 0.39782 * math.sin(TO_RAD*L)
        cosDec = math.cos(math.asin(sinDec))

        #7a. calculate the Sun's local hour angle
        cosH = (math.cos(TO_RAD*zenith) - (sinDec * math.sin(TO_RAD*latitude))) / (cosDec * math.cos(TO_RAD*latitude))

        if cosH > 1:
            return {'status': False, 'msg': 'the sun never rises on this location (on the specified date)'}

        if cosH < -1:
            return {'status': False, 'msg': 'the sun never sets on this location (on the specified date)'}

        #7b. finish calculating H and convert into hours

        if isRiseTime:
            H = 360 - (1/TO_RAD) * math.acos(cosH)
        else: #setting
            H = (1/TO_RAD) * math.acos(cosH)

        H = H / 15

        #8. calculate local mean time of rising/setting
        T = H + RA - (0.06571 * t) - 6.622

        #9. adjust back to UTC
        UT = T - lngHour
        UT = self.forceRange( UT, 24) # UTC time in decimal format (e.g. 23.23)

        #9a. adjust to TZ LOCAL TIME by j00zek
        now_timestamp = time.time()
        offset = datetime.datetime.fromtimestamp(now_timestamp) - datetime.datetime.utcfromtimestamp(now_timestamp)
        offset = divmod(offset.seconds,3600)[0]
        LT = UT + offset
        LT = self.forceRange( LT, 24)
        
        #10. Return
        hr = self.forceRange(int(UT), 24)
        min = round((UT - int(UT))*60,0)
        if int(min) >= 60:
            min = 59

        #j00zek return in clock format
        Lhr = self.forceRange(int(LT), 24)
        if min >=10:
            UTCtime = "%s:%s" % (int(hr),int(min))
            TZtime = "%s:%s" % (int(Lhr),int(min))
        else:
            UTCtime = "%s:0%s" % (int(hr),int(min))
            TZtime = "%s:0%s" % (int(Lhr),int(min))
        
        return {
            'status': True,
            'UTCtimeDec': UT,
            'TZtimeDec': LT,
            'UTChr': hr,
            'min': min, 
            'TZhr': Lhr,
            'UTCtime': UTCtime,
            'TZtime': TZtime
        }

    def forceRange( self, v, max ):
        # force v to be >= 0 and < max
        if v < 0: return v + max
        elif v >= max: return v - max
        return v
        
class geo():
    Position = {}
    def __init__(self, DBG = False):
        self.DBG = DBG
        if self.DBG: print('[geo:__init__] >>>')
        try:
            from Components.config import config
            geo.Position['latitude'] = float(config.plugins.MSNweatherNP.Entry[0].geolatitude.value)
            geo.Position['longitude'] = float(config.plugins.MSNweatherNP.Entry[0].geolongitude.value)
            if self.DBG: print("[self:getPosition] configured latitude=%s, longitude=%s" % (geo.Position['latitude'],geo.Position['longitude']))
        except Exception as e:
            if self.DBG: print("[self:getPosition] >>> Error getting configured data: '%s'" % str(e))

    def readWebData(self):
        try:
            import urllib2
            response = urllib2.urlopen('https://dcinfos.abtasty.com/geolocAndWeather.php', timeout=1)
            response = response.read()
            geo.Position = json.loads(response.strip()[1:-1])
        except Exception as e:
            print(str(e))
            if self.DBG: print("Error importing twisted. Something wrong with the image?")
            

    def getLatitude(self):
        retVal = geo.Position.get('latitude', None)
        if retVal is None:
            self.readWebData()
            retVal = geo.Position.get('latitude', '?')
            if self.DBG: print("from Web getLatitude()='%s'" % retVal)
        else:
            if self.DBG: print("Read getLatitude()='%s'" % retVal)
        return retVal
        
    def getLongitude(self):
        retVal = geo.Position.get('longitude', None)
        if retVal is None:
            self.readWebData()
            retVal = geo.Position.get('longitude', '?')
            if self.DBG: print("from Web longitude()='%s'" % retVal)
        else:
            if self.DBG: print("Read longitude()='%s'" % retVal)
        return retVal

#for tests outside e2
if __name__ == '__main__':
    print(geo(True).getLatitude())
    print(geo(True).getLongitude())
