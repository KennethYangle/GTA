from itertools import permutations

per = permutations([i for i in range(4)], 4)
for p in per:
    print(p)