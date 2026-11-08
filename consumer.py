import paho.mqtt.client as mqtt
import json, time, csv

with open("midterm_logs.csv", mode='w') as f:
    f.write("protocol,condition,client_id,seq,t_send,t_recv,delay\n")

def on_message(client, userdata, msg):
    t_recv = time.time() * 1000
    try:
        data = json.loads(msg.payload.decode())
        delay = t_recv - data['t_send']
        with open("midterm_logs.csv", mode='a') as f:
            f.write(f"MQTT,current_test,{data['client_id']},{data['seq']},{data['t_send']},{t_recv},{delay}\n")
    except: pass

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.connect("10.0.0.1")
client.subscribe("iot/data", qos=1)
print("Consumer pregatit...")
client.loop_forever()
