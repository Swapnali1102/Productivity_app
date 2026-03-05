// Main JavaScript functionality for Productivity Tracker

// Auto-hide flash messages
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });
});

// Modal functionality
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// Close modal when clicking outside
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('form-modal')) {
        event.target.style.display = 'none';
    }
});

// Confirmation dialogs
function confirmDelete(message = 'Are you sure you want to delete this item?') {
    return confirm(message);
}

// Date formatting utilities
function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Local storage utilities
function saveToLocalStorage(key, data) {
    localStorage.setItem(key, JSON.stringify(data));
}

function getFromLocalStorage(key) {
    const data = localStorage.getItem(key);
    return data ? JSON.parse(data) : null;
}

// Timer functionality
let timerInterval;
let timerSeconds = 0;
let isTimerRunning = false;

function startTimer(duration = 1500) { // 25 minutes default
    if (isTimerRunning) return;
    
    timerSeconds = duration;
    isTimerRunning = true;
    
    timerInterval = setInterval(() => {
        timerSeconds--;
        updateTimerDisplay();
        
        if (timerSeconds <= 0) {
            stopTimer();
            onTimerComplete();
        }
    }, 1000);
    
    updateTimerControls();
}

function stopTimer() {
    clearInterval(timerInterval);
    isTimerRunning = false;
    updateTimerControls();
}

function resetTimer() {
    stopTimer();
    timerSeconds = 0;
    updateTimerDisplay();
}

function updateTimerDisplay() {
    const minutes = Math.floor(timerSeconds / 60);
    const seconds = timerSeconds % 60;
    const display = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    
    const timerDisplay = document.getElementById('timerDisplay');
    if (timerDisplay) {
        timerDisplay.textContent = display;
    }
    
    // Update page title with timer
    if (isTimerRunning) {
        document.title = `${display} - Focus Timer`;
    }
}

function updateTimerControls() {
    const startBtn = document.getElementById('startTimer');
    const stopBtn = document.getElementById('stopTimer');
    
    if (startBtn && stopBtn) {
        startBtn.disabled = isTimerRunning;
        stopBtn.disabled = !isTimerRunning;
    }
}

function onTimerComplete() {
    // Play notification sound (if available)
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('Focus Session Complete!', {
            body: 'Great job! Time for a break.',
            icon: '/static/favicon.ico'
        });
    }
    
    // Reset page title
    document.title = 'Personal Productivity Tracker';
    
    // Show completion message
    alert('Focus session complete! Great job!');
}

// Request notification permission
if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
}

// Chart utilities (for analytics)
function createSimpleChart(canvasId, data, labels) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Simple bar chart implementation
    const maxValue = Math.max(...data);
    const barWidth = width / data.length;
    
    data.forEach((value, index) => {
        const barHeight = (value / maxValue) * (height - 40);
        const x = index * barWidth;
        const y = height - barHeight - 20;
        
        // Draw bar
        ctx.fillStyle = '#667eea';
        ctx.fillRect(x + 5, y, barWidth - 10, barHeight);
        
        // Draw label
        ctx.fillStyle = '#333';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(labels[index], x + barWidth/2, height - 5);
        
        // Draw value
        ctx.fillText(value, x + barWidth/2, y - 5);
    });
}

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Ctrl/Cmd + N for new entry (diary)
    if ((event.ctrlKey || event.metaKey) && event.key === 'n') {
        const writeBtn = document.querySelector('a[href*="write_entry"]');
        if (writeBtn) {
            event.preventDefault();
            window.location.href = writeBtn.href;
        }
    }
    
    // Escape to close modals
    if (event.key === 'Escape') {
        const modals = document.querySelectorAll('.form-modal');
        modals.forEach(modal => {
            if (modal.style.display === 'block') {
                modal.style.display = 'none';
            }
        });
    }
});

// Auto-save functionality for forms
function enableAutoSave(formId, storageKey) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    // Load saved data
    const savedData = getFromLocalStorage(storageKey);
    if (savedData) {
        Object.keys(savedData).forEach(key => {
            const field = form.querySelector(`[name="${key}"]`);
            if (field) {
                field.value = savedData[key];
            }
        });
    }
    
    // Save on input
    form.addEventListener('input', function(event) {
        const formData = new FormData(form);
        const data = {};
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        saveToLocalStorage(storageKey, data);
    });
    
    // Clear saved data on submit
    form.addEventListener('submit', function() {
        localStorage.removeItem(storageKey);
    });
}