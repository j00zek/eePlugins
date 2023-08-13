# Copyright (c) 2017 Daniel Minor
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# All calculations taken from:
# Astronomical Algorithms; 2nd Edition, Jean Meeus, Willmann-Bell (1998)
from math import acos, asin, atan2, cos, fabs, floor, pi, sin, tan


# Julian Day of 2000 January 1.5, used as a standard equinox
J2000 = 2451545.0


# unit conversions
AU_TO_M = 149598000000
DEG_TO_RAD = pi/180.0
RAD_TO_DEG= 180.0/pi


# D, M, Mprime, F
LUNAR_LON_ARGS = [
    [0, 0, 1, 0],
    [2, 0, -1, 0],
    [2, 0, 0, 0],
    [0, 0, 2, 0],
    [0, 1, 0, 0],
    [0, 0, 0, 2],
    [2, 0, -2, 0],
    [2, -1, -1, 0],
    [2, 0, 1, 0],
    [2, -1, 0, 0],
    [0, 1, -1, 0],
    [1, 0, 0, 0],
    [0, 1, 1, 0],
    [2, 0, 0, -2],
    [0, 0, 1, 2],
    [0, 0, 1, -2],
    [4, 0, -1, 0],
    [0, 0, 3, 0],
    [4, 0, -2, 0],
    [2, 1, -1, 0],
    [2, 1, 0, 0],
    [1, 0, -1, 0],
    [1, 1, 0, 0],
    [2, -1, 1, 0],
    [2, 0, 2, 0],
    [4, 0, 0, 0],
    [2, 0, -3, 0],
    [0, 1, -2, 0],
    [2, 0, -1, 2],
    [2, -1, -2, 0],
    [1, 0, 1, 0],
    [2, -2, 0, 0],
    [0, 1, 2, 0],
    [0, 2, 0, 0],
    [2, -2, -1, 0],
    [2, 0, 1, -2],
    [2, 0, 0, 2],
    [4, -1, -1, 0],
    [0, 0, 2, 2],
    [3, 0, -1, 0],
    [2, 1, 1, 0],
    [4, -1, -2, 0],
    [0, 2, -1, 0],
    [2, 2, -1, 0],
    [2, 1, -2, 0],
    [2, -1, 0, -2],
    [4, 0, 1, 0],
    [0, 0, 4, 0],
    [4, -1, 0, 0],
    [1, 0, -2, 0],
    [2, 1, 0, -2],
    [0, 0, 2, -2],
    [1, 1, 1, 0],
    [3, 0, -2, 0],
    [4, 0, -3, 0],
    [2, -1, 2, 0],
    [0, 2, 1, 0],
    [1, 1, -1, 0],
    [2, 0, 3, 0],
    [2, 0, -1, -2],
]


# D, M, Mprime, F
LUNAR_LAT_ARGS = [
    [0, 0, 0, 1],
    [0, 0, 1, 1],
    [0, 0, 1, -1],
    [2, 0, 0, -1],
    [2, 0, -1, 1],
    [2, 0, -1, -1],
    [2, 0, 0, 1],
    [0, 0, 2, 1],
    [2, 0, 1, -1],
    [0, 0, 2, -1],
    [2, -1, 0, -1],
    [2, 0, -2, -1],
    [2, 0, 1, 1],
    [2, 1, 0, -1],
    [2, -1, -1, 1],
    [2, -1, 0, 1],
    [2, -1, -1, -1],
    [0, 1, -1, -1],
    [4, 0, -1, -1],
    [0, 1, 0, 1],
    [0, 0, 0, 3],
    [0, 1, -1, 1],
    [1, 0, 0, 1],
    [0, 1, 1, 1],
    [0, 1, 1, -1],
    [0, 1, 0, -1],
    [1, 0, 0, -1],
    [0, 0, 3, 1],
    [4, 0, 0, -1],
    [4, 0, -1, 1],
    [0, 0, 1, -3],
    [4, 0, -2, 1],
    [2, 0, 0, -3],
    [2, 0, 2, -1],
    [2, -1, 1, -1],
    [2, 0, -2, 1],
    [0, 0, 3, -1],
    [2, 0, -2, 1],
    [0, 0, 3, -1],
    [2, 0, 2, 1],
    [2, 0, -3, -1],
    [2, 1, -1, 1],
    [2, 1, 0, 1],
    [4, 0, 0, 1],
    [2, -1, 1, 1],
    [2, -2, 0, -1],
    [0, 0, 1, 3],
    [2, 1, 1, -1],
    [1, 1, 0, -1],
    [1, 1, 0, 1],
    [0, 1, -2, -1],
    [2, 1, -1, -1],
    [1, 0, 1, 1],
    [2, -1, -2, -1],
    [0, 1, 2, 1],
    [4, 0, -2, -1],
    [4, -1, -1, -1],
    [1, 0, 1, -1],
    [4, 0, 1, -1],
    [1, 0, -1, -1],
    [4, -1, 0, -1],
    [2, -2, 0, 1],
]


