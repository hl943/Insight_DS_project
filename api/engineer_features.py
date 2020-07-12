import pandas as pd
import numpy as np
from preprocessing_api import clean_weather_data, down_sample_df

def feat_eng(df_data, stride=[4,12,20,23], windows=1, agumented = True):
    """
    Args: 
        weather and soil training data (without the water stress ground truth)

    Output:
        dataset with engineered features ready for model prediction
    """

    # Calculate the moving average of features excluding hour and day of the year features
    # Filter for the relevant features
    X = df_data.filter(['Hour (PST)','Day of the Year','Baseline','VPD','ETo (mm)', 'Soil moisture content', 'Incident energy','Water stress'])
    lag = stride[-1]

    # Check if lag feature agumentation is true or not
    if agumented==True:
        offset = lag
        Xtr_fe = X.iloc[:,2:]
        Xtr_fe = Xtr_fe.rolling(window=windows).mean()
        Xtr_fe = sequenized(Xtr_fe, stride, lag, 1, True)
        Xtr_fe = pd.concat([X, Xtr_fe], axis=1)
        Xtr_fe.dropna(inplace=True)
    else: 
        offset = 0
        Xtr_fe = X
    return Xtr_fe


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

    # If uniform stride, then loop through the stride interval up to offset
    if isinstance(stride, int):
        for i in range(n_in, 0, -stride):
            cols.append(df.shift(i))
            names += [(df.columns[j]+'(t-%d)' % (i)) for j in range(n_vars)]
        agg = pd.concat(cols, axis=1)
        agg.columns = names

    # If non-uniform stride, then go through stride specified by the list: 
    elif type(stride) is list:
        for i in stride:
            if type(i) is not int: 
                raise TypeError("List of stride must only contains int")
            else:
                cols.append(df.shift(-i))
                names += [(df.columns[j]+'(t-%d)' % (i)) for j in range(n_vars)]
        agg = pd.concat(cols, axis=1)
        agg.columns = names

    else:
        raise TypeError("Input must be either int or list of int")

    if dropnan:
        agg.dropna(inplace=True)
    return agg   