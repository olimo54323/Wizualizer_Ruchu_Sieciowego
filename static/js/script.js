// Funkcje wizualizacji ruchu sieciowego
document.addEventListener('DOMContentLoaded', function() {
    // Inicjalizacja wyszukiwania pakietów
    initPacketSearch();
    
    // Inicjalizacja wykresów, jeśli są dostępne dane
    if (document.getElementById('protocolChart')) {
        initCharts();
    }
    
    // Inicjalizacja interfejsu generowania raportów, jeśli jest dostępny
    if (document.getElementById('generateReportBtn')) {
        initReportGenerator();
    }

    if (document.getElementById('networkMetricsDisplay')) {
        displayNetworkMetrics();
    }
    
    // Inicjalizacja zaawansowanego podglądu pakietów
    initAdvancedPacketViewer();
    
    // Inicjalizacja funkcjonalności filtrowanego raportu
    initFilteredReportGenerator();

    window.dispatchEvent(new Event('resize'));
});

window.addEventListener('resize', function() {
    // Aktualizacja wysokości kontenerów wykresów
    const chartContainers = document.querySelectorAll('.chart-container');
    const windowHeight = window.innerHeight;
    
    chartContainers.forEach(container => {
        // Ustaw wysokość kontenera na procent wysokości okna
        const newHeight = Math.max(250, windowHeight * 0.3); // Minimum 250px, maksymalnie 30% wysokości okna
        container.style.height = `${newHeight}px`;
    });
});

// Wyszukiwanie pakietów
function initPacketSearch() {
    const searchInput = document.getElementById('packetSearch');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase();
        const packetItems = document.querySelectorAll('.packet-item');
        
        packetItems.forEach(item => {
            const text = item.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    });
}

// Inicjalizacja wykresów
function initCharts() {
    // Wykres protokołów
    if (document.getElementById('protocolChart')) {
        initProtocolChart();
    }
    
    // Wykres portów
    if (document.getElementById('portChart')) {
        initPortChart();
    }
    
    // Wykres adresów MAC
    if (document.getElementById('macChart')) {
        initMacChart();
    }
    
    // Wykres producentów MAC
    if (document.getElementById('vendorChart')) {
        initVendorChart();
    }
    
    // Wykres czasowy
    if (document.getElementById('timeChart')) {
        initTimeChart();
    }
    
     // Wykres wielkości pakietów
   if (document.getElementById('packetSizeChart')) {
       initPacketSizeChart();
   }
   
   // Wykres komunikacji między hostami (sieć)
   if (document.getElementById('networkGraph')) {
       initNetworkGraph();
   }

   if (document.getElementById('payloadChart')) {
        initPayloadChart();
    }
    
    if (document.getElementById('throughputChart')) {
        initThroughputChart();
    }
    
    if (document.getElementById('protocolPayloadChart')) {
        initProtocolPayloadChart();
    }
    
    if (document.getElementById('networkEfficiencyChart')) {
        initNetworkEfficiencyChart();
    }
    
    if (document.getElementById('enhancedMacGraph')) {
        initEnhancedMacGraph();
    }
}

