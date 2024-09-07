"""
Analysis of public data from the Pierre Auger Observatory,
csv file downloaded from
https://opendata.auger.org/data.php#scalers
"""
import csv
import os
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
from Functions.data_time_operation import Sun
from Functions.data_time_operation import set_start_end, create_window, days_from_2000, date_range, sunrise_bin_window
from path_links import main_path, data_analysis_path

main_path2 =  "C:/Users/Ja/Downloads/datatime/Data_analysis/pierre_auger/"
pg_data = main_path2 + "scalers.csv"
# pg_data The "scaler.csv" file contains:
#     time: Unix time in seconds (seconds since 1st Jan 1970, w/o leap seconds)
#     rateCorr: corrected scaler rate [counts/m2/s]
#     arrayFraction:Fraction of array in operation [%]
#     rateUncorr: average detector scaler rate, uncorrected [counts/s]
#     pressure: barometric pressure [hPa]

# date will be passed to the function create_window
begin_date, end_date = "2005-01-03 00:00", "2020-01-01 00:00"
begin, end = set_start_end(begin_date, end_date)
# days, hours, minutes - size of a single window
w_d, w_h, w_m = 0, 0, 15
# Latitude: -34° 27' 59.99" S
# Longitude: -69° 18' 24.60" w
# PIERRE AUGER CORDS
coordinates = {'longitude': -69.182460, 'latitude': -35.275999}

# analysed_bin - id of the bin for which we are counting the difference
# sunrise_bin_date[window_date][N] - sunrise_bin_date[window_date][N-1]
analysed_bin = 1


def read_csv():
    """
    Reads the csv file, checks for each row in turn for its timestamp
    and whether it is within the time range we are looking for (range from begin_date to end_date).
    If so, it checks which particular window it matches and adds the rateCorr value there
    :return: Once all the values have been analysed, it runs the analyze_window function,
    specifying its window size (shift), 'window' dictionary and n_days - the default is 100 days.
    """
    shift, window, small_window = create_window(day=w_d, hour=w_h, minutes=w_m, starter=begin_date, ender=end_date)
    csvfile = open(pg_data)
    reader = csv.DictReader(csvfile)
    for row in reader:
        timestamp = int(row['time'])
        detects = row['rateCorr']  # corrected scaler rate [counts/m2/s]
        if timestamp > begin:
            timestamp_in_window = timestamp - timestamp % shift
            # utcfromtimestamp - da nam datetime w strefie 0
            data_time = datetime.utcfromtimestamp(timestamp_in_window).strftime('%Y-%m-%d %H:%M:%S')
            if data_time in window:  # data_time = 2014-09-16 09:00:00; window[data_time] = [179.43]
                window[data_time].append(float(detects))

    sunrise_bin_date, sunrise_dates = sunrise_bin_window(shift, window, coordinates)
    # AT THIS STAGE WE ALREADY HAVE A sunrise_bin_date DICTIONARY INCLUDING ALL WINDOWS (15 MIN) BETWEEN 1 AND 2 SUNRISE
    # ONE RECORD IS E.G. FOR 2019-05-02 WHERE SUNRISE IS 11:14:00
    # ['2019-05-02 11:00:00', '2019-05-02 11:15:00' (..) '2019-05-03 10:30:00', '2019-05-03 10:45:00']
    # SUNRISE 2019-05-03 IS AT 11:11:00 AM
    analyze_window(shift, window, sunrise_bin_date, sunrise_dates, n_days=3)
    # at this stage, we have already created a chart for a single bin. Now we will additionally create
    # a "scater plot" which will show what the results look like for given bins after sunrise.
    scater_analyze_window(shift, window, sunrise_bin_date, n_days=100)


