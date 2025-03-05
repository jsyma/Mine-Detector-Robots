from hashlib import sha256

def get_location_of_mines(map, map_info):
    '''
    Extracts the locations of mines from the map.

    Args:
        map (list): A 2D list of the map, with each cell being either '0' or '1'.    
        map_info (list): A list containing the dimensions of the map [rows, columns].

    Returns:
        list: A list of tuples representing (row, col) position of a mine. 
    '''
    mine_location_list = []
    rows = (int)(map_info[0])
    cols = (int)(map_info[1])
    for row in range(rows):
        for col in range(cols):
            if map[row][col] == 1:
                mine_location_list.append((row, col))
    return mine_location_list

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
    print(f'\nMine Serial Mapping: {mine_serial_mapping}\n')
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
            - hash_value (str): The SHA-256 hash value of the serial number and PIN, starts with '00000'. 
    '''
    pin = 0 
    while True:
        temporary_mine_key = f"{serial_number}{pin}".encode()
        hash_value = sha256(temporary_mine_key).hexdigest()
        if hash_value.startswith("00000"):
            return pin, hash_value
        pin += 1