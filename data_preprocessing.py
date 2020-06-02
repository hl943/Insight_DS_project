# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 21:07:34 2020

@author: hl943
"""
import dryscrape
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re

path = r'C:\Users\hl943\Documents\personal documents\data science\Insight DS\project directory\Rengo_weather_data.csv'
df = pd.read_csv(path)

df['date_time'] = df['date_time'].str.replace('T', ' ')
df['date_time'] = df['date_time'].str.replace('Z', '')
df = df.set_index(pd.DatetimeIndex(df['date_time']))
df.drop('date_time', axis=1, inplace=True)
df.drop(df.columns[[0]], axis=1, inplace=True)

# Calculate vapor pressure deficit
Te = df['air_temp_set_1'].to_numpy()
RH = df['relative_humidity_set_1'].to_numpy()
df['Vapor pressure deficit (Pa)'] = (5.018+0.32321*Te+8.1847e-3*Te**2+3.1243e-4*Te**3)*RH/100


# Rename columns with units
df.rename(columns={'air_temp_set_1':'Temperature (degC)'}, inplace=True)
df.rename(columns={'relative_humidity_set_1':'Relative humidity (%)'}, inplace=True)
df.rename(columns={'wind_speed_set_1':'Wind speed (m/s)'}, inplace=True)



# Scrape addtional precipitation data that is not available from mesonet
session = dryscrape.Session()
theurl ="https://www.wunderground.com/history/daily/cl/pudahuel/SCEL"
session.visit(theurl)
response = session.body()
soup = BeautifulSoup(response)
soup.find('table')

# scrape with bs4 only 
