import json
import random
from hashlib import sha256
import requests

def get_rover_commands(rover_id):
    '''
    Gets the rover commands from the provided api.

    Args: 
        rover_count (int): The Rover ID.
    
    Returns: 
        list: A list of Rover commands for the specified Rover ID.
    '''
    api = 'https://coe892.reev.dev/lab1/rover'
    r = requests.get(f'{api}/{rover_id}')
    if r.ok:
        content = json.loads(r.content)
        return content['data']['moves']
    else:
        raise Exception(f"Failed to fetch API for rover {rover_id}")

def generate_random_map(rows, cols, mine_percentage):
    '''
    Generates a random map with the amount of mines placed as a percentage of total cells.

    Args:
        rows (int): The number of rows for the map.
        cols (int): The number of columns for the map.
        mine_percentage (float): The percentage of mine cells.

    Returns:
        tuple: A tuple containing:
            - [rows, cols] (tuple): The dimensions of the map.
            - map (list): A 2D list of the map, with cells being '0' (empty) or '1' (mine).
    '''
    total_cells = rows * cols
    mine_count = int(total_cells * mine_percentage)
    
    map = [[0] * cols for _ in range(rows)]
    
    mine_positions = set()
    while len(mine_positions) < mine_count:
        pos = (random.randint(0, rows - 1), random.randint(0, cols - 1))
        mine_positions.add(pos)

    for row, col in mine_positions:
        map[row][col] = 1

    return [rows, cols], map    

def rotate_rover(current_direction, move) -> str:
    '''
    Rotate the rover's direction based on the given movement command using a predefined sequence of directions.

    Args:
        current_direction (str): The current direction of the rover. Valid options: "NORTH", "EAST", "SOUTH", "WEST".
        move (str): The rotation command. Valid options: "L", "R".

    Returns:
        str: The new direction of the rover after the rotation. 
    '''
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

def create_mine_serial_mapping(mine_file_name, map):
    '''
    Creates a dictionary mapping mine coordinates to their corresponding serial numbers. 

    Args:
        mine_file_name (str): The name of the file containing the list of mine serial numbers.
        map (list): A 2D list representing the map, with each cell being either 0 (empty) or 1 (mine).
        
    Returns:
        dict: A dictionary where the keys are tuples representing mine coordinates (row, col),
              and the values are the corresponding serial numbers for those mines.
    '''
    with open(mine_file_name, "r") as f:
        serial_numbers = f.read().splitlines()

    mine_serial_mapping = {}
    index = 0 

    for row in range(len(map)):
        for col in range(len(map[row])):
            if map[row][col] == 1:
                if index < len(serial_numbers):
                    mine_serial_mapping[(row, col)] = serial_numbers[index]
                    index += 1
                else:
                    print(f"Not enough serial numbers in mines.txt")
    return mine_serial_mapping

def disarm_mine(serial_number):
    '''
    Disarms a mine based on its serial number by iterating through potential PIN values and hashing the combination of serial 
    number and PIN until a hash is found that starts with '00000'. Simulates finding a correct PIN to disarm the mine. 

    Args: 
        serial_number (str): The serial number of the mine to be disarmed.
    
    Returns: 
        tuple: A tuple containing:
            - pin (int): The correct PIN to disarm the mine.
            - hash_value (str): The SHA-256 hash value of the serial number and PIN, starts with '000000'. 
    '''
    pin = 0 
    while True:
        temporary_mine_key = f"{serial_number}{pin}".encode()
        hash_value = sha256(temporary_mine_key).hexdigest()
        if hash_value.startswith("000000"):
            return pin, hash_value
        pin += 1

def get_rover_id():
    '''
    Prompt user to enter a Rover ID between 1 and 10.

    Returns:
        str: The valid Rover ID as an string. 
    '''
    while True:
        try:
            rover_id = input('Enter Rover ID: ')
            if ((int(rover_id) > 10) or (int(rover_id) < 1)):
                raise ValueError
            break
        except ValueError:
            rover_id = input('Please Enter a Valid Rover ID (1-10): ')
    return rover_id

def get_deminer_id():
    '''
    Prompt the user to enter a Deminer ID, either 1 or 2.

    Returns: 
        int: The valid Deminer ID as an integer.
    '''
    while True:
        try:
            deminer_id = int(input('Enter Deminer ID: '))
            if deminer_id not in [1, 2]:
                raise ValueError
            break
        except ValueError:
            deminer_id = int(input('Please Enter a Valid Deminer ID (1-2): '))
    return deminer_id