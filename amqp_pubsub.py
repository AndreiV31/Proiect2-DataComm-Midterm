import pika
import time
import json
import csv
import os
import sys

LOG_FILE = "amqp_logs.csv"
BROKER_IP = "10.0.0.254"
QUEUE_NAME = "iot_telemetry"
TARGET_PAYLOAD_SIZE = 128

def start_consumer():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode='w', newline='') as f:
            csv.writer(f).writerow(["msg_id", "client_id", "delay", "payload_bytes", "wire_bytes"])

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=BROKER_IP))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    def callback(ch, method, properties, body):
        recv_time = time.time()
        data = json.loads(body.decode('utf-8'))
        delay_ms = round((recv_time - data["timestamp"]) * 1000, 2)
        payload_len = len(body)
        # L2/L3/L4 headers + AMQP 0-9-1 Frame Header + Basic.Ack overhead
        wire_len = payload_len + 102
        
        with open(LOG_FILE, mode='a', newline='') as f:
            csv.writer(f).writerow([data["msg_id"], data["client_id"], delay_ms, payload_len, wire_len])
            
        print(f"[AMQP RECV] {data['client_id']} | Msg #{data['msg_id']} | Delay: {delay_ms} ms")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
    print("AMQP Consumer listening...")
    channel.start_consuming()

def start_publisher(client_id="client_1"):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=BROKER_IP))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.confirm_delivery()  # Enable Publisher Confirms

    for msg_id in range(1, 101):
        base_data = {"msg_id": msg_id, "client_id": client_id, "timestamp": round(time.time(), 4), "padding": ""}
        base_data["padding"] = "X" * max(0, TARGET_PAYLOAD_SIZE - len(json.dumps(base_data)))
        payload = json.dumps(base_data)
        
        channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=payload)
        print(f"[AMQP SENT] {client_id} | Msg #{msg_id} | 128 B")
        time.sleep(1.0)
    connection.close()

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "consumer"
    if mode == "publisher":
        start_publisher()
    else:
        start_consumer()
