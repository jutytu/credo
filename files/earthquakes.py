# This file creates .csv files with USGS data (earthquakes, their magnitued, coordinates, dates etc.) and filtered USGS data (magnitude: at least 4, 
# calculating sums over a day, medians over a given period etc.).

import pandas as pd
import glob
import os


data = pd.read_csv(r'C:\Users\Ja\PycharmProjects\credo\asciimosc.txt', sep=";", header=None)
# print(data.head().to_string())
# print(data.describe().to_string())

data["year"]=pd.to_datetime(data[0])

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

print(eq_df.head().to_string())
print(eq_df.describe().to_string())

eq_df["year"]=pd.to_datetime(eq_df['time'])

print(eq_df.head().to_string())


d = '2005-07-23 00:00:00'

def eq_data(date_path):
    usecols = ["time", "latitude", "longitude", "mag"]
    files = os.path.join(date_path, "*.csv")
    files = glob.glob(files)
    df = pd.concat(map(pd.read_csv, files), ignore_index=True)
    df = df[usecols]
    df = df[(df['mag'] >= 4)]  # save only rows where magnitude >= 4
    df.to_csv('C:/Users/Ja/Downloads/datatime/Data_analysis/eq_data.csv', index=False)
    # create second file with sum (from every day) and mean from N days (5 days)
    df["time"] = df.apply(lambda x: pd.to_datetime(x['time'].split(".")[0].replace("T"," "), format='%Y-%m-%d %H:%M:%S'), axis=1)
    df = df[(df['time'] >= pd.to_datetime(d))]

    new_row = pd.DataFrame({'time': pd.to_datetime(d),'latitude':0, 'longitude' : 0, 'mag': 0},
                           index=[0])
    # concatenate both dataframes
    df = pd.concat([new_row, df]).reset_index(drop=True)


    df.to_csv('C:/Users/Ja/Downloads/datatime/Data_analysis/eq_data.csv', index=False)
    df['date'] = df['time']
    df2 = df[["time", "date", 'mag']].copy()


    df2 = df2.groupby(pd.Grouper(key='date', freq='5D', origin='start'), as_index=False)['mag'].agg(['sum',"count"])
    df2.at[0,'count']=df2.at[0,'count']-1
    df2['date'] = df2['date'].dt.strftime("%Y-%m-%d %H:%M")
    df2['median']=0
    df2.to_csv('C:/Users/Ja/Downloads/datatime/Data_analysis/eq_data_msum.csv', index=False)

eq_data(r'C:\Users\Ja\OneDrive\Dokumenty\Materiały\credo\eq')