// Wykres payload (bar chart)
function initPayloadChart() {
    const payloadCtx = document.getElementById('payloadChart').getContext('2d');
    const payloadData = JSON.parse(document.getElementById('payloadStatsData').textContent);
    
    const chartData = {
        labels: ['Średni Payload', 'Max Payload', 'Min Payload'],
        datasets: [{
            label: 'Bajty',
            data: [
                payloadData.avg_payload_per_packet,
                payloadData.max_payload_size,
                payloadData.min_payload_size
            ],
            backgroundColor: [
                'rgba(54, 162, 235, 0.7)',
                'rgba(255, 99, 132, 0.7)',
                'rgba(255, 206, 86, 0.7)'
            ],
            borderColor: [
                'rgba(54, 162, 235, 1)',
                'rgba(255, 99, 132, 1)',
                'rgba(255, 206, 86, 1)'
            ],
            borderWidth: 1
        }]
    };
    
    new Chart(payloadCtx, {
        type: 'bar',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Bajty'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Statystyki Payload'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y.toFixed(2)} bajtów`;
                        }
                    }
                }
            }
        }
    });
}

// Wykres throughput (linia czasu)
function initThroughputChart() {
    const throughputCtx = document.getElementById('throughputChart');
    if (!throughputCtx) {
        console.log('Element throughputChart nie został znaleziony');
        return;
    }
    
    const throughputDataElement = document.getElementById('throughputStatsData');
    if (!throughputDataElement) {
        console.log('Element throughputStatsData nie został znaleziony');
        throughputCtx.parentElement.innerHTML = '<div class="alert alert-info text-center">Brak elementu danych throughput</div>';
        return;
    }
    
    if (!throughputDataElement.textContent) {
        console.log('throughputStatsData jest pusty');
        throughputCtx.parentElement.innerHTML = '<div class="alert alert-info text-center">Brak danych throughput</div>';
        return;
    }
    
    try {
        const throughputData = JSON.parse(throughputDataElement.textContent);
        console.log('Dane throughput:', throughputData);
        
        // Sprawdzenie czy dane są kompletne
        if (!throughputData || 
            !throughputData.time_labels || 
            !throughputData.bytes_per_second ||
            throughputData.time_labels.length === 0 ||
            throughputData.bytes_per_second.length === 0) {
            
            console.log('Niekompletne dane throughput:', throughputData);
            throughputCtx.parentElement.innerHTML = '<div class="alert alert-info text-center">Brak danych do wyświetlenia wykresu throughput</div>';
            return;
        }
        
        // Utworzenie wykresu
        new Chart(throughputCtx, {
            type: 'line',
            data: {
                labels: throughputData.time_labels,
                datasets: [{
                    label: 'Przepustowość (bajty/s)',
                    data: throughputData.bytes_per_second,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderWidth: 2,
                    tension: 0.1,
                    fill: true,
                    pointRadius: 3,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Przepustowość sieci w czasie',
                        font: {
                            size: 16
                        }
                    },
                    legend: {
                        display: true,
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.parsed.y;
                                if (value > 1024 * 1024) {
                                    return `${(value / 1024 / 1024).toFixed(2)} MB/s`;
                                } else if (value > 1024) {
                                    return `${(value / 1024).toFixed(2)} KB/s`;
                                } else {
                                    return `${value} B/s`;
                                }
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Czas'
                        },
                        grid: {
                            display: true,
                            color: 'rgba(0,0,0,0.1)'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Przepustowość (bajty/s)'
                        },
                        beginAtZero: true,
                        grid: {
                            display: true,
                            color: 'rgba(0,0,0,0.1)'
                        },
                        ticks: {
                            callback: function(value) {
                                if (value > 1024 * 1024) {
                                    return (value / 1024 / 1024).toFixed(1) + ' MB/s';
                                } else if (value > 1024) {
                                    return (value / 1024).toFixed(1) + ' KB/s';
                                } else {
                                    return value + ' B/s';
                                }
                            }
                        }
                    }
                }
            }
        });
        
        console.log('Wykres throughput został utworzony pomyślnie');
        
    } catch (error) {
        console.error('Błąd podczas tworzenia wykresu throughput:', error);
        throughputCtx.parentElement.innerHTML = '<div class="alert alert-danger text-center">Błąd podczas ładowania wykresu throughput</div>';
    }
}

// Wykres payload według protokołów (bar chart z dwiema osiami Y)
function initProtocolPayloadChart() {
    const protocolPayloadCtx = document.getElementById('protocolPayloadChart').getContext('2d');
    const protocolPayloadData = JSON.parse(document.getElementById('protocolPayloadData').textContent);
    
    const protocols = Object.keys(protocolPayloadData);
    const payloadTotals = protocols.map(proto => protocolPayloadData[proto].total);
    const avgPayloads = protocols.map(proto => 
        protocolPayloadData[proto].packets > 0 ? 
        protocolPayloadData[proto].total / protocolPayloadData[proto].packets : 0
    );
    
    new Chart(protocolPayloadCtx, {
        type: 'bar',
        data: {
            labels: protocols,
            datasets: [{
                label: 'Całkowity Payload (bajty)',
                data: payloadTotals,
                backgroundColor: 'rgba(54, 162, 235, 0.7)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1,
                yAxisID: 'y'
            }, {
                label: 'Średni Payload na pakiet (bajty)',
                data: avgPayloads,
                backgroundColor: 'rgba(255, 159, 64, 0.7)',
                borderColor: 'rgba(255, 159, 64, 1)',
                borderWidth: 1,
                yAxisID: 'y1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Payload według protokołów'
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Całkowity Payload (bajty)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Średni Payload (bajty)'
                    },
                    grid: {
                        drawOnChartArea: false,
                    }
                }
            }
        }
    });
}

// Wykres efektywności sieci
function initNetworkEfficiencyChart() {
    const efficiencyCtx = document.getElementById('networkEfficiencyChart').getContext('2d');
    const networkLoadData = JSON.parse(document.getElementById('networkLoadData').textContent);
    
    const payloadBytes = networkLoadData.total_bytes - networkLoadData.header_overhead;
    
    new Chart(efficiencyCtx, {
        type: 'doughnut',
        data: {
            labels: ['Payload (Dane użyteczne)', 'Nagłówki (Overhead)'],
            datasets: [{
                data: [payloadBytes, networkLoadData.header_overhead],
                backgroundColor: [
                    'rgba(75, 192, 192, 0.7)',
                    'rgba(255, 99, 132, 0.7)'
                ],
                borderColor: [
                    'rgba(75, 192, 192, 1)',
                    'rgba(255, 99, 132, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `Efektywność sieci: ${networkLoadData.payload_efficiency.toFixed(1)}%`
                },
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed * 100) / total).toFixed(1);
                            return `${context.label}: ${context.parsed.toLocaleString()} bajtów (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Dodaj funkcję do wyświetlania metryk w interface
function displayNetworkMetrics() {
    // Funkcja może być wywołana do wyświetlenia podsumowania metryk
    try {
        const payloadStats = JSON.parse(document.getElementById('payloadStatsData').textContent);
        const throughputStats = JSON.parse(document.getElementById('throughputStatsData').textContent);
        const networkLoad = JSON.parse(document.getElementById('networkLoadData').textContent);
        
        const metricsContainer = document.getElementById('networkMetricsDisplay');
        if (metricsContainer) {
            metricsContainer.innerHTML = `
                <div class="row">
                    <div class="col-md-3">
                        <div class="card">
                            <div class="card-body text-center">
                                <h5>Całkowity Payload</h5>
                                <h3 class="text-primary">${(payloadStats.total_payload_bytes / 1024 / 1024).toFixed(2)} MB</h3>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card">
                            <div class="card-body text-center">
                                <h5>Średni Throughput</h5>
                                <h3 class="text-success">${(throughputStats.avg_throughput / 1024).toFixed(2)} KB/s</h3>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card">
                            <div class="card-body text-center">
                                <h5>Peak Throughput</h5>
                                <h3 class="text-warning">${(throughputStats.peak_throughput / 1024).toFixed(2)} KB/s</h3>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card">
                            <div class="card-body text-center">
                                <h5>Efektywność</h5>
                                <h3 class="text-info">${networkLoad.payload_efficiency.toFixed(1)}%</h3>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error displaying network metrics:', error);
    }
}

// Wykres protokołów (Pie Chart)
function initProtocolChart() {
    const protocolCtx = document.getElementById('protocolChart').getContext('2d');
    const protocolData = JSON.parse(document.getElementById('protocolData').textContent);
    
    // Konfiguracja z lepszym zarządzaniem responsywnością
    new Chart(protocolCtx, {
        type: 'pie',
        data: {
            labels: Object.keys(protocolData),
            datasets: [{
                data: Object.values(protocolData),
                backgroundColor: [
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(255, 206, 86, 0.7)',
                    'rgba(75, 192, 192, 0.7)',
                    'rgba(153, 102, 255, 0.7)',
                    'rgba(255, 159, 64, 0.7)',
                    'rgba(201, 203, 207, 0.7)'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Rozkład protokołów',
                    font: {
                        size: 16
                    }
                },
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 15,
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    });
}

// Wykres portów (Bar Chart)
function initPortChart() {
   const portCtx = document.getElementById('portChart').getContext('2d');
   const portData = JSON.parse(document.getElementById('portData').textContent);
   
   const ports = portData.map(item => `Port ${item.port}`);
   const counts = portData.map(item => item.count);
   
   new Chart(portCtx, {
       type: 'bar',
       data: {
           labels: ports,
           datasets: [{
               label: 'Liczba pakietów',
               data: counts,
               backgroundColor: 'rgba(54, 162, 235, 0.7)',
               borderColor: 'rgba(54, 162, 235, 1)',
               borderWidth: 1
           }]
       },
       options: {
           responsive: true,
           maintainAspectRatio: false,
           scales: {
               y: {
                   beginAtZero: true,
                   title: {
                       display: true,
                       text: 'Liczba pakietów'
                   }
               },
               x: {
                   title: {
                       display: true,
                       text: 'Numery portów'
                   }
               }
           },
           plugins: {
               title: {
                   display: true,
                   text: 'Najczęściej używane porty'
               }
           }
       }
   });
}

// Wykres adresów MAC (Bar Chart)
function initMacChart() {
   const macCtx = document.getElementById('macChart').getContext('2d');
   const macData = JSON.parse(document.getElementById('macData').textContent);
   
   const macs = macData.map(item => item.mac.slice(-8)); // Pokazujemy tylko ostatnie 8 znaków dla czytelności
   const counts = macData.map(item => item.count);
   
   new Chart(macCtx, {
       type: 'bar',
       data: {
           labels: macs,
           datasets: [{
               label: 'Liczba pakietów',
               data: counts,
               backgroundColor: 'rgba(153, 102, 255, 0.7)',
               borderColor: 'rgba(153, 102, 255, 1)',
               borderWidth: 1
           }]
       },
       options: {
           responsive: true,
           maintainAspectRatio: false,
           scales: {
               y: {
                   beginAtZero: true,
                   title: {
                       display: true,
                       text: 'Liczba pakietów'
                   }
               },
               x: {
                   title: {
                       display: true,
                       text: 'Adresy MAC (ostatnie 8 znaków)'
                   }
               }
           },
           plugins: {
               title: {
                   display: true,
                   text: 'Najczęściej używane adresy MAC'
               },
               tooltip: {
                   callbacks: {
                       title: function(tooltipItems) {
                           // Pokazuje pełny adres MAC w tooltipie
                           const index = tooltipItems[0].dataIndex;
                           return macData[index].mac;
                       }
                   }
               }
           }
       }
   });
}

// Wykres producentów MAC (Pie Chart)
function initVendorChart() {
   const vendorCtx = document.getElementById('vendorChart').getContext('2d');
   const vendorData = JSON.parse(document.getElementById('vendorData').textContent);
   
   const vendors = Object.keys(vendorData);
   const counts = Object.values(vendorData);
   
   new Chart(vendorCtx, {
       type: 'pie',
       data: {
           labels: vendors,
           datasets: [{
               data: counts,
               backgroundColor: [
                   'rgba(255, 99, 132, 0.7)',
                   'rgba(54, 162, 235, 0.7)',
                   'rgba(255, 206, 86, 0.7)',
                   'rgba(75, 192, 192, 0.7)',
                   'rgba(153, 102, 255, 0.7)',
                   'rgba(255, 159, 64, 0.7)',
                   'rgba(201, 203, 207, 0.7)'
               ]
           }]
       },
       options: {
           responsive: true,
           maintainAspectRatio: false,
           plugins: {
               title: {
                   display: true,
                   text: 'Producenci urządzeń'
               },
               legend: {
                   position: 'right'
               }
           }
       }
   });
}

// Wykres czasowy ruchu (Line Chart)
function initTimeChart() {
   const timeCtx = document.getElementById('timeChart').getContext('2d');
   const timeData = JSON.parse(document.getElementById('timeData').textContent);
   
   new Chart(timeCtx, {
       type: 'line',
       data: {
           labels: timeData.labels,
           datasets: [{
               label: 'Liczba pakietów',
               data: timeData.values,
               borderColor: 'rgba(75, 192, 192, 1)',
               backgroundColor: 'rgba(75, 192, 192, 0.2)',
               borderWidth: 2,
               tension: 0.1,
               fill: true
           }]
       },
       options: {
           responsive: true,
           maintainAspectRatio: false,
           scales: {
               y: {
                   beginAtZero: true,
                   title: {
                       display: true,
                       text: 'Liczba pakietów'
                   }
               },
               x: {
                   title: {
                       display: true,
                       text: 'Czas'
                   }
               }
           },
           plugins: {
               title: {
                   display: true,
                   text: 'Rozkład czasowy ruchu'
               }
           }
       }
   });
}

// Wykres wielkości pakietów (Histogram)
function initPacketSizeChart() {
   const sizeCtx = document.getElementById('packetSizeChart').getContext('2d');
   const sizeData = JSON.parse(document.getElementById('packetSizeData').textContent);
   
   new Chart(sizeCtx, {
       type: 'bar',
       data: {
           labels: sizeData.labels,
           datasets: [{
               label: 'Liczba pakietów',
               data: sizeData.values,
               backgroundColor: 'rgba(255, 99, 132, 0.7)',
               borderColor: 'rgba(255, 99, 132, 1)',
               borderWidth: 1
           }]
       },
       options: {
           responsive: true,
           maintainAspectRatio: false,
           scales: {
               y: {
                   beginAtZero: true,
                   title: {
                       display: true,
                       text: 'Liczba pakietów'
                   }
               },
               x: {
                   title: {
                       display: true,
                       text: 'Wielkość pakietu (bajty)'
                   }
               }
           },
           plugins: {
               title: {
                   display: true,
                   text: 'Rozkład wielkości pakietów'
               }
           }
       }
   });
}


// Wspólne kolory i konfiguracja dla obu grafów
const UNIFIED_COLORS = {
    // Dla grafu IP (typy adresów)
    'Lokalne': '#96CEB4',
    'APIPA': '#FECA57', 
    'Publiczne': '#54A0FF',
    'Specjalne': '#FF6B6B',
    'Inne': '#4ECDC4',
    
    // Dla grafu MAC (protokoły)
    'TCP': '#FF6B6B',
    'UDP': '#4ECDC4',
    'ICMP': '#45B7D1',
    'ARP': '#96CEB4',
    'DNS': '#FECA57',
    'HTTP': '#FF9FF3',
    'HTTPS': '#54A0FF',
    'Other': '#DDA0DD',
    'Unknown': '#C8C8C8'
};

// Wspólna funkcja tworzenia legendy
function createUnifiedLegend(containerId, title, colorMap) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // Usuń istniejącą legendę
    const existingLegend = container.querySelector('.network-legend');
    if (existingLegend) existingLegend.remove();
    
    const legendContainer = document.createElement('div');
    legendContainer.className = 'network-legend';
    legendContainer.style.cssText = `
        position: absolute;
        top: 10px;
        right: 10px;
        background: rgba(255, 255, 255, 0.95);
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #ddd;
        font-size: 12px;
        font-family: Arial, sans-serif;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        z-index: 1000;
        max-width: 200px;
    `;
    
    let legendHTML = `<strong style="color: #333; margin-bottom: 8px; display: block;">${title}:</strong>`;
    Object.entries(colorMap).forEach(([type, color]) => {
        legendHTML += `
            <div style="margin: 4px 0; display: flex; align-items: center;">
                <span style="display: inline-block; width: 14px; height: 14px; background: ${color}; margin-right: 8px; border-radius: 50%; border: 1px solid #333;"></span>
                <span style="color: #333; font-size: 11px;">${type}</span>
            </div>
        `;
    });
    
    legendContainer.innerHTML = legendHTML;
    container.style.position = 'relative';
    container.appendChild(legendContainer);
}

// Graf IP - zunifikowany z kodem z dokumentu
function initNetworkGraph() {
    const networkContainer = document.getElementById('networkGraph');
    if (!networkContainer) return;
    
    const networkDataElement = document.getElementById('networkGraphData') || document.getElementById('networkData');
    if (!networkDataElement || !networkDataElement.textContent) {
        networkContainer.innerHTML = '<div class="alert alert-info text-center">Brak danych grafu IP</div>';
        return;
    }
    
    try {
        const networkData = JSON.parse(networkDataElement.textContent);
        
        if (!networkData || !networkData.nodes || networkData.nodes.length === 0) {
            networkContainer.innerHTML = '<div class="alert alert-info text-center">Brak danych do wyświetlenia grafu IP</div>';
            return;
        }
        
        // Przygotowanie węzłów z lepszym kolorowaniem - kod z dokumentu
        const nodes = new vis.DataSet(networkData.nodes.map(node => {
            let nodeColor = UNIFIED_COLORS.Inne;
            let ipType = 'Inne prywatne';
            
            if (node.id.startsWith('192.168.') || node.id.startsWith('10.') || node.id.startsWith('172.')) {
                nodeColor = UNIFIED_COLORS.Lokalne;
                ipType = 'Lokalne';
            } else if (node.id.startsWith('169.254.')) {
                nodeColor = UNIFIED_COLORS.APIPA;
                ipType = 'APIPA';
            } else if (node.id === '0.0.0.0' || node.id === '255.255.255.255') {
                nodeColor = UNIFIED_COLORS.Specjalne;
                ipType = 'Specjalne';
            } else if (!node.id.startsWith('192.168.') && !node.id.startsWith('10.') && 
                      !node.id.startsWith('172.') && !node.id.startsWith('169.254.')) {
                nodeColor = UNIFIED_COLORS.Publiczne;
                ipType = 'Publiczne';
            }
            
            const connections = networkData.edges.filter(edge => 
                edge.from === node.id || edge.to === node.id
            ).length;
            
            return {
                ...node,
                color: {
                    background: nodeColor,
                    border: '#000000',
                    highlight: {
                        background: nodeColor,
                        border: '#ff0000'
                    }
                },
                font: {
                    color: '#000000',
                    size: 12,
                    face: 'Arial'
                },
                shape: 'dot',
                size: Math.max(15, Math.min(50, node.value * 2)),
                borderWidth: 2,
                shadow: {
                    enabled: true,
                    color: 'rgba(0,0,0,0.3)',
                    size: 10,
                    x: 3,
                    y: 3
                },
                title: `IP: ${node.id}\nTyp: ${ipType}\nPakiety: ${node.value}\nPołączenia: ${connections}`,
                ipType: ipType,
                connections: connections
            };
        }));
        
        const edges = new vis.DataSet(networkData.edges.map(edge => ({
            ...edge,
            width: Math.max(1, Math.min(8, edge.value / 3)),
            color: {
                color: '#848484',
                highlight: '#ff0000',
                hover: '#999999'
            },
            smooth: {
                type: 'continuous',
                roundness: 0.5
            },
            arrows: {
                to: { 
                    enabled: true, 
                    scaleFactor: 1.2,
                    type: 'arrow'
                }
            },
            shadow: {
                enabled: true,
                color: 'rgba(0,0,0,0.2)',
                size: 5,
                x: 2,
                y: 2
            },
            title: `${edge.from} → ${edge.to}\nPakiety: ${edge.value}`
        })));
        
        const data = { nodes, edges };
        const options = {
            nodes: {
                borderWidth: 2,
                shadow: true,
                scaling: {
                    min: 15,
                    max: 50,
                    label: {
                        enabled: true,
                        min: 10,
                        max: 16,
                        maxVisible: 30,
                        drawThreshold: 5
                    }
                }
            },
            edges: {
                arrows: {
                    to: { enabled: true, scaleFactor: 1.2 }
                },
                shadow: true,
                smooth: {
                    type: 'continuous',
                    forceDirection: 'none',
                    roundness: 0.5
                }
            },
            physics: {
                enabled: true,
                solver: 'repulsion',
                repulsion: {
                    centralGravity: 0.1, 
                    springLength: 150,       
                    springConstant: 0.02,    
                    nodeDistance: 200,       
                    damping: 0.09
                }
            },
            interaction: {
                hover: true,
                tooltipDelay: 300,
                selectConnectedEdges: false,
                hoverConnectedEdges: true,
                zoomView: true,
                dragView: true,
                navigationButtons: true,
                keyboard: true
            },
            layout: {
                improvedLayout: true,
                randomSeed: 42
            }
        };
        
        networkContainer.style.height = '500px';
        const network = new vis.Network(networkContainer, data, options);
        
        // Dodaj legendę i kontrolki
        createUnifiedLegend('networkGraph', 'Typy adresów IP', {
            'Lokalne (192.168.x.x, 10.x.x.x)': UNIFIED_COLORS.Lokalne,
            'APIPA (169.254.x.x)': UNIFIED_COLORS.APIPA,
            'Publiczne': UNIFIED_COLORS.Publiczne,
            'Specjalne (0.0.0.0, 255.x.x.x)': UNIFIED_COLORS.Specjalne,
            'Inne prywatne': UNIFIED_COLORS.Inne
        });
        
        
    } catch (error) {
        console.error('Błąd podczas tworzenia grafu IP:', error);
        networkContainer.innerHTML = '<div class="alert alert-danger text-center">Błąd podczas ładowania grafu IP</div>';
    }
}

// Graf MAC - zunifikowany z kodem z dokumentu
function initEnhancedMacGraph() {
    const macContainer = document.getElementById('enhancedMacGraph');
    if (!macContainer) return;
    
    const macDataElement = document.getElementById('enhancedMacGraphData');
    if (!macDataElement || !macDataElement.textContent) {
        macContainer.innerHTML = '<div class="alert alert-info text-center">Graf niedostępny - brak danych</div>';
        return;
    }
    
    try {
        const macData = JSON.parse(macDataElement.textContent);
        
        if (!macData || !macData.nodes || macData.nodes.length === 0) {
            macContainer.innerHTML = '<div class="alert alert-info text-center">Graf niedostępny - brak komunikacji MAC</div>';
            return;
        }
        
        // Przygotowanie węzłów z protokołami
        const nodes = new vis.DataSet(macData.nodes.map(node => {
            const protocol = node.protocol || 'Unknown';
            const nodeColor = UNIFIED_COLORS[protocol] || UNIFIED_COLORS.Unknown;
            
            return {
                ...node,
                color: {
                    background: nodeColor,
                    border: '#000000',
                    highlight: {
                        background: nodeColor,
                        border: '#ff0000'
                    }
                },
                font: {
                    color: '#000000',
                    size: 12,
                    face: 'Arial'
                },
                shape: 'dot',
                size: Math.max(15, Math.min(50, (node.value || 1) / 2)),
                borderWidth: 2,
                shadow: {
                    enabled: true,
                    color: 'rgba(0,0,0,0.3)',
                    size: 10,
                    x: 3,
                    y: 3
                },
                title: `MAC: ${node.id}\nVendor: ${node.vendor || 'Unknown'}\nDominujący: ${protocol}\nPakiety: ${node.value || 0}`
            };
        }));
        
        const edges = new vis.DataSet((macData.edges || []).map(edge => ({
            ...edge,
            width: Math.max(1, Math.min(8, (edge.value || 1) / 3)),
            color: {
                color: '#848484',
                highlight: '#ff0000',
                hover: '#999999'
            },
            smooth: {
                type: 'continuous',
                roundness: 0.5
            },
            arrows: {
                to: {
                    enabled: true,
                    scaleFactor: 1.2
                }
            },
            shadow: {
                enabled: true,
                color: 'rgba(0,0,0,0.2)',
                size: 5,
                x: 2,
                y: 2
            },
            title: edge.title || `Packets: ${edge.value || 0}`
        })));
        
        const data = { nodes, edges };
        const options = {
            nodes: {
                borderWidth: 2,
                shadow: true,
                scaling: {
                    min: 15,
                    max: 50,
                    label: {
                        enabled: true,
                        min: 10,
                        max: 16,
                        maxVisible: 30,
                        drawThreshold: 5
                    }
                }
            },
            edges: {
                arrows: {
                    to: { enabled: true, scaleFactor: 1.2 }
                },
                shadow: true,
                smooth: {
                    type: 'continuous',
                    forceDirection: 'none',
                    roundness: 0.5
                }
            },
            physics: {
                enabled: true,
                solver: 'repulsion',
                repulsion: {
                    centralGravity: 0.1,    
                    springLength: 150,      
                    springConstant: 0.02,   
                    nodeDistance: 200,    
                    damping: 0.09
                }
            },
            interaction: {
                hover: true,
                tooltipDelay: 200,
                selectConnectedEdges: false,
                hoverConnectedEdges: true,
                zoomView: true,
                dragView: true,
                navigationButtons: true,
                keyboard: true
            },
            layout: {
                improvedLayout: true,
                randomSeed: 42
            }
        };
        
        macContainer.style.height = '500px';
        const network = new vis.Network(macContainer, data, options);
        
        const protocolsInGraph = [...new Set(macData.nodes.map(n => n.protocol).filter(p => p))];
        const legendItems = {};
        protocolsInGraph.forEach(protocol => {
            if (UNIFIED_COLORS[protocol]) {
                legendItems[protocol] = UNIFIED_COLORS[protocol];
            }
        });
        
        createUnifiedLegend('enhancedMacGraph', 'Dominujące protokoły', legendItems);
        
    } catch (error) {
        console.error('Błąd parsowania danych grafu MAC:', error);
        macContainer.innerHTML = '<div class="alert alert-warning text-center">Graf niedostępny - błąd przetwarzania</div>';
    }
}

function initAdvancedPacketViewer() {
    // Sprawdź czy DataTable już istnieje i zniszcz je
    if ($.fn.DataTable.isDataTable('#packetsTable')) {
        $('#packetsTable').DataTable().destroy();
    }
    
    // Inicjalizacja DataTables dla tabeli pakietów
    if (document.getElementById('packetsTable')) {
        $('#packetsTable').DataTable({
            pageLength: 25,
            order: [[0, 'asc']],
            responsive: true,
            destroy: true,
            columnDefs: [
                { responsivePriority: 1, targets: 0 },
                { responsivePriority: 2, targets: 1 },
                { responsivePriority: 3, targets: 2 }
            ],
            language: {
                "lengthMenu": "Pokaż _MENU_ wpisów na stronie",
                "zeroRecords": "Nie znaleziono pasujących pakietów",
                "info": "Pokazuje _START_ do _END_ z _TOTAL_ pakietów",
                "infoEmpty": "Pokazuje 0 do 0 z 0 pakietów",
                "infoFiltered": "(filtrowane z _MAX_ wszystkich pakietów)",
                "search": "Szukaj:",
                "paginate": {
                    "first": "Pierwszy",
                    "last": "Ostatni", 
                    "next": "Następny",
                    "previous": "Poprzedni"
                }
            }
        });
    }
    
    // Obsługa przycisków szczegółów pakietów - z delegacją zdarzeń
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('packet-details-btn')) {
            e.preventDefault();
            e.stopPropagation();
            
            const packetId = e.target.getAttribute('data-packet-id');
            console.log('Kliknięto przycisk szczegółów dla pakietu:', packetId);
            
            const packetDataElement = document.getElementById(`packet-data-${packetId}`);
            
            if (!packetDataElement) {
                console.error(`Nie znaleziono elementu packet-data-${packetId}`);
                alert('Nie można załadować szczegółów pakietu - brak danych');
                return;
            }
            
            const jsonContent = packetDataElement.textContent || packetDataElement.innerHTML;
            if (!jsonContent.trim()) {
                console.error(`Element packet-data-${packetId} jest pusty`);
                alert('Nie można załadować szczegółów pakietu - dane są puste');
                return;
            }
            
            try {
                console.log('Parsowanie JSON dla pakietu:', packetId);
                const packetData = JSON.parse(jsonContent);
                console.log('Dane pakietu:', packetData);
                displayPacketDetails(packetId, packetData);
            } catch (error) {
                console.error('Błąd parsowania danych pakietu:', error);
                console.error('JSON content:', jsonContent);
                alert('Błąd podczas ładowania szczegółów pakietu: nieprawidłowy format danych');
            }
        }
    });
}

function displayPacketDetails(packetId, packetData) {
    console.log('Wyświetlanie szczegółów pakietu:', packetId, packetData);
    
    // Sprawdź czy modal istnieje, jeśli nie - stwórz go
    let modal = document.getElementById('packetModal');
    if (!modal) {
        modal = createPacketModal();
        document.body.appendChild(modal);
    }
    
    // Wypełnij modal danymi
    const modalLabel = modal.querySelector('#packetModalLabel');
    const modalBody = modal.querySelector('#packetModalBody');
    
    if (!modalLabel || !modalBody) {
        console.error('Nie znaleziono elementów modalu');
        return;
    }
    
    modalLabel.textContent = `Pakiet #${packetId}`;
    
    // Generuj zawartość modalu
    modalBody.innerHTML = generatePacketDetailsHTML(packetData);
    
    // POPRAWKA: Prawidłowe zamknięcie modalu z obsługą błędów
    try {
        const modalInstance = new bootstrap.Modal(modal, {
            backdrop: true,
            keyboard: true
        });
        
        // Usuń poprzednie event listenery
        modal.removeEventListener('hidden.bs.modal', handleModalHidden);
        modal.removeEventListener('hide.bs.modal', handleModalHide);
        
        // Dodaj event listenery do prawidłowego zamknięcia
        modal.addEventListener('hidden.bs.modal', handleModalHidden);
        modal.addEventListener('hide.bs.modal', handleModalHide);
        
        modalInstance.show();
        console.log('Modal został wyświetlony');
        
    } catch (error) {
        console.error('Błąd podczas wyświetlania modalu:', error);
        alert('Błąd podczas otwierania okna szczegółów pakietu');
    }
}

function handleModalHide(event) {
    console.log('Modal się ukrywa...');
}

function handleModalHidden(event) {
    console.log('Modal został ukryty, czyszczenie...');
    
    // Wymuś usunięcie wszystkich backdrop-ów
    const backdrops = document.querySelectorAll('.modal-backdrop');
    backdrops.forEach(backdrop => {
        console.log('Usuwanie backdrop:', backdrop);
        backdrop.remove();
    });
    
    // Przywróć normalny stan body
    document.body.classList.remove('modal-open');
    document.body.style.overflow = '';
    document.body.style.paddingRight = '';
    
    // Usuń atrybut modal-open jeśli istnieje
    if (document.body.hasAttribute('data-bs-modal-open')) {
        document.body.removeAttribute('data-bs-modal-open');
    }
    
    console.log('Czyszczenie modalu zakończone');
}

function createPacketModal() {
    console.log('Tworzenie nowego modalu pakietu');
    
    // Usuń stary modal jeśli istnieje
    const existingModal = document.getElementById('packetModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    const modalHTML = `
        <div class="modal fade" id="packetModal" tabindex="-1" aria-labelledby="packetModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="packetModalLabel">Szczegóły Pakietu</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Zamknij"></button>
                    </div>
                    <div class="modal-body" id="packetModalBody">
                        <div class="text-center">
                            <div class="spinner-border" role="status">
                                <span class="visually-hidden">Ładowanie...</span>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Zamknij</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = modalHTML.trim();
    return tempDiv.firstElementChild;
}

function generatePacketDetailsHTML(packetData) {
    console.log('Generowanie HTML dla pakietu:', packetData);
    
    // Bezpieczne pobieranie czasu
    let displayTime = 'N/A';
    if (packetData.time_str) {
        displayTime = packetData.time_str;
    } else if (packetData.time) {
        displayTime = formatPacketTime(packetData.time);
    }
    
    // Bezpieczne sprawdzenie istnienia sekcji
    const hasEthernet = packetData.ethernet && typeof packetData.ethernet === 'object';
    const hasIP = packetData.ip && typeof packetData.ip === 'object';
    const hasTCP = packetData.tcp && typeof packetData.tcp === 'object';
    const hasUDP = packetData.udp && typeof packetData.udp === 'object';
    
    return `
        <div class="packet-tabs">
            <ul class="nav nav-tabs" id="packetTab" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="summary-tab" data-bs-toggle="tab" 
                            data-bs-target="#summary" type="button" role="tab">
                        Podsumowanie
                    </button>
                </li>
                ${hasEthernet ? `
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="ethernet-tab" data-bs-toggle="tab" 
                                data-bs-target="#ethernet" type="button" role="tab">
                            Ethernet
                        </button>
                    </li>
                ` : ''}
                ${hasIP ? `
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="ip-tab" data-bs-toggle="tab" 
                                data-bs-target="#ip" type="button" role="tab">
                            IP
                        </button>
                    </li>
                ` : ''}
                ${hasTCP ? `
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="tcp-tab" data-bs-toggle="tab" 
                                data-bs-target="#tcp" type="button" role="tab">
                            TCP
                        </button>
                    </li>
                ` : ''}
                ${hasUDP ? `
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="udp-tab" data-bs-toggle="tab" 
                                data-bs-target="#udp" type="button" role="tab">
                            UDP
                        </button>
                    </li>
                ` : ''}
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="raw-tab" data-bs-toggle="tab" 
                            data-bs-target="#raw" type="button" role="tab">
                        Raw JSON
                    </button>
                </li>
            </ul>
            <div class="tab-content" id="packetTabContent" style="margin-top: 15px;">
                <!-- Zakładka Podsumowanie -->
                <div class="tab-pane fade show active" id="summary" role="tabpanel">
                    <table class="table table-striped">
                        <tr><th width="30%">Numer pakietu</th><td>${packetData.packet_number || 'N/A'}</td></tr>
                        <tr><th>Czas</th><td>${displayTime}</td></tr>
                        <tr><th>Długość</th><td>${packetData.length || 0} bajtów</td></tr>
                        ${hasEthernet ? `
                            <tr><th>MAC Źródło</th><td><code>${packetData.ethernet.src}</code></td></tr>
                            <tr><th>MAC Cel</th><td><code>${packetData.ethernet.dst}</code></td></tr>
                            <tr><th>Producent (Źródło)</th><td>${packetData.ethernet.src_vendor || 'Unknown'}</td></tr>
                            <tr><th>Producent (Cel)</th><td>${packetData.ethernet.dst_vendor || 'Unknown'}</td></tr>
                        ` : ''}
                        ${hasIP ? `
                            <tr><th>IP Źródło</th><td><code>${packetData.ip.src}</code></td></tr>
                            <tr><th>IP Cel</th><td><code>${packetData.ip.dst}</code></td></tr>
                            <tr><th>Protokół IP</th><td>${packetData.ip.proto || 'N/A'}</td></tr>
                        ` : ''}
                        ${hasTCP ? `
                            <tr><th>Port źródłowy</th><td>${packetData.tcp.sport}</td></tr>
                            <tr><th>Port docelowy</th><td>${packetData.tcp.dport}</td></tr>
                            <tr><th>Flagi TCP</th><td>${formatTcpFlags(packetData.tcp)}</td></tr>
                        ` : ''}
                        ${hasUDP ? `
                            <tr><th>Port źródłowy</th><td>${packetData.udp.sport}</td></tr>
                            <tr><th>Port docelowy</th><td>${packetData.udp.dport}</td></tr>
                        ` : ''}
                    </table>
                </div>
                
                <!-- Zakładka Ethernet -->
                ${hasEthernet ? `
                    <div class="tab-pane fade" id="ethernet" role="tabpanel">
                        <table class="table table-striped">
                            <tr><th width="30%">MAC Źródło</th><td><code>${packetData.ethernet.src}</code></td></tr>
                            <tr><th>MAC Cel</th><td><code>${packetData.ethernet.dst}</code></td></tr>
                            <tr><th>Typ</th><td>${packetData.ethernet.type || 'N/A'}</td></tr>
                            <tr><th>Producent (Źródło)</th><td>${packetData.ethernet.src_vendor || 'Unknown'}</td></tr>
                            <tr><th>Producent (Cel)</th><td>${packetData.ethernet.dst_vendor || 'Unknown'}</td></tr>
                        </table>
                    </div>
                ` : ''}
                
                <!-- Zakładka IP -->
                ${hasIP ? `
                    <div class="tab-pane fade" id="ip" role="tabpanel">
                        <table class="table table-striped">
                            <tr><th width="30%">Wersja</th><td>${packetData.ip.version || 'N/A'}</td></tr>
                            <tr><th>IP Źródło</th><td><code>${packetData.ip.src}</code></td></tr>
                            <tr><th>IP Cel</th><td><code>${packetData.ip.dst}</code></td></tr>
                            <tr><th>Protokół</th><td>${packetData.ip.proto || 'N/A'}</td></tr>
                            <tr><th>TTL</th><td>${packetData.ip.ttl || 'N/A'}</td></tr>
                            <tr><th>Długość</th><td>${packetData.ip.len || 'N/A'} bajtów</td></tr>
                        </table>
                    </div>
                ` : ''}
                
                <!-- Zakładka TCP -->
                ${hasTCP ? `
                    <div class="tab-pane fade" id="tcp" role="tabpanel">
                        <table class="table table-striped">
                            <tr><th width="30%">Port źródłowy</th><td>${packetData.tcp.sport}</td></tr>
                            <tr><th>Port docelowy</th><td>${packetData.tcp.dport}</td></tr>
                            <tr><th>Numer sekwencyjny</th><td>${packetData.tcp.seq || 'N/A'}</td></tr>
                            <tr><th>Numer potwierdzenia</th><td>${packetData.tcp.ack || 'N/A'}</td></tr>
                            <tr><th>Rozmiar okna</th><td>${packetData.tcp.window || 'N/A'}</td></tr>
                            <tr><th>Flagi</th><td>${formatTcpFlags(packetData.tcp)}</td></tr>
                        </table>
                    </div>
                ` : ''}
                
                <!-- Zakładka UDP -->
                ${hasUDP ? `
                    <div class="tab-pane fade" id="udp" role="tabpanel">
                        <table class="table table-striped">
                            <tr><th width="30%">Port źródłowy</th><td>${packetData.udp.sport}</td></tr>
                            <tr><th>Port docelowy</th><td>${packetData.udp.dport}</td></tr>
                            <tr><th>Długość</th><td>${packetData.udp.len || 'N/A'} bajtów</td></tr>
                        </table>
                    </div>
                ` : ''}
                
                <!-- Zakładka Raw JSON -->
                <div class="tab-pane fade" id="raw" role="tabpanel">
                    <pre style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; max-height: 400px; overflow-y: auto;"><code class="language-json">${JSON.stringify(packetData, null, 2)}</code></pre>
                </div>
            </div>
        </div>
    `;
}

function formatTcpFlags(tcp) {
    if (!tcp) return 'N/A';
    
    const flags = [];
    
    // Sprawdź różne możliwe formaty flag
    if (tcp.flags_syn === true || (tcp.flags && tcp.flags.includes('S'))) flags.push('SYN');
    if (tcp.flags_ack === true || (tcp.flags && tcp.flags.includes('A'))) flags.push('ACK');
    if (tcp.flags_fin === true || (tcp.flags && tcp.flags.includes('F'))) flags.push('FIN');
    if (tcp.flags_rst === true || (tcp.flags && tcp.flags.includes('R'))) flags.push('RST');
    if (tcp.flags_psh === true || (tcp.flags && tcp.flags.includes('P'))) flags.push('PSH');
    if (tcp.flags_urg === true || (tcp.flags && tcp.flags.includes('U'))) flags.push('URG');
    
    // Jeśli nie znaleziono flag w powyższy sposób, spróbuj z raw flags
    if (flags.length === 0 && tcp.flags) {
        return tcp.flags.toString();
    }
    
    return flags.length > 0 ? flags.join(', ') : 'Brak flag';
}

function formatPacketTime(timeValue) {
    if (typeof timeValue === 'number') {
        return new Date(timeValue * 1000).toISOString().replace('T', ' ').substring(0, 23);
    } else if (typeof timeValue === 'string') {
        return timeValue;
    }
    return 'N/A';
}

// Generator raportów PDF
function initReportGenerator() {
    const reportBtn = document.getElementById('generateReportBtn');
    if (!reportBtn) return;
    
    reportBtn.addEventListener('click', function() {
        const reportModal = new bootstrap.Modal(document.getElementById('reportModal'));
        reportModal.show();
    });
    
    // Obsługa przycisku "Zaznacz wszystko"
    const selectAllBtn = document.getElementById('selectAllBtn');
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', function() {
            const checkboxes = document.querySelectorAll('#reportOptionsAccordion input[type="checkbox"], #reportOptions input[type="checkbox"]');
            checkboxes.forEach(checkbox => {
                checkbox.checked = true;
            });
        });
    }
    // Obsługa przycisku "Odznacz wszystko"
    const deselectAllBtn = document.getElementById('deselectAllBtn');
    if (deselectAllBtn) {
        deselectAllBtn.addEventListener('click', function() {
            const checkboxes = document.querySelectorAll('#reportOptionsAccordion input[type="checkbox"], #reportOptions input[type="checkbox"]');
            checkboxes.forEach(checkbox => {
                checkbox.checked = false;
            });
            // NIE POKAZUJ komunikatu błędu przy odznaczaniu
        });
    }
    
    // Obsługa formularza generowania raportu
    const generateForm = document.getElementById('generateReportForm');
    if (generateForm) {
        generateForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Zbieranie zaznaczonych opcji
            const options = [];
            const checkboxes = document.querySelectorAll('#reportOptionsAccordion input[type="checkbox"]:checked, #reportOptions input[type="checkbox"]:checked');
            
            checkboxes.forEach(checkbox => {
                options.push(checkbox.value);
            });
            
            // Sprawdzenie czy cokolwiek jest zaznaczone TYLKO przy wysyłaniu
            if (options.length === 0) {
                alert('Zaznacz co najmniej jedną opcję do wygenerowania raportu.');
                return;
            }
            
            // Zamknięcie modalu
            const modal = bootstrap.Modal.getInstance(document.getElementById('reportModal'));
            if (modal) modal.hide();
            
            // Przekierowanie z parametrami
            const params = new URLSearchParams();
            options.forEach(option => {
                params.append('options[]', option);
            });
            
            // Użyj właściwej zmiennej (filename lub analysisId)
            const targetId = typeof filename !== 'undefined' ? filename : 
                           (typeof analysisId !== 'undefined' ? analysisId : 'unknown');
            
            window.location.href = `/generate_report/${targetId}?${params.toString()}`;
        });
    }
}

// Generator filtrowanych raportów
function initFilteredReportGenerator() {
   const filteredReportBtn = document.getElementById('generateFilteredReportBtn');
   const filteredCSVBtn = document.getElementById('generateFilteredCSVBtn');
   
   if (filteredReportBtn) {
       // Obsługa kliknięcia przycisku "Raport z filtrów"
       filteredReportBtn.addEventListener('click', function() {
           generateFilteredExport('report');
       });
   }
   
   if (filteredCSVBtn) {
       // Obsługa kliknięcia przycisku "Filtrowany CSV"
       filteredCSVBtn.addEventListener('click', function() {
           generateFilteredExport('csv');
       });
   }
   
   // Wspólna funkcja do generowania eksportów
   function generateFilteredExport(exportType) {
       // Pobieranie wartości filtrów
       const srcMac = document.getElementById('filter-src-mac').value;
       const dstMac = document.getElementById('filter-dst-mac').value;
       const srcIp = document.getElementById('filter-src-ip').value;
       const dstIp = document.getElementById('filter-dst-ip').value;
       const protocol = document.getElementById('filter-protocol').value;
       const port = document.getElementById('filter-port').value;
       const lengthMin = document.getElementById('filter-length-min').value;
       const lengthMax = document.getElementById('filter-length-max').value;
       const timeStart = document.getElementById('filter-time-start').value;
       const timeEnd = document.getElementById('filter-time-end').value;
       
       // Przygotowanie danych do wysłania
       const filterData = {
           srcMac: srcMac,
           dstMac: dstMac,
           srcIp: srcIp,
           dstIp: dstIp,
           protocol: protocol,
           port: port,
           lengthMin: lengthMin,
           lengthMax: lengthMax,
           timeStart: timeStart,
           timeEnd: timeEnd
       };
       
       // Określenie przycisku i endpointu
       let button, endpoint, loadingText, originalText;
       
       if (exportType === 'csv') {
           button = filteredCSVBtn;
           endpoint = `/export_filtered_csv/${analysisId}`;
           loadingText = '<i class="fas fa-spinner fa-spin"></i> Eksportowanie CSV...';
           originalText = '<i class="fas fa-file-csv"></i> Filtrowany CSV';
       } else {
           button = filteredReportBtn;
           endpoint = `/generate_filtered_report/${analysisId}`;
           loadingText = '<i class="fas fa-spinner fa-spin"></i> Generowanie raportu...';
           originalText = '<i class="fas fa-file-pdf"></i> Raport z filtrów';
       }
       
       // Wyświetlenie informacji o trwającym generowaniu
       button.disabled = true;
       button.innerHTML = loadingText;
       
       // Wysłanie żądania do serwera
       fetch(endpoint, {
           method: 'POST',
           headers: {
               'Content-Type': 'application/json',
           },
           body: JSON.stringify(filterData)
       })
       .then(response => {
           if (!response.ok) {
               throw new Error('Network response was not ok');
           }
           return response.json();
       })
       .then(data => {
           // Przywrócenie przycisku
           button.disabled = false;
           button.innerHTML = originalText;
           
           if (data.success) {
               // Przekierowanie do pobrania wygenerowanego pliku
               if (exportType === 'csv') {
                   window.location.href = data.csv_url;
                   // Wyświetl informację o liczbie wyeksportowanych pakietów
                   alert(`Wyeksportowano ${data.total_packets} pakietów do pliku CSV.`);
               } else {
                   window.location.href = data.report_url;
               }
           } else {
               alert(`Błąd ${exportType === 'csv' ? 'eksportu CSV' : 'generowania raportu'}: ${data.error}`);
           }
       })
       .catch(error => {
           console.error('Error:', error);
           // Przywrócenie przycisku
           button.disabled = false;
           button.innerHTML = originalText;
           alert(`Wystąpił błąd podczas ${exportType === 'csv' ? 'eksportu CSV' : 'generowania raportu'}. Sprawdź konsolę przeglądarki.`);
       });
   }
   
   // Obsługa przycisku "Zastosuj filtry"
   const applyFiltersBtn = document.getElementById('apply-filters');
   if (applyFiltersBtn) {
       applyFiltersBtn.addEventListener('click', function() {
           // Tutaj można dodać kod do filtrowania tabeli bez generowania raportu PDF
           // Na przykład filtrowanie w DataTables
           
           // Pobieranie wartości filtrów
           const srcMac = document.getElementById('filter-src-mac').value.toLowerCase();
           const dstMac = document.getElementById('filter-dst-mac').value.toLowerCase();
           const srcIp = document.getElementById('filter-src-ip').value.toLowerCase();
           const dstIp = document.getElementById('filter-dst-ip').value.toLowerCase();
           const protocol = document.getElementById('filter-protocol').value;
           const port = document.getElementById('filter-port').value;
           const lengthMin = parseInt(document.getElementById('filter-length-min').value) || 0;
           const lengthMax = parseInt(document.getElementById('filter-length-max').value) || Number.MAX_SAFE_INTEGER;
           
           // Zastosowanie niestandardowego filtra do DataTables
           const dataTable = $('#packetsTable').DataTable();
           
           // Własny filtr wyszukiwania
           $.fn.dataTable.ext.search.push(
               function(settings, data, dataIndex) {
                   // Indeksy kolumn w tabeli
                   const srcMacIdx = 2; // MAC Źródłowe
                   const dstMacIdx = 3; // MAC Docelowe
                   const srcIdx = 5;    // Źródło IP
                   const dstIdx = 6;    // Cel IP
                   const protoIdx = 7;  // Protokół
                   const portsIdx = 8;  // Porty
                   const lengthIdx = 9; // Długość
                   
                   // Dane z wiersza
                   const rowSrcMac = data[srcMacIdx].toLowerCase();
                   const rowDstMac = data[dstMacIdx].toLowerCase();
                   const rowSrc = data[srcIdx].toLowerCase();
                   const rowDst = data[dstIdx].toLowerCase();
                   const rowProto = data[protoIdx];
                   const rowPorts = data[portsIdx];
                   const rowLength = parseInt(data[lengthIdx]) || 0;
                   
                   // Sprawdzanie warunków filtrowania
                   let match = true;
                   
                   if (srcMac && !rowSrcMac.includes(srcMac)) match = false;
                   if (dstMac && !rowDstMac.includes(dstMac)) match = false;
                   if (srcIp && !rowSrc.includes(srcIp)) match = false;
                   if (dstIp && !rowDst.includes(dstIp)) match = false;
                   if (protocol && rowProto !== protocol) match = false;
                   if (port && !rowPorts.includes(port)) match = false;
                   if (rowLength < lengthMin || rowLength > lengthMax) match = false;
                   
                   return match;
               }
           );
           
           // Przeładowanie tabeli z uwzględnieniem filtrów
           dataTable.draw();
           
           // Usunięcie filtra po zastosowaniu
           $.fn.dataTable.ext.search.pop();
       });
   }
   
   // Obsługa przycisku "Resetuj filtry"
   const resetFiltersBtn = document.getElementById('reset-filters');
   if (resetFiltersBtn) {
       resetFiltersBtn.addEventListener('click', function() {
           // Czyszczenie pól filtrów
           document.getElementById('filter-src-mac').value = '';
           document.getElementById('filter-dst-mac').value = '';
           document.getElementById('filter-src-ip').value = '';
           document.getElementById('filter-dst-ip').value = '';
           document.getElementById('filter-protocol').value = '';
           document.getElementById('filter-port').value = '';
           document.getElementById('filter-length-min').value = '';
           document.getElementById('filter-length-max').value = '';
           document.getElementById('filter-time-start').value = '';
           document.getElementById('filter-time-end').value = '';
           
           // Przywrócenie oryginalnej tabeli
           $('#packetsTable').DataTable().search('').columns().search('').draw();
       });
   }
}