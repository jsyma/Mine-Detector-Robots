import grpc
import pika
import rovers_pb2
import rovers_pb2_grpc
import utils

# Establishing Connection with RabbitMQ Server
connectionMQ = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channelMQ = connectionMQ.channel()

# Declare the 'Demine-Queue' For Mine Defusal Requests 
channelMQ.queue_declare(queue='Demine-Queue', durable=True)

def main():
    rover_id = utils.get_rover_id()
    
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = rovers_pb2_grpc.RoverControlStub(channel)

        response = stub.GetMap(rovers_pb2.Empty())
        rover_map = [[val for val in row.mine_val] for row in response.map_row]
        commands = stub.GetCommands(rovers_pb2.RoverID(id=rover_id)).commands   

        current_direction = 'SOUTH'
        rover_row_pos = 0
        rover_col_pos = 0

        for move in commands:
            if move == 'L' or move == 'R':
                current_direction = utils.rotate_rover(current_direction, move)
            elif move == 'M':
                rover_row_pos, rover_col_pos = utils.move_rover(rover_row_pos, rover_col_pos, current_direction, rover_map)

                if rover_map[rover_row_pos][rover_col_pos]:
                    serial_number = stub.GetMineSerialNum(rovers_pb2.MineLocation(row=rover_row_pos, col=rover_col_pos)).serialNum
                    mine_defusal_message = f'{rover_row_pos} {rover_col_pos} {serial_number}'

                    # Send Mine Info Details to the 'Demine-Mine' Queue
                    channelMQ.basic_publish(
                        exchange='',
                        routing_key='Demine-Queue',
                        body=mine_defusal_message,
                        properties=pika.BasicProperties(
                            delivery_mode=pika.DeliveryMode.Persistent
                        )
                    )
                    print(f"[i] Sent Mine Info to Deminer: '{mine_defusal_message}'")
                    
    channelMQ.close()
    
if __name__ == "__main__":
    main()
