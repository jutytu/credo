import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import glob
import statistics
import os
import math
from time import mktime
from datetime import datetime, date, timedelta, timezone
import sys


# d = '2014-03-02 22:07:12'
# l = 335
# t = '5D'
# shift = 15

# usecols = ["time", "latitude", "longitude", "mag"]
# files = os.path.join(r'C:\Users\Ja\OneDrive\Dokumenty\Materiały\credo\eq', "*.csv")
# files = glob.glob(files)
# df = pd.concat(map(pd.read_csv, files), ignore_index=True)
# df = df[usecols]
# df = df[(df['mag'] >= 4)]  # save only row where mag >= 4
# # df.to_csv('C:/Users/Ja/Downloads/datatime/Data_analysis/eq_data.csv', index=False)
# # create second file with sum (from every day) and mean from N days (5 days)
# df["time"] = df.apply(
#     lambda x: pd.to_datetime(x['time'].split(".")[0].replace("T", " "), format='%Y-%m-%d %H:%M:%S'), axis=1)

def pdf(d, l, t, shift):
    d = pd.to_datetime(d) + timedelta(days=shift)
    d_end = d + timedelta(days=(l - 1) * int(t[:-1]))

    if d < pd.to_datetime('2005-03-30 20:52:00'):
        print('too early')
        sys.exit(1)

    df = pd.read_csv(r'C:\Users\Ja\Downloads\datatime\Data_analysis\eq_data.csv', sep=",")
    df['time'] = pd.to_datetime(df['time'])
    df = df[(df['time'] >= d)]
    df.index = range(len(df))
    new_row = pd.DataFrame({'time': pd.to_datetime(d), 'latitude': 0, 'longitude': 0, 'mag': 0},
                           index=[0])
    # simply concatenate both dataframes
    df = pd.concat([new_row, df]).reset_index(drop=True)

    df = df[(df['time'] <= pd.to_datetime(d_end))]
    df.index = range(len(df))
    new_row = pd.DataFrame({'time': pd.to_datetime(d_end), 'latitude': 0, 'longitude': 0, 'mag': 0},
                           index=[len(df)])
    df = pd.concat([new_row, df]).reset_index(drop=True)

    # df.to_csv('C:/Users/Ja/Downloads/datatime/Data_analysis/eq_data.csv', index=False)
    df['date'] = df['time']
    df2 = df[["time", "date", 'mag']].copy()

    df2 = df2.groupby(pd.Grouper(key='date', freq=t, origin='start'), as_index=False)['mag'].agg(['sum', "count"])
    # df2 = df2.groupby(pd.Grouper(key='date', freq='T'), as_index=False)['sum'].agg(['mean'])
    # df2["mean"] = df2.apply(lambda x: round(x['mean'], 1), axis=1)
    df2.at[0, 'count'] = df2.at[0, 'count'] - 1
    df2.at[len(df2) - 1, 'count'] = df2.at[len(df2) - 1, 'count'] - 1
    df2['date'] = df2['date'].dt.strftime("%Y-%m-%d %H:%M:%S")
    df2['median'] = 0
    df2.to_csv('C:/Users/Ja/Downloads/datatime/Data_analysis/eq_data_msum.csv', index=False)

    eq_df = df2
    #
    # list = []
    # n = 0
    #
    # while n < eq_df.size / 4:
    #     list.append(eq_df.at[n, 'sum'])
    #     n = n + 1

    eq_df['median'] = eq_df['sum'].median()

    eq_df['A'] = eq_df['sum'] / eq_df['median'] - 1

    eq_df.to_csv('C:/Users/Ja/Downloads/datatime/Data_analysis/eq_data_A.csv', index=False)

    # print(eq_df.head(400).to_string())

    d = d - timedelta(days=shift)
    d_end = d + timedelta(days=(l - 1) * int(t[:-1]))

    pa_df = pd.read_csv(r'C:\Users\Ja\Downloads\datatime\Data_analysis\pierre_auger\scalers.csv', sep=",")

    # pa_df['date'] = datetime.fromtimestamp(pa_df['time'])
    pa_df['date'] = pd.to_datetime(pa_df['time'], unit='s')
    pa_df['date'] = pa_df['date'].dt.strftime("%Y-%m-%d %H:%M:%S")
    pa_df['date'] = pd.to_datetime(pa_df['date'])
    # print(pa_df.head(50).to_string())

    pa_df = pa_df[(pa_df['date'] >= (pd.to_datetime(d)) - timedelta(days=int(t[:-1])))]
    pa_df.index = range(len(pa_df))
    new_row = pd.DataFrame({'time': 0, 'rateCorr': 0, 'arrayFraction': 0, 'rateUncorr': 0, 'pressure': 0,
                            'date': pd.to_datetime(d) - timedelta(days=int(t[:-1]))}, index=[0])
    pa_df = pd.concat([new_row, pa_df]).reset_index(drop=True)

    pa_df = pa_df[(pa_df['date'] <= pd.to_datetime(d_end))]
    pa_df.index = range(len(pa_df))
    new_row = pd.DataFrame({'time': 0, 'rateCorr': 0, 'arrayFraction': 0, 'rateUncorr': 0, 'pressure': 0,
                            'date': pd.to_datetime(d_end)}, index=[len(pa_df)])
    pa_df = pd.concat([new_row, pa_df]).reset_index(drop=True)

    pa_df = pa_df.groupby(pd.Grouper(key='date', freq=t, origin='start'), as_index=False)['rateCorr'].agg(
        ['sum', "count"])

    # print(pa_df.head(400).to_string())

    pa_df['avg'] = 0
    pa_df.at[0, 'count'] = pa_df.at[0, 'count'] - 1
    pa_df.at[len(pa_df) - 1, 'count'] = pa_df.at[len(pa_df) - 1, 'count'] - 1

    # print(pa_df.head(500).to_string())
    pa_df.index = range(len(pa_df))

    n = 0
    while n < len(pa_df):
        if pa_df.at[n, 'count'] != 0:
            pa_df.at[n, 'avg'] = pa_df.at[n, 'sum'] / pa_df.at[n, 'count']
        n = n + 1

    pa_df['delta'] = 0
    # print(pa_df.head(350).to_string())

    n = 1
    while n < len(pa_df):
        pa_df.at[n, 'delta'] = abs(pa_df.at[n, 'avg'] - pa_df.at[n - 1, 'avg'])
        n = n + 1

    pa_df = pa_df.drop(pa_df.index[0])
    pa_df.index = range(len(pa_df))

    # list = []
    # n = 0
    #
    # while n < len(pa_df):
    #     list.append(pa_df.at[n, 'delta'])
    #     n = n + 1

    pa_df['median'] = pa_df['delta'].median()

    pa_df['B'] = pa_df['delta'] / pa_df['median'] - 1

    pa_df.index = range(len(pa_df))

    # print(pa_df.head(50).to_string())
    # print(eq_df.head(50).to_string())

    c = pd.DataFrame()
    c['date eq'] = eq_df['date']
    c['A'] = eq_df['A']
    c['date pa'] = pa_df['date']
    c['B'] = pa_df['B']
    c['c'] = np.sign(c['A'] * c['B'])
    c = c.head(l)
    # or pa_df.at[n-1, 'count'] == 0 or c.at[n, 'c'] == 0 or eq_df.at[n, 'sum'] == 0
    n = 1
    to_drop = []
    while n < len(c.index):
        if (pa_df.at[n, 'count'] == 0 or pa_df.at[n - 1, 'count'] == 0 or c.at[n, 'c'] == 0 or eq_df.at[n, 'sum'] == 0):
            to_drop.append(n)
        n = n + 1

    c = c.drop(c.index[to_drop])
    c.index = range(len(c))
    # print(c.head(450).to_string())

    n = c['c'].value_counts()[1]
    N = len(c)
    newton = math.comb(N, n)*((1/2)**N)
    return newton



data = pd.DataFrame()
date = pd.to_datetime('2012-03-02 22:07:12')
# print(pdf(date.strftime("%Y-%m-%d %H:%M:%S"), 335, '5D', 15))
# print(pdf('2014-04-02 22:07:12', 335, '5D', 15))


while date <= pd.to_datetime('2014-06-02 22:07:12'):
    row = pd.DataFrame({'date': date, 'pdf': pdf(date.strftime("%Y-%m-%d %H:%M:%S"), 335, '5D', 15)},
                       index = [len(data)])
    data = pd.concat([row, data]).reset_index(drop=True)
    data.to_csv('C:/Users/Ja/Downloads/datatime/Data_analysis/pdf_data2.csv', sep= ";", index=False)
    date = date + timedelta(hours = 6)
    print(date)


