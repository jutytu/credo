import csv
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math
from datetime import datetime, timedelta
from Functions.data_time_operation import Sun
from Functions.data_time_operation import set_start_end, create_window, days_from_2000, date_range, sunrise_bin_window
from path_links import main_path, data_analysis_path

"""
how to calculate pdf:
1. calculate A - for a given time window
2. calculate B - for a given time window
"""
"""
A: 

1. I need to define a function that yields a dictionary: keys are dates (strptime/datetime! from documentation?) t_i, start from
t_0 (first t_i is t_0 - P), spaced by d, each key contains the sum of the magnitudes > m for a given interval d, whatever 
t_0 we need to add shift del_t (proper t_0 will be used for CR ratio in B) (sums)

2. another function to calculate the median from period P:
with dict from 1. for datetime >= t_0 add key to the new dict with t_i starting from t_0: each key contains the median of 
P/d records from dict1 from t_0 - P + i*d to t_0 + i*d (medians)

3. for each index i: dict A sums/medians-1
"""

os.chdir(r'C:\Users\Ja\OneDrive\Dokumenty\Materiały\credo\eq')
csv_files = [f for f in os.listdir() if f.endswith('.csv')]
dfs = []
for csv in csv_files:
    df = pd.read_csv(csv)
    dfs.append(df)

eq_df = pd.concat(dfs, ignore_index=True)
eq_df["year"]=pd.to_datetime(eq_df['time'])
df["time"] = df.apply(lambda x: pd.to_datetime(x['time'].split(".")[0].replace("T"," "), format='%Y-%m-%d %H:%M:%S'), axis=1)
df['year'] = df['time']

eq_df = pd.read_csv(r'C:\Users\Ja\Downloads\datatime\Data_analysis\eq_data_msum.csv', sep=",", header=None)

print(eq_df.head().to_string())
print(eq_df.describe().to_string())

def sums(t_0, t_end, P, d, del_t,):
    t_mod = pd.to_datetime(t_0)
    t_mod = t_mod - timedelta(days=P)
    t_mod = t_mod.strftime("%Y-%m-%d %H:%M")
    a, dict, b = create_window(day=d, hour=0, minutes=0, starter=t_mod, ender=t_end )
    n=0
    for key, value in dict.items():
        dict[key] = eq_df[value]

    return dict





dict = sums("2022-07-01", "2023-07-05", 1, 2, 3)
print(dict)




