/* ============================
   BLOOD NEED - INTERACTIVE FEATURES
   ============================ */

'use strict';

// ---------- REAL-TIME COUNTERS ----------
function initCounters() {
    // Donor counter
    const donorCount = document.getElementById('donorCount');
    if (donorCount) {
        animateCounter(donorCount, 0, 256, 3000);
    }
    
    // Request counter
    const requestCount = document.getElementById('requestCount');
    if (requestCount) {
        animateCounter(requestCount, 0, 48, 2000);
    }
    
    // Lives saved counter
    const livesCount = document.getElementById('livesCount');
    if (livesCount) {
        animateCounter(livesCount, 0, 1024, 4000);
    }
}

function animateCounter(element, start, end, duration) {
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const current = Math.floor(start + (end - start) * easeOutQuart(progress));
        element.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

function easeOutQuart(t) {
    return 1 - Math.pow(1 - t, 4);
}

// ---------- NOTIFICATION PUSH SIMULATION ----------
function simulateNotification(message, type = 'info') {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('🩸 Blood Need', {
            body: message,
            icon: '🩸'
        });
    }
    showNotification(message, type);
}

// Request notification permission
function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
}

// ---------- PROGRESS ANIMATION ----------
function animateProgressBar(element, target, duration = 1000) {
    const start = 0;
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const current = start + (target - start) * easeOutQuart(progress);
        element.style.width = `${current}%`;
        element.textContent = `${Math.round(current)}%`;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

// ---------- SEARCH AUTOCOMPLETE ----------
function initAutocomplete(input, suggestions, onSelect) {
    let currentSuggestions = [];
    let activeIndex = -1;
    
    input.addEventListener('input', function() {
        const value = this.value.toLowerCase();
        if (value.length < 2) {
            clearSuggestions();
            return;
        }
        
        const matches = suggestions.filter(s => 
            s.toLowerCase().includes(value)
        ).slice(0, 10);
        
        showSuggestions(matches);
    });
    
    input.addEventListener('keydown', function(e) {
        const items = document.querySelectorAll('.autocomplete-item');
        if (items.length === 0) return;
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            activeIndex = Math.min(activeIndex + 1, items.length - 1);
            highlightItem(items);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            activeIndex = Math.max(activeIndex - 1, -1);
            highlightItem(items);
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (activeIndex >= 0 && activeIndex < items.length) {
                const selected = items[activeIndex];
                const value = selected.dataset.value;
                input.value = value;
                clearSuggestions();
                if (onSelect) onSelect(value);
            }
        } else if (e.key === 'Escape') {
            clearSuggestions();
        }
    });
    
    function showSuggestions(items) {
        clearSuggestions();
        const container = document.createElement('div');
        container.className = 'autocomplete-container';
        
        items.forEach((item, index) => {
            const div = document.createElement('div');
            div.className = 'autocomplete-item';
            div.dataset.value = item;
            div.textContent = item;
            div.addEventListener('click', function() {
                input.value = this.dataset.value;
                clearSuggestions();
                if (onSelect) onSelect(this.dataset.value);
            });
            container.appendChild(div);
        });
        
        input.parentNode.appendChild(container);
    }
    
    function clearSuggestions() {
        const container = document.querySelector('.autocomplete-container');
        if (container) container.remove();
        activeIndex = -1;
    }
    
    function highlightItem(items) {
        items.forEach((item, index) => {
            item.classList.toggle('active', index === activeIndex);
        });
        if (activeIndex >= 0) {
            items[activeIndex].scrollIntoView({ block: 'nearest' });
        }
    }
}

