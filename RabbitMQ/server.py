import sys
import grpc
import threading
from concurrent import futures
import pika
import utils
import rovers_pb2
import rovers_pb2_grpc

# Establishing Connection with RabbitMQ Server
connectionMQ = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channelMQ = connectionMQ.channel()

# Declare the 'Defused-Mines' For Mine Defusal Confirmations
channelMQ.queue_declare(queue='Defused-Mines', durable=True)
print("[*] Waiting for Mine Defusal Confirmations...")

def callback(ch, method, properties, body: bytearray):
    print(f"[+] {body.decode()}")

channelMQ.basic_consume(queue='Defused-Mines', on_message_callback=callback, auto_ack=True)

class RoverControlServicer(rovers_pb2_grpc.RoverControlServicer):

    def GetMap(self, request, context):
        map_info, map = utils.generate_random_map(10, 10, 0.1)
        map_info_response = rovers_pb2.MapInfo()
        map_info_response.row = int(map_info[0])
        map_info_response.col = int(map_info[1])

        for row in map:
            map_row = map_info_response.map_row.add()
            map_row.mine_val.extend(row)

        self.mine_list = utils.create_mine_serial_mapping("mines.txt", map)
        return map_info_response

    def GetCommands(self, request, context):
        return rovers_pb2.Commands(commands=utils.get_rover_commands(request.id))

    def GetMineSerialNum(self, request, context):
        serial_num = self.mine_list.get((request.row, request.col))
        if serial_num:
            return rovers_pb2.SerialNum(serialNum=serial_num)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rovers_pb2_grpc.add_RoverControlServicer_to_server(RoverControlServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    try:
        threading.Thread(target=serve).start()
        channelMQ.start_consuming()
    except KeyboardInterrupt:
        print("[X] Server interrupted.")
        sys.exit(0)
