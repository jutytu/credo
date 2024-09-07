import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import glob
import statistics
import os
import math
from time import mktime
from datetime import datetime, date, timedelta, timezone

def sums(t_0, t_end, P, d, del_t,):
    a, dict, b = create_window(day=d, hour=0, minutes=0, starter=t_mod, ender=t_end )

    return dict

eq_df = pd.read_csv(r'C:\Users\Ja\Downloads\datatime\Data_analysis\eq_data_msum.csv', sep=",")

print(eq_df.head().to_string())
print(eq_df.describe().to_string())


# t_0 = '2005-07-23 12:10:10'
# a, dict, b = create_window(day=5, hour=0, minutes=0, starter=t_0, ender=t_end )

A = {}

list=[]
l=335
n = 0
print(eq_df.at[n, 1])
print(eq_df.size)
while n < eq_df.size/4:
    if n < l-1:
        list.append(eq_df.at[n, 1])
        print(list)
        print(n)
        n=n+1

    if n >= l-1:
        list.append(eq_df.at[n, 1])
        list.pop(0)
        eq_df.at[n, 3] = statistics.median(list)
        print(n)
        print(list)
        n=n+1



eq_df['A'] = eq_df[1]/eq_df[3]-1
eq_df.to_csv('C:/Users/Ja/Downloads/datatime/Data_analysis/eq_data_A.csv', index=False)

print(eq_df.head(400).to_string())
# print(eq_df.describe().to_string())