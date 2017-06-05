"""
Script to convert Excel file from the Goodwe EzExplorer exported format
into CSV-style output suitable for pvoutput.org
"""

from pprint import PrettyPrinter
import xlrd

FILENAME = "data/14600SSU12A00118_201703.xls"
EXCEL_FIELD_DATETIME = 0
EXCEL_FIELD_POWERNOW = 6
EXCEL_FIELD_ENERGY = 10
ROW_DATE = 0
ROW_OUTPUT = 1
ROW_POWER = 2
ROW_TIME = 3

PP = PrettyPrinter(indent=4)


def main():
    """Convert Goodwe Excel file to CSV format for pvoutput.org."""
    data = get_file_data(FILENAME)
    day_data = reduce_data_to_days(data)
    print_for_pvoutput(day_data)


def get_file_data(filename=FILENAME):
    """Extract all data from file into a list, converting formats."""
    workbook = xlrd.open_workbook(filename)
    sheet = workbook.sheet_by_index(0)
    data = []
    for i in range(1, sheet.nrows):
        row_values = sheet.row_values(i)
        date, time = row_values[EXCEL_FIELD_DATETIME].split()
        date = date.replace('.', '-')  # format date for pvoutput.org
        time = time[:-3]  # strip seconds
        row = [date, row_values[EXCEL_FIELD_ENERGY],
               row_values[EXCEL_FIELD_POWERNOW], time]
        data.append(row)
    return data


def reduce_data_to_days(data):
    """Reduce all data to list of one aggregate entry per day."""
    # data elements look like: [date, total_output, power, time]
    day_data = []
    current_date, total_output, peak_power, peak_time = data[0]
    for row in data[1:]:
        # check for change of date, update and store entry
        if row[ROW_DATE] != current_date:
            day_data.append(
                [current_date, total_output, peak_power, peak_time])
            current_date = row[ROW_DATE]
            peak_power = 0
        # update peak power and time
        if row[ROW_POWER] > peak_power:
            peak_power = row[ROW_POWER]
            peak_time = row[ROW_TIME]
        # save total_output so it's set for the previous record when adding
        total_output = row[ROW_OUTPUT]
    # add final row details
    day_data.append([current_date, total_output, peak_power, peak_time])
    return day_data


def print_for_pvoutput(day_data):
    """Print output from nested list in pvoutput.org CSV format."""
    # CSV sample data
    # 2011-05-27,13.836,,,2700,11:05
    # date(yyyy-mm-dd),output(kwh),,,peak_power(w),time(HH:mm)
    for single_day_data in day_data:
        print("{},{},,,{},{}".format(*single_day_data))


main()
