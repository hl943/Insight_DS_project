import pandas as pd
import numpy as np

def clean_weather_data(weather_path):
    """
    Args:
        file path of weather data 
    Output:
        Cleaned dataframe with datetime index 
    """
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

def clean_mt_data(mT_path):
    """
    Args:
        file path of microtensiometer data 
    Output:
        Cleaned dataframe with datetime index 
    """
    df = pd.read_csv(mT_path)
    col_name = 'Averaged reading '+mT_path.rsplit('\\', 1)[-1]
    df = df.set_index(pd.DatetimeIndex(df['Human readable date']))
    df[col_name] = df.iloc[:,1:3].mean(axis = 1)
    df.drop(df.columns[[0,1,2,3]],axis=1,inplace = True)
    return df

def down_sample_df(df, period='H'):
    return df.resample(period).mean()