import paho.mqtt.client as mqtt
import time
import json
import sys

# Default client ID if none is passed via command line arguments
CLIENT_ID = sys.argv[1] if len(sys.argv) > 1 else "client_1"
BROKER_IP = "10.0.0.254"
TOPIC = "iot/telemetry"
TARGET_PAYLOAD_SIZE = 128

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=CLIENT_ID)
    print(f"[{CLIENT_ID}] Connecting to broker at {BROKER_IP}...")
    client.connect(BROKER_IP, 1883, 60)
    client.loop_start()

    msg_id = 1
    try:
        while True:
            base_data = {
                "msg_id": msg_id,
                "client_id": CLIENT_ID,
                "timestamp": round(time.time(), 4),
                "padding": ""
            }
            
            # Pad the JSON string so the exact serialized payload size is 128 bytes
            temp_json = json.dumps(base_data)
            pad_len = max(0, TARGET_PAYLOAD_SIZE - len(temp_json))
            base_data["padding"] = "X" * pad_len
            
            payload = json.dumps(base_data)
            
            # Publish with QoS 1 (At least once delivery)
            info = client.publish(TOPIC, payload, qos=1)
            info.wait_for_publish()
            
            print(f"[SENT] {CLIENT_ID} | Msg ID: {msg_id} | Size: {len(payload)} B")
            msg_id += 1
            time.sleep(1.0)  # 1 Hz publication rate
            
    except KeyboardInterrupt:
        print(f"\n[{CLIENT_ID}] Stopping publisher...")
        client.loop_stop()
        client.disconnect()

if __name__ == '__main__':
    main()
