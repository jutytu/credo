# Concatenating multiple earthquake data files.

import pandas as pd
import glob
import os

usecols = ["time", "latitude", "longitude", "mag"]
files = os.path.join(r'C:\Users\Ja\OneDrive\Dokumenty\Materiały\credo\eq', "*.csv")
files = glob.glob(files)
df = pd.concat(map(pd.read_csv, files), ignore_index=True)
df = df[usecols]
df = df[(df['mag'] >= 4)]  # save only row where mag >= 4
# df.to_csv('C:/Users/Ja/Downloads/datatime/Data_analysis/eq_data.csv', index=False)
# create second file with sum (from every day) and mean from N days (5 days)
df["time"] = df.apply(
    lambda x: pd.to_datetime(x['time'].split(".")[0].replace("T", " "), format='%Y-%m-%d %H:%M:%S'), axis=1)

df.to_csv('C:/Users/Ja/Downloads/datatime/Data_analysis/eq_data.csv', index=False)
