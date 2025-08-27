from datetime import datetime, timedelta

class PacketFilter:
    def filter_packets(self, packets, filters):
        filtered = []
        
        for packet in packets:
            if self.packet_matches_filters(packet, filters):
                filtered.append(packet)
        
        return filtered
    
    def packet_matches_filters(self, packet, filters):
        # IP filters
        if filters.get('srcIp'):
            if 'ip' not in packet or filters['srcIp'] not in packet['ip'].get('src', ''):
                return False
        
        if filters.get('dstIp'):
            if 'ip' not in packet or filters['dstIp'] not in packet['ip'].get('dst', ''):
                return False
        
        # MAC filters
        if filters.get('srcMac'):
            if 'ethernet' not in packet or \
               filters['srcMac'].lower() not in packet['ethernet'].get('src', '').lower():
                return False
        
        if filters.get('dstMac'):
            if 'ethernet' not in packet or \
               filters['dstMac'].lower() not in packet['ethernet'].get('dst', '').lower():
                return False
        
        # Protocol filter
        if filters.get('protocol'):
            packet_proto = self.get_protocol(packet)
            if filters['protocol'] != packet_proto:
                return False
        
        # Port filter
        if filters.get('port'):
            if not self.has_port(packet, int(filters['port'])):
                return False
        
        # Length filters
        if filters.get('lengthMin'):
            if packet['length'] < int(filters['lengthMin']):
                return False
        
        if filters.get('lengthMax'):
            if packet['length'] > int(filters['lengthMax']):
                return False
        
        # Time filters
        if filters.get('timeStart') or filters.get('timeEnd'):
            packet_time = datetime.fromisoformat(packet['time'])
            
            if filters.get('timeStart'):
                start_time = datetime.fromisoformat(filters['timeStart'])
                if packet_time < start_time:
                    return False
            
            if filters.get('timeEnd'):
                end_time = datetime.fromisoformat(filters['timeEnd'])
                if packet_time > end_time:
                    return False
        
        return True
    
    def get_protocol(self, packet):
        if 'tcp' in packet:
            return 'TCP'
        elif 'udp' in packet:
            return 'UDP'
        elif 'ip' in packet:
            return f"IP({packet['ip']['proto']})"
        return 'Other'
    
    def has_port(self, packet, port):
        if 'tcp' in packet:
            return packet['tcp']['sport'] == port or packet['tcp']['dport'] == port
        elif 'udp' in packet:
            return packet['udp']['sport'] == port or packet['udp']['dport'] == port
        return False