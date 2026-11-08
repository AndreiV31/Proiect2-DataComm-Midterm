import paho.mqtt.client as mqtt
import json, time, sys

client_id = sys.argv[1]
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=client_id)
client.connect("10.0.0.1")

seq = 0
while True:
    t_send = time.time() * 1000
    data = {"client_id": client_id, "seq": seq, "t_send": t_send}
    msg_str = json.dumps(data)
    data["pad"] = "X" * (128 - len(msg_str))
    
    client.publish("iot/data", json.dumps(data), qos=1)
    seq += 1
    time.sleep(1)
