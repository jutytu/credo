import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import glob
import statistics

import os
import math
from time import mktime
from datetime import datetime, date, timedelta, timezone

# data = pd.read_csv(r'C:\Users\Ja\OneDrive\Dokumenty\Materiały\SPE\nmdb.eu_nest_draw_graph.php.txt', sep=";", header=None)
data = pd.read_csv(r'C:\Users\Ja\PycharmProjects\credo\asciimosc.txt', sep=";", header=None)
# print(data.head().to_string())
# print(data.describe().to_string())



# data["time_stamp"] = int(mktime(datetime.strptime(data[0], '%Y-%m-%d %H:%M').timetuple()))
#
# print(data.head().to_string())

data["year"]=pd.to_datetime(data[0])
# data["year"]=data['year'].dt.year


df = pd.DataFrame(data)
# print(df)
df.rename(columns = {0:'time'}, inplace = True)
df.rename(columns = {1:'counts'}, inplace = True)\

# df['counts']=df['counts']*0.9
#
# print(df)
# df.iloc[0:20000:10].plot(x='year', y='counts', kind='scatter')
# plt.show()

os.chdir(r'C:\Users\Ja\OneDrive\Dokumenty\Materiały\credo\eq')
csv_files = [f for f in os.listdir() if f.endswith('.csv')]
dfs = []
for csv in csv_files:
    df = pd.read_csv(csv)
    dfs.append(df)

eq_df = pd.concat(dfs, ignore_index=True)

#print(eq_df.head().to_string())
# print(eq_df.describe().to_string())

eq_df["year"]=pd.to_datetime(eq_df['time'])

print(eq_df.head().to_string())

# def nwm(t0,t, delt,):
#     magns = []
#     sum = 0
#     for i in eq_df.index:
#         if eq_df['year'][i] >= (t0+timedelta(days=delt) & eq_df['year'][i]<= t0+timedelta(days=delt+t):
#             sum = sum + eq_df['mag'][i]
#         if eq_df['year'][i] > (t0+delt+t):
#             t0 = t0 + timedelta(days=t)
#             magns.append(sum)
#     return magns
# print(nwm())



# t0='1992-07-19T00:00:000Z'
# t0=pd.to_datetime(t0)
# delt=3
# t=5
# sum = 0
# magns=[]
# for i in eq_df.index:
#     if eq_df['year'][i] >= t0+ timedelta(days=delt) and eq_df['year'][i] <= t0 + timedelta(days=delt+t):
#         sum = sum + eq_df['mag'][i]
#         print(sum)
#     elif eq_df['year'][i] < t0+ timedelta(days=delt):
#         continue
#     else:
#         magns.append(sum)
#         sum=0
#         t0=t0+timedelta(days=t)
#
# print(magns)

d = '2005-07-23 00:00:00'



def eq_data(date_path):
    usecols = ["time", "latitude", "longitude", "mag"]
    files = os.path.join(date_path, "*.csv")
    files = glob.glob(files)
    df = pd.concat(map(pd.read_csv, files), ignore_index=True)
    df = df[usecols]
    df = df[(df['mag'] >= 4)]  # save only row where mag >= 4
    # df.to_csv('C:/Users/Ja/Downloads/datatime/Data_analysis/eq_data.csv', index=False)
    # create second file with sum (from evry day) and mean from N days (5 days)
    df["time"] = df.apply(lambda x: pd.to_datetime(x['time'].split(".")[0].replace("T"," "), format='%Y-%m-%d %H:%M:%S'), axis=1)
    df = df[(df['time'] >= pd.to_datetime(d))]

    new_row = pd.DataFrame({'time': pd.to_datetime(d),'latitude':0, 'longitude' : 0, 'mag': 0},
                           index=[0])
    # simply concatenate both dataframes
    df = pd.concat([new_row, df]).reset_index(drop=True)


    df.to_csv('C:/Users/Ja/Downloads/datatime/Data_analysis/eq_data.csv', index=False)
    df['date'] = df['time']
    df2 = df[["time", "date", 'mag']].copy()


    df2 = df2.groupby(pd.Grouper(key='date', freq='5D', origin='start'), as_index=False)['mag'].agg(['sum',"count"])
    # df2 = df2.groupby(pd.Grouper(key='date', freq='T'), as_index=False)['sum'].agg(['mean'])
    # df2["mean"] = df2.apply(lambda x: round(x['mean'], 1), axis=1)
    df2.at[0,'count']=df2.at[0,'count']-1
    df2['date'] = df2['date'].dt.strftime("%Y-%m-%d %H:%M")
    df2['median']=0
    df2.to_csv('C:/Users/Ja/Downloads/datatime/Data_analysis/eq_data_msum.csv', index=False)

eq_data(r'C:\Users\Ja\OneDrive\Dokumenty\Materiały\credo\eq')


