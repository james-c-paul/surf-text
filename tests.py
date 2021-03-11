from datetime import date, time, datetime, timedelta
import requests
import numpy as np
import pandas as pd 
import pygrib
from itertools import cycle
#from models import User, Locations
#from app import db
from sqlalchemy import insert


today='20210308'
hour='00'

surf_hours = []
surf_locations = []
surf_data = {}

for a in range(0, 3, 3): #384 potential files
    surf_hours.append(a)
    if len(str(a)) == 1:
        req = requests.get(f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.{today}/{hour}/wave/gridded/gefs.wave.t00z.c00.global.0p25.f00{a}.grib2")
    elif len(str(a)) == 2:
        req = requests.get(f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.{today}/{hour}/wave/gridded/gefs.wave.t00z.c00.global.0p25.f0{a}.grib2")
    else:
        req = requests.get(f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.{today}/{hour}/wave/gridded/gefs.wave.t00z.c00.global.0p25.f{a}.grib2")
    print(req.status_code)
    with open('grib2data.grib2', 'wb') as f:
        f.write(req.content)
    gr = pygrib.open('grib2data.grib2')
    msg = gr[1:24]
    latlons = [[33.460304, 242.314139], [33.416018, 242.381431], [33.374922, 242.429478]]
    #latlons = db.session.query(Locations.id, Locations.loc_lat, Locations.loc_lon, Locations.tolerance, Locations.surf_data).all()
    for spot in latlons:
        surf_locations.append(spot)
        tolerence = 0.25
        specific_surf_data = {}
        for i in range(1, 21):
            data, lats, lons = msg[i].data(lat1=spot[0]-tolerence,lat2=spot[0]+tolerence,lon1=spot[1]-tolerence,lon2=spot[1]+tolerence)
            specific_surf_data[a].append(data.mean())  
        spot.surf_data
        #surf_data.append(specific_surf_data)

print(surf_data)
        

'''surf_hours = []
surf_locations = []
surf_data = []
for a in range(0, 9, 3):
    surf_hours.append(a)
    for i in range(1, 3):
        surf_locations.append(i)
        #surf_data.append([n for n in range(1, 23)])
        for x in range(1, 23):
            surf_data.append([n for n in range(1, 23)])
            #print(tuple(zip(surf_hours, surf_variables)))
            #surf_data.append(x)'''

'''data_iter = iter(surf_data)
result = {}
for hour in surf_hours:
    result[hour] = dict(zip(surf_locations, data_iter))
#result = dict(zip(surf_variables, cycle(surf_hours)))
print(result)'''

#print(surf_hours)
#print(surf_locations)
#print(surf_data)

#print(tuple(zip(surf_hours, surf_variables, surf_data)))








'''200
1:Wind speed:m s**-1 (instant):regular_ll:surface:level 1:fcst time 0 hrs:from 202103020000
2:Wind direction:Degree true (instant):regular_ll:surface:level 1:fcst time 0 hrs:from 202103020000
3:U component of wind:m s**-1 (instant):regular_ll:surface:level 1:fcst time 0 hrs:from 202103020000
4:V component of wind:m s**-1 (instant):regular_ll:surface:level 1:fcst time 0 hrs:from 202103020000
5:Sea ice area fraction:(0 - 1) (instant):regular_ll:surface:level 1:fcst time 0 hrs:from 202103020000
6:Significant height of combined wind waves and swell:m (instant):regular_ll:surface:level 1:fcst time 0 hrs:from 202103020000
7:25:25 (instant):regular_ll:surface:level 1:fcst time 0 hrs:from 202103020000
8:Mean wave period:s (instant):regular_ll:surface:level 1:fcst time 0 hrs:from 202103020000
9:Primary wave mean period:s (instant):regular_ll:surface:level 1:fcst time 0 hrs:from 202103020000
10:Mean wave direction:Degree true (instant):regular_ll:surface:level 1:fcst time 0 hrs:from 202103020000
11:Primary wave direction:Degree true (instant):regular_ll:surface:level 1:fcst time 0 hrs:from 202103020000
12:Significant height of wind waves:m (instant):regular_ll:surface:level 1:fcst time 0 hrs:from 202103020000
13:Significant height of swell waves:m (instant):regular_ll:unknown:level 1 241:fcst time 0 hrs:from 202103020000
14:Significant height of swell waves:m (instant):regular_ll:unknown:level 2 241:fcst time 0 hrs:from 202103020000
15:Significant height of swell waves:m (instant):regular_ll:unknown:level 3 241:fcst time 0 hrs:from 202103020000
16:Mean period of wind waves:s (instant):regular_ll:surface:level 1:fcst time 0 hrs:from 202103020000
17:Mean period of swell waves:s (instant):regular_ll:unknown:level 1 241:fcst time 0 hrs:from 202103020000
18:Mean period of swell waves:s (instant):regular_ll:unknown:level 2 241:fcst time 0 hrs:from 202103020000
19:Mean period of swell waves:s (instant):regular_ll:unknown:level 3 241:fcst time 0 hrs:from 202103020000
20:Direction of wind waves:Degree true (instant):regular_ll:surface:level 1:fcst time 0 hrs:from 202103020000
21:Direction of swell waves:Degree true (instant):regular_ll:unknown:level 1 241:fcst time 0 hrs:from 202103020000
22:Direction of swell waves:Degree true (instant):regular_ll:unknown:level 2 241:fcst time 0 hrs:from 202103020000'''

#def find_nearest(array, value):
    #array = np.asarray(array)
    #idx = (np.abs(array - value)).argmin()
    #return array[idx]
