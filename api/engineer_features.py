import pandas as pd
import numpy as np
from preprocessing_api import clean_weather_data, down_sample_df

def feat_eng(df_data, freq=4, lag=24):
    """
    Args: 
        weather data and soil data paths

    Output:
        dataset with engineered features ready for model prediction
    """
    
    # Drop and combine solar radiation feature 
    df_data['incident energy'] = df_data['Sol Rad (W/sq.m)']*df_data['sunshine duration']/60/1000
    df_data.drop('Sol Rad (W/sq.m)', axis=1, inplace=True)
    df_data.drop('sunshine duration', axis=1, inplace=True)

    #Drop irrelevant features
    df_data.drop(columns = 'Vap Pres (kPa)',inplace=True)
    df_data.drop(columns = 'Dew Point (C)',inplace=True)

    # Remove simulated Eto, since station Eto is available
    df_data.drop('Eto simulated', axis=1, inplace=True)

    # sequnezie the dataframe
    n_in = int(lag/freq)
    X = sequenized(Xtr_fe, freq, n_in, 1, True)
    X.dropna(inplace=True)
    return X


def sequenized(df, stride=1, n_in=1, n_out=1, dropnan=True):
    """
    Args: 
        data: input dataframe with weather and soil history
        stride: stride of the sliding window
        n_in: the number of lags from current time
        n_out: the number of advances from current time

    Output:
        dataframe with augmented historical values
    """
    n_vars = df.shape[1]
    cols, names = list(), list()
    for i in range(n_in, 0, -stride):
        cols.append(df.shift(i))
        names += [(df.columns[j]+'(t-%d)' % (i)) for j in range(n_vars)]
    for i in range(0, n_out):
        cols.append(df.shift(-i))
        if i == 0:
            names += [(df.columns[j]+'(t)') for j in range(n_vars)]
        else:
            names += [('var%d(t+%d)' % (j+1, i)) for j in range(n_vars)]
    agg = pd.concat(cols, axis=1)
    agg.columns = names
    if dropnan:
        agg.dropna(inplace=True)
    return agg   