def analyze_window(shift, window_list, sunrise_bin_date, sunrise_dates, n_days=100):
    """
    Function responsible for the entire analysis of counting the averages of n_days
    for the difference in detection increment for a given window number "analysed_bin" after sunrise.
    :param shift: the size of a single window specified in seconds. E.g. 15 minutes is 900 seconds - then shift = 900
    :param window_list: a dictionary with all windows in the range from begin_date to end_date.
            A single window contains counts /m2/second e.g. window_list["2020-07-10 09:00:00"] = [178.39].
    :param sunrise_bin_date: sunrise dictionary with all the bins (individual windows) belonging to a given day
            between one sunrise and the other
    :param sunrise_dates: dictionary with dates and time of sunrise for a given day and a given location
            based on given coordinates
    :param n_days: the number of days for which we calculate the average for each bin.
    :return: It saves the results to a csv file and the graph as a png
    """

    diff_sunrise_bin_date = {}  # For a given analysed_bin we calculate the bin1-bin0 differences
    for window_date in sunrise_bin_date:
        time_bin1 = sunrise_bin_date[window_date][analysed_bin]  # i.e 2005-01-03 09:30:00
        time_bin0 = sunrise_bin_date[window_date][analysed_bin - 1]  # i.e 2005-01-03 09:15:00
        if len(window_list[time_bin1]) > 0 and len(window_list[time_bin0]) > 0:
            # A single element in the window_list dictionary is a list, so even if it's a one-element list
            # we have to refer to it by its position in the list - the first element is 0 i.e. window_list[time_bin1][0]
            bin_1 = window_list[time_bin1][0]  # i.e 188.954
            bin_0 = window_list[time_bin0][0]  # i.e 188.954
            # the values have 3 decimal places so we also want 3 decimal places in the difference
            diff_detects = round(bin_1 - bin_0, 3)
            # print(window_date, bin_0,bin_1,diff_detects)  # 2019-09-29 180.62 180.675 0.055
            diff_sunrise_bin_date[window_date] = diff_detects

    # Once we have calculated the differences for our bin for all dates,
    # we can count the average of the "n_days" for each date

    avg_sunrise_bin_date = {}  # average of variances of n_day
    sum_sunrise_bin_date = {}  # sum of the n_day (100) most recent days
    active_sunrise_bin_date = {} # list of differences in values over the last N-days
    for window_date in sunrise_bin_date:
        avg_sunrise_bin_date[window_date] = []
        date_of_end = datetime.strptime(window_date, "%Y-%m-%d").date()
        start_date = (date_of_end - timedelta(days=n_days - 1))
        # timedelta(days=n_days - 1) - 1 because it does not take into account the end date "today"

        # first avg_sunrise_bin_date will be a list of differences from n_days
        for single_date in date_range(start_date, date_of_end):
            current_date = single_date.strftime("%Y-%m-%d")
            if current_date in diff_sunrise_bin_date:
                avg_sunrise_bin_date[window_date].append(diff_sunrise_bin_date[current_date])

        # Above if we had n_days = 100 then we added 99 results to avg_sunrise_bin_date[window_date],
        # now we will add the result for the end date
        if date_of_end.strftime("%Y-%m-%d") in diff_sunrise_bin_date:
            avg_sunrise_bin_date[window_date].append(diff_sunrise_bin_date[date_of_end.strftime("%Y-%m-%d")])

        #  Having already created a list of differences for a given "window_date"
        #  (number: n_days) we calculate the average
        # Currently, I have set that the result is analysed if there is a minimum of 2 out of n_days
        # (the condition refers to the beginning of the set, or the date after a long break - if it would exist)
        if len(avg_sunrise_bin_date[window_date]) > 2:
            # print(window_date, len(avg_sunrise_bin_date[window_date]))
            totals = sum(avg_sunrise_bin_date[window_date])
            sum_sunrise_bin_date[window_date] = totals
            elements = len(avg_sunrise_bin_date[window_date])
            active_sunrise_bin_date[window_date] = avg_sunrise_bin_date[window_date]
            averages = totals / elements
            avg_sunrise_bin_date[window_date] = averages
            # print(start_date, date_of_end, avg_sunrise_bin_date[window_date])
        else:
            avg_sunrise_bin_date[window_date] = []

    # After the calculation, we can save the results to a file
    i = 0
    window_csv_header = ["N_day", "date", "sunrise", "bin_1", "bin_2", "delta2_1", "suma", "active", "avg_2_1"]
    window_csv_body = []
    days = 1943 # fixing the day number since 2000, so far rigid - this can be refined.
    # This way we have the days in the file day by day. This number is needed for the first value - then it sets itself.
    for window_date in sunrise_bin_date:
        days_old = days
        days = int(days_from_2000(window_date))
        elements_n = sunrise_bin_date[window_date]
        time_bin2 = elements_n[analysed_bin]  # np 2005-01-03 09:45:00
        time_bin1 = elements_n[analysed_bin - 1]  # np 2005-01-03 09:30:00
        if len(window_list[time_bin1]) > 0 and len(window_list[time_bin2]) > 0:
            if days - days_old == 1:
                bin_2 = window_list[time_bin2][0]
                bin_1 = window_list[time_bin1][0]
                delta2_1 = round(bin_2 - bin_1, 3)
                avg_2_1 = avg_sunrise_bin_date[window_date]
                if str(avg_2_1) != "[]":
                    suma = sum_sunrise_bin_date[window_date]
                    active = active_sunrise_bin_date[window_date]
                    info = {"N_day": days, "date": window_date, "sunrise": sunrise_dates[window_date],
                            "bin_1": bin_1, "bin_2": bin_2, "delta2_1": delta2_1, "suma": suma,
                            "active": active, "avg_2_1": avg_2_1}
                    window_csv_body.append(info)
                days_old = days

        # if you want to add empty lines to the csv file then uncomment the elif.
        # Without this - if there is a break in work for several days we will not see it in the file quickly
        # with a large number of lines.
        # elif 7210 > days > 1943:  # jesli chcemy puste linie d
        #     n = days - days_old
        #     print(window_date, days, days_old, n)
        #     for i in range(n):
        #         info = {"N_day": days + i, "data": "", "sunrise": "",
        #                 "bin_1": "", "bin_2": "", "delta2_1": "", "avg_2_1": ""}
        #         window_csv_body.append(info)
        i += 1

    avg_window_device_path2 = main_path2 + "csv/"
    csv_path = avg_window_device_path2 + str(analysed_bin) + "_new_control_bin_window_" + str(n_days) + "_days.csv"
    os.makedirs(avg_window_device_path2, exist_ok=True)

    with open(csv_path, "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=window_csv_header)
        writer.writeheader()
        writer.writerows(window_csv_body)

    # the stage of creating plots for a single bin N after sunrise. Theoretically, you can do it
    # without loading from the file.

    avg_window_device_path3 = main_path2 + "png/"
    os.makedirs(avg_window_device_path3, exist_ok=True)
    # reading data from csv using pandas library
    # decimal = a character separating the integer from the rest,
    # e.g. In CSV, Excel, the separator is "comma", in python it is "period", e.g 1.31 -> decimal = "."
    df = pd.read_csv(csv_path, decimal=".")
    x_value, y_value = 'N_day', 'avg_2_1' # what should be on the x-axis and what should be on the y-axis in the graph
    save_path = avg_window_device_path3 + str(analysed_bin) + "_bin_window_" + str(n_days) + "_days_" + str(
        int(shift / 60)) + "_shift.png"
    title = "n_days: %s; shift: %s H; bin_id: %s; numbering starts at sunrise." % (
        n_days, round(shift / 3600, 2), analysed_bin)
    create_plot(x_value, y_value, df, save_path, title)


def scater_analyze_window(shift, window_list, sunrise_bin_date, n_days=100):
    """
    The function responsible for the entire analysis of counting averages from n_days for the difference of the
    detection increment for the selected range of numbers for "analysed_bin" after sunrise. This function is similar
    to analyze_window, except that instead of one bin we will do, for example, for the first 50 bins after sunrise.
    The difference is also in the appearance of the graph that will be created after the calculations.
    :param shift: the size of a single window specified in seconds. E.g. 15 minutes is 900 seconds - then shift = 900
    :param window_list: a dictionary with all windows in the range from begin_date to end_date.
            A single window contains counts /m2/second e.g. window_list["2020-07-10 09:00:00"] = [178.39].
    :param sunrise_bin_date: sunrise dictionary with all the bins (individual windows) belonging to a given day
            between one sunrise and the other
    :param n_days: the number of days for which we calculate the average for each bin.
    :return: It saves the results to a csv file and the graph as a png
    """
    window_csv_header2 = ["bin", "value"]
    scater_plot_raw_data = {}
    window_csv_body2 = []

    diff_sunrise_bin_date = {}  # For a given analysed_bin we calculate the bin1-bin0 differences

    # we set the number of bins below, it can be set manually, or edited to specify the range when running the function
    for i in range(1, 30):
        for window_date in sunrise_bin_date:
            if len(sunrise_bin_date[window_date]) > i:
                time_bin1 = sunrise_bin_date[window_date][i]  # i.e 2005-01-03 09:30:00
                time_bin0 = sunrise_bin_date[window_date][i - 1]    # i.e 2005-01-03 09:15:00
                if len(window_list[time_bin1]) > 0 and len(window_list[time_bin0]) > 0:
                    # A single element in the window_list dictionary is a list, so even if it's a one-element list
                    # we have to refer to it by its position in the list  - the first element is 0
                    bin_1 = window_list[time_bin1][0]  # i.e 188.954
                    bin_0 = window_list[time_bin0][0]  # i.e 188.954
                    diff_detects = round(bin_1 - bin_0, 3)
                    diff_sunrise_bin_date[window_date] = diff_detects

        # Once we have calculated the differences for our bin for all dates,
        # we can count the average of the "n_days" for each date

        avg_sunrise_bin_date = {}  # average of variances of n_day
        for window_date in sunrise_bin_date:
            avg_sunrise_bin_date[window_date] = []
            date_of_end = datetime.strptime(window_date, "%Y-%m-%d").date()
            start_date = (date_of_end - timedelta(days=n_days - 1))
            # timedelta(days=n_days - 1) - 1 because it does not take into account the end date "today"

            # first avg_sunrise_bin_date will be a list of differences from n_days
            for single_date in date_range(start_date, date_of_end):
                current_date = single_date.strftime("%Y-%m-%d")
                if current_date in diff_sunrise_bin_date:
                    avg_sunrise_bin_date[window_date].append(diff_sunrise_bin_date[current_date])

            # Above if we had n_days = 100 then we added 99 results to avg_sunrise_bin_date[window_date],
            # now we will add the result for the end date
            if date_of_end.strftime("%Y-%m-%d") in diff_sunrise_bin_date:
                avg_sunrise_bin_date[window_date].append(diff_sunrise_bin_date[date_of_end.strftime("%Y-%m-%d")])

            #  Having already created a list of differences for a given "window_date"
            #  (number: n_days) we calculate the average
            # Currently, I have set that the result is analysed if there is a minimum of 2 out of n_days
            # (the condition refers to the beginning of the set, or the date after a long break - if it would exist)
            if len(avg_sunrise_bin_date[window_date]) > 2:
                totals = sum(avg_sunrise_bin_date[window_date])
                elements = len(avg_sunrise_bin_date[window_date])
                averages = totals / elements
                info = {"bin": i, "value": averages}
                window_csv_body2.append(info)

    # After the calculation, we can save the results to a file
    avg_window_device_path2 = main_path2 + "csv/"
    csv_path = avg_window_device_path2 + "_scater_plot_data.csv"

    with open(csv_path, "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=window_csv_header2)
        writer.writeheader()
        writer.writerows(window_csv_body2)

    avg_window_device_path3 = main_path2 + "png/"
    os.makedirs(avg_window_device_path3, exist_ok=True)

    # reading data from csv using pandas library
    # decimal = a character separating the integer from the rest,
    # e.g. In CSV, Excel, the separator is "comma", in python it is "period", e.g 1.31 -> decimal = "."
    df = pd.read_csv(csv_path, decimal=".")  # decimal = znak odzielajacy l.calkowite od reszty np 1.31 -> decimal = "."
    x_value, y_value = "bin", "value"
    save_path = avg_window_device_path3 + "scater_plot.png"
    title = "n_days: %s; shift: %s H; scater_plot; numbering starts at sunrise." % (n_days, round(shift / 3600, 2))
    create_plot(x_value, y_value, df, save_path, title, lines="no", opt=2)


def create_plot(x_value, y_value, df, png_save_path, title, lines="yes", opt=1):
    """
    Chart generation function based on received data
    :param x_value: name of the column to appear on the X axis - the name applies to elements in df
    :param y_value: name of the column to appear on the Y axis - the name applies to elements in df
    :param df: data set - must be properly divided into columns or elements
    :param png_save_path: chart save path
    :param title: chart title
    :param lines: whether vertical lines should appear, e.g. for January 1, 20XX
    :param opt: style option for individual elements in the chart
    :return: saving the chart to a file
    """

    if opt == 1:
        window_plot = df.plot.line(x=x_value, y=y_value, grid=True, title=title)
    else:
        # window_plot = df.plot.line(x='N_day', y='meant', xticks=xticks, grid=True, title=title)
        # window_plot = df.plot(x='N_day', y='meant', grid=True, title=title,style='.-')
        window_plot = df.plot(x=x_value, y=y_value, grid=True, title=title, style='.')

    if lines == "yes":
        # Part to be refined in the future, showing vertical lines
        window_plot.axhline(0, color="red", linestyle="-")  # pozioma linia
        window_plot.axvline(days_from_2000("2010-01-01"), color="yellow", linestyle="--")
        window_plot.axvline(days_from_2000("2015-01-01"), color="green", linestyle="--")
        window_plot.axvline(days_from_2000("2020-01-01"), color="yellow", linestyle="--")

    # saving the plot to a file
    fig = window_plot.get_figure()
    fig.savefig(png_save_path)

    # clearing the plot memory for safety (if it runs many times without clearing, data may overlap).
    plt.cla()  # Clear the current axes.
    plt.clf()  # Clear the current figure.
    plt.close(fig)  # Closes all the figure windows.


def main():
    read_csv()


if __name__ == '__main__':
    main()
