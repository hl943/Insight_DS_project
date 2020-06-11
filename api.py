import flask
from flask import request, jsonify
import requests
import re
import json
import pandas as pd
import Multiv_LSTM

app = flask.Flask(__name__)
app.config["DEBUG"] = True

water_stress = [{
      "entries": [{
        "context": "reftime_time_lat_lon",
        "axes": {
          "reftime": "2016-04-24T12:00:00",
          "time": "2016-04-24T12:00:00",
          "longitude": -49.99999999999997,
          "latitude": 50.0
        },
        "data": {
          "Water_potential": 4.409999847412109
        }
      }]
    }
]


def get_location(ip_address):
    try:
        #response = requests.get("http://ip-api.com/json/{}".format(ip_address))
        response = requests.get("http://ip-api.com/json/24.97.110.216")
        js = response.json()
        lat = js['lat']
        lon = js['lon']
        return lat, lon
    except Exception as e:
        return "Unknown"

def get_weather(lat, lon):
    #Mesonet API calls 
    apikey = 'KyogSUIJlOdpjyU3wdzVwT15e1G4Vayt2ZJgY3dRWR' 
    apitoken = 'b9a25b2f723c4467933d7613f26b007c' 
    #radius=str(lat)+','+str(lon)+',100&limit=1' # Rengo chile geolocation
    #variables ='air_temp,relative_humidity,wind_speed,solar_radiation,precip_accum_one_hour'
    #theurl='https://api.synopticdata.com/v2/stations/timeseries?'+'radius='+radius+'recent=120&vars='+variables+'&token='+apitoken
    theurl='https://api.synopticdata.com/v2/stations/timeseries?stid=kslc'+'&recent=120'+'&token='+apitoken
    data = requests.get(theurl)
    json_dict = data.json()
    req_data = json_dict['STATION'][0]['OBSERVATIONS']
    df = pd.DataFrame(req_data)
    df=df.set_index('date_time')
    return df
    # Agro API calls
# =============================================================================
#     apikey = 'abcab6e33060c3157e72b4ab35c3c79f'
#     polyid = '5ee0461edf80700007068b02'
# =============================================================================
@app.route('/api/v1/data/all', methods = ['GET'])  
def get_stress(df):
    Y_pred = Multiv_LSTM.forecast(df)
    water_stress = {'Water stress': Y_pred}
    json_obj = json.dumps(water_stress)
    return json_obj

# Homepage of the app 
@app.route('/', methods=['GET'])
def home():
    ip_address = request.remote_addr
    (lat, lon) = get_location(ip_address)
    df_weather = get_weather(lat, lon)
    header = "<h1>WaterUp API</h1>"
    para1 = "<br> <p>This site is a prototype API for requesting real time water stress for grapes in Napa California.</p>"
    para2 = "<p> To request water stress data, follow this link: This returns a json project wit the follow fields: </p>"
    return header+para1+para2+df_weather.columns[0]

# =============================================================================
# @app.route("/")
# def index():
#     ip_address = request.headers.get('X-Forwarded-For')
#     url = 'http://ipinfo.io/'+ip_address+'/json'
#     http = urllib3.PoolManager()
#     response = http.request('GET', url)
#     ip_data = json.load(response)
#     IP=ip_data['ip']
#     org=ip_data['org']
#     city = ip_data['city']
#     country=ip_data['country']
#     region=ip_data['region']
# =============================================================================

# Think about how to write this
# =============================================================================
# def api_hour():
#     if 'end' in request.args:
#         hour = int(request.args['end'])
#     else:
#         return "Error: Please enter a valid end point (hour of the day) in [0, 23]"
#     
#     results = []
#     now = 0 # Pull current hour 
#     for hours in range(now+1, hour):
#         if water_stress['hour'] == hours:
#             results.append(water_stress)
#     return jsonify(results)
# =============================================================================
app.run()