# lon, dist, lat
LUNAR_COEFF =[
    [6288774, -20905355, 5128122],
    [1274027, -3699111, 280602],
    [658314, -2955968, 277693],
    [213618, -569925, 173237],
    [-185116, 48888, 55413],
    [-114332, -3149, 46271],
    [58793, 246158, 32573],
    [57066, -152138, 17198],
    [53322, -170733, 9266],
    [45758, -204586, 8822],
    [-40923, -129620, 8216],
    [-34720, 108743, 4324],
    [-30383, 104755, 4200],
    [15327, 10321, -3359],
    [-12528, 0, 2463],
    [10980, 79661, 2211],
    [10675, -34782, 2065],
    [10034, -23210, -1870],
    [8548, -21636, 1828],
    [-7888, 24208,  -1794],
    [-6766, 30824, -1749],
    [-5163, -8379, -1565],
    [4987, -16675, -1491],
    [4036, -12831, -1475],
    [3994, -10445, -1410],
    [3861, -11650, -1344],
    [3665, 14403, -1335],
    [-2689, -7003, 1107],
    [-2602, 0, 1021],
    [2390, 10056, 833],
    [-2348, 6322, 777],
    [2236, -9884, 671],
    [-2120, 5751, 607],
    [-2069, 0, 596],
    [2048, -4950, 491],
    [-1773, 4130, -451],
    [-1595, 0, 439],
    [1215, -3958, 422],
    [-1110, 0, 421],
    [-892, 3258, -366],
    [-810, 2616, -351],
    [759, -1897, 331],
    [-713, -2117, 315],
    [-700, 2354, 302],
    [691, 0, -283],
    [596, 0, -229],
    [549, -1423, 223],
    [537, -1117, 223],
    [520, -1571, -220],
    [-487, -1739, -220],
    [-399, 0, -185],
    [-381, -4421, 181],
    [351, 0, -177],
    [-340, 0, 176],
    [330, 0, 166],
    [327, 0, -164],
    [-323, 1165, 132],
    [299, 0, -119],
    [294, 0, 115],
    [0, 8752, 107],
]


