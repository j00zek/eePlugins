from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
try:
    from Components.Converter.MSNWeatherWebDaily import MSNWeatherWebDaily as j00zekMSNWeatherWebDaily
except Exception:
    from Components.Converter.j00zekMissingConverter import j00zekMissingConverter as j00zekMSNWeatherWebDaily 
