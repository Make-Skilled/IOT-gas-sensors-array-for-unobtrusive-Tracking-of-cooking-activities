// Enhanced Chart Configuration
const chartConfig = {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Temperature (°C)',
            data: [],
            borderColor: '#3498db',
            backgroundColor: 'rgba(52, 152, 219, 0.1)',
            fill: true,
            tension: 0.4,
            pointRadius: 4,
            pointHoverRadius: 6
        }, {
            label: 'Gas Level (ppm)',
            data: [],
            borderColor: '#e74c3c',
            backgroundColor: 'rgba(231, 76, 60, 0.1)',
            fill: true,
            tension: 0.4,
            pointRadius: 4,
            pointHoverRadius: 6
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    usePointStyle: true,
                    padding: 20
                }
            },
            tooltip: {
                mode: 'index',
                intersect: false,
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                padding: 12,
                borderColor: 'white',
                borderWidth: 1,
                titleFont: {
                    size: 14,
                    weight: 'bold'
                },
                bodyFont: {
                    size: 13
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                grid: {
                    drawBorder: false,
                    color: 'rgba(0, 0, 0, 0.05)'
                }
            },
            x: {
                grid: {
                    display: false
                }
            }
        },
        interaction: {
            intersect: false,
            mode: 'nearest'
        }
    }
};

// Initialize Chart.js
const ctx = document.getElementById('sensorChart').getContext('2d');
const sensorChart = new Chart(ctx, chartConfig);

// Enhanced Data Fetching with Error Handling
async function fetchSensorData() {
    try {
        const response = await fetch('/get_data');
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        
        updateUI(data);
        updateChart(data);
        checkAlerts(data);
    } catch (error) {
        console.error('Error fetching sensor data:', error);
        showErrorNotification('Failed to update sensor data');
    }
}

// Enhanced UI Updates
function updateUI(data) {
    // Update with smooth transitions
    const elements = {
        temperature: document.getElementById('temperature'),
        gasLevel: document.getElementById('gas-level'),
        systemStatus: document.getElementById('system-status')
    };

    Object.entries(elements).forEach(([key, element]) => {
        if (element) {
            const newValue = key === 'temperature' ? `${data[key]} °C` :
                           key === 'gasLevel' ? `${data[key]} ppm` :
                           data[key];
            
            if (element.textContent !== newValue) {
                element.style.animation = 'pulse 0.3s ease';
                element.textContent = newValue;
                setTimeout(() => element.style.animation = '', 300);
            }
        }
    });

    updateStatusIndicators(data);
}

// Status Indicators
function updateStatusIndicators(data) {
    const statusClasses = {
        normal: 'active',
        warning: 'warning',
        danger: 'danger'
    };

    const status = determineStatus(data);
    const indicator = document.querySelector('.status-indicator');
    
    if (indicator) {
        // Remove all possible status classes
        Object.values(statusClasses).forEach(cls => 
            indicator.classList.remove(cls));
        
        // Add current status class
        indicator.classList.add(statusClasses[status]);
    }
}

// Alert System
function checkAlerts(data) {
    const alerts = [];
    
    if (data.temperature > 80) {
        alerts.push({
            type: 'danger',
            message: 'High temperature detected!'
        });
    }
    
    if (data.gas_level > 1000) {
        alerts.push({
            type: 'danger',
            message: 'Dangerous gas levels detected!'
        });
    }

    alerts.forEach(alert => showNotification(alert));
}

// Modern Notifications
function showNotification({ type, message }) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close">&times;</button>
        </div>
    `;

    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => notification.classList.add('show'), 100);

    // Auto dismiss
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 5000);

    // Close button
    notification.querySelector('.notification-close').onclick = () => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    };
}

function updateGasStatus(gasLevel) {
    const statusElement = document.getElementById('gas-status');
    if (gasLevel < 500) {
        statusElement.textContent = 'Normal';
        statusElement.className = 'status-normal';
    } else if (gasLevel < 800) {
        statusElement.textContent = 'Warning';
        statusElement.className = 'status-warning';
    } else {
        statusElement.textContent = 'Danger';
        statusElement.className = 'status-danger';
    }
}

function updateChart(data) {
    const timestamp = new Date().toLocaleTimeString();
    
    sensorChart.data.labels.push(timestamp);
    sensorChart.data.datasets[0].data.push(data.temperature);
    sensorChart.data.datasets[1].data.push(data.gas_level);

    // Keep only last 10 data points
    if (sensorChart.data.labels.length > 10) {
        sensorChart.data.labels.shift();
        sensorChart.data.datasets[0].data.shift();
        sensorChart.data.datasets[1].data.shift();
    }

    sensorChart.update();
}

function updateRecipeInfo() {
    const recipeSelect = document.getElementById('recipe_type');
    const recipeInfo = document.getElementById('recipe_info');
    const dishNameInput = document.getElementById('dish_name');
    const cookingTimeInput = document.getElementById('cooking_time');
    const temperatureInput = document.getElementById('temperature');

    if (recipeSelect.value && recipeSelect.value !== 'custom') {
        fetch(`/get_cooking_guide/${recipeSelect.value}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('recommended_temp').textContent = data.recommended_temp;
                document.getElementById('recommended_time').textContent = data.cooking_time;
                document.getElementById('cooking_tips').textContent = data.tips;
                
                dishNameInput.value = data.name;
                cookingTimeInput.value = data.cooking_time;
                temperatureInput.value = data.recommended_temp;
                
                recipeInfo.classList.remove('hidden');
            });
    } else {
        recipeInfo.classList.add('hidden');
        dishNameInput.value = '';
        cookingTimeInput.value = '';
        temperatureInput.value = '';
    }
}

function updateStep(activityIndex, step) {
    fetch(`/update_step/${activityIndex}/${step}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                location.reload();
            }
        })
        .catch(error => console.error('Error updating step:', error));
}

// Add new cooking activity
function addActivity(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    fetch('/add_activity', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            location.reload(); // Refresh page to show new activity
        }
    })
    .catch(error => console.error('Error adding activity:', error));

    return false;
}

// Complete cooking activity
function completeActivity(index) {
    fetch(`/complete_activity/${index}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                location.reload(); // Refresh page to update status
            }
        })
        .catch(error => console.error('Error completing activity:', error));
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeChart();
    fetchSensorData();
    setInterval(fetchSensorData, 2000);
});

