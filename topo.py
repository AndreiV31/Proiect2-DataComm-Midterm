from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.node import OVSController

class IoTTopo(Topo):
    def build(self, n=10, delay='20ms', loss=0):
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        
        self.addLink(s1, s2, cls=TCLink, delay=delay, loss=loss)
        
        broker = self.addHost('broker')
        consumer = self.addHost('consumer')
        self.addLink(s2, broker)
        self.addLink(s2, consumer)
        
        for i in range(n):
            client = self.addHost(f'h{i+1}')
            self.addLink(client, s1)

if __name__ == '__main__':
    setLogLevel('info')
    import sys
    loss_val = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    topo = IoTTopo(n=10, delay='20ms', loss=loss_val)
    
    # Am specificat explicit controller=OVSController
    net = Mininet(topo=topo, link=TCLink, controller=OVSController)
    net.start()
    CLI(net)
    net.stop()
