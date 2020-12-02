"""
Advent of Code 2020
https://adventofcode.com/2020/
"""


def day_1():
    file_in = open('data/adventofcode/expense_report.txt')
    values = [int(value) for value in file_in.readlines()]
    for value in values:
        for second_value in values:
            for third_value in values:
                if value + second_value + third_value == 2020:
                    print(value, second_value, third_value, value * second_value * third_value)
                    return
    file_in.close()


def day_2():
    file_in = open('data/adventofcode/day2.txt')
    number_of_valid_passwords = 0
    for line in file_in:
        parts = line.split()
        position_parts = parts[0].split('-')
        first_position = int(position_parts[0])
        second_position = int(position_parts[1])
        character = parts[1][0]
        password = parts[2]
        # count = password.count(character)
        is_first_position_ok = password[first_position - 1] == character
        is_second_position_ok = password[second_position - 1] == character
        count = is_first_position_ok + is_second_position_ok
        if count == 1:
            number_of_valid_passwords += 1
    file_in.close()
    print(number_of_valid_passwords)


day_2()
