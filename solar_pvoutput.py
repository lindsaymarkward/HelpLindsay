"""
Script to convert Excel file from the Goodwe EzExplorer exported format
into a CSV file suitable for pvoutput.org
"""

import openpyxl
from pprint import PrettyPrinter

ROW_CURRENT_DATE = 0
ROW_OUTPUT = 1
ROW_POWER = 2
ROW_TIME = 3

EXCEL_FIELD_DATETIME = 0
EXCEL_FIELD_POWERNOW = 6
EXCEL_FIELD_ENERGY = 10

pp = PrettyPrinter(indent=4)


def main():
    # data = get_file_data("data/Solar_201703.xlsx")
    # data = [['2017/03/01', 0, 0, '06:12'],
    #         ['2017/03/01', 0, 137, '07:09'],
    #         ['2017/03/01', 0.2, 281, '08:09'],
    #         ['2017/03/01', 1, 1321, '09:09'],
    #         ['2017/03/01', 2.7, 683, '10:09'],
    #         ['2017/03/01', 5.3, 3390, '11:09'],
    #         ['2017/03/01', 8.7, 3798, '12:09'],
    #         ['2017/03/01', 12.5, 3084, '13:09'],
    #         ['2017/03/01', 16.2, 4069, '14:09'],
    #         ['2017/03/01', 19.7, 3822, '15:09'],
    #         ['2017/03/01', 22.9, 2282, '16:09'],
    #         ['2017/03/01', 25.5, 2171, '17:09'],
    #         ['2017/03/01', 27, 676, '18:09'],
    #         ['2017/03/02', 0, 55, '06:33'],
    #         ['2017/03/02', 0.2, 555, '07:33'],
    #         ['2017/03/02', 0.7, 902, '08:33'],
    #         ['2017/03/02', 2.2, 2609, '09:33'],
    #         ['2017/03/02', 4.2, 777, '10:33'],
    #         ['2017/03/02', 6.5, 3852, '11:33'],
    #         ['2017/03/02', 9.4, 1199, '12:33'],
    #         ['2017/03/02', 12.1, 4111, '13:33'],
    #         ['2017/03/02', 15.2, 4380, '14:33'],
    #         ['2017/03/02', 17, 769, '15:33'],
    #         ['2017/03/02', 17.6, 858, '16:33'],
    #         ['2017/03/02', 18.3, 1192, '17:33'],
    #         ['2017/03/02', 18.5, 46, '18:33'],
    #         ['2017/03/03', 0, 62, '06:51'],
    #         ['2017/03/03', 0.3, 606, '07:51'],
    #         ['2017/03/03', 1.1, 868, '08:51'],
    #         ['2017/03/03', 2.2, 1280, '09:51'],
    #         ['2017/03/03', 3.3, 428, '10:51'],
    #         ['2017/03/03', 4.2, 1452, '11:51'],
    #         ['2017/03/03', 6.5, 3600, '12:51'],
    #         ['2017/03/03', 8.1, 894, '13:51'],
    #         ['2017/03/03', 8.9, 791, '14:51'],
    #         ['2017/03/03', 10.1, 672, '16:09'],
    #         ['2017/03/03', 10.4, 17, '17:57'],
    #         ['2017/03/04', 0, 45, '06:45'],
    #         ['2017/03/04', 0.1, 536, '07:45'],
    #         ['2017/03/04', 0.9, 1194, '08:45'],
    #         ['2017/03/04', 1.9, 1180, '09:45'],
    #         ['2017/03/04', 2.7, 1235, '10:45'],
    #         ['2017/03/04', 5.2, 4383, '11:45'],
    #         ['2017/03/04', 7.4, 1924, '12:45'],
    #         ['2017/03/04', 9.6, 3910, '13:45'],
    #         ['2017/03/04', 13, 2206, '14:45'],
    #         ['2017/03/04', 16.1, 2702, '15:45'],
    #         ['2017/03/04', 17.5, 750, '16:45'],
    #         ['2017/03/04', 18, 335, '17:45']]
    # pp.pprint(data)
    # day_data = reduce_data_to_days(data)
    day_data = [['2017/03/01', 27.2, 4667, '13:51'],
                ['2017/03/02', 18.5, 5053, '12:39'],
                ['2017/03/03', 10.4, 4043, '13:00'],
                ['2017/03/04', 18.1, 5037, '13:42']]
    pp.pprint(day_data)


def get_file_data(filename='solar.xlsx'):
    """Extract relevant data from file, converting formats."""
    workbook = openpyxl.load_workbook(filename)
    sheet = workbook.active
    data = []
    for i in range(1, sheet.max_row - 1):
        # for i in range(1, 3):
        # convert cells to text in those cells (.value)
        cell_text = [cell.value for cell in sheet.rows[i]]
        date, time = cell_text[EXCEL_FIELD_DATETIME].split()
        date = date.replace('.', '/')
        time = time[:-3]
        row = [date, cell_text[EXCEL_FIELD_ENERGY],
               cell_text[EXCEL_FIELD_POWERNOW], time]
        data.append(row)
    return data


def reduce_data_to_days(data):
    """Reduce list of all data elements to list of one valid entry per day."""
    # data elements look like: [date, time, output]
    # CSV sample data
    # date,output(kwh),,,peak_power(w),time
    # 2011-05-27,13.836,,,2700,11:05
    day_data = []
    current_date, max_output, peak_power, peak_time = data[0]
    # print(current_date, max_output, peak_power, peak_time)
    for row in data[1:]:
        # check for change of date, update and store entry
        if row[ROW_CURRENT_DATE] != current_date:
            day_data.append([current_date, max_output, peak_power, peak_time])
            current_date = row[ROW_CURRENT_DATE]
            peak_power = 0

        if row[ROW_POWER] > peak_power:
            peak_power = row[ROW_POWER]
            peak_time = row[ROW_TIME]

        # save max_output so it's for the previous record when adding
        max_output = row[ROW_OUTPUT]
    # add final row details
    day_data.append([current_date, max_output, peak_power, peak_time])
    return day_data


main()
