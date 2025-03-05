import os
import requests
import json
import random

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

def create_rover_path(rover_id, rover_map, output_folder):
    '''
    Writes the rover's path/updated map to a .txt file in the specified output_folder.

    Args: 
        rover_id (int): The over ID.
        rover_map (list): A 2D list representing the rover's path/map, with each cell being '0', '1' or '*'. 
        output_folder (str): The directory to output the path_{rover_id}.txt file.
    '''
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    file_name = os.path.join(output_folder, f'path_{rover_id}.txt')
    with open(file_name, 'w') as f:
        for row in rover_map:
            f.write(" ".join([str(cell) for cell in row]) + "\n")