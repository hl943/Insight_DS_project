# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 21:07:34 2020

@author: hl943
"""

import pandas as pd
import numpy as np
# Define cleaning function to clean weather data
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

# Clean tensiometer data:
def clean_mt_data(mT_path):
    df = pd.read_csv(mT_path)
    col_name = 'Averaged reading '+mT_path.rsplit('\\', 1)[-1]
    df = df.set_index(pd.DatetimeIndex(df['Human readable date']))
    df[col_name] = df.iloc[:,1:3].mean(axis = 1)
    df.drop(df.columns[[0,1,2,3]],axis=1,inplace = True)
    return df

# Down sample data in tighter time interval to match dataframe, by default resample to hourly data
def down_sample_df(df, period='H'):
    return df.resample(period).mean()