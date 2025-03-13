// Import all modules
import ApiService from './api/api.js';
import * as Auth from './auth/auth.js';
import * as UI from './ui/ui.js';
import * as Dashboard from './dashboard/dashboard.js';
import * as Rounds from './rounds/rounds.js';

// Main initialization function
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is authenticated
    Auth.checkAuthentication()
        .then(() => {
            // Initialize UI components
            UI.initNavigation();
            UI.setupEventListeners();
            
            // Initialize logout handler
            Auth.initLogoutHandler();
            
            // Initialize dashboard
            Dashboard.initDashboard();
            
            // Initialize rounds view
            Rounds.initRoundsView();
            
            // Listen for route changes
            window.addEventListener('hashchange', handleRouteChange);
            
            // Handle initial route
            handleRouteChange();
        })
        .catch(error => {
            console.error('Authentication error:', error);
        });
});

// Handle route changes
function handleRouteChange() {
    const hash = window.location.hash.substring(1) || 'dashboard';
    console.log(`Route changed to: ${hash}`);
    
    // Update based on route
    switch (hash) {
        case 'dashboard':
            Dashboard.loadDashboardData();
            break;
        case 'rounds':
            Rounds.loadRoundsData();
            break;
        // Add other routes as needed
    }
}

// Export the app for global access if needed
window.GolfStatsApp = {
    auth: Auth,
    ui: UI,
    dashboard: Dashboard,
    rounds: Rounds,
    api: ApiService
};