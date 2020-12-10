"""
Advent of Code 2020
https://adventofcode.com/2020/
"""
import copy
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


def determine_seat_id(boarding_pass):
    low = 0
    high = 127
    for character in boarding_pass[:7]:
        gap = high - low + 1
        if character == 'F':
            high -= gap // 2
        else:
            low += gap // 2
        # print(character, low, high)
    row = low
    # print(f"Row: {row}")

    low = 0
    high = 7
    for character in boarding_pass[-3:]:
        gap = high - low + 1
        if character == 'L':
            high -= gap // 2
        else:
            low += gap // 2
    column = low
    # print(f"Column: {column}")
    seat_id = row * 8 + column
    return seat_id


def day_5():
    # s = 'FBFBBFFRLR'
    # print(determine_seat_id(s))
    file_in = open('day5.txt')
    boarding_passes = [line.strip() for line in file_in.readlines()]
    file_in.close()
    seats = []
    for boarding_pass in boarding_passes:
        seat_id = determine_seat_id(boarding_pass)
        seats.append(seat_id)
    seats.sort()

    # print("\n".join((str(seat) for seat in seats)))
    for i, seat in enumerate(seats):
        if seats[i + 1] - seat > 1:
            print(seat + 1)
            break


def day_6():
    total = 0
    file_in = open("day6.txt")
    group = []
    for line in file_in:
        if line == "\n":  # blank line is delimiter
            # print(f"Counting: {group}")
            if len(group) == 1:
                total += len(group[0])
            else:
                for char in group[0]:
                    count = 0
                    for answers in group[1:]:
                        if char in answers:
                            count += 1
                    if count == len(group[1:]):
                        total += 1
            group = []
        else:
            values = list(line.strip())
            group.append(values)
    file_in.close()

    print(total)


def determine_number_of_bags(colour, rules):
    # print("counting", colour)
    contents = rules[colour]
    if not contents:
        # print(f"Base case {colour}")
        return 1
    count = 0
    for content in contents:
        number = content[0]
        colour = content[1]
        # print(number, colour)
        count += (number * determine_number_of_bags(colour, rules))
    return count + 1


def day_7():
    rules = {}
    my_colour = 'shiny gold'
    file_in = open("day7.txt")
    for line in file_in:
        bags = line.strip('.\n').split(' bags contain ')
        try:
            contents = [(int(bag[0]), bag[1:].strip('bags').strip()) for bag in bags[1].split(', ')]
        except ValueError:
            # "... contain no other bags
            contents = []
        rules[bags[0]] = contents
    file_in.close()

    count = determine_number_of_bags(my_colour, rules)
    # -1 since we don't include my actual bag
    print(count - 1)  # 8417 is too low; 11415 is too high; was 9569


def day_8():
    instructions = []
    file_in = open('day8.txt')
    for line in file_in:
        parts = line.split(' ')
        operation = parts[1][0]
        value = int(parts[1][1:])
        instruction = [parts[0], operation, value]
        instructions.append(instruction)
    file_in.close()
    number_of_instructions = len(instructions)
    is_solved = False
    index_to_try = 0
    while not is_solved:

        if index_to_try == number_of_instructions:
            print("Got to the end...")
            break
        print(index_to_try, instructions[index_to_try])
        # Interesting: slice or shallow copy mean changing the 2nd list does actually modify the first, even though they're different lists
        # instructions_to_try = instructions[:]
        # instructions_to_try = instructions.copy()
        instructions_to_try = copy.deepcopy(instructions)

        if instructions[index_to_try][0] == 'nop':
            instructions_to_try[index_to_try][0] = 'jmp'
        elif instructions[index_to_try][0] == 'jmp':
            instructions_to_try[index_to_try][0] = 'nop'
            # print(instructions == instructions_to_try, id(instructions), id(instructions_to_try))
            # input()
        else:
            index_to_try += 1
            continue

        i = 0
        accumulator = 0
        used_instructions = []
        while True:
            instruction = instructions_to_try[i]
            if i in used_instructions:
                # We have an infinite loop; try next one
                print("infinite")
                break
            used_instructions.append(i)
            if instruction[0] == 'acc':
                if instruction[1] == '+':
                    accumulator += instruction[2]
                else:
                    accumulator -= instruction[2]
                i += 1
            elif instruction[0] == 'jmp':
                if instruction[1] == '+':
                    i += instruction[2]
                else:
                    i -= instruction[2]
            else:  # nop
                i += 1

            if i == number_of_instructions:
                print(f"Found it :) {index_to_try}")
                print(accumulator)
                is_solved = True
                break
        index_to_try += 1


def is_number_ok(number, pre_numbers):
    for first_number in pre_numbers:
        for second_number in pre_numbers:
            if first_number == second_number:
                continue
            if first_number + second_number == number:
                print(f"{first_number} + {second_number} = {number}")
                return True
    return False


def day_9():
    # my_number = 127  # from part 1
    # file_in = open("day9test.txt")
    my_number = 88311122  # from part 1
    file_in = open("day9.txt")
    numbers = [int(line) for line in file_in]
    file_in.close()
    for i in range(len(numbers)):
        if numbers[i] > my_number:
            print("Done :(")
            return
        j = i + 1
        total = 0
        while total < my_number:
            j += 1
            total = sum(numbers[i:j])
            # print(i, j, total, numbers[i:j])
        if total == my_number:
            print("Found it :)")
            print(i, j, numbers[i:j])
            print(min(numbers[i:j]) + max(numbers[i:j]))
            return
        else:
            continue


def day_10():
    file_in = open("day10.txt")
    numbers = [int(line) for line in file_in]
    file_in.close()
    numbers.sort()
    differences = [numbers[i + 1] - numbers[i] for i in range(len(numbers) - 1)]
    number_of_1s = differences.count(1) + 1
    number_of_3s = differences.count(3) + 1
    print(len(numbers), len(differences), number_of_1s, number_of_3s)
    print(number_of_1s * number_of_3s)


day_10()
