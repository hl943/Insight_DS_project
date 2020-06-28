import pandas as pd
import numpy as np
from preprocessing_api import clean_weather_data, down_sample_df

def feat_eng(df_data, stride=4, lag=24):
    """
    Args: 
        weather and soil training data 

    Output:
        dataset with engineered features ready for model prediction
    """

    # Calculate the moving average of features excluding hour and day of the year features
    X = df_data.drop(columns=['Hour (PST)', 'Day of the Year'])
    X_fe = X.rolling(window=stride).mean()
    for column in X_fe.columns:
        X_fe.rename(columns = {column: column+'_MA_'+str(stride)},inplace=True)

    # augment features with historical moving average
    X_fe = sequenized(X_fe, stride, lag, 1, True)
    X_fe = pd.concat([df_data, X_fe], axis=1)
    X_fe.dropna(inplace=True)
    return X_fe


def sequenized(df, stride=1, n_in=1, n_out=1, dropnan=True):
    """
    Args: 
        data: input dataframe with weather and soil history
        stride: stride of the sliding window
        lag: the time lag of features
        n_out: the number of advances from current time

    Output:
        dataframe with augmented lag features
    """
    n_vars = df.shape[1]
    cols, names = list(), list()
    for i in range(n_in, 0, -stride):
        cols.append(df.shift(i))
        names += [(df.columns[j]+'(t-%d)' % (i)) for j in range(n_vars)]
    agg = pd.concat(cols, axis=1)
    agg.columns = names
    if dropnan:
        agg.dropna(inplace=True)
    return agg   