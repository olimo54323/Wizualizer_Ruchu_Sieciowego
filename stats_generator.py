from datetime import datetime, timedelta
from collections import Counter
import numpy as np
from mac_vendors import get_mac_vendor

class StatsGenerator:
    def generate_stats(self, packets):
        """Główna metoda generująca wszystkie statystyki"""
        stats = {
            'total_packets': len(packets),
            'protocols': {},
            'top_ips': {},
            'top_ports': {},
            'top_mac_addresses': {},
            'top_mac_vendors': {},
            'packet_sizes': [],
            'time_distribution': {},
            'network_graph': {'nodes': [], 'edges': []},
            'mac_graph': {'nodes': [], 'edges': []},
            'geo_data': []
        }
        
        # Podstawowe statystyki
        self.collect_basic_stats(packets, stats)
        
        # Zaawansowane statystyki sieciowe
        stats['payload_stats'] = self.calculate_payload_stats(packets)
        stats['throughput_stats'] = self.calculate_throughput_stats(packets)
        stats['network_load'] = self.calculate_network_load(packets)
        stats['protocol_payload'] = self.calculate_protocol_payload(packets)
        stats['mac_protocol_stats'] = self.calculate_mac_protocol_stats(packets)
        
        # Rozkład czasowy i wielkości
        stats['time_distribution'] = self.calculate_time_distribution(packets)
        stats['packet_size_distribution'] = self.calculate_size_distribution(stats['packet_sizes'])
        
        # Grafy sieciowe
        self.build_network_graph(packets, stats)
        self.build_mac_graph(packets, stats)
        
        # Ulepszony graf MAC z protokołami
        stats['enhanced_mac_graph'] = self.build_enhanced_mac_graph(packets, stats['mac_protocol_stats'])
        
        # Sortowanie i limitowanie TOP wartości
        stats['top_ips'] = dict(Counter(stats['top_ips']).most_common(10))
        stats['top_ports'] = dict(Counter(stats['top_ports']).most_common(10))
        stats['top_mac_addresses'] = dict(Counter(stats['top_mac_addresses']).most_common(10))
        stats['top_mac_vendors'] = dict(Counter(stats['top_mac_vendors']).most_common(10))
        
        # Dane dla wykresów
        stats['top_ports_data'] = [{'port': p, 'count': c} for p, c in list(stats['top_ports'].items())[:5]]
        stats['top_mac_data'] = [{'mac': m, 'count': c} for m, c in list(stats['top_mac_addresses'].items())[:5]]
        
        return stats
    
    def collect_basic_stats(self, packets, stats):
        for packet in packets:
            stats['packet_sizes'].append(packet['length'])
            
            if 'ethernet' in packet:
                src_mac = packet['ethernet']['src']
                dst_mac = packet['ethernet']['dst']
                stats['top_mac_addresses'][src_mac] = stats['top_mac_addresses'].get(src_mac, 0) + 1
                stats['top_mac_addresses'][dst_mac] = stats['top_mac_addresses'].get(dst_mac, 0) + 1
                
                src_vendor = packet['ethernet']['src_vendor']
                dst_vendor = packet['ethernet']['dst_vendor']
                stats['top_mac_vendors'][src_vendor] = stats['top_mac_vendors'].get(src_vendor, 0) + 1
                stats['top_mac_vendors'][dst_vendor] = stats['top_mac_vendors'].get(dst_vendor, 0) + 1
            
            if 'ip' in packet:
                if 'tcp' in packet:
                    stats['protocols']['TCP'] = stats['protocols'].get('TCP', 0) + 1
                    stats['top_ports'][packet['tcp']['sport']] = stats['top_ports'].get(packet['tcp']['sport'], 0) + 1
                    stats['top_ports'][packet['tcp']['dport']] = stats['top_ports'].get(packet['tcp']['dport'], 0) + 1
                elif 'udp' in packet:
                    stats['protocols']['UDP'] = stats['protocols'].get('UDP', 0) + 1
                    stats['top_ports'][packet['udp']['sport']] = stats['top_ports'].get(packet['udp']['sport'], 0) + 1
                    stats['top_ports'][packet['udp']['dport']] = stats['top_ports'].get(packet['udp']['dport'], 0) + 1
                else:
                    proto = f"Protocol {packet['ip']['proto']}"
                    stats['protocols'][proto] = stats['protocols'].get(proto, 0) + 1
                
                src_ip = packet['ip']['src']
                dst_ip = packet['ip']['dst']
                stats['top_ips'][src_ip] = stats['top_ips'].get(src_ip, 0) + 1
                stats['top_ips'][dst_ip] = stats['top_ips'].get(dst_ip, 0) + 1
    
    def calculate_time_distribution(self, packets):
        """Oblicza rozkład czasowy pakietów"""
        if not packets:
            return {'labels': [], 'values': []}
        
        # Funkcja pomocnicza do konwersji czasu
        def get_packet_time(packet):
            time_val = packet.get('time', 0)
            if isinstance(time_val, (int, float)):
                return float(time_val)
            elif isinstance(time_val, str):
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(time_val.replace('Z', '+00:00'))
                    return dt.timestamp()
                except:
                    try:
                        dt = datetime.strptime(time_val, '%Y-%m-%d %H:%M:%S.%f')
                        return dt.timestamp()
                    except:
                        try:
                            dt = datetime.strptime(time_val, '%Y-%m-%d %H:%M:%S')
                            return dt.timestamp()
                        except:
                            return 0
            return 0
        
        # Sortowanie pakietów według czasu
        packets_with_time = []
        for packet in packets:
            packet_time = get_packet_time(packet)
            if packet_time > 0:
                packets_with_time.append(packet_time)
        
        if not packets_with_time:
            return {'labels': ['0s'], 'values': [len(packets)]}
        
        packets_with_time.sort()
        
        # Znajdź zakres czasowy
        start_time = packets_with_time[0]
        end_time = packets_with_time[-1]
        
        if start_time == end_time:
            # Wszystkie pakiety w tym samym czasie
            from datetime import datetime
            time_str = datetime.fromtimestamp(start_time).strftime('%H:%M:%S')
            return {
                'labels': [time_str],
                'values': [len(packets_with_time)]
            }
        
        # Podziel na równomierne okna czasowe
        duration = end_time - start_time
        num_buckets = min(50, max(10, len(packets_with_time) // 10))  # 10-50 bucketów
        bucket_size = duration / num_buckets
        
        # Inicjalizacja bucketów
        buckets = [0] * num_buckets
        labels = []
        
        # Wypełnij buckety
        for packet_time in packets_with_time:
            bucket_index = int((packet_time - start_time) / bucket_size)
            if bucket_index >= num_buckets:
                bucket_index = num_buckets - 1
            buckets[bucket_index] += 1
        
        # Generuj etykiety czasowe
        from datetime import datetime
        for i in range(num_buckets):
            bucket_time = start_time + (i * bucket_size)
            if duration < 60:  # mniej niż minuta - pokazuj sekundy
                label = datetime.fromtimestamp(bucket_time).strftime('%H:%M:%S.%f')[:-3]
            elif duration < 3600:  # mniej niż godzina - pokazuj minuty i sekundy
                label = datetime.fromtimestamp(bucket_time).strftime('%H:%M:%S')
            else:  # więcej niż godzina - pokazuj godziny i minuty
                label = datetime.fromtimestamp(bucket_time).strftime('%H:%M')
            labels.append(label)
        
        return {
            'labels': labels,
            'values': buckets
        }

    def calculate_size_distribution(self, packet_sizes):
        """Oblicza rozkład wielkości pakietów"""
        if not packet_sizes:
            return {'labels': [], 'values': []}
        
        import numpy as np
        
        # Znajdź zakresy wielkości
        min_size = min(packet_sizes)
        max_size = max(packet_sizes)
        
        if min_size == max_size:
            return {
                'labels': [f'{min_size} B'],
                'values': [len(packet_sizes)]
            }
        
        # Stwórz histogram z inteligentnym podziałem
        num_bins = min(20, max(5, len(set(packet_sizes))))
        hist, bin_edges = np.histogram(packet_sizes, bins=num_bins)
        
        # Generuj etykiety dla przedziałów
        labels = []
        for i in range(len(bin_edges) - 1):
            start = int(bin_edges[i])
            end = int(bin_edges[i + 1])
            if end - start == 1:
                labels.append(f'{start} B')
            else:
                labels.append(f'{start}-{end} B')
        
        return {
            'labels': labels,
            'values': hist.tolist()
        }
    
    def build_network_graph(self, packets, stats):
        edges = {}
        nodes = {}
        
        for packet in packets:
            if 'ip' in packet:
                src = packet['ip']['src']
                dst = packet['ip']['dst']
                
                nodes[src] = nodes.get(src, 0) + 1
                nodes[dst] = nodes.get(dst, 0) + 1
                
                edge_key = f"{src}->{dst}"
                edges[edge_key] = edges.get(edge_key, 0) + 1
        
        stats['network_graph']['nodes'] = [
            {'id': ip, 'label': ip, 'value': count}
            for ip, count in nodes.items()
        ]
        
        stats['network_graph']['edges'] = [
            {'from': key.split('->')[0], 'to': key.split('->')[1], 'value': count}
            for key, count in edges.items()
        ]
    
    def build_mac_graph(self, packets, stats):
        edges = {}
        nodes = {}
        
        for packet in packets:
            if 'ethernet' in packet:
                src = packet['ethernet']['src']
                dst = packet['ethernet']['dst']
                
                nodes[src] = nodes.get(src, 0) + 1
                nodes[dst] = nodes.get(dst, 0) + 1
                
                edge_key = f"{src}->{dst}"
                edges[edge_key] = edges.get(edge_key, 0) + 1
        
        stats['mac_graph']['nodes'] = [
            {'id': mac, 'label': mac, 'value': count, 'title': get_mac_vendor(mac)}
            for mac, count in nodes.items()
        ]
        
        stats['mac_graph']['edges'] = [
            {'from': key.split('->')[0], 'to': key.split('->')[1], 'value': count}
            for key, count in edges.items()
        ]
    
    def calculate_payload_stats(self, packets):
        total = 0
        count = 0
        max_size = 0
        min_size = float('inf')
        
        for packet in packets:
            size = packet.get('length', 0)
            header_size = 14  # Ethernet
            if 'ip' in packet:
                header_size += 20
            if 'tcp' in packet:
                header_size += 20
            elif 'udp' in packet:
                header_size += 8
            
            payload = max(0, size - header_size)
            if payload > 0:
                total += payload
                count += 1
                max_size = max(max_size, payload)
                min_size = min(min_size, payload)
        
        return {
            'total_payload_bytes': total,
            'avg_payload_per_packet': total / len(packets) if packets else 0,
            'max_payload_size': max_size,
            'min_payload_size': min_size if min_size != float('inf') else 0
        }
    
    def calculate_throughput_stats(self, packets):
        """Oblicza statystyki przepustowości w czasie - POPRAWIONA WERSJA"""
        if not packets:
            return {
                'avg_throughput': 0,
                'peak_throughput': 0,
                'time_labels': [],
                'bytes_per_second': [],
                'packets_per_second': []
            }
        
        # Sortowanie pakietów wg czasu - obsługa różnych formatów
        def get_packet_time(packet):
            time_val = packet.get('time', 0)
            if isinstance(time_val, (int, float)):
                return float(time_val)
            elif isinstance(time_val, str):
                try:
                    # Próba parsowania jako ISO format
                    from datetime import datetime
                    dt = datetime.fromisoformat(time_val.replace('Z', '+00:00'))
                    return dt.timestamp()
                except:
                    try:
                        # Próba parsowania innych formatów
                        dt = datetime.strptime(time_val, '%Y-%m-%d %H:%M:%S.%f')
                        return dt.timestamp()
                    except:
                        try:
                            dt = datetime.strptime(time_val, '%Y-%m-%d %H:%M:%S')
                            return dt.timestamp()
                        except:
                            print(f"Nie można sparsować czasu: {time_val}")
                            return 0
            else:
                return 0
        
        # Sortowanie pakietów wg czasu
        sorted_packets = sorted(packets, key=get_packet_time)
        
        # Znajdź zakres czasowy
        start_time = get_packet_time(sorted_packets[0])
        end_time = get_packet_time(sorted_packets[-1])
        
        if end_time == start_time or start_time == 0:
            # Jeśli wszystkie pakiety mają ten sam czas lub błędny czas
            total_bytes = sum(p.get('length', 0) for p in packets)
            return {
                'avg_throughput': total_bytes,
                'peak_throughput': total_bytes,
                'time_labels': ['0s'],
                'bytes_per_second': [total_bytes],
                'packets_per_second': [len(packets)]
            }
        
        # Podziel na okna czasowe
        duration = end_time - start_time
        if duration < 10:  # mniej niż 10 sekund
            window_size = max(0.1, duration / 50)  # max 50 okien
        else:
            window_size = max(1.0, duration / 100)  # max 100 okien
        
        time_windows = {}
        
        for packet in sorted_packets:
            packet_time = get_packet_time(packet)
            if packet_time == 0:
                continue
                
            window_index = int((packet_time - start_time) / window_size)
            
            if window_index not in time_windows:
                time_windows[window_index] = {'bytes': 0, 'packets': 0}
            
            time_windows[window_index]['bytes'] += packet.get('length', 0)
            time_windows[window_index]['packets'] += 1
        
        # Przygotuj dane dla wykresu
        max_window = max(time_windows.keys()) if time_windows else 0
        time_labels = []
        bytes_per_second = []
        packets_per_second = []
        
        for i in range(max_window + 1):
            # Format etykiety czasowej
            if duration < 60:  # mniej niż minuta
                time_label = f"{(i * window_size):.1f}s"
            elif duration < 3600:  # mniej niż godzina
                minutes = int((i * window_size) // 60)
                seconds = int((i * window_size) % 60)
                time_label = f"{minutes:02d}:{seconds:02d}"
            else:  # więcej niż godzina
                hours = int((i * window_size) // 3600)
                minutes = int(((i * window_size) % 3600) // 60)
                time_label = f"{hours}h {minutes:02d}m"
            
            time_labels.append(time_label)
            
            if i in time_windows:
                bytes_rate = time_windows[i]['bytes'] / window_size
                packets_rate = time_windows[i]['packets'] / window_size
            else:
                bytes_rate = 0
                packets_rate = 0
            
            bytes_per_second.append(int(bytes_rate))
            packets_per_second.append(int(packets_rate))
        
        # Oblicz średnią i szczytową przepustowość
        total_bytes = sum(p.get('length', 0) for p in packets)
        avg_throughput = total_bytes / duration if duration > 0 else 0
        peak_throughput = max(bytes_per_second) if bytes_per_second else 0
        
        return {
            'avg_throughput': int(avg_throughput),
            'peak_throughput': int(peak_throughput),
            'time_labels': time_labels,
            'bytes_per_second': bytes_per_second,
            'packets_per_second': packets_per_second
        }
    
    def calculate_network_load(self, packets):
        total_bytes = sum(p.get('length', 0) for p in packets)
        header_overhead = 0
        
        for packet in packets:
            overhead = 14  # Ethernet
            if 'ip' in packet:
                overhead += 20
            if 'tcp' in packet:
                overhead += 20
            elif 'udp' in packet:
                overhead += 8
            header_overhead += overhead
        
        payload_bytes = total_bytes - header_overhead
        
        return {
            'total_bytes': total_bytes,
            'header_overhead': header_overhead,
            'payload_efficiency': (payload_bytes / total_bytes * 100) if total_bytes > 0 else 0
        }
    
    def calculate_protocol_payload(self, packets):
        protocol_stats = {}
        
        for packet in packets:
            if 'tcp' in packet:
                proto = 'TCP'
            elif 'udp' in packet:
                proto = 'UDP'
            elif 'ip' in packet:
                proto = f"IP({packet['ip']['proto']})"
            else:
                proto = 'Other'
            
            if proto not in protocol_stats:
                protocol_stats[proto] = {'total': 0, 'packets': 0}
            
            protocol_stats[proto]['packets'] += 1
            protocol_stats[proto]['total'] += packet.get('length', 0)
        
        return protocol_stats
    
    def calculate_mac_protocol_stats(self, packets):
        """Oblicza statystyki protokołów dla każdego adresu MAC"""
        mac_stats = {}
        
        for packet in packets:
            if 'ethernet' not in packet:
                continue
                
            src_mac = packet['ethernet']['src']
            dst_mac = packet['ethernet']['dst']
            
            # Określ protokół
            if 'tcp' in packet:
                protocol = 'TCP'
            elif 'udp' in packet:
                protocol = 'UDP'
            elif 'ip' in packet:
                protocol = 'Other'
            else:
                protocol = 'Other'
            
            # Zliczaj dla src_mac
            if src_mac not in mac_stats:
                mac_stats[src_mac] = {'TCP': 0, 'UDP': 0, 'Other': 0}
            mac_stats[src_mac][protocol] += 1
            
            # Zliczaj dla dst_mac
            if dst_mac not in mac_stats:
                mac_stats[dst_mac] = {'TCP': 0, 'UDP': 0, 'Other': 0}
            mac_stats[dst_mac][protocol] += 1
        
        return mac_stats

    def build_enhanced_mac_graph(self, packets, mac_protocol_stats):
        """Buduje ulepszony graf MAC z informacjami o protokołach"""
        enhanced_mac_graph = {
            'nodes': [],
            'edges': []
        }
        
        if not packets or not mac_protocol_stats:
            return enhanced_mac_graph
        
        # Mapa kolorów dla protokołów
        color_map = {
            'TCP': '#FF6B6B',
            'UDP': '#4ECDC4', 
            'ICMP': '#45B7D1',
            'ARP': '#96CEB4',
            'DNS': '#FECA57',
            'HTTP': '#FF9FF3',
            'HTTPS': '#54A0FF',
            'Other': '#DDA0DD',
            'Unknown': '#C8C8C8'
        }
        
        # Import do pobierania informacji o producentach
        try:
            from mac_vendors import get_mac_vendor
        except ImportError:
            def get_mac_vendor(mac):
                return "Unknown"
        
        # Przygotuj węzły MAC z informacjami o protokołach
        for mac, protocol_stats in mac_protocol_stats.items():
            if not protocol_stats or sum(protocol_stats.values()) == 0:
                continue
                
            # Znajdź dominujący protokół
            dominant_protocol = max(protocol_stats, key=protocol_stats.get)
            total_packets = sum(protocol_stats.values())
            
            # Pobierz kolor dla dominującego protokołu
            node_color = color_map.get(dominant_protocol, color_map['Unknown'])
            
            # Pobierz informacje o producencie
            vendor = get_mac_vendor(mac)
            
            enhanced_mac_graph['nodes'].append({
                'id': mac,
                'label': mac[-8:],  # Ostatnie 8 znaków MAC
                'title': f"MAC: {mac}\\nVendor: {vendor}\\nDominant: {dominant_protocol}\\nPackets: {total_packets}",
                'value': total_packets,
                'color': node_color,
                'protocol': dominant_protocol,
                'protocol_stats': protocol_stats,
                'vendor': vendor
            })
        
        # Przygotuj krawędzie z informacjami o komunikacji
        edges_data = {}
        
        for packet in packets:
            if 'ethernet' not in packet:
                continue
                
            src_mac = packet['ethernet']['src']
            dst_mac = packet['ethernet']['dst']
            
            # Sprawdź czy oba MAC są w naszych węzłach
            if src_mac not in mac_protocol_stats or dst_mac not in mac_protocol_stats:
                continue
            
            edge_key = f"{src_mac}->{dst_mac}"
            
            # Określ protokół krawędzi
            if 'tcp' in packet:
                edge_protocol = 'TCP'
            elif 'udp' in packet:
                edge_protocol = 'UDP'
            elif 'ip' in packet:
                edge_protocol = f"IP({packet['ip'].get('proto', '?')})"
            else:
                edge_protocol = 'Other'
            
            if edge_key not in edges_data:
                edges_data[edge_key] = {
                    'from': src_mac,
                    'to': dst_mac,
                    'value': 0,
                    'protocols': set()
                }
            
            edges_data[edge_key]['value'] += 1
            edges_data[edge_key]['protocols'].add(edge_protocol)
        
        # Konwertuj krawędzie do formatu vis.js
        for edge_key, edge_data in edges_data.items():
            protocols_list = list(edge_data['protocols'])
            protocols_str = ', '.join(protocols_list)
            
            enhanced_mac_graph['edges'].append({
                'from': edge_data['from'],
                'to': edge_data['to'],
                'value': edge_data['value'],
                'title': f"Packets: {edge_data['value']}\\nProtocols: {protocols_str}",
                'width': min(10, max(1, edge_data['value'] / 10)),
                'protocols': protocols_list
            })
        
        return enhanced_mac_graph