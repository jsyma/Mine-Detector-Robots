import json
import random
from hashlib import sha256
import requests

def get_rover_commands(rover_id):
    api = 'https://coe892.reev.dev/lab1/rover'
    r = requests.get(f'{api}/{rover_id}')
    if r.ok:
        content = json.loads(r.content)
        commands = content['data']['moves']
        commands = content['data']['moves']
        return {"commands": ''.join(commands)}
    else:
        raise Exception(f"Failed to fetch API for rover {rover_id}")

def generate_new_map(row, col):
    map, mines = generate_random_map(row, col)
    if map[0][0] == 1:
        map[0][0] = 0
        for mine_info in mines:
            if mine_info[0] == 0 and mine_info[1] == 0:
                mines.remove(mine_info)
                break
    return map, mines

def generate_random_map(row, col):
    map = []
    mines = []
    serial_num_list = random.sample(range(1000, 10000), 9000)

    for i in range(row):
        curr_row = []
        for j in range(col):
            if random.randint(1, 10) < 3:
                mines.append([i, j, serial_num_list.pop()])
                curr_row.append(1)
            else:
                curr_row.append(0)
        map.append(curr_row)

    return map, mines 

def rotate_rover(current_direction, move) -> str:
    directions = ["NORTH", "EAST", "SOUTH", "WEST"]
    idx = directions.index(current_direction)
    
    if move == "L":
        return directions[(idx - 1) % 4]
    elif move == "R":
        return directions[(idx + 1) % 4]
    else:
        raise ValueError("Invalid move. Use 'L' for left or 'R' for right.")

def move_rover(rover_row_pos, rover_col_pos, current_direction, map):
    if current_direction == "SOUTH" and rover_row_pos < len(map) - 1:
        rover_row_pos += 1
    elif current_direction == "NORTH" and rover_row_pos > 0:
        rover_row_pos -= 1
    elif current_direction == "EAST" and rover_col_pos < len(map[0]) - 1:
        rover_col_pos += 1
    elif current_direction == "WEST" and rover_col_pos > 0:
        rover_col_pos -= 1
    return rover_row_pos, rover_col_pos

def disarm_mine(serial_number):
    pin = 0 
    while True:
        temporary_mine_key = f"{serial_number}{pin}".encode()
        hash_value = sha256(temporary_mine_key).hexdigest()
        if hash_value.startswith("00000"):
            return pin
        pin += 1