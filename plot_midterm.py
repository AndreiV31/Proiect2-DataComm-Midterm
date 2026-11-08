import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 1. Load raw per-message logs for each protocol stack
df_mqtt = pd.read_csv("mqtt_logs.csv")
df_coap = pd.read_csv("coap_logs.csv")
df_amqp = pd.read_csv("amqp_logs.csv")

# Print KPI statistics (Mean, p50, p95) to console
print("--- End-to-End Delay Statistics (ms) ---")
for name, df in [("MQTT", df_mqtt), ("CoAP", df_coap), ("AMQP", df_amqp)]:
    mean_val = df['delay'].mean()
    p50_val = np.percentile(df['delay'], 50)
    p95_val = np.percentile(df['delay'], 95)
    print(f"[{name}] Mean: {mean_val:.2f} ms | p50: {p50_val:.2f} ms | p95: {p95_val:.2f} ms")

# 2. Generate End-to-End Delay Boxplot
plt.figure(figsize=(10, 5))
plt.boxplot([df_mqtt['delay'], df_coap['delay'], df_amqp['delay']], 
            labels=['MQTT QoS 1', 'CoAP CON', 'AMQP Confirms'])
plt.title('End-to-End Delay under Emulated WAN (20ms RTT, 3% Loss) - 10 Clients')
plt.ylabel('End-to-End Delay (ms)')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig('midterm_delay.png')
plt.close()

# 3. Calculate and Plot Protocol Overhead (Wire bytes / Payload bytes)
oh_mqtt = (df_mqtt['wire_bytes'] / df_mqtt['payload_bytes']).mean()
oh_coap = (df_coap['wire_bytes'] / df_coap['payload_bytes']).mean()
oh_amqp = (df_amqp['wire_bytes'] / df_amqp['payload_bytes']).mean()

plt.figure(figsize=(8, 5))
plt.bar(['MQTT', 'CoAP', 'AMQP'], [oh_mqtt, oh_coap, oh_amqp], color=['#1f77b4', '#2ca02c', '#ff7f0e'])
plt.title('Protocol Overhead Ratio (Wire Bytes / Payload Bytes)')
plt.ylabel('Overhead Ratio')
plt.axhline(1.0, color='red', linestyle='dashed', label='Ideal Payload Ratio (1:1)')
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.savefig('midterm_overhead.png')
plt.close()

print("Charts successfully saved: midterm_delay.png, midterm_overhead.png")
