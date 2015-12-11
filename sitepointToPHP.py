import random
__author__ = 'Lindsay Ward'

f = open("tsw15-2.csv")

lines = f.readlines()
chosen = random.sample(lines, 2)

for choice in chosen:
    parts = choice.split(",")
    print(parts[0], parts[1], "-", parts[2].strip())

# for line in f:
#     parts = line.split(",")
    # print('"{}" => ["{}", "{}", "{}"], '.format(parts[0].lower(), parts[1], parts[2], parts[3].strip()))

    # "david@davidjb.com" => ["David", "Beitey", "https://www.sitepoint.com/premium/voucher/3be11c6309b2bb04ffc34992"],
    # "sstanden21@gmail.com" => ["Sarah", "Standen", "https://www.sitepoint.com/premium/voucher/2fad8003c571b3b83b0dfbf8"]
