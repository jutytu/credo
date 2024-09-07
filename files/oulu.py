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

    o_df = pd.read_csv(r'C:\Users\Ja\Downloads\datatime\Data_analysis\Oulu.csv', sep=";")
    o_df['date'] = pd.to_datetime(o_df['start_date_time'])
    o_df['RCORR_E']=o_df['RCORR_E'].astype(float)
    o_df = o_df[(o_df['date'] >= (pd.to_datetime(d)) - timedelta(days=int(t[:-1])))]
    o_df.index = range(len(o_df))
    new_row = pd.DataFrame({'start_date_time': pd.to_datetime(d) - timedelta(days=int(t[:-1])),
                            'RCORR_E': 0, 'date': pd.to_datetime(d) - timedelta(days=int(t[:-1]))}, index=[0])
    o_df = pd.concat([new_row, o_df]).reset_index(drop=True)
    o_df = o_df[(o_df['date'] <= pd.to_datetime(d_end))]
    o_df = o_df.groupby(pd.Grouper(key='date', freq=t, origin='start'), as_index=False)['RCORR_E'].agg(
        ['sum', "count"])
    o_df.at[0, 'count'] = o_df.at[0, 'count'] - 1


    c = pd.DataFrame()
    c['o date'] = o_df['date']
    c['eq date'] = eq_df['date']
    c['o sum'] = o_df['sum']
    c['o count'] = o_df['count']
    c['eq sum'] = eq_df['sum']

    c['o delta'] = 0
    n = 1
    while n < len(c):
        if (c.at[n, 'o count'] != 0 and c.at[n-1, 'o count'] != 0):
            c.at[n, 'o delta'] = abs(c.at[n, 'o sum']/c.at[n, 'o count'] - c.at[n - 1, 'o sum']/c.at[n - 1, 'o count'])
        n = n + 1

    n = 1
    to_drop = []
    while n < len(c.index) - 1:
        if (c.at[n, 'o sum'] == 0 or c.at[n - 1, 'o sum'] == 0 or c.at[n + 1, 'o sum'] == 0 or
                c.at[n, 'eq sum'] == 0):
            to_drop.append(n)
        n = n + 1

    c = c.drop(c.index[to_drop])
    c.index = range(len(c))

    c['eq median'] = c['eq sum'].median()
    c['o median'] = c['o delta'].median()

    c['A'] = c['eq sum']/c['eq median'] - 1
    c['B'] = c['o delta']/c['o median'] - 1
    c['c'] = np.sign(c['A'] * c['B'])
    c = c.drop(c.index[0])
    c.index = range(len(c))

    # print(eq_df.head())
    # print(o_df.head())
    # print(c.tail())
    # print(c.head().to_string())
    # print(c.tail().to_string())
    #
    # print(len(c))
    # print(c['c'].value_counts()[1])

    n = c['c'].value_counts()[1]
    N = len(c)
    newton = math.comb(N, n) * ((1 / 2) ** N)
    return newton

# print(pdf('1969-07-12 07:32:12', 670, '5D', 15))

data = pd.DataFrame()
# n = pd.to_datetime("1969-07-07 07:37:12")
#
# # print(pdf('1969-07-16 03:32:12', 670, '5D', 15))
#
# while n <= pd.to_datetime('1969-07-17 07:37:12'):
#     print(n)
#     row = pd.DataFrame({'date': n, 'pdf': pdf(n.strftime("%Y-%m-%d %H:%M:%S"), 670, '5D', 15)},
#                        index = [0])
#     data = pd.concat([row, data]).reset_index(drop=True)
#     data.to_csv('C:/Users/Ja/Downloads/datatime/Data_analysis/o_datashift.csv', index=False)
#     n = n + timedelta(hours=1)

n = 1


while n <= 30:
    print(n)
    row = pd.DataFrame({'date': n, 'pdf': pdf('1969-07-10 01:37:12', 670, '5D', n)},
                       index = [0])
    data = pd.concat([row, data]).reset_index(drop=True)
    data.to_csv('C:/Users/Ja/Downloads/datatime/Data_analysis/o_datashift.csv', index=False)
    n = n + 1