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

df = pd.read_csv(r'C:\Users\Ja\Downloads\datatime\Data_analysis\pdf_data4.csv', sep=",")

print(df.head().to_string())

df['date'] = pd.to_datetime(df['date'])
# df['pdf'].apply(lambda x: float(x))
df['pdf'] = np.log10(df['pdf'])

print(df.pdf.min())
print(df.at[df['pdf'].argmin(), 'date'])

df = df.sort_values('date', ascending=True)
plt.plot(df['date'], df['pdf'], '*')
# plt.ylabel("")
plt.axhline(df.pdf.min())
# plt.yscale("log")
plt.xticks(rotation=15)
plt.savefig('pa_final.png')
plt.show()
