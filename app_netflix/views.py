from django.http import JsonResponse
from django.shortcuts import render
import pandas as pd

def load_data_netflix():
    # Read data from csv file
    df_data = pd.read_csv('app_netflix\dataset\chen_shih_chung_data.csv',sep=',')
    global response
    response = dict(list(df_data.values))
    del df_data

# load data
load_data_netflix()

#print(response)

def home(request):
    return render(request,'app_netflix/home.html', response)

print('app_netflix was loaded!')