#D, M, Mprime, F, omega
NUTATION_ARGS = [
    [0, 0, 0, 0, 1],
    [-2, 0, 0, 2, 2],
    [0, 0, 0, 2, 2],
    [0, 0, 0, 0, 2],
    [0, 1, 0, 0, 0],
    [0, 0, 1, 0, 0],
    [-2, 1, 0, 2, 2],
    [0, 0, 0, 2, 1],
    [0, 0, 1, 2, 2],
    [-2, -1, 0, 2, 2],
    [-2, 0, 1, 0, 0],
    [-2, 0, 0, 2, 1],
    [0, 0, -1, 2, 2],
    [2, 0, 0, 0, 0],
    [0, 0, 1, 0, 1],
    [2, 0, -1, 2, 2],
    [0, 0, -1, 0, 1],
    [0, 0, 1, 2, 1],
    [-2, 0, 2, 0, 0],
    [0, 0, -2, 2, 1],
    [2, 0, 0, 2, 2],
    [0, 0, 2, 2, 2],
    [0, 0, 2, 0, 0],
    [-2, 0, 1, 2, 2],
    [0, 0, 0, 2, 0],
    [-2, 0, 0, 2, 0],
    [0, 0, -1, 2, 1],
    [0, 2, 0, 0, 0],
    [2, 0, -1, 0, 1],
    [-2, 2, 0, 2, 2],
    [0, 1, 0, 0, 1],
    [-2, 0, 1, 0, 1],
    [0, -1, 0, 0, 1],
    [0, 0, 2, -2, 0],
    [2, 0, -1, 2, 1],
    [2, 0, 1, 2, 2],
    [0, 1, 0, 2, 2],
    [-2, 1, 1, 0, 0],
    [0, -1, 0, 2, 2],
    [2, 0, 0, 2, 1],
    [2, 0, 1, 0, 0],
    [-2, 0, 2, 2, 2],
    [-2, 0, 1, 2, 1],
    [2, 0, -2, 0, 1],
    [2, 0, 0, 0, 1],
    [0, -1, 1, 0, 0],
    [-2, -1, 0, 2, 1],
    [-2, 0, 0, 0, 1],
    [0, 0, 2, 2, 1],
    [-2, 0, 2, 0, 1],
    [-2, 1, 0, 2, 1],
    [0, 0, 1, -2, 0],
    [-1, 0, 1, 0, 0],
    [-2, 1, 0, 0, 0],
    [1, 0, 0, 0, 0],
    [0, 0, 1, 2, 0],
    [0, 0, -2, 2, 2],
    [-1, -1, 1, 0, 0],
    [0, 1, 1, 0, 0],
    [0, -1, 1, 2, 2],
    [2, -1, -1, 2, 2],
    [0, 0, 3, 2, 2],
    [2, -1, 0, 2, 2],
]

NUTATION_SIN_COEFF = [
    [-171996, -174.2],
    [-13187, -1.6],
    [-2274, -0.2],
    [2062, 0.2],
    [1426, -3.4],
    [712, 0.1],
    [-517, 1.2],
    [-386, -0.4],
    [-301, 0],
    [217, -0.5],
    [-158, 0],
    [129, 0.1],
    [123, 0],
    [63, 0],
    [63, 0.1],
    [-59, 0],
    [-58, -0.1],
    [-51, 0],
    [48, 0],
    [46, 0],
    [-38, 0],
    [-31, 0],
    [29, 0],
    [29, 0],
    [26, 0],
    [-22, 0],
    [21, 0],
    [17, -0.1],
    [16, 0],
    [-16, 0.1],
    [-15, 0],
    [-13, 0],
    [-12, 0],
    [11, 0],
    [-10, 0],
    [-8, 0],
    [7, 0],
    [-7, 0],
    [-7, 0],
    [-7, 0],
    [6, 0],
    [6, 0],
    [6, 0],
    [-6, 0],
    [-6, 0],
    [5, 0],
    [-5, 0],
    [-5, 0],
    [-5, 0],
    [4, 0],
    [4, 0],
    [4, 0],
    [-4, 0],
    [-4, 0],
    [-4, 0],
    [3, 0],
    [-3, 0],
    [-3, 0],
    [-3, 0],
    [-3, 0],
    [-3, 0],
    [-3, 0],
    [-3, 0],
]


NUTATION_COS_COEFF = [
    [92025, 8.9],
    [5736, -3.1],
    [977, -0.5],
    [-895, 0.5],
    [54, -0.1],
    [-7, 0],
    [224, -0.6],
    [200, 0],
    [129, -0.1],
    [-95, 0.3],
    [0, 0],
    [-70, 0],
    [-53, 0],
    [0, 0],
    [-33, 0],
    [26, 0],
    [32, 0],
    [27, 0],
    [0, 0],
    [-24, 0],
    [16, 0],
    [13, 0],
    [0, 0],
    [-12, 0],
    [0, 0],
    [0, 0],
    [-10, 0],
    [0, 0],
    [-8, 0],
    [7, 0],
    [9, 0],
    [7, 0],
    [6, 0],
    [0, 0],
    [5, 0],
    [3, 0],
    [-3, 0],
    [0, 0],
    [3, 0],
    [3, 0],
    [0, 0],
    [-3, 0],
    [-3, 0],
    [3, 0],
    [3, 0],
    [0, 0],
    [3, 0],
    [3, 0],
    [3, 0],
    [0, 0],
    [0, 0],
    [0, 0],
    [0, 0],
    [0, 0],
    [0, 0],
    [0, 0],
    [0, 0],
    [0, 0],
    [0, 0],
    [0, 0],
    [0, 0],
    [0, 0],
    [0, 0],
]


def apparent_sidereal_time_greenwich(y, m, d):
    """Calculate the apparent sidereal time at Greenwich for the specified date.

    The result is in hours.
    """
    M = mean_sidereal_time_greenwich(y, m, d)
    delta_phi, delta_eps, eps = nutation(y, m, d)
    return M + delta_phi*cos(DEG_TO_RAD*(eps + delta_eps))


def deg_to_hms(d):
    """Convert right ascension in decimal degrees to hours, minutes and seconds."""

    hours = d/15.0
    h = int(floor(hours))
    hours -= h
    m = int(floor(hours*60.0))
    hours -= m/60.0
    s = hours*3600.0
    return h, m, s


def hms_to_deg(h, m, s):
    """Convert right ascension in hours, minutes and seconds to decimal degrees."""

    return 15.0*(h + m/60.0 + s/3600.0)


def illuminated_fraction_of_moon(y, m, d):
    """Return illuminated fraction of the moon's disc at the specified date."""

    a0, d0, r0 = lunar_position(y, m, d)
    a, d, r = solar_position(y, m, d)

    a0 *= DEG_TO_RAD
    d0 *= DEG_TO_RAD
    a *= DEG_TO_RAD
    d *= DEG_TO_RAD
    r *= AU_TO_M

    phi = acos(sin(d0)*sin(d) + cos(d0)*cos(d)*cos(a0 - a))
    i = atan2(r*sin(phi), (r0 - r*cos(phi)))
    return 0.5 * (1 + cos(i))


def julian_day(y, m, d, gregorian=True):
    """Calculate Julian Day

       The Julian Day is the number of days elapsed since
       noon on January 1st of the year -4712.

       y: year
       m: month (1 = January, 2 = February, ...)
       d: day (fractional to indicate portion of a day)
       gregorian: True if date is in the Gregorian calendar,
                  False if date is in the Julian calendar.
    """

    if m <= 2:
        y -= 1
        m += 12

    if gregorian:
        a = floor(y/100.0)
        b = 2 - a + floor(a/4.0)
    else:
        b = 0

    return floor(365.25*(y + 4716)) + floor(30.6001*(m + 1)) + d + b - 1524.5


