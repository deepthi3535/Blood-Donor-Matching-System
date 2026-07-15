/* ============================
   BLOOD NEED - UTILITY FUNCTIONS
   ============================ */

'use strict';

// ---------- DOM UTILITIES ----------

// Get element by ID with error handling
function getElement(id) {
    const el = document.getElementById(id);
    if (!el) {
        console.warn(`Element with ID "${id}" not found`);
    }
    return el;
}

// Query selector with error handling
function qs(selector, context = document) {
    const el = context.querySelector(selector);
    if (!el) {
        console.warn(`Element with selector "${selector}" not found`);
    }
    return el;
}

// Query selector all
function qsa(selector, context = document) {
    return context.querySelectorAll(selector);
}

// Create element with attributes and children
function createElement(tag, attributes = {}, children = []) {
    const el = document.createElement(tag);
    
    for (const [key, value] of Object.entries(attributes)) {
        if (key === 'className') {
            el.className = value;
        } else if (key === 'textContent') {
            el.textContent = value;
        } else if (key === 'innerHTML') {
            el.innerHTML = value;
        } else if (key === 'style' && typeof value === 'object') {
            Object.assign(el.style, value);
        } else {
            el.setAttribute(key, value);
        }
    }
    
    children.forEach(child => {
        if (typeof child === 'string') {
            el.appendChild(document.createTextNode(child));
        } else if (child instanceof Node) {
            el.appendChild(child);
        }
    });
    
    return el;
}

// ---------- STRING UTILITIES ----------

// Capitalize first letter
function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Truncate string
function truncate(str, length = 50, suffix = '...') {
    if (!str) return '';
    if (str.length <= length) return str;
    return str.substring(0, length) + suffix;
}

// Generate random ID
function generateId(length = 8) {
    return Math.random().toString(36).substring(2, 2 + length);
}

// Slugify string
function slugify(str) {
    return str
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-+|-+$/g, '');
}

// ---------- NUMBER UTILITIES ----------

// Format number with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// Format percentage
function formatPercentage(num, decimals = 1) {
    return `${(num * 100).toFixed(decimals)}%`;
}

// Clamp number between min and max
function clamp(num, min, max) {
    return Math.min(Math.max(num, min), max);
}

// Random number between min and max
function randomBetween(min, max) {
    return Math.random() * (max - min) + min;
}

// ---------- DATE UTILITIES ----------

// Format date
function formatDate(date, format = 'MMM DD, YYYY') {
    const d = new Date(date);
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const day = d.getDate().toString().padStart(2, '0');
    const month = months[d.getMonth()];
    const year = d.getFullYear();
    const hours = d.getHours().toString().padStart(2, '0');
    const minutes = d.getMinutes().toString().padStart(2, '0');
    
    return format
        .replace('MMM', month)
        .replace('DD', day)
        .replace('YYYY', year)
        .replace('HH', hours)
        .replace('MM', minutes);
}

// Get time ago
function timeAgo(date) {
    const seconds = Math.floor((Date.now() - new Date(date).getTime()) / 1000);
    
    if (seconds < 60) return 'Just now';
    
    const intervals = [
        { label: 'year', seconds: 31536000 },
        { label: 'month', seconds: 2592000 },
        { label: 'week', seconds: 604800 },
        { label: 'day', seconds: 86400 },
        { label: 'hour', seconds: 3600 },
        { label: 'minute', seconds: 60 }
    ];
    
    for (const interval of intervals) {
        const count = Math.floor(seconds / interval.seconds);
        if (count >= 1) {
            return `${count} ${interval.label}${count > 1 ? 's' : ''} ago`;
        }
    }
    return 'Just now';
}

// Check if date is today
function isToday(date) {
    const today = new Date();
    const d = new Date(date);
    return d.getDate() === today.getDate() &&
           d.getMonth() === today.getMonth() &&
           d.getFullYear() === today.getFullYear();
}

