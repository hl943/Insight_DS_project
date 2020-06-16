# For App
from flask import Flask, request, jsonify, render_template
from flask_restx import Resource, Api, fields, reqparse
from keras.models import load_model
import requests
import re
import json


# For model
import pandas as pd
#import Multiv_LSTM
import pickle


flask_app = Flask(__name__)
app = Api(
    app=flask_app,
    version="v1.0",
    title="WaterUP",
    description="Get water stress status at client's geo-location")


name_space = app.namespace(
    'apis', description='APIs associated with weather and geolocation')



predict_parser = reqparse.RequestParser()
predict_parser.add_argument('start_date',
                            type=str,
                            required=False,
                            default='2019-05-01')
predict_parser.add_argument('end_date',
                            type=str,
                            required=False,
                            default='2019-05-31')

@name_space.route("/predict")
class Predict(Resource):
    def get_location(ip_address):
        try:
            #response = requests.get("http://ip-api.com/json/{}".format(ip_address))
            response = requests.get("http://ip-api.com/json/24.97.110.216")
            js = response.json()
            region = js['region']
            city = js['city']
            lat = js['lat']
            lon = js['lon']
            return region, city, lat, lon
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
    
    def load_keras_model():
        model = load_model('../pretained_model/model/h5')
        
# =============================================================================
# truth_parser = reqparse.RequestParser()
# truth_parser.add_argument('start_date',
#                           type=str,
#                           required=False,
#                           default='2019-05-01')
# truth_parser.add_argument('end_date',
#                           type=str,
#                           required=False,
#                           default='2019-05-31')
# 
# =============================================================================

    

    # Agro API calls
# =============================================================================
#     apikey = 'abcab6e33060c3157e72b4ab35c3c79f'
#     polyid = '5ee0461edf80700007068b02'
# =============================================================================
# =============================================================================
# @app.route('/api/predict', methods = ['GET'])  
# def get_stress(df):
#     Y_pred = Multiv_LSTM.forecast(df)
#     water_stress = {'Water stress': Y_pred}
#     json_obj = json.dumps(water_stress)
#     return json_obj
# =============================================================================

# =============================================================================
# # Homepage of the app 
# @app.route('/', methods=['GET'])
# def home():
#     ip_address = request.remote_addr
#     (lat, lon) = get_location(ip_address)
#     df_weather = get_weather(lat, lon)
#     header = "<h1>WaterUp API</h1>"
#     para1 = "<br> <p>This site is a prototype API for requesting real time water stress for grapes in Napa California.</p>"
#     para2 = "<p> To request water stress data, follow this link: This returns a json project wit the follow fields: </p>"
#     return header+para1+para2+df_weather.columns[0]
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
if __name__ =='__main__': 
    app.run(port='5000', debug=True)
