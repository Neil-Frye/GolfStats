// Import all modules
import ApiService from './api/api.js';
import * as Auth from './auth/auth.js';
import * as UI from './ui/ui.js';
import * as Dashboard from './dashboard/dashboard.js';
import * as Rounds from './rounds/rounds.js';
import * as Shots from './shots/shots.js';

// Create a clubs module with enhanced functionality
const Clubs = {
    initClubsView: function() {
        // Set up event handlers for club buttons
        const addClubBtns = document.querySelectorAll('.add-btn, .add-club');
        const addFirstClubBtn = document.querySelector('.add-first-club-btn');
        const clubsContainer = document.querySelector('.clubs-container');
        const clubsLoading = document.getElementById('clubs-loading');
        const clubsEmptyState = document.querySelector('.clubs-empty-state');
        
        // Function to show the add club form modal
        const showAddClubForm = () => {
            // Create the club form modal if it doesn't exist yet
            let clubModal = document.getElementById('club-form-modal');
            
            if (!clubModal) {
                // Create modal if it doesn't exist
                clubModal = document.createElement('div');
                clubModal.id = 'club-form-modal';
                clubModal.className = 'modal';
                clubModal.innerHTML = `
                    <div class="modal-content">
                        <div class="modal-header">
                            <h2>Add New Club</h2>
                            <button class="close-modal">&times;</button>
                        </div>
                        <div class="modal-body">
                            <form id="club-form">
                                <div class="form-group">
                                    <label for="club-type">Club Type</label>
                                    <select id="club-type" name="club-type" required>
                                        <option value="">Select Club Type</option>
                                        <option value="driver">Driver</option>
                                        <option value="wood">Fairway Wood</option>
                                        <option value="hybrid">Hybrid</option>
                                        <option value="iron">Iron</option>
                                        <option value="wedge">Wedge</option>
                                        <option value="putter">Putter</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label for="club-name">Club Name</label>
                                    <input type="text" id="club-name" name="club-name" placeholder="e.g. 7 Iron, Driver, Sand Wedge" required>
                                </div>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="club-brand">Brand</label>
                                        <input type="text" id="club-brand" name="club-brand" placeholder="e.g. TaylorMade, Titleist" required>
                                    </div>
                                    <div class="form-group">
                                        <label for="club-model">Model</label>
                                        <input type="text" id="club-model" name="club-model" placeholder="e.g. Stealth, T200" required>
                                    </div>
                                </div>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="club-loft">Loft (degrees)</label>
                                        <input type="number" id="club-loft" name="club-loft" step="0.5" min="0" max="70" placeholder="e.g. 10.5">
                                    </div>
                                    <div class="form-group">
                                        <label for="club-distance">Typical Distance (yards)</label>
                                        <input type="number" id="club-distance" name="club-distance" min="0" max="400" placeholder="e.g. 150">
                                    </div>
                                </div>
                                <div class="form-group">
                                    <label for="club-shaft">Shaft</label>
                                    <input type="text" id="club-shaft" name="club-shaft" placeholder="e.g. True Temper AMT Black S300">
                                </div>
                                <div class="form-group">
                                    <label for="club-notes">Notes</label>
                                    <textarea id="club-notes" name="club-notes" rows="2" placeholder="Add any notes about this club..."></textarea>
                                </div>
                                <div class="form-buttons">
                                    <button type="button" class="btn-secondary cancel-btn">Cancel</button>
                                    <button type="submit" class="btn-primary">Save Club</button>
                                </div>
                            </form>
                        </div>
                    </div>
                `;
                document.body.appendChild(clubModal);
                
                // Initialize the modal
                UI.initModal('club-form-modal');
                
                // Add form submit handler
                const form = document.getElementById('club-form');
                form.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    
                    // Show loading state on the button
                    const submitBtn = form.querySelector('button[type="submit"]');
                    const originalText = submitBtn.textContent;
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
                    
                    try {
                        // Collect form data
                        const formData = new FormData(form);
                        const clubData = {};
                        
                        formData.forEach((value, key) => {
                            clubData[key.replace('-', '_')] = value;
                        });
                        
                        // Format data for API
                        const apiClubData = {
                            type: clubData.club_type,
                            name: clubData.club_name,
                            brand: clubData.club_brand,
                            model: clubData.club_model,
                            loft: clubData.club_loft ? parseFloat(clubData.club_loft) : null,
                            distance: clubData.club_distance ? parseInt(clubData.club_distance) : null,
                            shaft: clubData.club_shaft || '',
                            notes: clubData.club_notes || ''
                        };
                        
                        // Send to API
                        const response = await ApiService.saveClub(apiClubData);
                        
                        if (response && response.club) {
                            // Success - show message
                            UI.showToast('Club added successfully!', 'success');
                            
                            // Close modal and reset form
                            UI.closeModal('club-form-modal');
                            form.reset();
                            
                            // Refresh the clubs view
                            this.loadClubsData();
                        } else {
                            throw new Error('Failed to save club');
                        }
                    } catch (error) {
                        console.error('Error saving club:', error);
                        UI.showToast(`Error: ${error.message || 'Failed to save club'}`, 'error');
                    } finally {
                        // Reset button state
                        submitBtn.disabled = false;
                        submitBtn.textContent = originalText;
                    }
                });
            }
            
            // Show the modal
            UI.openModal('club-form-modal');
        };
        
        // Function to load clubs data
        this.loadClubsData = async () => {
            if (!clubsContainer || !clubsLoading) return;
            
            // Show loading state
            clubsLoading.style.display = 'flex';
            clubsContainer.style.display = 'none';
            
            if (clubsEmptyState) {
                clubsEmptyState.style.display = 'none';
            }
            
            try {
                // Fetch clubs from API
                const data = await ApiService.getClubs();
                
                // Hide loading state
                clubsLoading.style.display = 'none';
                
                // Check if we have clubs
                if (data && data.clubs && data.clubs.length > 0) {
                    // Update the UI with clubs
                    this.updateClubsDisplay(data.clubs);
                    clubsContainer.style.display = 'block';
                } else {
                    // Show empty state
                    if (clubsEmptyState) {
                        clubsEmptyState.style.display = 'flex';
                    }
                }
            } catch (error) {
                console.error('Error loading clubs:', error);
                clubsLoading.style.display = 'none';
                
                // Show empty state with error message
                if (clubsEmptyState) {
                    clubsEmptyState.style.display = 'flex';
                    
                    // Add error message
                    const errorMsg = document.createElement('p');
                    errorMsg.className = 'error-message';
                    errorMsg.textContent = 'Failed to load clubs. Please try again.';
                    clubsEmptyState.querySelector('.empty-state-content').appendChild(errorMsg);
                }
                
                // Show error toast
                UI.showToast('Failed to load clubs. Please try again.', 'error');
            }
        };
        
        // Method to update the clubs display
        this.updateClubsDisplay = (clubs) => {
            // Implementation for updating the clubs display would go here
            // For now, this is a placeholder since we'd need to create proper UI elements
            console.log('Updating clubs display with', clubs.length, 'clubs');
        };
        
        // Add event listener to all "Add Club" buttons
        if (addClubBtns.length > 0) {
            addClubBtns.forEach(btn => {
                // Only attach to buttons in the clubs view to avoid conflicts
                if (btn.closest('#clubs-view')) {
                    btn.addEventListener('click', showAddClubForm);
                }
            });
        }
        
        // Add event listener to "Add Your First Club" button
        if (addFirstClubBtn) {
            addFirstClubBtn.addEventListener('click', showAddClubForm);
        }
        
        // Add event listener to club edit buttons
        document.addEventListener('click', function(e) {
            if (e.target.closest('.edit-club')) {
                const clubCard = e.target.closest('.club-card');
                const clubId = clubCard?.dataset.clubId;
                
                if (clubId) {
                    // Show edit form for this club
                    UI.showToast('Club editing will be available soon!', 'info');
                } else {
                    UI.showToast('Could not find club information to edit', 'error');
                }
            }
        });
        
        // Initialize by loading clubs data
        this.loadClubsData();
    }
};

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
            
            // Initialize clubs view
            Clubs.initClubsView();
            
            // Initialize shots view
            Shots.initShotsView();
            
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
        case 'shots':
            Shots.loadRangeSessions();
            break;
        case 'clubs':
            // Ensure club buttons are initialized when navigating directly to clubs
            Clubs.initClubsView();
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
    shots: Shots,
    clubs: Clubs,
    api: ApiService
};