// Check if date is this week
function isThisWeek(date) {
    const now = new Date();
    const d = new Date(date);
    const firstDay = new Date(now.setDate(now.getDate() - now.getDay()));
    const lastDay = new Date(firstDay);
    lastDay.setDate(lastDay.getDate() + 6);
    return d >= firstDay && d <= lastDay;
}

// ---------- ARRAY UTILITIES ----------

// Shuffle array (Fisher-Yates)
function shuffleArray(arr) {
    const shuffled = [...arr];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
}

// Group array by key
function groupBy(arr, key) {
    return arr.reduce((acc, item) => {
        const group = item[key];
        if (!acc[group]) acc[group] = [];
        acc[group].push(item);
        return acc;
    }, {});
}

// Unique array
function unique(arr) {
    return [...new Set(arr)];
}

// Chunk array
function chunkArray(arr, size) {
    const chunks = [];
    for (let i = 0; i < arr.length; i += size) {
        chunks.push(arr.slice(i, i + size));
    }
    return chunks;
}

// ---------- OBJECT UTILITIES ----------

// Deep clone object
function deepClone(obj) {
    if (obj === null || typeof obj !== 'object') return obj;
    if (obj instanceof Date) return new Date(obj);
    if (obj instanceof Array) return obj.map(item => deepClone(item));
    if (obj instanceof Object) {
        const cloned = {};
        for (const key in obj) {
            if (obj.hasOwnProperty(key)) {
                cloned[key] = deepClone(obj[key]);
            }
        }
        return cloned;
    }
    return obj;
}

// Merge objects (deep)
function deepMerge(target, ...sources) {
    if (!sources.length) return target;
    const source = sources.shift();
    
    if (isObject(target) && isObject(source)) {
        for (const key in source) {
            if (isObject(source[key])) {
                if (!target[key]) Object.assign(target, { [key]: {} });
                deepMerge(target[key], source[key]);
            } else {
                Object.assign(target, { [key]: source[key] });
            }
        }
    }
    return deepMerge(target, ...sources);
}

function isObject(item) {
    return item && typeof item === 'object' && !Array.isArray(item);
}

// Pick properties from object
function pick(obj, keys) {
    return keys.reduce((acc, key) => {
        if (obj.hasOwnProperty(key)) {
            acc[key] = obj[key];
        }
        return acc;
    }, {});
}

// Omit properties from object
function omit(obj, keys) {
    const result = { ...obj };
    keys.forEach(key => delete result[key]);
    return result;
}

// ---------- VALIDATION UTILITIES ----------

// Validate email
function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Validate phone (Indian)
function isValidPhone(phone) {
    return /^[6-9]\d{9}$/.test(phone);
}

// Validate blood group
function isValidBloodGroup(group) {
    return ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'].includes(group);
}

// Validate password strength
function getPasswordStrength(password) {
    let score = 0;
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    if (/[a-z]/.test(password)) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^a-zA-Z0-9]/.test(password)) score++;
    
    if (score <= 2) return { level: 'weak', color: '#DC3545', message: 'Weak' };
    if (score <= 4) return { level: 'medium', color: '#FFC107', message: 'Medium' };
    return { level: 'strong', color: '#28A745', message: 'Strong' };
}

// Validate PIN code
function isValidPin(pin) {
    return /^[1-9][0-9]{5}$/.test(pin);
}

// ---------- STORAGE UTILITIES ----------

// Set item with expiry
function setItemWithExpiry(key, value, expiryMinutes = 60) {
    const item = {
        value,
        expiry: Date.now() + expiryMinutes * 60 * 1000
    };
    localStorage.setItem(key, JSON.stringify(item));
}

// Get item with expiry check
function getItemWithExpiry(key) {
    const item = localStorage.getItem(key);
    if (!item) return null;
    
    const parsed = JSON.parse(item);
    if (Date.now() > parsed.expiry) {
        localStorage.removeItem(key);
        return null;
    }
    return parsed.value;
}

// ---------- COOKIE UTILITIES ----------