// Add autocomplete styles
function addAutocompleteStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .autocomplete-container {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #ddd;
            border-radius: 0 0 8px 8px;
            max-height: 200px;
            overflow-y: auto;
            z-index: 1000;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .autocomplete-item {
            padding: 8px 12px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .autocomplete-item:hover,
        .autocomplete-item.active {
            background: #f0f0f0;
        }
    `;
    document.head.appendChild(style);
}

// ---------- THEME TOGGLE ----------
function initThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    if (!themeToggle) return;
    
    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    
    themeToggle.addEventListener('click', function() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    });
}

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    
    // Update toggle button
    const toggle = document.getElementById('themeToggle');
    if (toggle) {
        toggle.textContent = theme === 'dark' ? '☀️' : '🌙';
        toggle.title = theme === 'dark' ? 'Switch to Light' : 'Switch to Dark';
    }
}

// Add theme styles
function addThemeStyles() {
    const style = document.createElement('style');
    style.textContent = `
        [data-theme="dark"] {
            --light-gray: #1a1a2e;
            --dark: #ffffff;
            --white: #16213e;
            --shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        [data-theme="dark"] .navbar {
            background: #16213e;
        }
        [data-theme="dark"] .feature-card,
        [data-theme="dark"] .stat-card,
        [data-theme="dark"] .dashboard-card,
        [data-theme="dark"] .auth-card,
        [data-theme="dark"] .sidebar-card {
            background: #1a1a2e;
            border-color: #2a2a4e;
        }
        [data-theme="dark"] .form-group input,
        [data-theme="dark"] .form-group select,
        [data-theme="dark"] .form-group textarea {
            background: #1a1a2e;
            border-color: #2a2a4e;
            color: #fff;
        }
        [data-theme="dark"] .donor-card {
            background: #1a1a2e;
            border-color: #2a2a4e;
        }
    `;
    document.head.appendChild(style);
}

// ---------- TOOLTIP SYSTEM ----------
function initTooltips() {
    document.querySelectorAll('[data-tooltip]').forEach(element => {
        const tooltipText = element.dataset.tooltip;
        
        element.addEventListener('mouseenter', function(e) {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip-popup';
            tooltip.textContent = tooltipText;
            tooltip.style.cssText = `
                position: fixed;
                background: rgba(0,0,0,0.8);
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 12px;
                pointer-events: none;
                z-index: 10000;
                max-width: 200px;
                text-align: center;
                transition: opacity 0.2s;
            `;
            
            const rect = element.getBoundingClientRect();
            tooltip.style.top = (rect.top - 10) + 'px';
            tooltip.style.left = (rect.left + rect.width / 2) + 'px';
            tooltip.style.transform = 'translate(-50%, -100%)';
            
            document.body.appendChild(tooltip);
            element._tooltip = tooltip;
        });
        
        element.addEventListener('mouseleave', function() {
            if (element._tooltip) {
                element._tooltip.remove();
                delete element._tooltip;
            }
        });
    });
}

// ---------- KEYBOARD SHORTCUTS ----------
function initKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl + / for help
        if (e.ctrlKey && e.key === '/') {
            e.preventDefault();
            showKeyboardHelp();
        }
        
        // Escape for closing modals
        if (e.key === 'Escape') {
            closeAllModals();
        }
        
        // Ctrl + N for new request
        if (e.ctrlKey && e.key === 'n') {
            e.preventDefault();
            const requestBtn = document.querySelector('.quick-action.emergency');
            if (requestBtn) requestBtn.click();
        }
    });
}

function showKeyboardHelp() {
    const shortcuts = [
        { key: 'Ctrl + /', description: 'Show keyboard shortcuts' },
        { key: 'Ctrl + N', description: 'New blood request' },
        { key: 'Ctrl + D', description: 'Go to dashboard' },
        { key: 'Ctrl + P', description: 'Go to profile' },
        { key: 'Esc', description: 'Close modals/popups' }
    ];
    
    let html = `
        <div class="modal-overlay" onclick="this.remove()">
            <div class="modal-content" onclick="event.stopPropagation()">
                <h3>⌨️ Keyboard Shortcuts</h3>
                <table style="width:100%;margin-top:1rem;">
    `;
    
    shortcuts.forEach(s => {
        html += `
            <tr>
                <td style="padding:8px;font-weight:600;">${s.key}</td>
                <td style="padding:8px;">${s.description}</td>
            </tr>
        `;
    });
    
    html += `
                </table>
                <button onclick="this.closest('.modal-overlay').remove()" 
                        style="margin-top:1rem;padding:8px 24px;background:#DC3545;color:white;border:none;border-radius:6px;cursor:pointer;">
                    Close
                </button>
            </div>
        </div>
    `;
    
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
    `;
    overlay.innerHTML = html;
    document.body.appendChild(overlay);
    
    // Close on overlay click
    overlay.addEventListener('click', function() {
        this.remove();
    });
}

function closeAllModals() {
    document.querySelectorAll('.modal-overlay').forEach(el => el.remove());
}

// ---------- INITIALIZE ALL ----------
document.addEventListener('DOMContentLoaded', function() {
    // Counter animation
    initCounters();
    
    // Notification permission
    requestNotificationPermission();
    
    // Theme toggle
    addThemeStyles();
    initThemeToggle();
    
    // Tooltips
    initTooltips();
    
    // Keyboard shortcuts
    initKeyboardShortcuts();
    
    // Autocomplete styles
    addAutocompleteStyles();
    
    console.log('🩸 Blood Need - Interactive features initialized!');
});