// Navigation & UI Functions
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('active');
}

function showNotification(message, type = 'info') {
    // Show toast notification
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 5000);
}

function setActiveNav(page) {
    // Highlight active navigation item
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.page === page) {
            link.classList.add('active');
        }
    });
}

// Form Validation
function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function validatePhone(phone) {
    return /^[6-9]\d{9}$/.test(phone);
}

function validatePassword(password) {
    return password.length >= 8;
}

function checkPasswordStrength(password) {
    if (!password) return '';
    if (window.Utils && typeof window.Utils.getPasswordStrength === 'function') {
        return window.Utils.getPasswordStrength(password).message;
    }
    if (password.length < 8) return 'Weak';
    if (password.length < 12) return 'Medium';
    return 'Strong';
}

// Donor Availability Toggle
async function updateDonorAvailability(available) {
    if (window.API?.donor) {
        return API.donor.updateAvailability(available);
    }
}

function toggleAvailability() {
    const toggle = document.getElementById('availabilityToggle');
    const status = document.getElementById('availabilityStatus');
    
    if (toggle.checked) {
        status.textContent = 'Available';
        status.className = 'badge-success';
        // API call to update availability
        updateDonorAvailability(true);
    } else {
        status.textContent = 'Not Available';
        status.className = 'badge-danger';
        updateDonorAvailability(false);
    }
}

// Emergency Level Selection
function setEmergencyLevel(level) {
    const buttons = document.querySelectorAll('.emergency-btn');
    buttons.forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.level === level) {
            btn.classList.add('active');
        }
    });
    document.getElementById('emergencyLevel').value = level;
}

// Blood Group Display
const bloodGroupColors = {
    'A+': '#FF6B6B',
    'A-': '#FF4757',
    'B+': '#2ED573',
    'B-': '#2BCB70',
    'AB+': '#FFA502',
    'AB-': '#F9CA24',
    'O+': '#1E90FF',
    'O-': '#3742FA'
};

function getBloodGroupColor(group) {
    return bloodGroupColors[group] || '#6C757D';
}