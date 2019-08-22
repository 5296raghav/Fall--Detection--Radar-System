import numpy as np
from numpy import loadtxt
from keras.models import load_model
from numpy import zeros, newaxis
from keras.utils import np_utils
# load model
model = load_model('model.h5')
# summarize model.
model.summary()
test_sample = (new_data+1.983725091504531e-06)/ 0.002995897201083166
preds = model.predict(test_sample.reshape(1,3000,1))
print(preds)