def lunar_position(y, m, d):
    """Calculate the apparent right ascension, declination and distance of the Moon at the specified date.

    """
    jd = julian_day(y, m, d) - J2000
    t = jd/36525.0

    # mean longitude of the Moon
    lprime = DEG_TO_RAD*((218.3164477 + 481267.88123421*t - 0.0015786*t*t + t*t*t/538841.0 - t*t*t*t/65194000.0) % 360)

    # mean elongation of the Moon
    D = DEG_TO_RAD*((297.8501921 + 445267.1114034*t - 0.0018819*t*t + t*t*t/545868.0 - t*t*t*t/113065000.0) % 360)

    # mean anomaly of the Sun
    # note: this doesn't quite match the calculation used for solar position
    M = DEG_TO_RAD*((357.52911 + 35999.0502909*t - 0.0001536*t*t + t*t*t/24490000) % 360)

    # mean anomaly of the Moon
    Mprime = DEG_TO_RAD*((134.9633964 + 477198.8675055*t + 0.0087414*t*t + t*t*t/69699.0 - t*t*t*t/14712000.0) % 360)

    # argument of latitude of the Moon
    f = DEG_TO_RAD*((93.2720950 + 483202.0175233*t - 0.0036539*t*t - t*t*t/3526000.0 + t*t*t*t/863310000.0) % 360)

    # three further arguments, a1 is due to Venus, a2 is due to Jupiter
    a1 = DEG_TO_RAD*((119.75 + 131.849*t) % 360)
    a2 = DEG_TO_RAD*((53.09 + 479264.290*t) % 360)
    a3 = DEG_TO_RAD*((313.45 + 481266.484*t) % 360)

    # "correction" for eccentricity of Earth's orbit
    e = 1.0 - 0.002516*t - 0.0000074*t*t
    e2 = e*e

    sigmal = 0.0
    sigmab = 0.0
    sigmar = 0.0
    for i, args in enumerate(LUNAR_LON_ARGS):
        coeff = LUNAR_COEFF[i]
        x = args[0]*D + args[1]*M + args[2]*Mprime + args[3]*f
        if args[1] == 1 or args[1] == -1:
            sigmal += e*coeff[0]*sin(x)
            sigmar += e*coeff[1]*cos(x)
        elif args[1] == 2 or args[1] == -2:
            sigmal += e2*coeff[0]*sin(x)
            sigmar += e2*coeff[1]*cos(x)
        else:
            sigmal += coeff[0]*sin(x)
            sigmar += coeff[1]*cos(x)

        args = LUNAR_LAT_ARGS[i]
        x = args[0]*D + args[1]*M + args[2]*Mprime + args[3]*f
        if args[1] == 1 or args[1] == -1:
            sigmab += e*coeff[2]*sin(x)
        elif args[1] == 2 or args[1] == -2:
            sigmab += e2*coeff[2]*sin(x)
        else:
            sigmab += coeff[2]*sin(x)

    sigmal += 3958*sin(a1) + 1962*sin(lprime - f) + 318*sin(a2)
    sigmab += (-2235*sin(lprime) + 382*sin(a3) + 175*sin(a1 - f) +
               175*sin(a1 + f) + 127*sin(lprime - Mprime) -
               115*sin(lprime + Mprime))

    true_lon = RAD_TO_DEG*lprime + sigmal*1e-6

    # TODO: the calculation for latitude is slightly off compared to the reference
    true_lat = sigmab*1e-6
    radius = 385000.56 + sigmar*1e-3

    # apparent longitude
    delta_phi, _, eps = nutation(y, m, d)
    apparent_lon = true_lon + delta_phi

    eps *= DEG_TO_RAD

    right_ascension = atan2(cos(eps)*sin(DEG_TO_RAD*apparent_lon) - sin(eps)*tan(DEG_TO_RAD*true_lat), cos(DEG_TO_RAD*apparent_lon))*RAD_TO_DEG
    declination = asin(sin(DEG_TO_RAD*true_lat)*cos(eps) + sin(eps)*sin(DEG_TO_RAD*apparent_lon)*cos(DEG_TO_RAD*true_lat))*RAD_TO_DEG

    return right_ascension, declination, radius


def mean_sidereal_time_greenwich(y, m, d):
    """Calculate mean sidereal time at Greenwich for the specified date

    The result is in hours.
    """

    jd = julian_day(y, m, d) - J2000
    t = jd/36525.0
    return (280.46061837 + 360.98564736629*jd + 0.000387933*t*t - t*t*t/38710000.0) % 360.0


def moonrise_moonset(lat, lon, y, m, d, h0=0.125, dt=0.0):
    """ Calculate time of moonrise and moonset.

    lat, lon: latitude and longitude of observer.
    y, m, d: year, month and day for which to do the calculation.
    h0: geometric altitude of the Moon. The default value corresponds to the
        mean value, the actual value varies with the Moon's horizontal parallax.
    dt: delta between universal time and dynamical time.

    This returns the time of moonrise and moonset in UT.
    """

    positions = [
        lunar_position(y, m, floor(d - 1)),
        lunar_position(y, m, floor(d)),
        lunar_position(y, m, floor(d + 1))
    ]

    moonrise, _, moonset = rise_transit_set(lat, lon, y, m, d, h0, positions)

    return moonrise*24.0, moonset*24.0


