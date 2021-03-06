# Import api related packages
from fastapi import FastAPI, Request, Depends, BackgroundTasks
from fastapi.templating import Jinja2Templates
import uvicorn 
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import List
from preprocessing_api import clean_weather_data


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


xbg = joblib.load("pretrained_model/xgb_final.pkl")

app = FastAPI()


templates = Jinja2Templates(directory = "static/templates")


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
        js = response.json()
        region = js['region']
        city = js['city']
        lat = js['lat']
        lon = js['lon']
        return region, city, lat, lon
    except Exception as e:
        return "Unknown"

# Get location weather based on client's geolocation 
def get_weather(lat, lon, lag=23, stride=1):
    """
    Args: 
        lat, lon: the cooridinate of the geolocation
        stride: the stride at which moving average is taken, default is 4
        lag: the total weather history to consider in unit of hours, default is 24
    Output:
        feature matrix ready for model inference
        the datetime index of the feature maxtrix
    """
    # Mesonet API calls, the following code fetches weather data at given location. API keys are hidden...
    # apitoken = ***************
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
    start_date = pd.Timestamp.now().round('60min')+relativedelta(hours=-lag)+relativedelta(hours=-stride)+relativedelta(years=-1) 
    end_date = pd.Timestamp.now().round('60min')+relativedelta(years=-1)
    hour_range = pd.date_range(start_date, end_date, freq='H')
    data = data[start_date: end_date]
    X_fe = engineer_features.feat_eng(data)
    return X_fe, hour_range

def get_forecast(lat, lon, period, lag=23, stride=1):
    """
    Args: 
        lat, lon: the cooridinate of the geolocation
        period: forecast requested by client in unit of hours 
        stride: the stride at which moving average is taken, default is 4
        lag: the total weather history to consider in unit of hours, default is 24
    Output:
        weather forecast data from weather api up to forecast period
    """

    # Note here since I did not pay for forecasting service on the training data, only historical data is used. 
    data = clean_weather_data("lib/Napa_weather_data_test.csv")
    start_date = pd.Timestamp.now().round('60min')+relativedelta(hours=-lag)+relativedelta(hours=-stride)+relativedelta(years=-1)
    end_date = pd.to_datetime(start_date)+pd.DateOffset(hours=period)
    data = data[start_date: end_date]
    hour_range = pd.date_range(start_date, end_date, freq='H')
    X_fe = engineer_features.feat_eng(data)
    return X_fe, hour_range


@app.get("/")
def home(request: Request): 
    """
    displays the mainpage of the waterUp api with pictures and graphs for water stress 
    """
    ip_address = request.client.host
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
    prediction = xbg.predict(data)
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
        predictions = xbg.predict(data)
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