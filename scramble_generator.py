import random

moves_3 = ["R", "L", "U", "D", "F", "B"]
modifications = ["", "'", "2"]

def generate_scramble():
    scramble = ""
    prev_move = ""
    for _ in range(20):
        move = random.choice(moves_3)
        while move == prev_move or move == prev_move[::-1]:
            move = random.choice(moves_3)
        modifier = random.choice(modifications)
        scramble += move + modifier + " "
        prev_move = move
    return scramble.strip()