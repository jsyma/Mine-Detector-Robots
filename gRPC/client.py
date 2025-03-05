import grpc
import rovers_pb2
import rovers_pb2_grpc
import sys

from map import create_rover_path
from mines import get_location_of_mines, disarm_mine

def main():
    if len(sys.argv) != 2:
        print("Usage: python client.py <rover_id>")
        sys.exit(1)

    rover_id = sys.argv[1]

    with grpc.insecure_channel('localhost:50051') as channel:
        stub = rovers_pb2_grpc.RoverControlStub(channel)
        
        # Fetching Map
        response = stub.GetMap(rovers_pb2.Empty())
        rover_map = [[val for val in row.mine_val] for row in response.map_row]

        map_row_size, map_col_size = response.row, response.col
        print("\nMap Data:")
        for map_row in rover_map:
            print(map_row) 
        
        # Fetching Commands 
        request = rovers_pb2.RoverID(id=rover_id)
        response = stub.GetCommands(request)
        rover_commands = response.commands
        print(f'\nRover {rover_id} commands: {rover_commands}\n')

        # Start of Command Execution
        request = rovers_pb2.BotMessage(_message=f'Starting execution of commands for Rover {rover_id}\n')
        response = stub.NotifyServer(request)
        updated_map = rover_movement(rover_id, rover_commands, [map_row_size, map_col_size], rover_map, stub)

        # Create Path File after Command Execution
        create_rover_path(rover_id, updated_map, 'output')

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

def rover_movement(rover_id, commands, map_info, map, stub):
    '''
    Simulates a rover's movement on the map based on a sequence of commands, 
    updating the map as the rover moves and handles interaction with mines. 

    Args:
        rover_id (int): The Rover ID.
        commands (list): A list of command sequences for the rover.
        map_info (list): A list containing the dimensions of the map [rows, columns].
        map (list): A 2D list of the map, with each cell being either '0' or '1'.
        stub: Used to communicate with the server for notifications and requests.
    
    Returns:
        list: The updated map after processing the rover's movement and interactions with mines.
    '''
    number_of_rows = int(map_info[0])
    number_of_cols = int(map_info[1]) - 1
    rover_row_pos = 0
    rover_col_pos = 0
    current_direction = "SOUTH"
    disarm = False
    mine_locations = get_location_of_mines(map, map_info)
    map[rover_row_pos][rover_col_pos] = "*"

    success = True 

    for move in commands:
        if move == 'L' or move == 'R':
            current_direction = rotate_rover(current_direction, move)
        elif move == 'M':
            update = False
            prev_row = rover_row_pos
            prev_col = rover_col_pos
            if current_direction == "SOUTH" and rover_row_pos + 1 < number_of_rows:
                rover_row_pos += 1
                update = True
            elif current_direction == "NORTH" and rover_row_pos - 1 >= 0:
                rover_row_pos -= 1
                update = True
            elif current_direction == "WEST" and rover_col_pos - 1 >= 0:
                rover_col_pos -= 1
                update = True
            elif current_direction == "EAST" and rover_col_pos + 1 <= number_of_cols:
                rover_col_pos += 1
                update = True
            if update: 
                if not disarm and ((prev_row, prev_col) in mine_locations):
                    map[prev_row][prev_col] = "X"
                    request = rovers_pb2.BotMessage(_message=f'Rover {rover_id} hit a mine at ({prev_row}, {prev_col})!')
                    response = stub.NotifyServer(request)
                    success = False
                    break
                disarm = False
                map[rover_row_pos][rover_col_pos] = "*"
        elif move == 'D':
            disarm = True
            if (rover_row_pos, rover_col_pos) in mine_locations:
                request = rovers_pb2.MineLocation(row = rover_row_pos, col = rover_col_pos)
                response = stub.GetMineSerialNum(request)
                pin = disarm_mine(response.serialNum)

                request = rovers_pb2.RoverInfo(
                        pin_num=str(pin),
                        rover_id=str(rover_id),
                        row=str(rover_row_pos),
                        col=str(rover_col_pos)
                    )        
                response = stub.MinePin(request) 

                # Ensure once mine is disarmed no need to disarm again
                mine_locations.remove((rover_row_pos, rover_col_pos))
                map[rover_row_pos][rover_col_pos] = "*"
    if success:
        request = rovers_pb2.BotMessage(_message=f'Rover {rover_id} has executed all the commands successfully.')
        response = stub.NotifyServer(request)
    else: 
        request = rovers_pb2.BotMessage(_message=f'Rover {rover_id} did not finish all the commands due to mine explosion.')
        response = stub.NotifyServer(request)

    return map

if __name__ == '__main__':
    main()
