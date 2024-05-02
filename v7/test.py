import random
import os

A_count = 0
B_count = 0
clear_terminal = lambda: os.system('cls')


def get_weight(A_count, B_count):
    count_dif = 1/(abs(A_count - B_count) + 2)
    A_weight = count_dif if A_count > B_count else 1 - count_dif
    B_weight = 1 - count_dif if A_count > B_count else count_dif

    return [A_weight, B_weight]

for i in range(100):
    clear_terminal()

    A_weight, B_weight = get_weight(A_count, B_count)

    print(f"A: {A_count}, B: {B_count} [counts]")
    print(f"A: {A_weight}, B: {B_weight} [weights]")
    

    rand_sound = random.choices(["A", "B"], weights=[A_weight, B_weight])[0]

    if rand_sound == "A":
        A_count += 1
    else:
        B_count += 1

    
    
    #input("Press Enter to continue...")

