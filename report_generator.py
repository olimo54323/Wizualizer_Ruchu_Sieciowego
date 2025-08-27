import os
import csv
from datetime import datetime, timedelta
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

class ReportGenerator:
    def __init__(self, upload_folder='uploads'):
        self.upload_folder = upload_folder
        
    def generate_pdf(self, filename, packets, stats, options):
        """
        Generowanie kompletnego raportu PDF z wszystkimi wykresami z dashboardu
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = os.path.splitext(os.path.basename(filename))[0]
        report_filename = f"report_{base_filename}_{timestamp}.pdf"
        report_path = os.path.join(self.upload_folder, report_filename)
        
        # Tworzenie dokumentu
        doc = SimpleDocTemplate(
            report_path,
            pagesize=A4,
            rightMargin=72, leftMargin=72,
            topMargin=72, bottomMargin=72
        )
        
        # Style
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        subtitle_style = styles['Heading2']
        normal_style = styles['Normal']
        
        # Lista elementów do dodania do dokumentu
        elements = []
        
        # Tytuł
        elements.append(Paragraph(f"Network Traffic Analysis Report", title_style))
        elements.append(Paragraph(f"File: {filename}", subtitle_style))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
        elements.append(Spacer(1, 0.5*inch))
        
        # Spis treści
        elements.append(Paragraph("Table of Contents", subtitle_style))
        
        # Tworzenie dynamicznego spisu treści
        toc_items = []
        if 'summary' in options:
            toc_items.append("Summary")
        if 'protocols' in options and stats.get('protocols'):
            toc_items.append("Protocol Distribution")
        if 'ports' in options and stats.get('top_ports'):
            toc_items.append("Most Used Ports")
        if 'mac_addresses' in options and stats.get('top_mac_addresses'):
            toc_items.append("Most Used MAC Addresses")
        if 'mac_vendors' in options and stats.get('top_mac_vendors'):
            toc_items.append("MAC Vendors Distribution")
        if 'payload_stats' in options and stats.get('payload_stats'):
            toc_items.append("Payload Statistics")
        if 'throughput_stats' in options and stats.get('throughput_stats'):
            toc_items.append("Throughput Analysis")
        if 'network_efficiency' in options and stats.get('network_load'):
            toc_items.append("Network Efficiency")
        if 'protocol_payload' in options and stats.get('protocol_payload'):
            toc_items.append("Protocol Payload Analysis")
        if 'time' in options and stats.get('time_distribution'):
            toc_items.append("Time Distribution")
        if 'packet_size' in options and stats.get('packet_size_distribution'):
            toc_items.append("Packet Size Distribution")
        if 'top_ips' in options and stats.get('top_ips'):
            toc_items.append("Most Common IP Addresses")
        
        # Dodanie spisu treści jako zwykłego tekstu
        for title in toc_items:
            elements.append(Paragraph(f"• {title}", normal_style))
        elements.append(Spacer(1, 0.5*inch))
        
        # PODSUMOWANIE - rozszerzone
        if 'summary' in options:
            elements.append(Paragraph("Summary", subtitle_style))
            
            summary_data = [
                ["Metric", "Value"],
                ["Total number of packets", str(stats.get('total_packets', 0))],
            ]
            
            # Dodaj wskaźniki payload/netload do podsumowania
            if stats.get('payload_stats'):
                payload_mb = stats['payload_stats'].get('total_payload_bytes', 0) / (1024 * 1024)
                summary_data.append(["Total payload", f"{payload_mb:.2f} MB"])
                summary_data.append(["Average payload per packet", 
                                   f"{stats['payload_stats'].get('avg_payload_per_packet', 0):.2f} bytes"])
            
            if stats.get('network_load'):
                total_mb = stats['network_load'].get('total_bytes', 0) / (1024 * 1024)
                summary_data.append(["Total network traffic", f"{total_mb:.2f} MB"])
                summary_data.append(["Network efficiency", 
                                   f"{stats['network_load'].get('payload_efficiency', 0):.1f}%"])
            
            if stats.get('throughput_stats'):
                avg_throughput_kbps = stats['throughput_stats'].get('avg_throughput', 0) / 1024
                peak_throughput_kbps = stats['throughput_stats'].get('peak_throughput', 0) / 1024
                summary_data.append(["Average throughput", f"{avg_throughput_kbps:.2f} KB/s"])
                summary_data.append(["Peak throughput", f"{peak_throughput_kbps:.2f} KB/s"])
            
            # Dodanie głównych protokołów do podsumowania
            if stats.get('protocols'):
                top_protocols = sorted(stats['protocols'].items(), key=lambda x: x[1], reverse=True)[:3]
                protocols_str = ", ".join([f"{proto}: {count}" for proto, count in top_protocols])
                summary_data.append(["Top protocols", protocols_str])
            
            summary_table = Table(summary_data, colWidths=[200, 300])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(summary_table)
            elements.append(Spacer(1, 0.3*inch))
        
        # WYKRES PROTOKOŁÓW
        if 'protocols' in options and stats.get('protocols'):
            elements.append(Paragraph("Protocol Distribution", subtitle_style))
            
            # Generowanie wykresu
            chart_img = self.create_pie_chart(
                stats['protocols'], 
                'Protocol Distribution'
            )
            if chart_img:
                elements.append(Image(chart_img, width=400, height=300))
            elements.append(Spacer(1, 0.3*inch))
        
        # WYKRES PORTÓW
        if 'ports' in options and stats.get('top_ports'):
            elements.append(Paragraph("Most Used Ports", subtitle_style))
            
            top_ports_sorted = sorted(stats['top_ports'].items(), key=lambda x: x[1], reverse=True)[:10]
            ports_labels = [str(port) for port, _ in top_ports_sorted]
            ports_values = [count for _, count in top_ports_sorted]
            
            chart_img = self.create_bar_chart(
                {'labels': ports_labels, 'values': ports_values},
                'Top 10 Ports'
            )
            if chart_img:
                elements.append(Image(chart_img, width=400, height=300))
            elements.append(Spacer(1, 0.3*inch))
        
        # WYKRES ADRESÓW MAC
        if 'mac_addresses' in options and stats.get('top_mac_addresses'):
            elements.append(Paragraph("Most Used MAC Addresses", subtitle_style))
            
            top_macs = sorted(stats['top_mac_addresses'].items(), key=lambda x: x[1], reverse=True)[:10]
            mac_labels = [mac[-8:] for mac, _ in top_macs]
            mac_values = [count for _, count in top_macs]
            
            chart_img = self.create_bar_chart(
                {'labels': mac_labels, 'values': mac_values},
                'Top 10 MAC Addresses'
            )
            if chart_img:
                elements.append(Image(chart_img, width=400, height=300))
            elements.append(Spacer(1, 0.3*inch))
        
        # WYKRES CZASOWY
        if 'time' in options and stats.get('time_distribution'):
            elements.append(Paragraph("Time Distribution", subtitle_style))
            
            if 'labels' in stats['time_distribution'] and 'values' in stats['time_distribution']:
                # Ograniczenie liczby punktów dla czytelności
                time_labels = stats['time_distribution']['labels']
                time_values = stats['time_distribution']['values']
                
                if len(time_labels) > 20:
                    step = len(time_labels) // 20
                    time_labels = time_labels[::step]
                    time_values = time_values[::step]
                
                chart_img = self.create_line_chart(
                    {'labels': time_labels, 'values': time_values},
                    'Packets Over Time'
                )
                if chart_img:
                    elements.append(Image(chart_img, width=400, height=300))
            elements.append(Spacer(1, 0.3*inch))
        
        # WYKRES WIELKOŚCI PAKIETÓW
        if 'packet_size' in options and stats.get('packet_size_distribution'):
            elements.append(Paragraph("Packet Size Distribution", subtitle_style))
            
            if 'bins' in stats['packet_size_distribution'] and 'counts' in stats['packet_size_distribution']:
                chart_img = self.create_histogram(
                    {'labels': stats['packet_size_distribution']['bins'],
                     'values': stats['packet_size_distribution']['counts']},
                    'Packet Sizes'
                )
                if chart_img:
                    elements.append(Image(chart_img, width=400, height=300))
            elements.append(Spacer(1, 0.3*inch))
        
        # STATYSTYKI PAYLOAD
        if 'payload_stats' in options and stats.get('payload_stats'):
            elements.append(Paragraph("Payload Statistics", subtitle_style))
            
            payload_data = stats['payload_stats']
            payload_table_data = [
                ["Metric", "Value"],
                ["Total Payload", f"{payload_data.get('total_payload_bytes', 0) / (1024*1024):.2f} MB"],
                ["Average Payload per Packet", f"{payload_data.get('avg_payload_per_packet', 0):.2f} bytes"],
                ["Maximum Payload Size", f"{payload_data.get('max_payload_size', 0)} bytes"],
                ["Minimum Payload Size", f"{payload_data.get('min_payload_size', 0)} bytes"],
            ]
            
            payload_table = Table(payload_table_data, colWidths=[250, 250])
            payload_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(payload_table)
            elements.append(Spacer(1, 0.3*inch))
        
        # ANALIZA THROUGHPUT
        if 'throughput_stats' in options and stats.get('throughput_stats'):
            elements.append(Paragraph("Throughput Analysis", subtitle_style))
            
            throughput_data = stats['throughput_stats']
            
            # Tabela z metrykami
            throughput_table_data = [
                ["Metric", "Value"],
                ["Average Throughput", f"{throughput_data.get('avg_throughput', 0) / 1024:.2f} KB/s"],
                ["Peak Throughput", f"{throughput_data.get('peak_throughput', 0) / 1024:.2f} KB/s"],
            ]
            
            throughput_table = Table(throughput_table_data, colWidths=[250, 250])
            throughput_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(throughput_table)
            
            # Wykres throughput w czasie
            if throughput_data.get('time_labels') and throughput_data.get('bytes_per_second'):
                if len(throughput_data['time_labels']) > 0:
                    # Ograniczenie liczby punktów
                    labels = throughput_data['time_labels']
                    values = throughput_data['bytes_per_second']
                    
                    if len(labels) > 30:
                        step = len(labels) // 30
                        labels = labels[::step]
                        values = values[::step]
                    
                    chart_img = self.create_line_chart(
                        {'labels': labels, 'values': values},
                        'Throughput Over Time (bytes/s)'
                    )
                    if chart_img:
                        elements.append(Image(chart_img, width=400, height=300))
            
            elements.append(Spacer(1, 0.3*inch))
        
        # EFEKTYWNOŚĆ SIECI
        if 'network_efficiency' in options and stats.get('network_load'):
            elements.append(Paragraph("Network Efficiency", subtitle_style))
            
            network_data = stats['network_load']
            
            # Wykres kołowy efektywności
            efficiency_data = {
                'Payload': network_data.get('payload_bytes', 0),
                'Headers/Overhead': network_data.get('total_bytes', 0) - network_data.get('payload_bytes', 0)
            }
            
            chart_img = self.create_pie_chart(
                efficiency_data,
                f"Network Efficiency: {network_data.get('payload_efficiency', 0):.1f}%"
            )
            if chart_img:
                elements.append(Image(chart_img, width=400, height=300))
            elements.append(Spacer(1, 0.3*inch))
        
        # TOP IP ADDRESSES
        if 'top_ips' in options and stats.get('top_ips'):
            elements.append(Paragraph("Most Common IP Addresses", subtitle_style))
            
            top_ips_sorted = sorted(stats['top_ips'].items(), key=lambda x: x[1], reverse=True)[:15]
            
            ip_table_data = [["IP Address", "Packet Count"]]
            for ip, count in top_ips_sorted:
                ip_table_data.append([ip, str(count)])
            
            ip_table = Table(ip_table_data, colWidths=[300, 200])
            ip_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(ip_table)
            elements.append(Spacer(1, 0.3*inch))
        
        # Dodanie numeracji stron
        def add_page_number(canvas, doc):
            canvas.saveState()
            canvas.setFont('Helvetica', 10)
            canvas.drawCentredString(
                doc.pagesize[0] / 2, 
                20, 
                f"Page {canvas.getPageNumber()}"
            )
            canvas.restoreState()
        
        # Budowanie dokumentu PDF
        doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
        
        return report_path
    
    def create_pie_chart(self, data, title):
        """Tworzenie wykresu kołowego"""
        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            
            if isinstance(data, dict):
                labels = list(data.keys())
                values = list(data.values())
            else:
                labels = data.get('labels', [])
                values = data.get('values', [])
            
            colors_list = plt.cm.Set3(range(len(labels)))
            wedges, texts, autotexts = ax.pie(
                values, 
                labels=labels, 
                autopct='%1.1f%%',
                colors=colors_list,
                startangle=90
            )
            
            # Poprawa czytelności etykiet
            for text in texts:
                text.set_fontsize(9)
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(8)
            
            ax.set_title(title, fontsize=12, fontweight='bold', pad=20)
            plt.tight_layout()
            
            img_data = BytesIO()
            plt.savefig(img_data, format='png', bbox_inches='tight', dpi=150)
            img_data.seek(0)
            plt.close(fig)
            
            return img_data
            
        except Exception as e:
            print(f"Error creating pie chart: {e}")
            plt.close('all')
            return None
    
    def create_bar_chart(self, data, title):
        """Tworzenie wykresu słupkowego"""
        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            
            labels = data.get('labels', [])
            values = data.get('values', [])
            
            ax.bar(labels, values, color='skyblue', edgecolor='navy')
            ax.set_xlabel('', fontsize=10)
            ax.set_ylabel('Count', fontsize=10)
            ax.set_title(title, fontsize=12, fontweight='bold', pad=20)
            
            plt.xticks(rotation=45, ha='right', fontsize=9)
            plt.yticks(fontsize=9)
            ax.grid(True, linestyle='--', alpha=0.3)
            plt.tight_layout()
            
            img_data = BytesIO()
            plt.savefig(img_data, format='png', bbox_inches='tight', dpi=150)
            img_data.seek(0)
            plt.close(fig)
            
            return img_data
            
        except Exception as e:
            print(f"Error creating bar chart: {e}")
            plt.close('all')
            return None
    
    def create_line_chart(self, data, title):
        """Tworzenie wykresu liniowego"""
        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            
            labels = data.get('labels', [])
            values = data.get('values', [])
            
            ax.plot(labels, values, marker='o', linestyle='-', linewidth=2, markersize=4)
            ax.set_xlabel('', fontsize=10)
            ax.set_ylabel('Value', fontsize=10)
            ax.set_title(title, fontsize=12, fontweight='bold', pad=20)
            
            # Ograniczenie liczby etykiet na osi X
            if len(labels) > 10:
                step = len(labels) // 10
                ax.set_xticks(range(0, len(labels), step))
                ax.set_xticklabels([labels[i] for i in range(0, len(labels), step)])
            
            plt.xticks(rotation=45, ha='right', fontsize=8)
            plt.yticks(fontsize=9)
            ax.grid(True, linestyle='--', alpha=0.3)
            plt.tight_layout()
            
            img_data = BytesIO()
            plt.savefig(img_data, format='png', bbox_inches='tight', dpi=150)
            img_data.seek(0)
            plt.close(fig)
            
            return img_data
            
        except Exception as e:
            print(f"Error creating line chart: {e}")
            plt.close('all')
            return None
    
    def create_histogram(self, data, title):
        """Tworzenie histogramu"""
        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            
            labels = data.get('labels', [])
            values = data.get('values', [])
            
            ax.bar(labels, values, color='lightgreen', edgecolor='darkgreen')
            ax.set_xlabel('Packet Size (bytes)', fontsize=10)
            ax.set_ylabel('Count', fontsize=10)
            ax.set_title(title, fontsize=12, fontweight='bold', pad=20)
            
            plt.xticks(rotation=45, ha='right', fontsize=9)
            plt.yticks(fontsize=9)
            ax.grid(True, linestyle='--', alpha=0.3)
            plt.tight_layout()
            
            img_data = BytesIO()
            plt.savefig(img_data, format='png', bbox_inches='tight', dpi=150)
            img_data.seek(0)
            plt.close(fig)
            
            return img_data
            
        except Exception as e:
            print(f"Error creating histogram: {e}")
            plt.close('all')
            return None
    
    def export_csv(self, packets):
        """Eksport pakietów do pliku CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"packets_{timestamp}.csv"
        csv_path = os.path.join(self.upload_folder, csv_filename)
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['packet_number', 'time', 'length', 'src_mac', 'dst_mac', 
                         'src_ip', 'dst_ip', 'protocol', 'src_port', 'dst_port']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for packet in packets:
                row = {
                    'packet_number': packet.get('packet_number', ''),
                    'time': packet.get('time', ''),
                    'length': packet.get('length', ''),
                    'src_mac': packet.get('ethernet', {}).get('src', ''),
                    'dst_mac': packet.get('ethernet', {}).get('dst', ''),
                    'src_ip': packet.get('ip', {}).get('src', ''),
                    'dst_ip': packet.get('ip', {}).get('dst', ''),
                    'protocol': self.get_protocol_name(packet),
                    'src_port': self.get_port(packet, 'sport'),
                    'dst_port': self.get_port(packet, 'dport')
                }
                writer.writerow(row)
        return csv_path
    
    def generate_filtered_pdf(self, filename, packets, filters):
        """Generowanie raportu dla przefiltrowanych pakietów"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"filtered_report_{timestamp}.pdf"
        report_path = os.path.join(self.upload_folder, report_filename)
        
        doc = SimpleDocTemplate(report_path, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        elements.append(Paragraph(f"Filtered Report - {filename}", styles['Heading1']))
        elements.append(Paragraph(f"Total packets: {len(packets)}", styles['Normal']))
        elements.append(Spacer(1, 0.5*inch))
        
        # Filter summary
        elements.append(Paragraph("Applied Filters:", styles['Heading2']))
        filter_data = [["Filter", "Value"]]
        for k, v in filters.items():
            if v:
                filter_data.append([k, str(v)])
        
        if len(filter_data) > 1:
            filter_table = Table(filter_data, colWidths=[150, 350])
            filter_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(filter_table)
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Statystyki przefiltrowanych pakietów
        elements.append(Paragraph("Filtered Packets Statistics:", styles['Heading2']))
        
        # Oblicz podstawowe statystyki
        protocols = {}
        for packet in packets:
            proto = self.get_protocol_name(packet)
            protocols[proto] = protocols.get(proto, 0) + 1
        
        stats_data = [["Metric", "Value"]]
        stats_data.append(["Total Packets", str(len(packets))])
        for proto, count in sorted(protocols.items(), key=lambda x: x[1], reverse=True)[:5]:
            stats_data.append([f"Protocol: {proto}", str(count)])
        
        stats_table = Table(stats_data, colWidths=[200, 300])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(stats_table)
        
        doc.build(elements)
        return report_path
    
    def get_protocol_name(self, packet):
        """Pomocnicza funkcja do określania protokołu"""
        if 'tcp' in packet:
            return 'TCP'
        elif 'udp' in packet:
            return 'UDP'
        elif 'icmp' in packet:
            return 'ICMP'
        elif 'arp' in packet:
            return 'ARP'
        elif 'dns' in packet:
            return 'DNS'
        elif 'http' in packet:
            return 'HTTP'
        elif 'https' in packet:
            return 'HTTPS'
        elif 'ip' in packet:
            return f"IP({packet['ip'].get('proto', 'Unknown')})"
        return 'Other'
    
    def get_port(self, packet, port_type):
        """Pomocnicza funkcja do pobierania portu"""
        if 'tcp' in packet:
            return packet['tcp'].get(port_type, '')
        elif 'udp' in packet:
            return packet['udp'].get(port_type, '')
        return ''