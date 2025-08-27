from scapy.all import rdpcap, IP, TCP, UDP, Ether
from datetime import datetime
import ipaddress
from mac_vendors import get_mac_vendor

class PcapAnalyzer:
    def __init__(self):
        self.packets = []
        
    def analyze_file(self, file_path):
        try:
            packets = rdpcap(file_path)
            result = []
            
            for i, packet in enumerate(packets):
                packet_data = self.parse_packet(packet, i + 1)
                result.append(packet_data)
            
            return result
        except Exception as e:
            raise Exception(f"Error analyzing PCAP: {str(e)}")
    
    def parse_packet(self, packet, packet_number):
        packet_time = float(packet.time)
        
        packet_data = {
            'packet_number': packet_number,
            'time': packet_time, 
            'time_str': str(datetime.fromtimestamp(packet_time)),
            'length': len(packet),
        }
        
        if Ether in packet:
            packet_data['ethernet'] = {
                'src': packet[Ether].src,
                'dst': packet[Ether].dst,
                'type': hex(packet[Ether].type),
                'src_vendor': get_mac_vendor(packet[Ether].src),
                'dst_vendor': get_mac_vendor(packet[Ether].dst)
            }
        
        if IP in packet:
            packet_data['ip'] = {
                'src': packet[IP].src,
                'dst': packet[IP].dst,
                'proto': packet[IP].proto,
                'ttl': packet[IP].ttl,
                'version': packet[IP].version,
                'len': packet[IP].len if hasattr(packet[IP], 'len') else len(packet[IP])
            }
            
            if TCP in packet:
                packet_data['tcp'] = {
                    'sport': packet[TCP].sport,
                    'dport': packet[TCP].dport,
                    'flags': str(packet[TCP].flags),
                    'seq': packet[TCP].seq,
                    'ack': packet[TCP].ack,
                    'window': packet[TCP].window,
                    # Dodaj flagi TCP dla lepszego wyświetlania
                    'flags_syn': bool(packet[TCP].flags & 0x02),
                    'flags_ack': bool(packet[TCP].flags & 0x10),
                    'flags_fin': bool(packet[TCP].flags & 0x01),
                    'flags_rst': bool(packet[TCP].flags & 0x04),
                    'flags_psh': bool(packet[TCP].flags & 0x08),
                    'flags_urg': bool(packet[TCP].flags & 0x20)
                }
            elif UDP in packet:
                packet_data['udp'] = {
                    'sport': packet[UDP].sport,
                    'dport': packet[UDP].dport,
                    'len': packet[UDP].len
                }
        
        # Obsługa payload
        if hasattr(packet, 'load') and packet.load:
            try:
                packet_data['payload'] = packet.load.decode('utf-8', errors='replace')
            except:
                packet_data['payload_hex'] = packet.load.hex()
        
        return packet_data