from random import sample

seats = []
for letter in "ABCDEF":
    for i in range(1, 51):
        seats.append("{}{}".format(letter, i))

for letter in "ABCDEFGHIJKLMNOPQR":
    for i in range(59, 67):
        seats.append("{}{}".format(letter, i))
    for i in range(70, 86):
        seats.append("{}{}".format(letter, i))
    for i in range(90, 106):
        seats.append("{}{}".format(letter, i))
    for i in range(109, 117):
        seats.append("{}{}".format(letter, i))

# rows S and T
for i in range(59, 67):
    seats.append("{}{}".format('S', i))
for i in range(70, 82):
    seats.append("{}{}".format('S', i))
for i in range(94, 106):
    seats.append("{}{}".format('S', i))
for i in range(109, 117):
    seats.append("{}{}".format('S', i))
for i in range(59, 82):
    seats.append("{}{}".format('T', i))
for i in range(94, 116):
    seats.append("{}{}".format('T', i))

# These seats shouldn't win tickets
seats.remove('G64')
seats.remove('G65')
seats.remove('G66')

print(len(seats))
# print(seats)
print()
chosen_seats = sample(seats, 15)
chosen_seats.sort()
print(chosen_seats)