function setCookie(name, value, days = 7) {
    const expires = new Date(Date.now() + days * 864e5).toUTCString();
    document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/; SameSite=Strict`;
}

function getCookie(name) {
    return document.cookie.split('; ').reduce((acc, cookie) => {
        const [key, value] = cookie.split('=');
        return key === name ? decodeURIComponent(value) : acc;
    }, null);
}

function deleteCookie(name) {
    document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
}

// ---------- URL UTILITIES ----------

// Get URL parameters
function getURLParams() {
    const params = new URLSearchParams(window.location.search);
    const result = {};
    for (const [key, value] of params) {
        result[key] = value;
    }
    return result;
}

// Build query string
function buildQueryString(params) {
    return Object.entries(params)
        .filter(([, value]) => value !== null && value !== undefined)
        .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
        .join('&');
}

// ---------- COLOR UTILITIES ----------

// Get blood group color
const BLOOD_GROUP_COLORS = {
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
    return BLOOD_GROUP_COLORS[group] || '#6C757D';
}

// Get emergency level color
const EMERGENCY_COLORS = {
    'Normal': '#28A745',
    'Urgent': '#FFC107',
    'Critical': '#DC3545'
};

function getEmergencyColor(level) {
    return EMERGENCY_COLORS[level] || '#6C757D';
}

// Hex to RGB
function hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

// ---------- FILE UTILITIES ----------

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Get file extension
function getFileExtension(filename) {
    return filename.split('.').pop()?.toLowerCase() || '';
}

// ---------- BROWSER UTILITIES ----------

// Check if on mobile
function isMobile() {
    return window.innerWidth <= 768;
}

// Check if on tablet
function isTablet() {
    return window.innerWidth > 768 && window.innerWidth <= 1024;
}

// Check if on desktop
function isDesktop() {
    return window.innerWidth > 1024;
}

// Check browser support
function browserSupports(api) {
    try {
        return typeof window[api] !== 'undefined';
    } catch {
        return false;
    }
}

// ---------- PERFORMANCE UTILITIES ----------

// Debounce function
function debounce(func, wait = 300) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// Throttle function
function throttle(func, wait = 300) {
    let lastTime = 0;
    return function(...args) {
        const now = Date.now();
        if (now - lastTime >= wait) {
            lastTime = now;
            func.apply(this, args);
        }
    };
}
// ---------- LOCATION UTILITIES ----------

function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Radius of Earth in km

    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;

    const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(lat1 * Math.PI / 180) *
        Math.cos(lat2 * Math.PI / 180) *
        Math.sin(dLon / 2) *
        Math.sin(dLon / 2);

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return R * c;
}

// ---------- EXPORT UTILITIES ----------
window.Utils = {
    // DOM
    getElement,
    qs,
    qsa,
    createElement,
    
    // String
    capitalize,
    truncate,
    generateId,
    slugify,
    
    // Number
    formatNumber,
    formatPercentage,
    clamp,
    randomBetween,
    
    // Date
    formatDate,
    timeAgo,
    isToday,
    isThisWeek,
    
    // Array
    shuffleArray,
    groupBy,
    unique,
    chunkArray,
    
    // Object
    deepClone,
    deepMerge,
    pick,
    omit,
    
    // Validation
    isValidEmail,
    isValidPhone,
    isValidBloodGroup,
    getPasswordStrength,
    isValidPin,
    
    // Storage
    setItemWithExpiry,
    getItemWithExpiry,
    
    // Cookie
    setCookie,
    getCookie,
    deleteCookie,
    
    // URL
    getURLParams,
    buildQueryString,
    
    // Color
    getBloodGroupColor,
    getEmergencyColor,
    hexToRgb,
    
    // File
    formatFileSize,
    getFileExtension,
    
    // Browser
    isMobile,
    isTablet,
    isDesktop,
    browserSupports,
    
    // Performance
    debounce,
    throttle,
    
    // Location
    calculateDistance
};