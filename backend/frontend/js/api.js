// Dynamic Base URL configuration: uses current domain in production (Render) or localhost port 8000 in dev
const API_URL = (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") && window.location.port !== "8000" && window.location.port !== ""
    ? "http://127.0.0.1:8000"
    : window.location.origin;

/**
 * Helper function to retrieve standard request headers 
 * and append JWT tokens dynamically from localStorage.
 */
function getHeaders() {
    const token = localStorage.getItem("access_token");
    return {
        "Content-Type": "application/json",
        "Authorization": token ? `Bearer ${token}` : ""
    };
}

/**
 * Centralized global API request wrapper utilizing fetch API.
 * Automatically handles JSON parsing and tracks auth expirations.
 */
async function apiRequest(endpoint, method = "GET", data = null) {
    try {
        const options = { 
            method, 
            headers: getHeaders() 
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(`${API_URL}${endpoint}`, options);
        
        // Graceful interception if user auth state expires or drops
        if (response.status === 401) {
            alert("Your session has expired. Redirecting to login page...");
            localStorage.clear();
            window.location.href = "login.html";
            return null;
        }
        
        return await response.json();
    } catch (error) {
        console.error(`[API Error] Request to ${endpoint} failed:`, error);
        return null;
    }
}