def getMoonTimes(date, lat, lng):
    moonrise, moonset = moonrise_moonset(lat, lng, date.year, date.month, date.day)
    return moonrise, moonset
    
def nutation(y, m, d):
    """Calculate the nutation ("wobble" in the Earth's axis of rotation) for the specified date.

    This returns delta_phi and delta_eps in hours and
    eps in decimal degrees.
    """

    jd = julian_day(y, m, d) - J2000
    t = jd/36525.0

    # mean elongation of Moon from Sun
    D = DEG_TO_RAD*(297.85036 + 445267.111480*t - 0.0019142*t*t + t*t*t/189474.0)

    # mean anomaly of the Sun
    M = DEG_TO_RAD*(357.52772 + 35999.050340*t - 0.0001603*t*t + t*t*t/300000.0)

    # mean anomaly of the Moon
    Mprime = DEG_TO_RAD*(134.96298 + 477198.867398*t + 0.0086972*t*t + t*t*t/56250.0)

    # Moon's argument of latitude
    F = DEG_TO_RAD*(93.27191 + 483202.017538*t - 0.0036825*t*t + t*t*t/327270.0)

    # longitude of the ascending node of the Moon's mean orbit on the
    # elliptic, measured from the mean equinox of the date.
    omega = DEG_TO_RAD*(125.04452 - 1934.136261*t + 0.0020708*t*t + t*t*t/450000.0)

    delta_phi = 0.0
    delta_eps = 0.0
    for i, args in enumerate(NUTATION_ARGS):
        x = args[0]*D + args[1]*M + args[2]*Mprime + args[3]*F + args[4]*omega
        delta_phi += (NUTATION_SIN_COEFF[i][0] + NUTATION_SIN_COEFF[i][1]*t)*sin(x)
        delta_eps += (NUTATION_COS_COEFF[i][0] + NUTATION_COS_COEFF[i][1]*t)*cos(x)

    # convert results from 0.0001 seconds to hours
    delta_phi /= 1e4*3600
    delta_eps /= 1e4*3600

    # mean obliquity of the ecliptic
    eps0 = 23.0 + 26/60.0 + (21.448 - 46.8150*t - 0.00059*t*t + 0.001813*t*t*t)/3600.0

    return delta_phi, delta_eps, eps0


def solar_position(y, m, d):
    """Calculate the right ascension, declination and distance of the Sun at the specified time.

    The right ascension and declination are in degrees, the distance is in AU.

    The accuracy is to within 0.01 degree.

    """

    jd = julian_day(y, m, d) - J2000
    t = jd/36525.0

    # mean longitude of the Sun
    mean_lon  = (280.46646 + 36000.76983*t + 0.0003032*t*t) % 360

    # mean anomaly of the Sun
    M = DEG_TO_RAD*((357.52911 + 35999.05028*t - 0.0001537*t*t) % 360)

    # eccentricity of the Earth's orbit
    ecc = 0.016708634 - 0.000042037*t - 0.0000001267*t*t

    # center
    c = ((1.914602 - 0.004817*t - 0.000014*t*t)*sin(M) +
         (0.019993 - 0.000101*t )*sin(2*M) +
         0.000289*sin(3*M))

    # true longitude and true anomaly
    true_lon = mean_lon + c
    true_anomaly = M*RAD_TO_DEG + c

    # distance
    r = 1.000001018*(1 - ecc*ecc) / (1 + ecc*cos(DEG_TO_RAD*true_anomaly))

    # apparent longitude
    omega = DEG_TO_RAD*(125.04 - 1934.136*t)
    apparent_lon = DEG_TO_RAD*((true_lon - 0.00569 - 0.00478*sin(omega)) % 360)

    _, _, eps = nutation(y, m, d)

    # correct epsilon for apparent location
    eps = DEG_TO_RAD*(eps + 0.00256*cos(omega))

    right_ascension = atan2(cos(eps)*sin(apparent_lon), cos(apparent_lon))*RAD_TO_DEG
    declination = asin(sin(eps)*sin(apparent_lon))*RAD_TO_DEG

    return right_ascension, declination, r


