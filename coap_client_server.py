import asyncio
import time
import json
import csv
import os
from aiocoap import Context, Message, CON, POST
import aiocoap.resource as resource

LOG_FILE = "coap_logs.csv"
TARGET_PAYLOAD_SIZE = 128

class TelemetryResource(resource.Resource):
    async def render_post(self, request):
        recv_time = time.time()
        try:
            data = json.loads(request.payload.decode('utf-8'))
            send_time = data.get("timestamp", recv_time)
            msg_id = data.get("msg_id", 0)
            client_id = data.get("client_id", "client_1")
            
            delay_ms = round((recv_time - send_time) * 1000, 2)
            payload_len = len(request.payload)
            # Ethernet (14B) + IP (20B) + UDP (8B) + CoAP Header (4B) + ACK
            wire_len = payload_len + 18
            
            with open(LOG_FILE, mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([msg_id, client_id, delay_ms, payload_len, wire_len])
                
            print(f"[CoAP RECV] {client_id} | Msg #{msg_id} | Delay: {delay_ms} ms")
        except Exception as e:
            print(f"[ERROR] {e}")
            
        return Message( payload=b"ACK" )

async def run_client(client_id="client_1", broker_ip="10.0.0.253"):
    protocol = await Context.create_client_context()
    msg_id = 1
    while msg_id <= 100:
        base_data = {
            "msg_id": msg_id,
            "client_id": client_id,
            "timestamp": round(time.time(), 4),
            "padding": ""
        }
        pad_len = max(0, TARGET_PAYLOAD_SIZE - len(json.dumps(base_data)))
        base_data["padding"] = "X" * pad_len
        payload = json.dumps(base_data).encode('utf-8')
        
        request = Message(code=POST, payload=payload, mtype=CON, uri=f"coap://{broker_ip}/telemetry")
        await protocol.request(request).response
        print(f"[CoAP SENT] {client_id} | Msg #{msg_id} | 128 B")
        msg_id += 1
        await asyncio.sleep(1.0)

if __name__ == "__main__":
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode='w', newline='') as f:
            csv.writer(f).writerow(["msg_id", "client_id", "delay", "payload_bytes", "wire_bytes"])
    print("CoAP Telemetry Module Ready.")
