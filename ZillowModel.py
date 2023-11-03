import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.compose import make_column_transformer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

import tensorflow as tf
from tensorflow import keras
from keras import layers, optimizers, metrics
from keras.models import Sequential, Model
from keras import backend as K

from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)



def RMSE(y_true, y_pred):
  return K.sqrt(K.mean(K.square(y_pred - y_true)))

class ZillowModel():
  def __init__(self, zipCode:str):
    df = pd.read_csv('ValidZipCodes.csv', converters={'DELIVERY ZIPCODE':str})
    validZipCodes = list(df['DELIVERY ZIPCODE'])
    if zipCode not in validZipCodes:
      raise ValueError(f'Invalid Zip-Code: {zipCode}')

    df = self.GetData(zipCode)
    self.TrainModel(df, showLoss=True)

  
  def GetData(self, zipCode:str):
    df = pd.read_csv('Listings.csv', converters={'zipCode':str})
    df = df[df['zipCode'] == zipCode]
    df = df.drop(['zipCode', 'address', 'timeOnZillow', 'detailURL'], axis=1)
    df = df.dropna()
    return df
  

  def TrainModel(self, df, showLoss=False):
    X = df.drop(['price'], axis=1)
    Y = df['price']
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=32)

    self.transformer = make_column_transformer(
      (MinMaxScaler(), ['latitude', 'longitude', 'numBeds', 'numBaths', 'area'])
    )

    self.transformer.fit(X_train)
    X_train = self.transformer.transform(X_train)
    X_test = self.transformer.transform(X_test)

    tf.random.set_seed(32)
    self.model = Sequential()
    self.model.add(layers.Dense(256, activation='relu'))
    self.model.add(layers.Dense(128, activation='relu'))
    self.model.add(layers.Dense(64, activation='relu'))
    self.model.add(layers.Dense(32, activation='relu'))
    self.model.add(layers.Dense(1))

    self.model.compile(loss=RMSE, optimizer="adam", metrics=[RMSE])
    history = self.model.fit(X_train, Y_train, validation_data=(X_test, Y_test), epochs=150, batch_size=32, verbose=0)

    if showLoss:
      plt.figure(figsize=(15,10))
      plt.subplot(1,2,1)
      plt.plot(history.epoch, history.history['loss'])
      plt.plot(history.epoch, history.history['val_loss'])
      plt.title('Model Loss')
      plt.ylabel('Loss')
      plt.xlabel('Epoch')
      plt.legend(['Train', 'Test'], loc='upper right')

      predictions = np.ravel(self.model.predict(X_test))
      samples = list(range(len(X_test)))

      plt.subplot(1,2,2)
      plt.plot(samples, Y_test, label='True')
      plt.plot(samples, predictions, label='Predicted')
      plt.title('True vs. Predicted')
      plt.ylabel('Price')
      plt.xlabel('Sample')
      plt.legend(loc='upper right')
      plt.show()

      rmse = RMSE(Y_test, predictions).numpy()
      print("RMSE:", rmse)
  

  def ModelPredict(self, params):
    col_values = ['latitude', 'longitude', 'numBeds', 'numBaths', 'area']
    
    inputs = [params['latitude'], params['longitude'], params['numBeds'], params['numBaths'], params['area']]
    inputs = np.array(inputs).reshape(1, -1)
    inputs = pd.DataFrame(data=inputs, columns=col_values)
    inputs = self.transformer.transform(inputs)
    y_pred = np.ravel(self.model(inputs))
    y_pred = float(y_pred[0])

    return y_pred


if __name__ == '__main__':
  zipCodes = '37920'
  zm = ZillowModel(zipCodes)