def rise_transit_set(lat, lon, y, m, d, h0, pos, dt=0.0):
    """Calculate time of rise, transit and set for an astronomical body.

    lat, lon: observer latitude and longitude.
    y, m, d: year, month and day.
    h0: the "standard" altitude, the geometric altitude of the center of the
        body at the time of rising or setting.
    pos: array of three (right ascension, declination) pairs for the body
         on d - 1, d, and d + 1.
    dt: delta between universal time and dynamical time.

    This returns the rise, transit and set times in hours. If the body does not rise or set on that date it returns NaN instead.
    """

    # calculate approximate times
    theta = apparent_sidereal_time_greenwich(y, m, floor(d))

    cos_H0 = (sin(DEG_TO_RAD*h0) - sin(DEG_TO_RAD*lat)*sin(DEG_TO_RAD*pos[1][1])) / (cos(DEG_TO_RAD*lat)*cos(DEG_TO_RAD*pos[1][1]))

    # in this case the body does not rise or set on that date.
    if fabs(cos_H0) > 1.0:
        return float("nan"), float("nan"), float("nan")

    H0 = acos(cos_H0)*RAD_TO_DEG

    m0 = (pos[1][0] - lon - theta)/360.0
    m1 = m0 - H0/360.0
    m2 = m0 + H0/360.0

    def normalize(m):
        if m < 0:
            m += 1.0
        if m > 1:
            m -= 1.0
        return m

    m0 = normalize(m0)
    m1 = normalize(m1)
    m2 = normalize(m2)

    def interpolate(xs, n):
        n += dt/86400.0

        a = xs[1] - xs[0]
        b = xs[2] - xs[1]
        c = xs[0] + xs[2] - 2*xs[1]
        return xs[1] + 0.5*n*(a + b + n*c)

    def correct(m, transit):
        # sidereal time
        st = (theta + 360.985647*m) % 360

        # interpolate right ascension and declination
        alpha = interpolate([pos[0][0], pos[1][0], pos[2][0]], m)
        delta = interpolate([pos[0][1], pos[1][1], pos[2][1]], m)

        H = st + lon - alpha
        h = asin(sin(DEG_TO_RAD*lat)*sin(DEG_TO_RAD*delta) +
                 cos(DEG_TO_RAD*lat)*cos(DEG_TO_RAD*delta)*cos(DEG_TO_RAD*H))*RAD_TO_DEG

        if transit:
            return -H/360.0
        else:
            return (h - h0)/(360.0*cos(DEG_TO_RAD*delta)*cos(DEG_TO_RAD*lat)*sin(DEG_TO_RAD*H))

    m0 += correct(m0, True)
    m1 += correct(m1, False)
    m2 += correct(m2, False)

    return m1, m0, m2


def sunrise_sunset(lat, lon, y, m, d, h0=-0.8333, dt=0.0):
    """ Calculate time of sunrise and sunset.

    lat, lon: latitude and longitude of observer.
    y, m, d: year, month and day for which to do the calculation.
    h0: geometric altitude of the Sun. The default value corresponds to 0.5
        degrees below the horizon, so the upper edge of the Sun is just at
        the horizon. Use -6 for civil twilight, -12 for nautical twilight,
        -18 for astronomical twilight.
    dt: delta between universal time and dynamical time.

    This returns the time of sunrise and sunset in UT.
    """

    positions = [
        solar_position(y, m, floor(d - 1)),
        solar_position(y, m, floor(d)),
        solar_position(y, m, floor(d + 1))
    ]

    sunrise, _, sunset = rise_transit_set(lat, lon, y, m, d, h0, positions)

    return sunrise*24.0, sunset*24.0
    
