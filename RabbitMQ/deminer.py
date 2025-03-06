import pika
import utils

def main():
    deminer_id = utils.get_deminer_id()

    # Establishing Connection with RabbitMQ Server
    connectionMQ = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channelMQ = connectionMQ.channel()

    channelMQ.queue_declare(queue='Demine-Queue', durable=True)
    print(f"[*] Deminer {deminer_id} Waiting for Mine Defusal Requests...")

    def callback(ch, method, properties, body: bytearray):
        mine_info = body.decode()
        row, col, serial_num = mine_info.split()
        print(f"[i] Received Mine Defusal Request: '{mine_info}'")

        # Disarm Mine and Generate PIN
        pin = utils.disarm_mine(serial_num)
        print(f"[+] Finished Disarming Mine. PIN: {pin}")    

        ch.basic_ack(delivery_tag=method.delivery_tag)    

        defused_mine_channel = connectionMQ.channel()
        defused_mine_channel.queue_declare(queue='Defused-Mines', durable=True)
        defused_mine_message = f"Mine Defused at ({row}, {col}) with PIN: {pin}"

        # Send Defused Mine Details to the 'Defused-Mine' Queue
        defused_mine_channel.basic_publish(
            exchange='',
            routing_key='Defused-Mines',
            body=defused_mine_message,
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent
            )
        )
        print(f"[i] Sent Defused Mine Confirmation: {defused_mine_message}")
        defused_mine_channel.close()

    channelMQ.basic_qos(prefetch_count=1)
    channelMQ.basic_consume(queue='Demine-Queue', on_message_callback=callback)
    channelMQ.start_consuming()

if __name__ == "__main__":
    main()
