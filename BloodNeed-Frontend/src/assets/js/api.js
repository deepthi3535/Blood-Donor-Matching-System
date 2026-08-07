/* ============================
   BLOOD NEED - API INTEGRATION
   ============================ */

'use strict';

// ---------- API CONFIGURATION ----------
function getLoginPageUrl() {
    return window.location.pathname.includes('/pages/') ? 'login.html' : 'pages/login.html';
}

const API_CONFIG = {
    BASE_URL: 'http://localhost:5000/api',
    TIMEOUT: 30000,
    HEADERS: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
};

// ---------- API HELPER FUNCTIONS ----------
class API {
    constructor() {
        this.baseURL = API_CONFIG.BASE_URL;
        this.timeout = API_CONFIG.TIMEOUT;
    }

    // Get auth token from storage
    getToken() {
        return localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
    }

    // Set auth token
    setToken(token, remember = false) {
        if (remember) {
            localStorage.setItem('auth_token', token);
        } else {
            sessionStorage.setItem('auth_token', token);
        }
    }

    // Clear auth token
    clearToken() {
        localStorage.removeItem('auth_token');
        sessionStorage.removeItem('auth_token');
    }

    // Get headers with auth
    getHeaders() {
        const headers = { ...API_CONFIG.HEADERS };
        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        return headers;
    }

