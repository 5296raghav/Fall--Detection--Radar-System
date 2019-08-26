import os
import numpy as np
from numpy import loadtxt
from keras.models import load_model
from numpy import zeros, newaxis
from keras.utils import np_utils

class ModelCNN():
    def __init__(self, path = "C:\\Users\\Shan\\Downloads\\Fall_Detection\\Radar_data-master\\Radar_data-master\\"):
        self.model = load_model(path + 'model.h5')
# summarize model.
        print(self.model.summary()) 
    def predict(self,test_sample ):
        return self.model.predict(test_sample.reshape(1,3000,1))