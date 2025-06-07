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
            // Get the existing modal from HTML
            const clubModal = document.getElementById('add-club-modal');
            
            if (clubModal) {
                // Initialize the modal if not already done
                UI.initModal('add-club-modal');
                
                // Add form submit handler if not already added
                const form = document.getElementById('add-club-form');
                if (form && !form.hasAttribute('data-handler-added')) {
                    form.setAttribute('data-handler-added', 'true');
                    
                    form.addEventListener('submit', async (e) => {
                        e.preventDefault();
                        
                        // Show loading state on the button
                        const submitBtn = e.target.querySelector('button[type="submit"]');
                        const originalText = submitBtn.textContent;
                        submitBtn.disabled = true;
                        submitBtn.textContent = 'Saving...';
                        
                        try {
                            // Get form data
                            const formData = new FormData(e.target);
                            const clubData = {};
                            formData.forEach((value, key) => {
                                clubData[key] = value;
                            });
                            
                            // Format data for API - matching the backend expectations
                            const apiClubData = {
                                club_type: clubData.club_type,
                                name: clubData.name,
                                brand: clubData.brand || '',
                                model: clubData.model || '',
                                loft: clubData.loft ? parseFloat(clubData.loft) : null
                            };
                            
                            console.log('Sending club data:', apiClubData);
                            
                            // Send to API
                            const response = await ApiService.saveClub(apiClubData);
                            
                            if (response && response.club) {
                                // Success - show message
                                UI.showToast('Club added successfully!', 'success');
                                
                                // Close modal and reset form
                                UI.closeModal('add-club-modal');
                                form.reset();
                                
                                // Refresh the clubs view if the function exists
                                if (typeof this.loadClubsData === 'function') {
                                    this.loadClubsData();
                                }
                            } else {
                                throw new Error(response?.error || 'Failed to save club');
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
                    
                    // Add cancel button handler
                    const cancelBtn = form.querySelector('.cancel-btn');
                    if (cancelBtn) {
                        cancelBtn.addEventListener('click', () => {
                            UI.closeModal('add-club-modal');
                            form.reset();
                        });
                    }
                }
                
                // Show the modal
                UI.openModal('add-club-modal');
            } else {
                console.error('Add club modal not found in HTML');
            }
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

// Add error handling for module loading issues
window.addEventListener('error', function(e) {
    console.error('Script error:', e);
    if (e.error && e.error.stack) {
        console.error('Stack trace:', e.error.stack);
    }
});

// Add debug logging for hash changes
window.addEventListener('hashchange', function() {
    console.log('Hash changed to:', window.location.hash);
});

// Main initialization function
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing application...');
    
    // Add special debugging function to window for troubleshooting
    window.debugNavigation = function() {
        const hash = window.location.hash.substring(1) || 'dashboard';
        console.log('Current hash:', hash);
        
        const contentSections = document.querySelectorAll('.content-section');
        console.log('Total content sections:', contentSections.length);
        
        contentSections.forEach(section => {
            console.log(`Section ${section.id} - active: ${section.classList.contains('active')}`);
        });
        
        const navLinks = document.querySelectorAll('.sidebar-nav a');
        console.log('Navigation links:', navLinks.length);
        
        const allSections = document.querySelectorAll('section');
        console.log('All sections in document:', allSections.length);
        allSections.forEach(section => {
            console.log(`Section: ${section.id} - classes: ${section.className}`);
        });
    };
    
    // Check if user is authenticated
    Auth.checkAuthentication()
        .then(() => {
            console.log('User authenticated, setting up UI components...');
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
            
            // Log successful initialization
            console.log('Application initialized successfully - navigation should be working');
            
            // Run debug after a short delay to ensure everything is ready
            setTimeout(() => {
                console.log('Running navigation debug check:');
                window.debugNavigation();
            }, 1000);
        })
        .catch(error => {
            console.error('Authentication error:', error);
        });
});

// Handle route changes
function handleRouteChange() {
    const hash = window.location.hash.substring(1) || 'dashboard';
    console.log(`Route changed to: ${hash}`);
    
    // Get the content sections and sidebar links
    const contentSections = document.querySelectorAll('.content-section');
    const navLinks = document.querySelectorAll('.sidebar-nav a');
    
    // First, toggle visibility of the correct content section
    if (contentSections.length > 0) {
        // Hide all sections
        contentSections.forEach(section => {
            section.classList.remove('active');
        });
        
        // Show the target section
        const targetSection = document.getElementById(`${hash}-view`);
        if (targetSection) {
            console.log(`Activating section: ${hash}-view`);
            targetSection.classList.add('active');
            
            // Update page title
            const pageTitle = document.getElementById('page-title');
            const activeLink = document.querySelector(`.sidebar-nav a[href="#${hash}"]`);
            if (pageTitle && activeLink) {
                pageTitle.textContent = activeLink.querySelector('span').textContent;
            }
            
            // Update active nav link
            navLinks.forEach(link => {
                link.parentElement.classList.remove('active');
            });
            
            if (activeLink) {
                activeLink.parentElement.classList.add('active');
            }
        } else {
            console.error(`Target section not found: ${hash}-view`);
        }
    }
    
    // Then, load the data for this route
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
        case 'stats':
            console.log('Stats view selected - loading statistics');
            // Add stats loading code when implemented
            break;
        case 'insights':
            console.log('Insights view selected - loading insights');
            // Add insights loading code when implemented
            break;
        case 'goals':
            console.log('Goals view selected - loading goals');
            // Add goals loading code when implemented
            break;
        case 'settings':
            console.log('Settings view selected');
            // Add settings loading code when implemented
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