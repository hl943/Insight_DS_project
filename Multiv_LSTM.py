# multivariate lstm example
import numpy as np
import matplotlib.pyplot as plt
from numpy import array
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Conv1D, MaxPooling1D, Bidirectional
from tensorflow.keras.layers import Dense, Dropout
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from statsmodels.tools.eval_measures import rmse
from tensorflow.keras.preprocessing import sequence
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error


def train_test_split(X,Y, split_size):
    assert(X.shape[0]==Y.shape[0])
    n = X.shape[0]
    n_tr = int((n*split_size))
    Xtr = X[:n_tr,:]
    Xte = X[n_tr+1:,:]
    Ytr = Y[:n_tr,:]
    Yte = Y[n_tr+1:,:]
    return Xtr, Xte, Ytr, Yte

def scale(train, test):
    scaler = StandardScaler()
    scaler = scaler.fit(train)
    
    train = train.reshape(train.shape[0], train.shape[1])
    train_scaled = scaler.transform(train)
    
    test = test.reshape(test.shape[0], test.shape[1])
    test_scaled = scaler.transform(test)   

    return scaler, train_scaled, test_scaled


# split a multivariate sequence into samples
def split_sequences(sequences, n_steps):
    X, y = list(), list()
    for i in range(len(sequences)):
        # find the end of this pattern
        end_ix = i + n_steps
        # check if we are beyond the dataset
        if end_ix > len(sequences):
            break
        # gather input and output parts of the pattern
        seq_x, seq_y = sequences[i:end_ix, :-1], sequences[end_ix-1, -1]
        X.append(seq_x)
        y.append(seq_y)
    return array(X), array(y)

# # Try using keras's built in function for time-series generator
# def sequence_generator(sequences, strides, length, batch_size, sampling_rate=1):
#     targets = sequences[:,-1]
#     sequences = sequences[:,:-1]
#     data_gen = sequence.TimeseriesGenerator(sequences, targets, length, sampling_rate, batch_size)
#     return data_gen

def build_model(Xtr, Xte, Ytr, Yte, n_steps):
    #reframe to sequences
    Xtr_seq, Ytr_seq = split_sequences(np.hstack((Xtr,Ytr)), n_steps)
    Ytr_seq=Ytr_seq.reshape(-1,1)
    Xte_seq, Yte_seq = split_sequences(np.hstack((Xte,Yte)), n_steps)
    Yte_seq=Yte_seq.reshape(-1,1)
    n_features = Xtr_seq.shape[2]
    opt = keras.optimizers.Adam(learning_rate = 0.0001)
    
    # Train and validation 
    #LSTM model
    model = Sequential()
    model.add(Bidirectional(LSTM(128, return_sequences=True), merge_mode='concat'))
    model.add(Dropout(0.2))
    model.add(LSTM(128, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(1))
    model.compile(optimizer=opt, loss='mse')
    history = model.fit(Xtr_seq, Ytr_seq, batch_size=32, epochs=100, verbose=0,validation_data=(Xte_seq, Yte_seq))    # plot history
    plt.plot(history.history['loss'], label='train')
    plt.plot(history.history['val_loss'], label='test')
    plt.legend()
    plt.show()
    return model

# make a forecast
def forecast(model, Xte, n_steps):
    dummy_y = np.zeros((Xte.shape[0],1))
    Xte_seq, _= split_sequences(np.hstack((Xte,dummy_y)), n_steps)
    yhat = model.predict(Xte_seq, verbose=0)
    # we only want the vector forecast
    return yhat

# nested cross validation 
def cv_model(X, Y, n_steps, n_split=5):
    tscv = TimeSeriesSplit(n_splits = n_split)
    rmse = []
    for train_index, test_index in tscv.split(X):
        cv_Xtr, cv_Xte = X[train_index], X[test_index]
        cv_Ytr, cv_Yte = Y[train_index], Y[test_index]
        model = build_model(cv_Xtr, cv_Xte, cv_Ytr, cv_Yte, n_steps)
        predictions = forecast(model, cv_Xte, n_steps)
        true_values = cv_Yte
        rmse.append(np.sqrt(mean_squared_error(true_values[n_steps-1:], predictions)))
    print("RMSE: {}".format(np.mean(rmse)))
    return model
