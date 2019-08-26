#!/usr/bin/env python
# coding: utf-8

# In[6]:


import pandas as pd
import numpy as np
import glob
from pathlib import Path
import os


# In[10]:


def clean_dataframe(rawdata):
    rd1_data = rawdata.iloc[:,19:-1]
    a = np.asarray(rd1_data)
    arr = []
    for v in a:
        row_arr = []
        for x in v:
            row_arr.append(complex(x).real)
            arr.append(row_arr)
#     print(len(arr), len(arr[0]))
    avg = np.mean(arr, axis=0)
    new_avg = avg.reshape((1,) + avg.shape)
    radardata = np.subtract(arr, avg)
    s_d = radardata.sum(axis = 1)
    s_d_0 = s_d[len(s_d)-1+1-3000:]
    in_data = np.transpose(s_d_0)
    new_data = in_data.reshape(1,3000)
    print(new_data, np.shape(new_data))
    return new_data  


# In[9]:


# data1 = pd.read_csv("C:\\Users\\Shan\\Downloads\\Fall_Detection\\newdata2\\GANGESH-FALL-PARALLELwMOVE-200Hz_20170831-174034_.csv")
# print(clean_dataframe(data1))


# In[ ]:




