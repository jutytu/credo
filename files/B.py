# Calculating the B factor (increase or decrease of cosmic ray intensity compared to the median over the previous 5 days)
# for the Pierre Auger observatory data.

import pandas as pd
import statistics


pa_df = pd.read_csv(r'C:\Users\Ja\Downloads\datatime\Data_analysis\pierre_auger\scalers.csv', sep=",")

# pa_df['date'] = datetime.fromtimestamp(pa_df['time'])
pa_df['date'] = pd.to_datetime(pa_df['time'], unit='s')
pa_df['date'] = pa_df['date'].dt.strftime("%Y-%m-%d %H:%M")
pa_df['date'] = pd.to_datetime(pa_df['date'])
pa_df = pa_df.groupby(pd.Grouper(key='date', freq='5D', origin='start'), as_index=False)['rateCorr'].agg(['sum',"count"])

pa_df['avg'] = pa_df['sum']/pa_df['count']
pa_df['delta'] = 0

n=1
while n < pa_df.size/5:
    pa_df.at[n, 'delta'] = abs(pa_df.at[n, 'avg'] - pa_df.at[n - 1, 'avg'])
    n = n+1


pa_df['median'] = 0

list=[]
l=335
n = 0

print(pa_df.size/6)

while n < pa_df.size/6:
    if n < l-1:
        list.append(pa_df.at[n, 'delta'])
        print(list)
        print(n)
        n=n+1

    if n >= l-1:
        print(n)
        list.append(pa_df.at[n, 'delta'])
        print(n)
        list.pop(0)
        pa_df.at[n,'median'] = statistics.median(list)
        print(n)
        print(list)
        n=n+1

pa_df['B'] = pa_df['delta']/pa_df['median']-1

print(pa_df.tail().to_string())
print(pa_df.describe().to_string())