    // Handle API response
    async handleResponse(response) {
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw {
                status: response.status,
                statusText: response.statusText,
                message: error.message || 'An error occurred',
                data: error
            };
        }
        return response.json();
    }

    // Generic request method
    async request(endpoint, method = 'GET', data = null, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            method,
            headers: this.getHeaders(),
            ...options
        };

        if (data) {
            config.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, config);
            return await this.handleResponse(response);
        } catch (error) {
            if (error.status === 401) {
                this.clearToken();
                window.location.href = getLoginPageUrl();
            }
            if (error.status) {
                throw error;
            }
            throw {
                status: 0,
                message: 'Failed to fetch',
                data: error
            };
        }
    }

    // Convenience methods
    get(endpoint, options = {}) {
        return this.request(endpoint, 'GET', null, options);
    }

    post(endpoint, data, options = {}) {
        return this.request(endpoint, 'POST', data, options);
    }

    put(endpoint, data, options = {}) {
        return this.request(endpoint, 'PUT', data, options);
    }

    delete(endpoint, options = {}) {
        return this.request(endpoint, 'DELETE', null, options);
    }

    patch(endpoint, data, options = {}) {
        return this.request(endpoint, 'PATCH', data, options);
    }

    // Upload file
    async upload(endpoint, file, fieldName = 'file', extraData = {}) {
        const formData = new FormData();
        formData.append(fieldName, file);
        
        for (const [key, value] of Object.entries(extraData)) {
            formData.append(key, value);
        }

        const url = `${this.baseURL}${endpoint}`;
        const config = {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.getToken()}`
            },
            body: formData
        };

        try {
            const response = await fetch(url, config);
            return await this.handleResponse(response);
        } catch (error) {
            throw error;
        }
    }
}

// ---------- AUTH API ----------
class AuthAPI {
    constructor(api) {
        this.api = api;
    }

    // Login user
    async login(email, password, remember = false) {
        const response = await this.api.post('/auth/login', { email, password });
        if (response.success && response.data?.token) {
            this.api.setToken(response.data.token, remember);
            localStorage.setItem('user_type', response.data.user_type || 'donor');
            localStorage.setItem('user_data', JSON.stringify(response.data.user));
        }
        return response;
    }

    // Register donor
    async registerDonor(data) {
        const response = await this.api.post('/auth/register/donor', data);
        if (response.success && response.data?.token) {
            this.api.setToken(response.data.token, true);
            localStorage.setItem('user_type', 'donor');
            localStorage.setItem('user_data', JSON.stringify(response.data.user));
        }
        return response;
    }

    // Register patient
    async registerPatient(data) {
        const response = await this.api.post('/auth/register/patient', data);
        if (response.success && response.data?.token) {
            this.api.setToken(response.data.token, true);
            localStorage.setItem('user_type', 'patient');
            localStorage.setItem('user_data', JSON.stringify(response.data.user));
        }
        return response;
    }

    // Register hospital
    async registerHospital(data) {
        const response = await this.api.post('/auth/register/hospital', data);
        if (response.success && response.data?.token) {
            this.api.setToken(response.data.token, true);
            localStorage.setItem('user_type', 'hospital');
            localStorage.setItem('user_data', JSON.stringify(response.data.user));
        }
        return response;
    }

    // Logout
    logout() {
        this.api.clearToken();
        localStorage.removeItem('user_type');
        localStorage.removeItem('user_data');
        localStorage.removeItem('current_request_id');
        window.location.href = getLoginPageUrl();
    }

    // Get current user
    async getCurrentUser() {
        return this.api.get('/auth/me');
    }

    // Forgot password
    async forgotPassword(email) {
        return this.api.post('/auth/forgot-password', { email });
    }

    // Reset password
    async resetPassword(token, password) {
        return this.api.post('/auth/reset-password', { token, password });
    }

    // Verify OTP
    async verifyOTP(email, otp) {
        return this.api.post('/auth/verify-otp', { email, otp });
    }
}

// ---------- DONOR API ----------
class DonorAPI {
    constructor(api) {
        this.api = api;
    }

    // Get donor profile
    async getProfile() {
        return this.api.get('/donor/profile');
    }

    // Update donor profile
    async updateProfile(data) {
        return this.api.put('/donor/profile', data);
    }

    // Update availability
    async updateAvailability(available) {
        return this.api.post('/donor/availability', { available });
    }

    // Get donation history
    async getHistory(page = 1, limit = 10) {
        return this.api.get(`/donor/history?page=${page}&limit=${limit}`);
    }

    // Get donor matches
    async getMatches() {
        return this.api.get('/donor/matches');
    }

    // Respond to request
    async respondToRequest(matchId, response) {
        return this.api.post('/donor/respond', { matchId, response });
    }

    // Get gamification stats
    async getGamification() {
        return this.api.get('/donor/gamification');
    }

    // Get donor stats
    async getStats() {
        return this.api.get('/donor/stats');
    }

    // Get upcoming requests
    async getUpcomingRequests() {
        return this.api.get('/donor/upcoming-requests');
    }
}

// ---------- PATIENT API ----------
class PatientAPI {
    constructor(api) {
        this.api = api;
    }

    // Get patient profile
    async getProfile() {
        return this.api.get('/patient/profile');
    }

    // Create blood request
    async createRequest(data) {
        return this.api.post('/request/blood', data);
    }

    // Get patient requests
    async getRequests() {
        return this.api.get('/request/patient/requests');
    }

    // Get request status
    async getRequestStatus(requestId) {
        return this.api.get(`/request/patient/request/${requestId}`);
    }

    // Cancel request
    async cancelRequest(requestId) {
        return this.api.post(`/request/patient/request/${requestId}/cancel`);
    }

    // Update request
    async updateRequest(requestId, data) {
        return this.api.put(`/patient/request/${requestId}`, data);
    }

    // Get patient stats
    async getStats() {
        return this.api.get('/patient/stats');
    }
}

// ---------- HOSPITAL API ----------
class HospitalAPI {
    constructor(api) {
        this.api = api;
    }

    // Get hospital profile
    async getProfile() {
        return this.api.get('/hospital/profile');
    }

    // Get hospital requests
    async getRequests(status = null) {
        const url = status ? `/hospital/requests?status=${status}` : '/hospital/requests';
        return this.api.get(url);
    }

    // Get hospital stats
    async getStats() {
        return this.api.get('/hospital/stats');
    }

    // Verify donation
    async verifyDonation(requestId, donorId, otp) {
        return this.api.post('/hospital/verify-donation', { requestId, donorId, otp });
    }

    // Get donors for hospital
    async getDonors() {
        return this.api.get('/hospital/donors');
    }
}

// ---------- MATCHING API ----------
class MatchingAPI {
    constructor(api) {
        this.api = api;
    }

    // Find donors for request
    async findDonors(requestId) {
        return this.api.post(`/matching/find-donors/${requestId}`);
    }

    // Get donor ranking
    async getRanking(requestId) {
        return this.api.get(`/matching/ranking/${requestId}`);
    }

    // Auto-select donor
    async autoSelect(requestId) {
        return this.api.post(`/matching/auto-select/${requestId}`);
    }

    // Get matching stats
    async getStats(requestId) {
        return this.api.get(`/matching/stats/${requestId}`);
    }

    // Update ranking weights
    async updateWeights(weights) {
        return this.api.post('/matching/weights', { weights });
    }
}

// ---------- NOTIFICATION API ----------
class NotificationAPI {
    constructor(api) {
        this.api = api;
    }

    // Get user notifications
    async getNotifications(page = 1, limit = 20) {
        return this.api.get(`/notifications?page=${page}&limit=${limit}`);
    }

    // Mark notification as read
    async markAsRead(notificationId) {
        return this.api.post(`/notifications/${notificationId}/read`);
    }

    // Mark all as read
    async markAllAsRead() {
        return this.api.post('/notifications/read-all');
    }

    // Clear all notifications
    async clearAll() {
        return this.api.delete('/notifications/clear');
    }

    // Get unread count
    async getUnreadCount() {
        return this.api.get('/notifications/unread-count');
    }

    // Subscribe to push notifications
    async subscribe(subscription) {
        return this.api.post('/notifications/subscribe', { subscription });
    }

    // Unsubscribe from push notifications
    async unsubscribe(subscription) {
        return this.api.post('/notifications/unsubscribe', { subscription });
    }
}

// ---------- ML API ----------
class MLAPI {
    constructor(api) {
        this.api = api;
    }

    // Predict donor response
    async predictResponse(donorId, requestId) {
        return this.api.get(`/ml/predict/${donorId}/${requestId}`);
    }

    // Get donor scores
    async getDonorScores(requestId) {
        return this.api.get(`/ml/donor-scores/${requestId}`);
    }

    // Get model accuracy
    async getAccuracy() {
        return this.api.get('/ml/accuracy');
    }

    // Get feature importance
    async getFeatureImportance() {
        return this.api.get('/ml/feature-importance');
    }

    // Retrain model
    async retrainModel() {
        return this.api.post('/ml/retrain');
    }
}

// ---------- GAMIFICATION API ----------
class GamificationAPI {
    constructor(api) {
        this.api = api;
    }

    // Get user gamification
    async getUserGamification() {
        return this.api.get('/gamification/user');
    }

    // Get leaderboard
    async getLeaderboard(period = 'monthly', limit = 50) {
        return this.api.get(`/gamification/leaderboard?period=${period}&limit=${limit}`);
    }

    // Get badges
    async getBadges() {
        return this.api.get('/gamification/badges');
    }

    // Get available challenges
    async getChallenges() {
        return this.api.get('/gamification/challenges');
    }
}

// ---------- LOCATION API ----------
class LocationAPI {
    constructor(api) {
        this.api = api;
    }

    // Get nearby donors
    async getNearbyDonors(lat, lng, radius = 10) {
        return this.api.get(`/location/donors?lat=${lat}&lng=${lng}&radius=${radius}`);
    }

    // Get nearby hospitals
    async getNearbyHospitals(lat, lng, radius = 10) {
        return this.api.get(`/location/hospitals?lat=${lat}&lng=${lng}&radius=${radius}`);
    }

    // Geocode address
    async geocode(address) {
        return this.api.post('/location/geocode', { address });
    }

    // Reverse geocode
    async reverseGeocode(lat, lng) {
        return this.api.get(`/location/reverse?lat=${lat}&lng=${lng}`);
    }

    // Calculate route
    async calculateRoute(origin, destination) {
        return this.api.post('/location/route', { origin, destination });
    }
}

// ---------- EXPORT API CLASSES ----------
const api = new API();

// Initialize all API modules
window.API = {
    api,
    getUserType: () => localStorage.getItem('user_type') || 'donor',
    isAuthenticated: () => !!api.getToken(),
    auth: new AuthAPI(api),
    donor: new DonorAPI(api),
    patient: new PatientAPI(api),
    hospital: new HospitalAPI(api),
    matching: new MatchingAPI(api),
    notification: new NotificationAPI(api),
    ml: new MLAPI(api),
    gamification: new GamificationAPI(api),
    location: new LocationAPI(api)
};

// ---------- API INTERCEPTORS ----------
// Add request interceptor
const originalRequest = api.request.bind(api);
api.request = async function(endpoint, method, data, options) {
    try {
        return await originalRequest(endpoint, method, data, options);
    } catch (error) {
        // Handle specific error codes
        if (error.status === 403) {
            showNotification('You do not have permission to perform this action.', 'error');
        } else if (error.status === 404) {
            showNotification('Resource not found.', 'error');
        } else if (error.status === 422) {
            if (error.data && error.data.errors) {
                const messages = Object.values(error.data.errors).flat().join(', ');
                showNotification(`Validation error: ${messages}`, 'error');
            }
        } else if (error.status === 500) {
            showNotification('Server error. Please try again later.', 'error');
        }
        throw error;
    }
};

// ---------- INITIALIZATION ----------
document.addEventListener('DOMContentLoaded', function() {
    const token = api.getToken();
    const storedUser = localStorage.getItem('user_data');
    if (token && storedUser) {
        try {
            window.currentUser = JSON.parse(storedUser);
            updateUserUI(window.currentUser);
        } catch {
            api.clearToken();
        }
    }
});

// Helper to update UI with user info
function updateUserUI(user) {
    // Update profile avatar
    const avatars = document.querySelectorAll('.profile-avatar');
    avatars.forEach(avatar => {
        if (user.avatar) {
            avatar.src = user.avatar;
        } else {
            avatar.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name)}&background=DC3545&color=fff`;
        }
    });

    // Update welcome message
    const welcomeElements = document.querySelectorAll('.welcome-message');
    welcomeElements.forEach(el => {
        el.textContent = `Welcome, ${user.name}!`;
    });

    // Update name displays
    const nameElements = document.querySelectorAll('.user-name');
    nameElements.forEach(el => {
        el.textContent = user.name;
    });
}