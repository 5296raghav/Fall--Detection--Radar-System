#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
from clean_data import clean_dataframe
from model_cnn import *
import pandas as pd
model = ModelCNN()
data1 = pd.read_csv("C:\\Users\\Shan\\Downloads\\Fall_Detection\\newdata2\\GANGESH-FALL-PARALLELwMOVE-200Hz_20170831-174034_.csv") 
clean_df = clean_dataframe(data1)
model.predict(clean_df)


# In[ ]:




