# Import api related packages
import models
from fastapi import FastAPI, Request, Depends, BackgroundTasks
from fastapi.templating import Jinja2Templates
import uvicorn 
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import List



# Import database packages 
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from pydantic import BaseModel

# Import ML model related packages
import pandas as pd
import joblib, os
import engineer_features


xbg_cv = joblib.load("pretrained_model/xgb_best.pkl")

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory = "templates")


# Define return class from prediction:
class Prediction(BaseModel):
    city: str
    region: str
    lat: str
    lon: str
    datetime: List[datetime]
    water_stress: List[float]
    Error: str


# Launching database
# def get_db():
#     try:
#         db = SessionLocal()
#         yield db
#     finally:
#         db.close()

# Get location based on client ip-address
def get_location(ip_address: str):
    """
    Args: 
        Client's IP address
    Output:
        Client's geolocation
    """
    try:
        response = requests.get("http://ip-api.com/json/{}".format(ip_address))
        # response = requests.get("http://ip-api.com/json/24.97.110.216")
        js = response.json()
        region = js['region']
        city = js['city']
        lat = js['lat']
        lon = js['lon']
        return region, city, lat, lon
    except Exception as e:
        return "Unknown"

# Get location weather based on client's geolocation 
def get_weather(lat, lon, period=1):
    """
    Args: 
        lat, lon: the cooridinate of the geolocation
        period: the stride at which moving average is taken
    Output:
        feature matrix ready for model inference
        the datetime index of the feature maxtrix
    """
    # Mesonet API calls, the following code fetches weather data at given location. API keys are hidden...
    # radius=str(lat)+','+str(lon)+",100&limit=1" 
    # variables ='air_temp,relative_humidity,wind_speed,solar_radiation,precip_accum_one_hour'
    # theurl='https://api.synopticdata.com/v2/stations/timeseries?'+'radius='+radius+'recent=120&vars='+variables+'&token='+apitoken
    # theurl='https://api.synopticdata.com/v2/stations/timeseries?stid=kslc'+'&recent=120'+'&token='+apitoken
    # data = requests.get(theurl)
    # json_dict = data.json()
    # req_data = json_dict['STATION'][0]['OBSERVATIONS']
    # df = pd.DataFrame(req_data)
    # df=df.set_index('date_time')

    # If we pay for the MeteoBlue history+ and forecast+, we can fetch soil data, Free API is not available, This part is incomplete
    # Use available data stored locally for demostration purpose:
    data = clean_weather_data("lib/Napa_weather_data_test.csv")

    # Here, due to the lack of availability of soil data, we used the data from previous year
    # By default, fetch one day history to make inference at next hour. 
    start_date = pd.Timestamp.now().round('60min')+relativedelta(days=-1)+relativedelta(years=-1) 
    end_date = pd.Timestamp.now().round('60min')+relativedelta(years=-1)
    hour_range = pd.date_range(start_date, end_date, freq='H')
    data = data[start_date: end_date]
    # data = engineer_features.feat_eng(data)
    return data.values, hour_range

def get_forecast(lat, lon, period=1):
    """
    Args: 
        Client's latitude, longtitude and forecast period
    Output:
        weather forecast data from weather api up to forecast period
    """
    # Note here since I did not pay for forecasting service on the training data, only historical data is used. 
    data = clean_weather_data("lib/Napa_weather_data_test.csv")
    start_date = pd.Timestamp.now().round('60min')+relativedelta(years=-1)+relativedelta(days=-1)
    end_date = pd.to_datetime(start_date)+pd.DateOffset(hours=period)
    data = data[start_date: end_date]
    hour_range = pd.date_range(start_date, end_date, freq='H')
    return data.values, hour_range


# Define cleaning function to clean weather data read from Mesonet_api
def clean_weather_data(weather_path):
    # clean on weather dataframe
    df = pd.read_csv(weather_path)
    Hour = df['Hour (PST)'].astype(str)
    i=0
    for hour in Hour:
        if len(hour)<4:
            hour="0"+str(hour)
        if hour[:2] == '24':
            hour = '0000'
        hour = str(hour[:2])+":"+str(hour[2:])
        Hour[i] = hour
        i+=1
    df = df.set_index(pd.DatetimeIndex(df['Datetime']))
    df.drop('Datetime', axis=1, inplace=True)
    return df


@app.get("/")
def home(request: Request): # background_tasks: BackgroundTasks
    """
    displays the mainpage of the waterUp api with pictures and graphs for water stress 
    """
    ip_address = request.client.host
    # ip_address = "24.97.110.216"
    try: 
        (region, city, lat, lon) = get_location(ip_address)
    except ValueError as VE:
        return templates.TemplateResponse("home.html", {
        "request": request,
        "water_stress": "Unknown location", 
        "ip_address": "None",
        "region": "None",
        "city": "None",
        "Error": "Unknown" 
        })
    data, hour_range= get_weather(lat, lon)
    prediction = xbg_cv.predict(data)
    water_stress=prediction[-1]

    return templates.TemplateResponse("home.html", {
        "request": request,
        "water_stress": water_stress, 
        "ip_address": ip_address,
        "region": region,
        "city": city,
        "Error": "None"
    })

@app.get("/forecast/period={period}")
async def get_prediction(request: Request, period:int):
    ip_address = request.client.host
    try: 
        (region, city, lat, lon) = get_location(ip_address)
        data, date_range = get_forecast(lat, lon, period)
        # X = engineer_features(data, )
        predictions = xbg_cv.predict(data)
        re_dict = Prediction(
            city=city,
            region=region,
            lat=str(lat),
            lon=str(lon),
            datetime=date_range.tolist(),
            water_stress=predictions.tolist(),
            Error="None"
        )
        json_re_dict=jsonable_encoder(re_dict)
    except ValueError as VE:
        re_dict = Prediction(
            city="None",
            region="None",
            lat="None",
            lon="None",
            datetime=[],
            water_stress=[],
            Error = "Location not found"
        )
        json_re_dict=jsonable_encoder(re_dict)
    return json_re_dict


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)