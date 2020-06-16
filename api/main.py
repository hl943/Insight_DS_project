# Import api related packages
from fastapi import FastAPI, Request, Depends, BackgroundTasks
from fastapi.templating import Jinja2Templates
import uvicorn 
import requests
import time
import json
from datetime import datetime


# Import database packages 
import models
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from pydantic import BaseModel

# Import ML model related packages
import pandas as pd
import joblib, os
import preprocessing_api #data preprocessing (specific to weather API, may need to modify if data source is different)

# Postgres Database
DATABASE_URL = "postgresql://usertest:usertest222@127.0.0.1"


# Load ML model from database? 
xbg_cv = joblib.load("pretrained_model/xgb_best.pkl")

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory = "templates")



def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# Get location based on client ip-address
def get_location(ip_address: str):
    try:
        response = requests.get("http://ip-api.com/json/{}".format(ip_address))
        #response = requests.get("http://ip-api.com/json/24.97.110.216")
        js = response.json()
        region = js['region']
        city = js['city']
        lat = js['lat']
        lon = js['lon']
        return region, city, lat, lon
    except Exception as e:
        return "Unknown"

# Get location weather based on client's geolocation 
def get_weather(lat, lon):
        #Mesonet API calls 
        apikey = "KyogSUIJlOdpjyU3wdzVwT15e1G4Vayt2ZJgY3dRWR"
        apitoken = "b9a25b2f723c4467933d7613f26b007c"
        radius=str(lat)+','+str(lon)+",100&limit=1"
        #variables ='air_temp,relative_humidity,wind_speed,solar_radiation,precip_accum_one_hour'
        #theurl='https://api.synopticdata.com/v2/stations/timeseries?'+'radius='+radius+'recent=120&vars='+variables+'&token='+apitoken
        # theurl='https://api.synopticdata.com/v2/stations/timeseries?stid=kslc'+'&recent=120'+'&token='+apitoken
        # data = requests.get(theurl)
        # json_dict = data.json()
        # req_data = json_dict['STATION'][0]['OBSERVATIONS']
        # df = pd.DataFrame(req_data)
        # df=df.set_index('date_time')
        # There is a missing step here, post data to the database, and retrive a csv file for data. Database and api query setup is not ready, use local csv first
        #transform into time series data sequence (If for LSTM, otherwise no need)

        data = preprocessing_api.clean_weather_data("lib/Napa_weather_data_test.csv")
        start_date = '2019-10-01 13:00:00'  # In an actual application, this is below
        start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        # start_date = pd.Timestamp.now().round('60min')
        end_date = pd.to_datetime(start_date)+pd.DateOffset(hours=1)
        data = data[start_date: end_date]
        return data.values

@app.get("/")
def home(request: Request): # background_tasks: BackgroundTasks
    """
    displays the mainpage of the waterUp api with pictures and graphs for water stress 
    """
    #ip_address = request.client.host
    ip_address = "24.97.110.216"
    (region, city, lat, lon) = get_location(ip_address)
    data = get_weather(lat, lon)
    prediction = xbg_cv.predict(data)
    water_stress=prediction[-1]
    # background_tasks.add_task(fetch_weather_data, lat, lon)


    return templates.TemplateResponse("home.html", {
        "request": request,
        "water_stress": water_stress, 
        "ip_address": ip_address,
        "region": region,
        "city": city,
    })
@app.get("/")
async def predict(data_frame):
    prediction = xbg_cv.predict(df_frame)
    return {"water_stress": np.min(prediction)}

# @app.post("/weather")
# def create_weather(weather_request: WeatherRequest, db: Session = Depends(get_db)):
#     """
#     create a weather and stores it in the database
#     """
#     weather = Weather()
#     weather.air_temp = weather_request.air_temp
#     db.add(weather)
#     db.commit()
#     return {
#         "code": success,
#         "message": "weather data created"
#     }
