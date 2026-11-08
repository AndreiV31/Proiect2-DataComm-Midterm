import paho.mqtt.client as mqtt
import time
import json
import csv
import os

LOG_FILE = "mqtt_logs.csv"

# Initialize CSV log file with headers if it does not exist
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["msg_id", "client_id", "delay", "payload_bytes", "wire_bytes"])

def on_message(client, userdata, msg):
    recv_time = time.time()
    try:
        data = json.loads(msg.payload.decode('utf-8'))
        send_time = data.get("timestamp", recv_time)
        msg_id = data.get("msg_id", 0)
        client_id = data.get("client_id", "unknown")
        
        # Calculate End-to-End Delay in milliseconds
        delay_ms = round((recv_time - send_time) * 1000, 2)
        payload_len = len(msg.payload)
        
        # Account for L2/L3/L4 headers (Ethernet + IP + TCP) + MQTT Fixed/Variable Header + PUBACK
        wire_len = payload_len + 52 
        
        print(f"[RECV] Client: {client_id} | Msg ID: {msg_id} | Delay: {delay_ms} ms | Wire: {wire_len} B")
        
        with open(LOG_FILE, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([msg_id, client_id, delay_ms, payload_len, wire_len])
            
    except Exception as e:
        print(f"[ERROR] Failed to process message: {e}")

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="telemetry_consumer")
    client.on_message = on_message
    
    broker_ip = "10.0.0.254"
    print(f"Connecting to broker at {broker_ip}:1883...")
    client.connect(broker_ip, 1883, 60)
    client.subscribe("iot/telemetry", qos=1)
    
    print("Consumer started. Listening for incoming telemetry packets...")
    client.loop_forever()

if __name__ == '__main__':
    main()
