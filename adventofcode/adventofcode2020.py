"""
Advent of Code 2020
https://adventofcode.com/2020/
"""
import numpy
import re

REQUIRED_KEYS = ['byr', 'iyr', 'eyr', 'hgt', 'hcl', 'ecl', 'pid']
VALID_EYE_COLOURS = ['amb', 'blu', 'brn', 'gry', 'grn', 'hzl', 'oth']
NUMBER_REQUIRED = len(REQUIRED_KEYS)


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
    number_of_valid = 0
    passports = []  # key, value pairs for each passport
    file_in = open("day4.txt")
    string = ""
    for line in file_in:
        if line == "\n":  # blank line is delimiter
            parts = string.strip().split(' ')
            pairs = [part.split(':') for part in parts]
            passports.append(pairs)
            string = ""
        else:
            string += line.replace("\n", " ")
    file_in.close()

    for passport in passports:
        if is_passport_valid(passport):
            number_of_valid += 1
        print()
    print(number_of_valid)


def is_passport_valid(passport):
    keys = [pair[0] for pair in passport]
    count = sum((key in REQUIRED_KEYS for key in keys))
    if count != NUMBER_REQUIRED:
        return False
    for pair in passport:
        is_valid = is_data_valid(pair[0], pair[1])
        print(is_valid)
        if not is_valid:
            return False  # something is wrong with this data
    print("Passport is valid")
    return True


def is_data_valid(key, value):
    print(f"Validating {key}: {value}", end=" ")
    # process each key, value
    if key == 'byr':
        if not is_number_valid(value, 1920, 2002):
            return False
    elif key == 'iyr':
        if not is_number_valid(value, 2010, 2020):
            return False
    elif key == 'eyr':
        if not is_number_valid(value, 2020, 2030):
            return False
    elif key == 'hgt':
        height = value[:-2]
        unit = value[-2:]
        if unit == 'cm':
            if not is_number_valid(height, 150, 193):
                return False
        elif unit == 'in':
            if not is_number_valid(height, 59, 76):
                return False
        else:
            return False
    elif key == 'hcl':
        if not re.search('^#(?:[0-9a-fA-F]{3}){1,2}$', value):
            return False
    elif key == 'ecl':
        if value not in VALID_EYE_COLOURS:
            return False
    elif key == 'pid':
        if not re.search('[0-9]{9}', value):
            return False
    return True


def is_number_valid(string, minimum, maximum):
    try:
        number = int(string)
        return minimum <= number <= maximum
    except ValueError:
        return False


day_4()
