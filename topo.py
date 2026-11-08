from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSBridge
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info

class IoTTopo(Topo):
    def build(self):
        # Create switches acting as transparent bridges
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        # Bottleneck link between s1 and s2: 10 Mbps, 20ms delay, 3% packet loss
        self.addLink(s1, s2, bw=10, delay='20ms', loss=3)

        # Add Broker and Consumer connected to s2
        broker = self.addHost('broker', ip='10.0.0.254/24')
        consumer = self.addHost('consumer', ip='10.0.0.253/24')
        self.addLink(broker, s2)
        self.addLink(consumer, s2)

        # Add 10 IoT Client nodes connected to s1
        for i in range(1, 11):
            client = self.addHost(f'client{i}', ip=f'10.0.0.{i}/24')
            self.addLink(client, s1)

def run():
    topo = IoTTopo()
    net = Mininet(topo=topo, switch=OVSBridge, link=TCLink, controller=None)
    net.start()
    
    info('*** Network topology started successfully.\n')
    info('*** Testing baseline connectivity...\n')
    net.pingAll()
    
    info('*** Starting CLI...\n')
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
