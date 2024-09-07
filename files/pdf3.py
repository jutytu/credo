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


def pdf(d, l, t, shift):

    d = pd.to_datetime(d) + timedelta(days=shift)
    d_end = d + timedelta(days=(l) * int(t[:-1]))

    eq_df = pd.read_csv(r'C:\Users\Ja\Downloads\datatime\Data_analysis\eq_data.csv', sep=",")
    eq_df['time'] = pd.to_datetime(eq_df['time'])
    eq_df = eq_df[(eq_df['time'] >= d - timedelta(days=int(t[:-1])))]
    eq_df.index = range(len(eq_df))
    new_row = pd.DataFrame({'time': pd.to_datetime(d) - timedelta(days=int(t[:-1])), 'latitude': 0, 'longitude': 0, 'mag': 0},
                           index=[0])
    eq_df = pd.concat([new_row, eq_df]).reset_index(drop=True)
    eq_df = eq_df[(eq_df['time'] <= pd.to_datetime(d_end))]
    eq_df['date'] = eq_df['time']
    eq_df = eq_df[["date", 'mag']]
    eq_df = eq_df.groupby(pd.Grouper(key='date', freq=t, origin='start'), as_index=False)['mag'].agg(['sum', "count"])
    eq_df.at[0, 'count'] = eq_df.at[0, 'count'] - 1

    d = d - timedelta(days=shift)
    d_end = d + timedelta(days=(l) * int(t[:-1]))

    pa_df = pd.read_csv(r'C:\Users\Ja\Downloads\datatime\Data_analysis\pierre_auger\scalers.csv', sep=",")
    pa_df['date'] = pd.to_datetime(pa_df['time'], unit='s')
    pa_df = pa_df[(pa_df['date'] >= (pd.to_datetime(d)) - timedelta(days=int(t[:-1])))]
    pa_df.index = range(len(pa_df))
    new_row = pd.DataFrame({'time': 0, 'rateCorr': 0, 'arrayFraction': 0, 'rateUncorr': 0, 'pressure': 0,
                            'date': pd.to_datetime(d) - timedelta(days=int(t[:-1]))}, index=[0])
    pa_df = pd.concat([new_row, pa_df]).reset_index(drop=True)
    pa_df = pa_df[(pa_df['date'] <= pd.to_datetime(d_end))]
    pa_df = pa_df.groupby(pd.Grouper(key='date', freq=t, origin='start'), as_index=False)['rateCorr'].agg(
        ['sum', "count"])
    pa_df.at[0, 'count'] = pa_df.at[0, 'count'] - 1


    c = pd.DataFrame()
    c['pa date'] = pa_df['date']
    c['eq date'] = eq_df['date']
    c['pa sum'] = pa_df['sum']
    c['pa count'] = pa_df['count']
    c['eq sum'] = eq_df['sum']

    c['pa delta'] = 0
    n = 1
    while n < len(c):
        if (c.at[n, 'pa count'] != 0 and c.at[n-1, 'pa count'] != 0):
            c.at[n, 'pa delta'] = abs(c.at[n, 'pa sum']/c.at[n, 'pa count'] - c.at[n - 1, 'pa sum']/c.at[n - 1, 'pa count'])
        n = n + 1

    n = 1
    to_drop = []
    while n < len(c.index) - 1:
        if (c.at[n, 'pa sum'] == 0 or c.at[n - 1, 'pa sum'] == 0 or c.at[n + 1, 'pa sum'] == 0 or
                c.at[n, 'eq sum'] == 0):
            to_drop.append(n)
        n = n + 1

    c = c.drop(c.index[to_drop])
    c.index = range(len(c))

    c['eq median'] = c['eq sum'].median()
    c['pa median'] = c['pa delta'].median()

    c['A'] = c['eq sum']/c['eq median'] - 1
    c['B'] = c['pa delta']/c['pa median'] - 1
    c['c'] = np.sign(c['A'] * c['B'])
    c = c.drop(c.index[0])
    c.index = range(len(c))

    # print(eq_df.head())
    # print(pa_df.head())
    # print(c.head().to_string())
    # print(c.tail().to_string())
    #
    # print(len(c))
    # print(c['c'].value_counts()[1])

    n = c['c'].value_counts()[1]
    N = len(c)
    newton = math.comb(N, n) * ((1 / 2) ** N)
    return newton

# print(pdf('2014-04-02 22:07:12', 335, '5D', 15))

data = pd.DataFrame()
date = pd.to_datetime('2012-03-02 22:07:12')


while date <= pd.to_datetime('2014-06-02 22:07:12'):
    print(date)
    row = pd.DataFrame({'date': date, 'pdf': pdf(date.strftime("%Y-%m-%d %H:%M:%S"), 335, '5D', 15)},
                       index = [0])
    data = pd.concat([row, data]).reset_index(drop=True)
    data.to_csv('C:/Users/Ja/Downloads/datatime/Data_analysis/pdf_data3.csv', index=False)
    date = date + timedelta(days = 1)
