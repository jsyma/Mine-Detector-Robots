import grpc
from concurrent import futures
import time
from map import get_rover_commands, generate_random_map
from mines import create_mine_serial_mapping

import rovers_pb2
import rovers_pb2_grpc

class RoverControlServicer(rovers_pb2_grpc.RoverControlServicer):
   
    def GetMap(self, request, context):
        map_info, map = generate_random_map(10, 10, 0.1)
        map_info_response = rovers_pb2.MapInfo()
        map_info_response.row = int(map_info[0])
        map_info_response.col = int(map_info[1])
        
        for row in map:
            map_row = map_info_response.map_row.add()
            map_row.mine_val.extend(row)

        self.mine_list = create_mine_serial_mapping("mines.txt", map)
        return map_info_response

    def GetCommands(self, request, context):
        return rovers_pb2.Commands(commands=get_rover_commands(request.id))

    def GetMineSerialNum(self, request, context):
        serial_num = self.mine_list.get((request.row, request.col))
    
        if serial_num:
            return rovers_pb2.SerialNum(serialNum=serial_num)

    def NotifyServer(self, request, context):
        print(request._message)
        return rovers_pb2.Empty()

    def MinePin(self, request, context):
        print(f'Mine Disarmed at row: {request.row}, col: {request.col}')
        print(f'Pin Received: {request.pin_num} for Rover {request.rover_id}\n')
        return rovers_pb2.Empty()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rovers_pb2_grpc.add_RoverControlServicer_to_server(RoverControlServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server is running on port 50051...")
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
