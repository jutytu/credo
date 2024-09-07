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

from scipy.stats import binom


def pdf(d, l, t, shift,shift2):
    d = pd.to_datetime(d) +timedelta(days=shift2)
    d_end = d + timedelta(days=l * int(t[:-1]))
    print("datetime dla EQ: ",d,d_end)
    eq_df = pd.read_csv(r'C:\Users\Ja\Downloads\datatime\Data_analysis\eq_data.csv', sep=",")
    eq_df['time'] = pd.to_datetime(eq_df['time'])
    eq_df = eq_df[(eq_df['time'] >= d - timedelta(days=shift))]
    eq_df.index = range(len(eq_df))
    # nadanie indexow
    new_row = pd.DataFrame({'time': pd.to_datetime(d) - timedelta(days=shift), 'latitude': 0, 'longitude': 0, 'mag': 0},
                           index=[0])
    eq_df = pd.concat([new_row, eq_df]).reset_index(drop=True)

    eq_df = eq_df[(eq_df['time'] <= pd.to_datetime(d_end))]
    eq_df['date'] = eq_df['time']
    eq_df = eq_df[["date", 'mag']]

    # eq_df = eq_df.groupby(pd.Grouper(key='date', freq=t, origin='start'), as_index=False)['mag'].agg(['mean', 'sum', "count"])
    eq_df = eq_df.groupby(pd.Grouper(key='date', freq=t, origin='start'), as_index=False)['mag'].agg(["count", "sum"])
    eq_df.at[0, 'count'] = eq_df.at[0, 'count'] - 1

    d = d - timedelta(days=shift2) # przesuniecie o 10
    print("datetime dla Auger: ",d,d_end)
    d_end = d + timedelta(days=l * int(shift))
    print(d_end)

    pa_df = pd.read_csv(r'C:\Users\Ja\Downloads\datatime\Data_analysis\pierre_auger\scalers.csv', sep=",")
    pa_df['date'] = pd.to_datetime(pa_df['time'], unit='s')
    pa_df = pa_df[(pa_df['date'] > (pd.to_datetime(d)) - timedelta(days=shift))]
    pa_df.index = range(len(pa_df))
    new_row = pd.DataFrame({'time': 0, 'rateCorr': 0, 'arrayFraction': 0, 'rateUncorr': 0, 'pressure': 0,
                            'date': pd.to_datetime(d) - timedelta(days=shift)}, index=[0])
    pa_df = pd.concat([new_row, pa_df]).reset_index(drop=True)
    pa_df = pa_df[(pa_df['date'] <= pd.to_datetime(d_end))]
    pa_df = pa_df.groupby(pd.Grouper(key='date', freq=t, origin='start'), as_index=False)['rateCorr'].agg(
        ['mean', 'sum', "count"])
    pa_df.at[0, 'count'] = pa_df.at[0, 'count'] - 1

    c = pd.DataFrame()
    c['pa date'] = pa_df['date']
    c['eq date'] = eq_df['date']
    c['pa sum'] = pa_df['sum']
    c['pa count'] = pa_df['count']
    c['eq sum'] = eq_df['sum']
    c["pa mean"] = pa_df['mean']

    c['pa delta3'] = abs(c['pa mean'].diff())

    c.index = range(len(c))
    c['pa median'] = c['pa delta3'].median()  # mediane liczymy przed usuwaniem pustych elementów

    # c = c[(c['pa mean'] > 0) & (c['pa delta'] > 0) & (c['pa delta3'] > 0)]  # usun element z dziura

    c = c[(c['pa delta3'] > 0)]  # usun element z dziura

    c['eq median'] = c['eq sum'].median()
    c['eq diff'] = c.apply(lambda x: round(x["eq sum"] - x['eq median'], 4), axis=1)

    c['A'] = c['eq sum']/c['eq median'] - 1
    c['B'] = c['pa delta3']/c['pa median'] - 1
    c['c'] = np.sign(c['A'] * c['B'])

    # c = c.drop(c.index[0])
    c.index = range(len(c))

    # print(eq_df.head())
    # print(pa_df.head())
    # print(c.head().to_string())
    # print(c.tail().to_string())
    #
    # print(len(c))
    # print(c['c'].value_counts()[1])
    coulumn = ["pa date", "eq date", "pa mean", "eq sum", "pa delta3", "eq median", "pa median", "eq diff", "A", "B", "c"]
    c.to_csv("pdf3.csv", index=False, columns=coulumn)

    tmp_c = c[(c['c'] > 0)] # nowe
    # newton = 1-binom.cdf(len(tmp_c),len(c),0.5,1) # nowe
    CDF = 1-binom.cdf(len(tmp_c),len(c),0.5,1) # nowe
    print("CDF: ", CDF)

    n = c['c'].value_counts()[1]
    N = len(c)
    PDF = math.comb(N, n) * ((1 / 2) ** N)
    return PDF


# 2014-04-02 22:07:12
print("PDF: ", pdf('2014-04-02 22:07:12', 335, '5D', 5,15))

data = pd.DataFrame()
date = pd.to_datetime('2012-03-02 22:07:12')


while date <= pd.to_datetime('2014-06-21 22:07:12'):
    print(date)
    row = pd.DataFrame({'date': date, 'pdf': pdf(date.strftime("%Y-%m-%d %H:%M:%S"), 335, '5D', 5, 15)},
                       index = [0])
    data = pd.concat([row, data]).reset_index(drop=True)
    data.to_csv('C:/Users/Ja/Downloads/datatime/Data_analysis/pdf_data4.csv', index=False)
    date = date + timedelta(days = 1)
