"""
Determine all combinations of a set using binary number (bit string) style combinations
"""
__author__ = 'Lindsay Ward'

subjects = ['CP3402', 'CP3046', 'CP3311', 'CP3003']
combinations = [subjects]
n = len(subjects)
# loop through all relevant bit strings (non-zero, non-all-1's)
for i in range(1, 2 ** n - 1):
    # print(bin(i))
    # print(str(bin(i)))
    bit_string = "{:0{}b}".format(i, n)
    if bit_string.count('1') > 1:
        # print(bit_string)
        combo = []
        for j, char in enumerate(bit_string):
            if char == '1':
                combo.append(subjects[j])
        combinations.append(combo)

print(len(combinations), combinations)
