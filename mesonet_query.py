# -*- coding: utf-8 -*-
"""
Created on Sun May 31 22:35:44 2020

@author: hl943
"""

# =============================================================================
# ac926a7e68c249e88b78da2c0d3f7bd0
# =============================================================================

import json
import requests
import pandas as pd
from pandas.io.json import json_normalize
# apikey = 'ac926a7e68c249e88b78da2c0d3f7bd0' #PlanetOS api key

sv_data = 0



# synpotic api key and token
apikey = 'KyogSUIJlOdpjyU3wdzVwT15e1G4Vayt2ZJgY3dRWR'
apitoken = '4f3a0272bbc542efb56befe40102f77f'
radius='-33.44,-70.67,200&limit=1' # Rengo chile geolocation
#radius='38.41,-122.34,50&limit=1' #Los Angeles
variable_wo_precip ='air_temp,relative_humidity,wind_speed,solar_radiation'
variable_precip = ''
variables = variable_wo_precip+variable_precip
start = '202005011200' 
end = '202005021200' 
theurl='https://api.synopticdata.com/v2/stations/timeseries?'+'radius='+radius+'&start='+start+'&end='+end+'&vars='+variables+'&token='+apitoken
data = requests.get(theurl)
json_dict = data.json()
req_data = json_dict['STATION'][0]['OBSERVATIONS']
df = pd.DataFrame(req_data)





# request precipitation data
precipurl = 'https://api.synopticdata.com/v2/stations/precip?'
pmode = 'intervals'
interval ='hour'
stid ='SCEL'
precipurl = precipurl+'stid='+stid+'&start='+start+'&end='+end+'&pmode='+pmode+'&interval='+interval+'&token='+apitoken
p_data = requests.get(precipurl)
json_p_dict = p_data.json()



if sv_data ==1:
    df.to_csv(r'C:\Users\hl943\Documents\personal documents\data science\Insight DS\project directory\Rengo_weather_data.csv')
