"""
Advent of Code 2020
https://adventofcode.com/2020/
"""
import numpy


def day_1():
    file_in = open('expense_report.txt')
    values = [int(value) for value in file_in.readlines()]
    for value in values:
        for second_value in values:
            for third_value in values:
                if value + second_value + third_value == 2020:
                    print(value, second_value, third_value, value * second_value * third_value)
                    return
    file_in.close()


def day_2():
    file_in = open('day2.txt')
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


def day_3():
    slopes = ((1, 1), (3, 1), (5, 1), (7, 1), (1, 2))  # right, down
    results = []
    file_in = open('day3.txt')
    lines = file_in.readlines()[1:]  # skip first line
    file_in.close()
    lines = [list(line.strip()) for line in lines]

    for slope in slopes:
        number_of_trees = 0
        position = 0
        for i, line in enumerate(lines):
            if slope[1] == 2 and i % 2 == 0:  # not extensible, but avoid preoptimising :)
                continue  # skip a line due to slope of 2
            position += slope[0]
            while True:
                try:
                    if line[position] == '#':
                        number_of_trees += 1
                    break  # successful; no need to extend pattern
                except IndexError:
                    line += line
        # print(number_of_trees)
        results.append(number_of_trees)
    print(results)
    print(numpy.prod(results))


def day_4():
    required_keys = ['byr', 'iyr', 'eyr', 'hgt', 'hcl', 'ecl', 'pid']
    number_required = len(required_keys)
    number_of_valid = 0
    # strings = []
    file_in = open("day4.txt")
    string = ""
    for line in file_in:
        if line == "\n":  # blank line is delimiter
            # strings.append(string)
            parts = string.split(' ')
            keys = [part.split(':')[0] for part in parts]
            count = sum((key in required_keys for key in keys))
            if count == number_required:
                number_of_valid += 1
            string = ""
        else:
            string += line.replace("\n", " ")
    file_in.close()
    print(number_of_valid)


day_4()
