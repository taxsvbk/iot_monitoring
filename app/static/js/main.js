// Initialize the charts
let temperatureChart, humidityChart, lightChart;
const maxDataPoints = 20; // Maximum number of points to show

function initializeCharts() {
    const commonOptions = {
        type: 'line',
        options: {
            animation: false,
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'second',
                        displayFormats: {
                            second: 'HH:mm:ss'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    beginAtZero: false
                }
            },
            plugins: {
                legend: {
                    display: true
                }
            }
        }
    };

    // Temperature Chart
    const tempCtx = document.getElementById('temperatureChart').getContext('2d');
    temperatureChart = new Chart(tempCtx, {
        ...commonOptions,
        data: {
            datasets: [{
                label: 'Temperature (°C)',
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                fill: true,
                data: []
            }]
        }
    });

    // Humidity Chart
    const humCtx = document.getElementById('humidityChart').getContext('2d');
    humidityChart = new Chart(humCtx, {
        ...commonOptions,
        data: {
            datasets: [{
                label: 'Humidity (%)',
                borderColor: 'rgb(54, 162, 235)',
                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                fill: true,
                data: []
            }]
        }
    });

    // Light Chart
    const lightCtx = document.getElementById('lightChart').getContext('2d');
    lightChart = new Chart(lightCtx, {
        ...commonOptions,
        data: {
            datasets: [{
                label: 'Light (lux)',
                borderColor: 'rgb(255, 206, 86)',
                backgroundColor: 'rgba(255, 206, 86, 0.1)',
                fill: true,
                data: []
            }]
        }
    });
}

function updateCharts() {
    fetch('/api/sensor-data')
        .then(response => response.json())
        .then(data => {
            const latestData = data.reduce((latest, current) => {
                return (!latest || current.timestamp > latest.timestamp) ? current : latest;
            }, null);

            if (latestData) {
                const timestamp = new Date(latestData.timestamp * 1000);
                
                // Update temperature chart
                temperatureChart.data.datasets[0].data.push({
                    x: timestamp,
                    y: latestData.temperature
                });

                // Update humidity chart
                humidityChart.data.datasets[0].data.push({
                    x: timestamp,
                    y: latestData.humidity
                });

                // Update light chart
                lightChart.data.datasets[0].data.push({
                    x: timestamp,
                    y: latestData.light
                });

                // Remove old data points if exceeding maxDataPoints
                if (temperatureChart.data.datasets[0].data.length > maxDataPoints) {
                    temperatureChart.data.datasets[0].data.shift();
                    humidityChart.data.datasets[0].data.shift();
                    lightChart.data.datasets[0].data.shift();
                }

                temperatureChart.update();
                humidityChart.update();
                lightChart.update();
            }
        })
        .catch(error => console.error('Error fetching sensor data:', error));
}

// Initialize charts when the page loads
document.addEventListener('DOMContentLoaded', () => {
    initializeCharts();
    // Update every 2 seconds
    setInterval(updateCharts, 2000);
}); 