#!/usr/bin/env python
# coding: utf-8
import pandas as pd
import numpy as np
#import matplotlib
import glob
#from numpy import zeros
#from scipy.signal import spectrogram
#from scipy.signal import window
from pathlib import Path
#import scipy.interpolate
#matplotlib.use('Qt4Agg')
#import matplotlib.pyplot as plt 
import os

data1 = pd.read_csv("C:\\Users\\Shan\\Downloads\\Fall_Detection\\newdata2\\GANGESH-FALL-PARALLELwMOVE-200Hz_20170831-174034_.csv") 
data1.dtypes
rd1_data = data1.iloc[:,19:-1]

a = np.asarray(rd1_data)
# print(np.shape(a))
print(complex(a[0][1:][0]).real)

# a = a[:][1:] # skipping the timestamp
arr = []
#print(type(a),len(a),len(a[0]))
for v in a:
    row_arr = []
    for x in v:
        row_arr.append(complex(x).real)
    arr.append(row_arr)
print(len(arr), len(arr[0]))
#df=pd.DataFrame(arr)
#print(df)
# print(arr[0])

TTS = 0
TTE = 15
FR = 200
CRD = 4*FR
[ROW, COL] = np.shape(arr)

distance = [(i+20)*0.0535 for i in range(COL)]
#print(distance)
#print(np.shape(distance))


avg = np.mean(arr, axis=0)
# print(avg)
print(np.shape(avg))
# new_avg = avg.reshape(1,np.shape(avg)[0])
new_avg = avg.reshape((1,) + avg.shape)
#print(new_avg, np.shape(new_avg))

radardata = np.subtract(arr, avg)
#print(radardata)
#print(np.shape(radardata))


s_d = radardata.sum(axis = 1)
print(s_d)
print(np.shape(s_d))
#S_d = s_d.reshape(3037,1)
#print(S_d, np.shape(S_d))

s_d_0 = s_d[len(s_d)-1+1-3000:]

#print(s_d_0, np.shape(s_d_0))

in_data = np.transpose(s_d_0)
#print(in_data)
#print(np.shape(in_data))
new_data = in_data.reshape(1,3000)
print(new_data, np.shape(new_data))
# print(new_data)
np.savetxt("test.csv", new_data, delimiter=",")


