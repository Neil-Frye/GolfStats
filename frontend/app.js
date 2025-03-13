// GolfStats Frontend Application
import { 
    checkAuthentication, 
    updateUserInfo, 
    initLogoutHandler,
    initProfileFormSubmission,
    initProfileImageUpload
} from './js/auth/auth.js';

import { 
    showToast,
    initNavigation,
    setupEventListeners
} from './js/ui/ui.js';

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    console.log('GolfStats frontend initialized');
    
    // Check authentication first
    checkAuthentication();
    
    // Initialize navigation and event listeners
    initNavigation();
    initNewRoundModal();
    initRoundDetailModal();
    setupEventListeners();
    initLogoutHandler();
    
    // Initialize profile-related functionality
    initProfileFormSubmission();
    initProfileImageUpload();
    
    // Load data for the active view
    const hash = window.location.hash.substring(1);
    if (hash && hash !== 'dashboard') {
        // If there's a hash, load the corresponding view
        console.log(`Initial hash: ${hash}`);
        
        // Trigger click on the navigation item
        const navLink = document.querySelector(`.sidebar-nav a[href="#${hash}"]`);
        if (navLink) {
            navLink.click();
        }
        
        // Load data for the specific view
        switch(hash) {
            case 'rounds':
                loadRoundsData('all');
                break;
            case 'stats':
                loadStatsData('all');
                break;
            case 'insights':
                // Insights charts will be initialized when the tab is clicked
                break;
            case 'clubs':
                // Clubs chart will be initialized when the tab is clicked
                break;
            case 'goals':
                // Goals chart will be initialized when the tab is clicked
                break;
        }
    } else {
        // Default to dashboard view
        loadDashboardData();
    }
});

// Check if user is authenticated
async function checkAuthentication() {
    // Don't check on login page to avoid redirect loops
    if (window.location.pathname.includes('login.html')) {
        return;
    }
    
    try {
        const response = await fetch('/api/auth/me', {
            credentials: 'include'
        });
        
        if (!response.ok) {
            // If not authenticated, redirect to login page
            window.location.href = '/login.html';
            return;
        }
        
        const data = await response.json();
        if (!data.user) {
            window.location.href = '/login.html';
            return;
        }
        
        // Update user info if available
        updateUserInfo(data.user);
    } catch (error) {
        console.error('Error checking authentication:', error);
        window.location.href = '/login.html';
    }
}

// Update user info in UI with data from API
function updateUserInfo(user) {
    if (!user) return;
    
    // Update sidebar user info
    const userNameElement = document.querySelector('.user-name');
    const userHandicapElement = document.querySelector('.user-handicap');
    const userAvatarImg = document.querySelector('.user-avatar img');
    
    if (userNameElement) {
        userNameElement.textContent = user.name || user.full_name || user.email.split('@')[0];
    }
    
    if (userHandicapElement && user.preferences) {
        userHandicapElement.textContent = `Handicap: ${user.preferences.handicap || 'N/A'}`;
    }
    
    // Update avatar in sidebar if available
    if (userAvatarImg && (user.avatar_url || user.profile_picture)) {
        userAvatarImg.src = user.avatar_url || user.profile_picture;
    }
    
    // Update profile form fields
    const fullnameInput = document.getElementById('fullname');
    const emailInput = document.getElementById('email');
    const handicapInput = document.getElementById('handicap');
    const phoneInput = document.getElementById('phone');
    const homeCourseInput = document.getElementById('home-course');
    const profileImagePreview = document.getElementById('profile-image-preview');
    
    if (fullnameInput) {
        fullnameInput.value = user.name || user.full_name || '';
    }
    
    if (emailInput) {
        emailInput.value = user.email || '';
    }
    
    if (phoneInput && user.preferences) {
        phoneInput.value = user.preferences.phone || '';
    }
    
    if (handicapInput && user.preferences) {
        handicapInput.value = user.preferences.handicap || '';
    }
    
    if (homeCourseInput && user.preferences) {
        homeCourseInput.value = user.preferences.home_course || '';
    }
    
    // Update profile image preview if available
    if (profileImagePreview && (user.avatar_url || user.profile_picture)) {
        profileImagePreview.src = user.avatar_url || user.profile_picture;
    }
    
    // Update profile completion indicator
    updateProfileCompletion(user);
}

// Update profile completion indicator based on completeness
function updateProfileCompletion(user) {
    if (!user) return;
    
    // Calculate profile completion percentage
    const totalFields = 5; // name, email, handicap, home course, profile image
    let completedFields = 0;
    
    if (user.name || user.full_name) completedFields++;
    if (user.email) completedFields++;
    if (user.avatar_url) completedFields++;
    
    // Check preferences
    if (user.preferences) {
        if (user.preferences.handicap) completedFields++;
        if (user.preferences.home_course) completedFields++;
    }
    
    const completionPercentage = Math.round((completedFields / totalFields) * 100);
    
    // Update sidebar profile completion indicator
    const profileCompletionElement = document.querySelector('.profile-completion');
    if (profileCompletionElement) {
        profileCompletionElement.style.display = 'block';
        profileCompletionElement.innerHTML = `
            <div class="completion-bar">
                <div class="completion-progress" style="width: ${completionPercentage}%"></div>
            </div>
            <p>Profile ${completionPercentage}% complete</p>
        `;
        
        // Add click event to go to profile settings if not complete
        if (completionPercentage < 100) {
            profileCompletionElement.style.cursor = 'pointer';
            profileCompletionElement.addEventListener('click', () => {
                navigateToProfileSettings();
            });
        }
    }
    
    // Update dashboard alert if profile is incomplete
    updateProfileAlert(completionPercentage);
    
    return completionPercentage;
}

// Update profile alert on dashboard
function updateProfileAlert(completionPercentage) {
    const profileAlert = document.getElementById('profile-completion-alert');
    if (!profileAlert) return;
    
    // Only show alert if profile is incomplete
    if (completionPercentage < 100) {
        // Update progress bar
        const progressBar = profileAlert.querySelector('.progress-value');
        if (progressBar) {
            progressBar.style.width = `${completionPercentage}%`;
        }
        
        // Update progress text
        const progressText = profileAlert.querySelector('.progress-text');
        if (progressText) {
            progressText.textContent = `${completionPercentage}% Complete`;
        }
        
        // Only show in dashboard view
        const dashboardView = document.getElementById('dashboard-view');
        if (dashboardView && dashboardView.classList.contains('active')) {
            profileAlert.style.display = 'flex';
        }
        
        // Setup close button
        const closeBtn = profileAlert.querySelector('.close-alert');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                profileAlert.style.display = 'none';
                
                // Remember that the user closed it for this session
                sessionStorage.setItem('profile_alert_closed', 'true');
            });
        }
        
        // Setup complete profile button
        const completeProfileBtn = document.getElementById('complete-profile-btn');
        if (completeProfileBtn) {
            completeProfileBtn.addEventListener('click', () => {
                navigateToProfileSettings();
            });
        }
    } else {
        profileAlert.style.display = 'none';
    }
}

// Navigate to profile settings
function navigateToProfileSettings() {
    // Navigate to settings view
    const settingsLink = document.querySelector('.sidebar-nav a[href="#settings"]');
    if (settingsLink) {
        settingsLink.click();
        
        // Select profile tab in settings
        const profileTab = document.querySelector('.settings-nav li[data-section="profile"]');
        if (profileTab) {
            profileTab.click();
        }
    }
}

// Load dashboard data
async function loadDashboardData() {
    console.log('Loading dashboard data...');
    
    try {
        // Show loading states if needed
        const scoreTrendChartContainer = document.getElementById('score-trend-chart');
        if (scoreTrendChartContainer) {
            const placeholder = scoreTrendChartContainer.querySelector('.chart-placeholder');
            if (placeholder) {
                placeholder.innerHTML = `
                    <div class="loading-container">
                        <div class="spinner"></div>
                        <p>Loading chart data...</p>
                    </div>
                `;
            }
        }
        
        // In a real app, you would fetch dashboard data from the API
        // For now, we'll use mock data and initialize charts
        
        // Initialize dashboard charts
        initDashboardCharts();
        
        // Initialize the recent rounds section (with mock data for now)
        // In a real app, you would load this from the API
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        // Show error state
    }
}

// Initialize all dashboard charts
function initDashboardCharts() {
    // Initialize score trend chart
    initScoreTrendChart();
    
    // Initialize other dashboard charts as needed
}

// Initialize score trend chart
function initScoreTrendChart() {
    // Get chart container
    const chartContainer = document.getElementById('score-trend-chart');
    if (!chartContainer) return;
    
    // Clear any existing content
    chartContainer.innerHTML = '';
    
    // Create canvas for Chart.js
    const canvas = document.createElement('canvas');
    chartContainer.appendChild(canvas);
    
    // Destroy existing chart if it exists
    if (window.scoreTrendChart) {
        window.scoreTrendChart.destroy();
        window.scoreTrendChart = null;
    }
    
    // Sample data - in a real app, this would come from the API
    const labels = ['Apr 2', 'Apr 16', 'May 1', 'May 14', 'May 28', 'Jun 12'];
    const scores = [93, 92, 90, 91, 89, 85];
    const pars = [72, 72, 72, 72, 72, 72];
    const scoresToPar = scores.map((score, i) => score - pars[i]);
    
    // Create chart
    window.scoreTrendChart = new Chart(canvas, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Score',
                    data: scores,
                    borderColor: 'rgba(44, 140, 88, 1)',
                    backgroundColor: 'rgba(44, 140, 88, 0.1)',
                    fill: true,
                    tension: 0.3,
                    yAxisID: 'y'
                },
                {
                    label: 'To Par',
                    data: scoresToPar,
                    borderColor: 'rgba(52, 152, 219, 1)',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    fill: true,
                    tension: 0.3,
                    yAxisID: 'y1',
                    hidden: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Score'
                    },
                    min: Math.min(...scores) - 5,
                    max: Math.max(...scores) + 5,
                    reverse: true // Lower scores are better in golf
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Score to Par'
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            return `Round: ${context[0].label}`;
                        },
                        label: function(context) {
                            if (context.datasetIndex === 0) {
                                return `Score: ${context.raw}`;
                            } else {
                                const value = context.raw;
                                return `To Par: ${value > 0 ? '+' + value : value}`;
                            }
                        }
                    }
                }
            }
        }
    });
    
    // Set up chart controls
    const chartControls = document.querySelectorAll('.chart-control');
    chartControls.forEach(control => {
        control.addEventListener('click', function() {
            chartControls.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // In a real app, you would update the chart data based on the period
            const period = this.dataset.period;
            console.log(`Changing chart period to: ${period}`);
            
            if (period === 'round') {
                window.scoreTrendChart.data.labels = ['Apr 2', 'Apr 16', 'May 1', 'May 14', 'May 28', 'Jun 12'];
                window.scoreTrendChart.data.datasets[0].data = [93, 92, 90, 91, 89, 85];
                window.scoreTrendChart.data.datasets[1].data = [21, 20, 18, 19, 17, 13];
            } else if (period === 'month') {
                window.scoreTrendChart.data.labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
                window.scoreTrendChart.data.datasets[0].data = [94, 93, 92, 91, 89, 87];
                window.scoreTrendChart.data.datasets[1].data = [22, 21, 20, 19, 17, 15];
            }
            
            window.scoreTrendChart.update();
        });
    });
}

// Initialize logout handler
function initLogoutHandler() {
    const logoutButton = document.getElementById('logout-button');
    if (logoutButton) {
        logoutButton.addEventListener('click', async function(e) {
            e.preventDefault();
            
            try {
                // Call logout endpoint
                const response = await fetch('/api/auth/logout', {
                    method: 'POST',
                    credentials: 'include'
                });
                
                if (response.ok) {
                    // Redirect to login page
                    window.location.href = '/login.html';
                } else {
                    console.error('Logout failed');
                }
            } catch (error) {
                console.error('Error during logout:', error);
            }
        });
    }
}

// Navigation handling
function initNavigation() {
    const navLinks = document.querySelectorAll('.sidebar-nav a');
    const contentSections = document.querySelectorAll('.content-section');
    const pageTitle = document.getElementById('page-title');
    const mobileToggle = document.getElementById('mobile-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    // Initialize settings tabs
    initSettingsTabs();
    // Initialize profile form submission
    initProfileFormSubmission();
    
    // Handle navigation clicks
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get the target section ID from the href
            const targetId = this.getAttribute('href').substring(1);
            const targetSection = document.getElementById(`${targetId}-view`);
            
            console.log(`Navigating to: ${targetId}`, targetSection);
            
            if (!targetSection) {
                console.error(`Target section not found: ${targetId}-view`);
                return;
            }
            
            // Update active nav link
            navLinks.forEach(link => {
                link.parentElement.classList.remove('active');
            });
            this.parentElement.classList.add('active');
            
            // Update visible section
            contentSections.forEach(section => {
                section.classList.remove('active');
            });
            targetSection.classList.add('active');
            
            // Update page title
            pageTitle.textContent = this.querySelector('span').textContent;
            
            // Close mobile sidebar if open
            if (window.innerWidth < 768) {
                sidebar.classList.remove('open');
            }
            
            // Update URL hash for better browser navigation
            window.location.hash = targetId;
        });
    });
    
    // Check for hash in URL and activate corresponding tab
    const checkUrlHash = () => {
        const hash = window.location.hash.substring(1);
        if (hash) {
            const linkToActivate = document.querySelector(`.sidebar-nav a[href="#${hash}"]`);
            if (linkToActivate) {
                linkToActivate.click();
            }
        }
    };
    
    // Check hash on initial load
    checkUrlHash();
    
    // Listen for hash changes
    window.addEventListener('hashchange', checkUrlHash);
    
    // Mobile menu toggle
    mobileToggle.addEventListener('click', function() {
        sidebar.classList.toggle('open');
    });
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(e) {
        if (window.innerWidth < 768 && 
            !sidebar.contains(e.target) && 
            !mobileToggle.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    });
}

// Initialize settings tabs functionality
function initSettingsTabs() {
    const settingsNavItems = document.querySelectorAll('.settings-nav li');
    const settingsSections = document.querySelectorAll('.settings-section');
    
    if (!settingsNavItems.length) return;
    
    settingsNavItems.forEach(item => {
        item.addEventListener('click', function() {
            // Update active tab
            settingsNavItems.forEach(item => item.classList.remove('active'));
            this.classList.add('active');
            
            // Show corresponding section
            const sectionId = this.getAttribute('data-section');
            settingsSections.forEach(section => {
                section.classList.remove('active');
            });
            
            const targetSection = document.getElementById(`${sectionId}-settings`);
            if (targetSection) {
                targetSection.classList.add('active');
            }
        });
    });
}

// Initialize profile form submission
function initProfileFormSubmission() {
    const profileForm = document.querySelector('#profile-settings form');
    
    if (!profileForm) return;
    
    // Initialize profile image upload
    initProfileImageUpload();
    
    profileForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Show loading state
        const submitBtn = profileForm.querySelector('.btn-primary');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
        
        try {
            // Get image file if selected
            const imageFile = document.getElementById('profile-image-upload').files[0];
            
            // Create FormData object for multipart form submission (for file upload)
            const formData = new FormData();
            
            // Add profile fields
            formData.append('name', document.getElementById('fullname').value);
            formData.append('email', document.getElementById('email').value);
            formData.append('handicap', document.getElementById('handicap').value);
            formData.append('phone', document.getElementById('phone').value);
            formData.append('home_course', document.getElementById('home-course').value);
            
            // Add image if available
            if (imageFile) {
                formData.append('profile_image', imageFile);
            }
            
            // Get the current user session with token
            const currentUser = await getSessionUser();
            const token = currentUser?.token;
            
            // Send update to API with multipart form data and token in Authorization header
            const response = await fetch('/api/auth/profile', {
                method: 'POST',
                credentials: 'include',
                headers: token ? {
                    'Authorization': `Bearer ${token}`
                } : {},
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('Failed to update profile');
            }
            
            // Get updated user data
            const result = await response.json();
            
            // Show success message
            const successMsg = document.createElement('div');
            successMsg.className = 'success-message';
            successMsg.textContent = 'Profile saved successfully!';
            profileForm.appendChild(successMsg);
            
            // Update user info in the UI
            if (result.user) {
                updateUserInfo(result.user);
            }
            
            // Reset form state
            setTimeout(() => {
                if (profileForm.contains(successMsg)) {
                    profileForm.removeChild(successMsg);
                }
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }, 3000);
        } catch (error) {
            console.error('Error updating profile:', error);
            
            // Show error message
            const errorMsg = document.createElement('div');
            errorMsg.className = 'error-message';
            errorMsg.textContent = error.message || 'An error occurred while saving your profile';
            profileForm.appendChild(errorMsg);
            
            // Reset button
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
            
            // Remove error after delay
            setTimeout(() => {
                if (profileForm.contains(errorMsg)) {
                    profileForm.removeChild(errorMsg);
                }
            }, 5000);
        }
    });
}

// Initialize profile image upload
function initProfileImageUpload() {
    const imageInput = document.getElementById('profile-image-upload');
    const imagePreview = document.getElementById('profile-image-preview');
    
    if (!imageInput || !imagePreview) return;
    
    // Handle image selection
    imageInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const reader = new FileReader();
            
            // When file is loaded, update the preview
            reader.onload = function(e) {
                imagePreview.src = e.target.result;
            };
            
            // Read the selected file
            reader.readAsDataURL(this.files[0]);
        }
    });
}

// Modal handling
function initNewRoundModal() {
    const modal = document.getElementById('new-round-modal');
    const openModalBtn = document.querySelector('.new-round-btn');
    const closeModalBtn = document.querySelector('.close-modal');
    const cancelBtn = document.querySelector('.cancel-btn');
    const form = document.getElementById('new-round-form');
    
    // Set default date to today
    const dateInput = document.getElementById('round-date');
    const today = new Date().toISOString().split('T')[0];
    dateInput.value = today;
    
    // Open modal
    openModalBtn.addEventListener('click', function() {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
    });
    
    // Close modal functions
    function closeModal() {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
    
    closeModalBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);
    
    // Close when clicking outside the modal content
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeModal();
        }
    });
    
    // Handle form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Show loading indication
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
        
        try {
            // Collect form data
            const formData = new FormData(form);
            const roundData = {};
            
            formData.forEach((value, key) => {
                // Convert numeric string values to numbers where appropriate
                if (!isNaN(value) && key !== 'course-name' && key !== 'tee-color' && key !== 'round-notes') {
                    roundData[key.replace('-', '_')] = Number(value);
                } else {
                    roundData[key.replace('-', '_')] = value;
                }
            });
            
            // Format data correctly for API
            const apiRoundData = {
                date: roundData.round_date,
                course_name: roundData.course_name,
                tee_color: roundData.tee_color,
                total_score: roundData.total_score,
                total_par: 72, // Default par value
                notes: roundData.round_notes || '',
                course_location: '',
                source_system: 'web',
                stats: {
                    fairways_hit: roundData.fairways_hit || 0,
                    fairways_total: 14, // Default for 18 holes
                    greens_in_regulation: roundData.greens_hit || 0,
                    putts_total: roundData.total_putts || 0
                }
            };
            
            // Send to API
            const response = await ApiService.saveRound(apiRoundData);
            
            if (response && response.round) {
                // Success - show message and reload dashboard
                const successMsg = document.createElement('div');
                successMsg.className = 'success-message';
                successMsg.textContent = 'Round saved successfully!';
                form.appendChild(successMsg);
                
                // Close modal after delay
                setTimeout(() => {
                    closeModal();
                    form.reset();
                    dateInput.value = today;
                    form.removeChild(successMsg);
                    
                    // Reload dashboard data
                    loadDashboardData();
                }, 1500);
            } else {
                throw new Error('Failed to save round');
            }
        } catch (error) {
            console.error('Error saving round:', error);
            
            // Show error message
            const errorMsg = document.createElement('div');
            errorMsg.className = 'error-message';
            errorMsg.textContent = `Error: ${error.message || 'Failed to save round'}`;
            form.appendChild(errorMsg);
            
            // Remove error message after delay
            setTimeout(() => {
                form.removeChild(errorMsg);
            }, 3000);
        } finally {
            // Reset button state
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    });
}

// Initialize charts
function initCharts() {
    // Reference to the chart container
    const chartContainer = document.getElementById('score-trend-chart');
    
    // For now, we'll just replace the placeholder with a Chart.js chart
    if (chartContainer) {
        const placeholder = chartContainer.querySelector('.chart-placeholder');
        if (placeholder) {
            placeholder.remove();
            
            // Create canvas for Chart.js
            const canvas = document.createElement('canvas');
            chartContainer.appendChild(canvas);
            
            // Sample data - in a real app, this would come from the server
            const labels = ['Apr 2', 'Apr 16', 'May 1', 'May 14', 'May 28', 'Jun 12'];
            const scores = [93, 92, 90, 91, 89, 85];
            
            // Create chart
            new Chart(canvas, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Score',
                        data: scores,
                        fill: false,
                        borderColor: '#2c8c58',
                        tension: 0.1,
                        pointBackgroundColor: '#2c8c58',
                        pointRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            reverse: true, // Lower scores are better in golf
                            min: 70,
                            max: 100,
                            ticks: {
                                stepSize: 5
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                title: function(context) {
                                    return `Round: ${context[0].label}`;
                                },
                                label: function(context) {
                                    return `Score: ${context.raw}`;
                                }
                            }
                        }
                    }
                }
            });
            
            // Set up chart controls
            const chartControls = document.querySelectorAll('.chart-control');
            chartControls.forEach(control => {
                control.addEventListener('click', function() {
                    chartControls.forEach(btn => btn.classList.remove('active'));
                    this.classList.add('active');
                    
                    // In a real app, you would update the chart data based on the selected period
                    const period = this.dataset.period;
                    console.log(`Changing chart period to: ${period}`);
                });
            });
        }
    }
}

// Set up other event listeners
function setupEventListeners() {
    // Handle round view buttons
    const viewRoundButtons = document.querySelectorAll('.view-round-btn');
    viewRoundButtons.forEach(button => {
        button.addEventListener('click', function() {
            // In a real app, this would navigate to the round details page
            // For now, just log the action
            const row = this.closest('tr');
            const date = row.cells[0].textContent;
            const course = row.cells[1].textContent;
            console.log(`Viewing round details for ${date} at ${course}`);
            
            // Simulate navigation to rounds view with the specific round highlighted
            const roundsLink = document.querySelector('a[href="#rounds"]');
            if (roundsLink) {
                roundsLink.click();
            }
        });
    });
    
    // Handle date filter changes
    const dateFilter = document.getElementById('date-range');
    if (dateFilter) {
        dateFilter.addEventListener('change', function() {
            console.log(`Date filter changed to: ${this.value}`);
            
            // Convert date-range values to API timeframe parameters
            let timeframe;
            switch(this.value) {
                case 'last30':
                    timeframe = '30days';
                    break;
                case 'last90':
                    timeframe = '90days';
                    break;
                case 'year':
                    timeframe = 'year';
                    break;
                case 'all':
                default:
                    timeframe = 'all';
                    break;
            }
            
            // Reload data with new timeframe
            loadDataWithTimeframe(timeframe);
        });
    }
    
    // Rounds tab filter
    const roundsFilter = document.getElementById('rounds-filter');
    if (roundsFilter) {
        roundsFilter.addEventListener('change', function() {
            console.log(`Rounds filter changed to: ${this.value}`);
            loadRoundsData(this.value);
        });
    }
    
    // Statistics tab timeframe filter
    const statsTimeframe = document.getElementById('stats-timeframe');
    if (statsTimeframe) {
        statsTimeframe.addEventListener('change', function() {
            console.log(`Stats timeframe changed to: ${this.value}`);
            loadStatsData(this.value);
        });
    }
    
    // Settings tab navigation
    const settingsNavItems = document.querySelectorAll('.settings-nav li');
    settingsNavItems.forEach(item => {
        item.addEventListener('click', function() {
            const section = this.getAttribute('data-section');
            
            // Update active nav item
            settingsNavItems.forEach(navItem => {
                navItem.classList.remove('active');
            });
            this.classList.add('active');
            
            // Show corresponding section
            const settingsSections = document.querySelectorAll('.settings-section');
            settingsSections.forEach(settingsSection => {
                settingsSection.classList.remove('active');
            });
            
            document.getElementById(`${section}-settings`).classList.add('active');
        });
    });
    
    // Handle integration connection buttons
    const connectButtons = document.querySelectorAll('.connect-integration-btn');
    connectButtons.forEach(button => {
        button.addEventListener('click', function() {
            const service = this.getAttribute('data-service');
            showIntegrationModal(service);
        });
    });
    
    // Add club button
    const addClubButton = document.querySelector('.club-card.add-club');
    if (addClubButton) {
        addClubButton.addEventListener('click', showAddClubModal);
    }
    
    // Add first club button (in empty state)
    const addFirstClubBtn = document.querySelector('.add-first-club-btn');
    if (addFirstClubBtn) {
        addFirstClubBtn.addEventListener('click', showAddClubModal);
    }
    
    // Add club button in section header
    const addClubHeaderBtn = document.querySelector('#clubs-view .add-btn');
    if (addClubHeaderBtn) {
        addClubHeaderBtn.addEventListener('click', showAddClubModal);
    }
    
    // Add goal button
    const addGoalButton = document.querySelector('#goals-view .add-btn');
    if (addGoalButton) {
        addGoalButton.addEventListener('click', function() {
            console.log('Add goal clicked');
            // In a real app, this would open a form to add a new goal
            alert('Add goal functionality will be implemented in a future update.');
        });
    }
    
    // Refresh insights button
    const refreshInsightsButton = document.querySelector('#insights-view .refresh-btn');
    if (refreshInsightsButton) {
        refreshInsightsButton.addEventListener('click', function() {
            console.log('Refresh insights clicked');
            // In a real app, this would refresh the insights data
            alert('Insights refresh functionality will be implemented in a future update.');
        });
    }
    
    // Function to load data with specific timeframe
    function loadDataWithTimeframe(timeframe) {
        // Show loading indicator only for the stats cards
        const statsCards = document.querySelectorAll('.stats-card');
        statsCards.forEach(card => {
            const cardValue = card.querySelector('.stats-card-value');
            const originalContent = cardValue.innerHTML;
            cardValue.innerHTML = '<div class="loading-spinner" style="width: 30px; height: 30px;"></div>';
            
            // Store original content for later
            cardValue.dataset.originalContent = originalContent;
        });
        
        // Show loading for chart
        const chartContainer = document.getElementById('score-trend-chart');
        if (chartContainer) {
            chartContainer.classList.add('loading');
        }
        
        // Fetch new data
        ApiService.getStats(timeframe)
            .then(data => {
                if (data && data.stats) {
                    // Update dashboard with new data
                    updateDashboardStats(data.stats);
                    
                    // Update chart data
                    if (window.scoreChart && data.stats.rounds_dates && data.stats.scores) {
                        const labels = data.stats.rounds_dates.map(dateStr => {
                            const date = new Date(dateStr);
                            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                        });
                        
                        window.scoreChart.data.labels = labels;
                        window.scoreChart.data.datasets[0].data = data.stats.scores;
                        window.scoreChart.update();
                    }
                }
            })
            .catch(error => {
                console.error('Error updating data with timeframe:', error);
                
                // Restore original content on error
                statsCards.forEach(card => {
                    const cardValue = card.querySelector('.stats-card-value');
                    if (cardValue.dataset.originalContent) {
                        cardValue.innerHTML = cardValue.dataset.originalContent;
                    }
                });
            })
            .finally(() => {
                // Remove loading state from chart
                if (chartContainer) {
                    chartContainer.classList.remove('loading');
                }
            });
    }
    
    // Pagination buttons for rounds
    const prevPageBtn = document.querySelector('.pagination-prev');
    const nextPageBtn = document.querySelector('.pagination-next');
    
    if (prevPageBtn && nextPageBtn) {
        prevPageBtn.addEventListener('click', function() {
            if (!this.hasAttribute('disabled')) {
                const currentPage = parseInt(document.querySelector('.current-page').textContent);
                if (currentPage > 1) {
                    navigateToPage(currentPage - 1);
                }
            }
        });
        
        nextPageBtn.addEventListener('click', function() {
            if (!this.hasAttribute('disabled')) {
                const currentPage = parseInt(document.querySelector('.current-page').textContent);
                const totalPages = parseInt(document.querySelector('.total-pages').textContent);
                if (currentPage < totalPages) {
                    navigateToPage(currentPage + 1);
                }
            }
        });
    }
    
    // Handle notification bell clicks
    const notificationBell = document.querySelector('.notification-bell');
    if (notificationBell) {
        notificationBell.addEventListener('click', function() {
            console.log('Notification bell clicked');
            // In a real app, this would open a notifications panel
        });
    }
    
    // Initialize charts when tabs are clicked
    const navLinks = document.querySelectorAll('.sidebar-nav a');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            const targetId = this.getAttribute('href').substring(1);
            
            // Initialize charts for the specific tab
            setTimeout(() => {
                switch(targetId) {
                    case 'stats':
                        initStatsCharts();
                        break;
                    case 'insights':
                        initInsightsCharts();
                        break;
                    case 'clubs':
                        loadClubsData();
                        break;
                    case 'goals':
                        initGoalsChart();
                        break;
                }
            }, 100); // Small delay to ensure DOM is ready
        });
    });
}

// Function to load rounds data
function loadRoundsData(filter = 'all') {
    const tableBody = document.getElementById('rounds-table-body');
    if (!tableBody) return;
    
    // Show loading state
    tableBody.innerHTML = `
        <tr class="loading-row">
            <td colspan="9">
                <div class="loading-indicator">
                    <div class="loading-spinner small"></div>
                    <span>Loading rounds...</span>
                </div>
            </td>
        </tr>
    `;
    
    // Fetch rounds data
    ApiService.getRounds({ filter: filter, limit: 10, page: 1 })
        .then(data => {
            if (data && data.rounds && data.rounds.length > 0) {
                // Update table with rounds
                updateRoundsTable(data.rounds, data.pagination);
            } else {
                // Show empty state
                showRoundsEmptyState();
            }
        })
        .catch(error => {
            console.error('Error loading rounds data:', error);
            tableBody.innerHTML = `
                <tr>
                    <td colspan="9" class="error-message">
                        Error loading rounds. Please try again.
                    </td>
                </tr>
            `;
        });
}

// Function to update rounds table
function updateRoundsTable(rounds, pagination) {
    const tableBody = document.getElementById('rounds-table-body');
    if (!tableBody) return;
    
    // Clear table
    tableBody.innerHTML = '';
    
    // Add rows
    rounds.forEach(round => {
        const row = document.createElement('tr');
        
        // Add data-round-id attribute to the row
        row.setAttribute('data-round-id', round.id);
        
        // Format date
        const date = new Date(round.date);
        const formattedDate = date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
        
        // Calculate to par
        const toPar = round.total_score - (round.course_par || 72);
        const toParDisplay = toPar > 0 ? `+${toPar}` : toPar;
        
        // Build row content
        row.innerHTML = `
            <td>${formattedDate}</td>
            <td>${round.course || 'N/A'}</td>
            <td>${round.total_score || 'N/A'}</td>
            <td>${toParDisplay}</td>
            <td>${round.fairways_hit_percentage || 'N/A'}%</td>
            <td>${round.gir_percentage || 'N/A'}%</td>
            <td>${round.total_putts || 'N/A'}</td>
            <td>${round.weather || 'N/A'}</td>
            <td>
                <button class="view-round-btn" data-round-id="${round.id}">View</button>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
    
    // Update pagination
    if (pagination) {
        updatePagination(pagination);
    }
    
    // Hide empty state if visible
    document.querySelector('.rounds-empty-state').style.display = 'none';
    
    // Re-attach event listeners
    attachRoundViewListeners();
}

// Function to show empty rounds state
function showRoundsEmptyState() {
    const tableBody = document.getElementById('rounds-table-body');
    if (!tableBody) return;
    
    // Clear table
    tableBody.innerHTML = '';
    
    // Show empty state
    document.querySelector('.rounds-empty-state').style.display = 'flex';
    
    // Update pagination
    updatePagination({ current_page: 1, total_pages: 1, total_items: 0 });
}

// Function to update pagination
function updatePagination(pagination) {
    const currentPage = document.querySelector('.current-page');
    const totalPages = document.querySelector('.total-pages');
    const prevButton = document.querySelector('.pagination-prev');
    const nextButton = document.querySelector('.pagination-next');
    
    if (currentPage && totalPages) {
        currentPage.textContent = pagination.current_page;
        totalPages.textContent = pagination.total_pages;
    }
    
    if (prevButton) {
        if (pagination.current_page <= 1) {
            prevButton.setAttribute('disabled', '');
        } else {
            prevButton.removeAttribute('disabled');
        }
    }
    
    if (nextButton) {
        if (pagination.current_page >= pagination.total_pages) {
            nextButton.setAttribute('disabled', '');
        } else {
            nextButton.removeAttribute('disabled');
        }
    }
}

// Function to navigate to a specific page
function navigateToPage(page) {
    const filter = document.getElementById('rounds-filter').value;
    
    // Show loading state
    const tableBody = document.getElementById('rounds-table-body');
    if (tableBody) {
        tableBody.innerHTML = `
            <tr class="loading-row">
                <td colspan="9">
                    <div class="loading-indicator">
                        <div class="loading-spinner small"></div>
                        <span>Loading rounds...</span>
                    </div>
                </td>
            </tr>
        `;
    }
    
    // Fetch data for the specified page
    ApiService.getRounds({ filter: filter, limit: 10, page: page })
        .then(data => {
            if (data && data.rounds && data.rounds.length > 0) {
                // Update table with rounds
                updateRoundsTable(data.rounds, data.pagination);
            } else {
                // Show empty state
                showRoundsEmptyState();
            }
        })
        .catch(error => {
            console.error('Error loading rounds data:', error);
            if (tableBody) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="9" class="error-message">
                            Error loading rounds. Please try again.
                        </td>
                    </tr>
                `;
            }
        });
}

// Function to load stats data
function loadStatsData(timeframe = 'all') {
    // Get stat value elements
    const avgScore = document.getElementById('avg-score');
    const scoreDiff = document.getElementById('score-diff');
    const bestRound = document.getElementById('best-round');
    const par3Avg = document.getElementById('par3-avg');
    const par4Avg = document.getElementById('par4-avg');
    const par5Avg = document.getElementById('par5-avg');
    const drivingAccuracy = document.getElementById('driving-accuracy');
    const girPercentage = document.getElementById('gir-percentage');
    const avgDrive = document.getElementById('avg-drive');
    const scrambling = document.getElementById('scrambling');
    const sandSaves = document.getElementById('sand-saves');
    const penalties = document.getElementById('penalties');
    const puttsPerRound = document.getElementById('putts-per-round');
    const puttsPerGir = document.getElementById('putts-per-gir');
    const onePutts = document.getElementById('one-putts');
    const threePutts = document.getElementById('three-putts');
    const putt3to5 = document.getElementById('putt-3-5');
    const putt6to10 = document.getElementById('putt-6-10');
    
    // Show loading state for all stats
    const statValues = document.querySelectorAll('.stat-value');
    statValues.forEach(value => {
        value.textContent = 'Loading...';
    });
    
    // Fetch stats data
    ApiService.getStats(timeframe)
        .then(data => {
            if (data && data.stats) {
                const stats = data.stats;
                
                // Update scoring stats
                if (avgScore) avgScore.textContent = stats.average_score || '--';
                if (scoreDiff) scoreDiff.textContent = stats.score_differential || '--';
                if (bestRound) bestRound.textContent = stats.best_score || '--';
                if (par3Avg) par3Avg.textContent = stats.par3_average ? stats.par3_average.toFixed(1) : '--';
                if (par4Avg) par4Avg.textContent = stats.par4_average ? stats.par4_average.toFixed(1) : '--';
                if (par5Avg) par5Avg.textContent = stats.par5_average ? stats.par5_average.toFixed(1) : '--';
                
                // Update tee to green stats
                if (drivingAccuracy) drivingAccuracy.textContent = stats.fairways_percentage ? `${stats.fairways_percentage}%` : '--';
                if (girPercentage) girPercentage.textContent = stats.gir_percentage ? `${stats.gir_percentage}%` : '--';
                if (avgDrive) avgDrive.textContent = stats.average_drive ? `${stats.average_drive} yds` : '--';
                if (scrambling) scrambling.textContent = stats.scrambling ? `${stats.scrambling}%` : '--';
                if (sandSaves) sandSaves.textContent = stats.sand_saves ? `${stats.sand_saves}%` : '--';
                if (penalties) penalties.textContent = stats.penalties_per_round || '--';
                
                // Update putting stats
                if (puttsPerRound) puttsPerRound.textContent = stats.putts_per_round || '--';
                if (puttsPerGir) puttsPerGir.textContent = stats.putts_per_gir || '--';
                if (onePutts) onePutts.textContent = stats.one_putts_percentage ? `${stats.one_putts_percentage}%` : '--';
                if (threePutts) threePutts.textContent = stats.three_putts_percentage ? `${stats.three_putts_percentage}%` : '--';
                if (putt3to5) putt3to5.textContent = stats.putt_3_5_ft ? `${stats.putt_3_5_ft}%` : '--';
                if (putt6to10) putt6to10.textContent = stats.putt_6_10_ft ? `${stats.putt_6_10_ft}%` : '--';
                
                // Initialize score distribution chart
                initScoreDistributionChart(stats);
            } else {
                // Handle empty data
                statValues.forEach(value => {
                    value.textContent = '--';
                });
            }
        })
        .catch(error => {
            console.error('Error loading stats data:', error);
            statValues.forEach(value => {
                value.textContent = '--';
            });
        });
}

// Initialize stats page charts
function initStatsCharts() {
    // Check if we've already initialized
    if (window.scoreDistChart) return;
    
    const scoreDistCanvas = document.getElementById('score-distribution-chart');
    if (!scoreDistCanvas) return;
    
    // Create a placeholder chart that will be updated with real data
    window.scoreDistChart = new Chart(scoreDistCanvas, {
        type: 'bar',
        data: {
            labels: ['70-75', '76-80', '81-85', '86-90', '91-95', '96-100', '100+'],
            datasets: [{
                label: 'Score Distribution',
                data: [1, 3, 6, 9, 4, 2, 1],
                backgroundColor: 'rgba(44, 140, 88, 0.7)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        title: function(tooltipItems) {
                            return tooltipItems[0].label;
                        },
                        label: function(context) {
                            return `${context.raw} rounds`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Rounds'
                    },
                    ticks: {
                        stepSize: 1
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Score Range'
                    }
                }
            }
        }
    });
    
    // Load stats data to update the chart
    loadStatsData('all');
}

// Update score distribution chart with real data
function initScoreDistributionChart(stats) {
    if (!window.scoreDistChart || !stats.score_distribution) return;
    
    const distributionData = stats.score_distribution;
    const labels = Object.keys(distributionData).sort((a, b) => parseInt(a) - parseInt(b));
    const data = labels.map(key => distributionData[key]);
    
    // Format labels for better display
    const displayLabels = labels.map(label => {
        const rangeStart = parseInt(label);
        return rangeStart >= 100 ? '100+' : `${rangeStart}-${rangeStart + 4}`;
    });
    
    window.scoreDistChart.data.labels = displayLabels;
    window.scoreDistChart.data.datasets[0].data = data;
    window.scoreDistChart.update();
}

// Initialize insights charts
function initInsightsCharts() {
    // Check if charts are already initialized
    if (window.improvementChart) return;
    
    const improvementCanvas = document.getElementById('improvement-chart');
    if (improvementCanvas) {
        window.improvementChart = new Chart(improvementCanvas, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Fairway Accuracy',
                    data: [54, 56, 58, 61, 65, 68],
                    borderColor: 'rgba(44, 140, 88, 0.8)',
                    backgroundColor: 'rgba(44, 140, 88, 0.1)',
                    fill: true,
                    tension: 0.3
                },
                {
                    label: 'Putts/Round',
                    data: [34.2, 33.8, 33.2, 32.5, 31.8, 31.4],
                    borderColor: 'rgba(52, 152, 219, 0.8)',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    fill: true,
                    tension: 0.3,
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        title: {
                            display: true,
                            text: 'Fairway Accuracy (%)'
                        },
                        min: 50,
                        max: 70
                    },
                    y1: {
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Putts/Round'
                        },
                        min: 30,
                        max: 35,
                        grid: {
                            drawOnChartArea: false
                        }
                    }
                }
            }
        });
    }
}

// Load clubs data and populate UI
async function loadClubsData() {
    // Show loading state
    const clubsContainer = document.querySelector('.clubs-container');
    const clubsEmptyState = document.querySelector('.clubs-empty-state');
    const loadingIndicator = document.getElementById('clubs-loading');
    
    if (loadingIndicator) loadingIndicator.style.display = 'block';
    if (clubsContainer) clubsContainer.style.display = 'none';
    if (clubsEmptyState) clubsEmptyState.style.display = 'none';
    
    try {
        // Fetch clubs from API
        const result = await ApiService.getClubs();
        const clubs = result.clubs || [];
        
        // Hide loading indicator
        if (loadingIndicator) loadingIndicator.style.display = 'none';
        
        // Check if we have clubs or need to show empty state
        if (clubs.length === 0) {
            // Show empty state
            if (clubsEmptyState) {
                clubsEmptyState.style.display = 'flex';
            }
        } else {
            // Show clubs container
            if (clubsContainer) {
                clubsContainer.style.display = 'grid';
                
                // Clear existing club cards
                clubsContainer.innerHTML = '';
                
                // Create a card for each club
                clubs.forEach(club => {
                    const clubCard = createClubCard(club);
                    clubsContainer.appendChild(clubCard);
                });
                
                // Add the "Add Club" card at the end
                const addClubCard = document.createElement('div');
                addClubCard.className = 'club-card add-club';
                addClubCard.innerHTML = `
                    <div class="card-icon">
                        <i class="fas fa-plus"></i>
                    </div>
                    <h3>Add Club</h3>
                    <p>Add a new club to your bag</p>
                `;
                addClubCard.addEventListener('click', showAddClubModal);
                clubsContainer.appendChild(addClubCard);
            }
        }
        
        // Initialize chart with real data
        initClubsChart(clubs);
    } catch (error) {
        console.error('Error loading clubs data:', error);
        if (loadingIndicator) loadingIndicator.style.display = 'none';
        if (clubsEmptyState) clubsEmptyState.style.display = 'flex';
    }
}

// Create a club card element from club data
function createClubCard(club) {
    const card = document.createElement('div');
    card.className = 'club-card';
    card.setAttribute('data-club-id', club.id);
    
    let distanceDisplay = '';
    if (club.avg_distance_yards) {
        distanceDisplay = `<p class="club-stat">Avg: ${club.avg_distance_yards} yards</p>`;
    }
    
    let maxDistanceDisplay = '';
    if (club.max_distance_yards) {
        maxDistanceDisplay = `<p class="club-stat">Max: ${club.max_distance_yards} yards</p>`;
    }
    
    card.innerHTML = `
        <div class="card-header">
            <h3>${club.name}</h3>
            <div class="card-actions">
                <button class="edit-button" data-club-id="${club.id}">
                    <i class="fas fa-edit"></i>
                </button>
            </div>
        </div>
        <div class="club-details">
            ${club.brand && club.model ? `<p>${club.brand} ${club.model}</p>` : ''}
            ${club.loft ? `<p class="club-stat">Loft: ${club.loft}°</p>` : ''}
            ${distanceDisplay}
            ${maxDistanceDisplay}
        </div>
    `;
    
    // Add event listener for edit button
    const editButton = card.querySelector('.edit-button');
    if (editButton) {
        editButton.addEventListener('click', (e) => {
            e.stopPropagation();
            showEditClubModal(club);
        });
    }
    
    return card;
}

// Show modal to add a new club
function showAddClubModal() {
    // Create the modal HTML
    const modalHtml = `
        <div class="modal" id="add-club-modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Add New Club</h2>
                    <button class="close-modal">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="add-club-form">
                        <div class="form-group">
                            <label for="club-name">Club Name <span class="required">*</span></label>
                            <input type="text" id="club-name" required placeholder="e.g., Driver, 7 Iron, SW">
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label for="club-type">Club Type <span class="required">*</span></label>
                                <select id="club-type" required>
                                    <option value="">Select Type</option>
                                    <option value="driver">Driver</option>
                                    <option value="wood">Wood</option>
                                    <option value="hybrid">Hybrid</option>
                                    <option value="iron">Iron</option>
                                    <option value="wedge">Wedge</option>
                                    <option value="putter">Putter</option>
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label for="club-loft">Loft (degrees)</label>
                                <input type="number" id="club-loft" min="0" max="72" step="0.5" placeholder="e.g., 10.5">
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label for="club-brand">Brand</label>
                                <input type="text" id="club-brand" placeholder="e.g., TaylorMade">
                            </div>
                            
                            <div class="form-group">
                                <label for="club-model">Model</label>
                                <input type="text" id="club-model" placeholder="e.g., Stealth">
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label for="club-avg-distance">Average Distance (yards)</label>
                                <input type="number" id="club-avg-distance" min="0" placeholder="e.g., 250">
                            </div>
                            
                            <div class="form-group">
                                <label for="club-max-distance">Max Distance (yards)</label>
                                <input type="number" id="club-max-distance" min="0" placeholder="e.g., 270">
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label for="club-notes">Notes</label>
                            <textarea id="club-notes" rows="3" placeholder="Any additional notes about this club..."></textarea>
                        </div>
                        
                        <div class="form-buttons">
                            <button type="button" class="btn-secondary cancel-modal">Cancel</button>
                            <button type="submit" class="btn-primary">Save Club</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to the document
    const modalContainer = document.createElement('div');
    modalContainer.innerHTML = modalHtml;
    document.body.appendChild(modalContainer.firstElementChild);
    
    // Get the modal element
    const modal = document.getElementById('add-club-modal');
    
    // Show the modal
    setTimeout(() => {
        modal.classList.add('show');
    }, 10);
    
    // Add event listeners
    const closeBtn = modal.querySelector('.close-modal');
    const cancelBtn = modal.querySelector('.cancel-modal');
    const form = document.getElementById('add-club-form');
    
    // Close modal events
    closeBtn.addEventListener('click', () => {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.remove();
        }, 300);
    });
    
    cancelBtn.addEventListener('click', () => {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.remove();
        }, 300);
    });
    
    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Get form values
        const clubData = {
            name: document.getElementById('club-name').value,
            club_type: document.getElementById('club-type').value,
            loft: document.getElementById('club-loft').value || null,
            brand: document.getElementById('club-brand').value || null,
            model: document.getElementById('club-model').value || null,
            avg_distance_yards: document.getElementById('club-avg-distance').value || null,
            max_distance_yards: document.getElementById('club-max-distance').value || null,
            notes: document.getElementById('club-notes').value || null,
            is_active: true
        };
        
        try {
            // Show loading state
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<div class="loading-spinner small"></div> Saving...';
            
            // Submit to API
            const result = await ApiService.saveClub(clubData);
            
            if (result.error) {
                throw new Error(result.error);
            }
            
            // Close modal
            modal.classList.remove('show');
            setTimeout(() => {
                modal.remove();
            }, 300);
            
            // Show success message
            // Show success toast
            showToast('Club added successfully!', 'success');
            
            // Reload clubs data
            loadClubsData();
        } catch (error) {
            console.error('Error adding club:', error);
            showToast('Failed to add club. Please try again.', 'error');
            
            // Reset submit button
            const submitBtn = form.querySelector('button[type="submit"]');
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    });
}

// Show modal to edit an existing club
function showEditClubModal(club) {
    // First fetch the club data if only ID was provided
    if (typeof club === 'number' || typeof club === 'string') {
        const clubId = club;
        ApiService.getClub(clubId)
            .then(response => {
                if (response && response.club) {
                    showEditClubModalWithData(response.club);
                } else {
                    showToast('Error loading club data', 'error');
                }
            })
            .catch(error => {
                console.error('Error fetching club data:', error);
                showToast('Error loading club data', 'error');
            });
    } else {
        // Club data was already provided
        showEditClubModalWithData(club);
    }
}

// Show edit club modal with populated data
function showEditClubModalWithData(club) {
    // Create the modal HTML
    const modalHtml = `
        <div class="modal" id="edit-club-modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Edit Club</h2>
                    <button class="close-modal">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="edit-club-form">
                        <input type="hidden" id="edit-club-id" value="${club.id}">
                        
                        <div class="form-group">
                            <label for="edit-club-name">Club Name <span class="required">*</span></label>
                            <input type="text" id="edit-club-name" required value="${club.name || ''}">
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label for="edit-club-type">Club Type <span class="required">*</span></label>
                                <select id="edit-club-type" required>
                                    <option value="">Select Type</option>
                                    <option value="driver" ${club.club_type === 'driver' ? 'selected' : ''}>Driver</option>
                                    <option value="wood" ${club.club_type === 'wood' ? 'selected' : ''}>Wood</option>
                                    <option value="hybrid" ${club.club_type === 'hybrid' ? 'selected' : ''}>Hybrid</option>
                                    <option value="iron" ${club.club_type === 'iron' ? 'selected' : ''}>Iron</option>
                                    <option value="wedge" ${club.club_type === 'wedge' ? 'selected' : ''}>Wedge</option>
                                    <option value="putter" ${club.club_type === 'putter' ? 'selected' : ''}>Putter</option>
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label for="edit-club-loft">Loft (degrees)</label>
                                <input type="number" id="edit-club-loft" min="0" max="72" step="0.5" value="${club.loft || ''}">
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label for="edit-club-brand">Brand</label>
                                <input type="text" id="edit-club-brand" value="${club.brand || ''}">
                            </div>
                            
                            <div class="form-group">
                                <label for="edit-club-model">Model</label>
                                <input type="text" id="edit-club-model" value="${club.model || ''}">
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label for="edit-club-avg-distance">Average Distance (yards)</label>
                                <input type="number" id="edit-club-avg-distance" min="0" value="${club.avg_distance_yards || ''}">
                            </div>
                            
                            <div class="form-group">
                                <label for="edit-club-max-distance">Max Distance (yards)</label>
                                <input type="number" id="edit-club-max-distance" min="0" value="${club.max_distance_yards || ''}">
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label for="edit-club-notes">Notes</label>
                            <textarea id="edit-club-notes" rows="3">${club.notes || ''}</textarea>
                        </div>
                        
                        <div class="form-buttons">
                            <button type="button" class="btn-danger delete-club-btn">Delete Club</button>
                            <div class="save-buttons">
                                <button type="button" class="btn-secondary cancel-modal">Cancel</button>
                                <button type="submit" class="btn-primary">Update Club</button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to the document
    const modalContainer = document.createElement('div');
    modalContainer.innerHTML = modalHtml;
    document.body.appendChild(modalContainer.firstElementChild);
    
    // Get the modal element
    const modal = document.getElementById('edit-club-modal');
    
    // Show the modal
    setTimeout(() => {
        modal.classList.add('show');
    }, 10);
    
    // Add event listeners
    const closeBtn = modal.querySelector('.close-modal');
    const cancelBtn = modal.querySelector('.cancel-modal');
    const deleteBtn = modal.querySelector('.delete-club-btn');
    const form = document.getElementById('edit-club-form');
    
    // Close modal events
    closeBtn.addEventListener('click', () => {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.remove();
        }, 300);
    });
    
    cancelBtn.addEventListener('click', () => {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.remove();
        }, 300);
    });
    
    // Delete button event
    deleteBtn.addEventListener('click', () => {
        // Close the edit modal first
        modal.classList.remove('show');
        setTimeout(() => {
            modal.remove();
            
            // Show confirmation modal
            confirmDeleteClub(club.id, club.name);
        }, 300);
    });
    
    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const clubId = document.getElementById('edit-club-id').value;
        
        // Get form values
        const clubData = {
            name: document.getElementById('edit-club-name').value,
            club_type: document.getElementById('edit-club-type').value,
            loft: document.getElementById('edit-club-loft').value || null,
            brand: document.getElementById('edit-club-brand').value || null,
            model: document.getElementById('edit-club-model').value || null,
            avg_distance_yards: document.getElementById('edit-club-avg-distance').value || null,
            max_distance_yards: document.getElementById('edit-club-max-distance').value || null,
            notes: document.getElementById('edit-club-notes').value || null,
            is_active: true
        };
        
        try {
            // Show loading state
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<div class="loading-spinner small"></div> Updating...';
            
            // Submit to API
            const result = await ApiService.updateClub(clubId, clubData);
            
            if (result.error) {
                throw new Error(result.error);
            }
            
            // Close modal
            modal.classList.remove('show');
            setTimeout(() => {
                modal.remove();
            }, 300);
            
            // Show success message
            showToast('Club updated successfully!', 'success');
            
            // Reload clubs data
            loadClubsData();
        } catch (error) {
            console.error('Error updating club:', error);
            showToast('Failed to update club. Please try again.', 'error');
            
            // Reset submit button
            const submitBtn = form.querySelector('button[type="submit"]');
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    });
}

// Confirm club deletion
function confirmDeleteClub(clubId, clubName) {
    // Create confirmation modal
    const modalHtml = `
        <div class="modal" id="delete-club-modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Delete Club</h2>
                    <button class="close-modal">&times;</button>
                </div>
                <div class="modal-body">
                    <p>Are you sure you want to delete <strong>${clubName}</strong>?</p>
                    <p class="text-danger">This action cannot be undone.</p>
                    
                    <div class="form-buttons">
                        <button type="button" class="btn-secondary cancel-modal">Cancel</button>
                        <button type="button" class="btn-danger confirm-delete-btn">Delete Club</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to the document
    const modalContainer = document.createElement('div');
    modalContainer.innerHTML = modalHtml;
    document.body.appendChild(modalContainer.firstElementChild);
    
    // Get the modal element
    const modal = document.getElementById('delete-club-modal');
    
    // Show the modal
    setTimeout(() => {
        modal.classList.add('show');
    }, 10);
    
    // Add event listeners
    const closeBtn = modal.querySelector('.close-modal');
    const cancelBtn = modal.querySelector('.cancel-modal');
    const confirmBtn = modal.querySelector('.confirm-delete-btn');
    
    // Close modal events
    closeBtn.addEventListener('click', () => {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.remove();
        }, 300);
    });
    
    cancelBtn.addEventListener('click', () => {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.remove();
        }, 300);
    });
    
    // Confirm delete action
    confirmBtn.addEventListener('click', async () => {
        try {
            // Show loading state
            confirmBtn.disabled = true;
            confirmBtn.innerHTML = '<div class="loading-spinner small"></div> Deleting...';
            
            // Submit to API
            const result = await ApiService.deleteClub(clubId);
            
            if (result.error) {
                throw new Error(result.error);
            }
            
            // Close modal
            modal.classList.remove('show');
            setTimeout(() => {
                modal.remove();
            }, 300);
            
            // Show success message
            showToast('Club deleted successfully!', 'success');
            
            // Reload clubs data
            loadClubsData();
        } catch (error) {
            console.error('Error deleting club:', error);
            showToast('Failed to delete club. Please try again.', 'error');
            
            // Reset button
            confirmBtn.disabled = false;
            confirmBtn.textContent = 'Delete Club';
        }
    });
}

// Show a toast notification
function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <i class="toast-icon fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
            <span class="toast-message">${message}</span>
        </div>
        <button class="toast-close">&times;</button>
    `;
    
    // Add to document
    document.body.appendChild(toast);
    
    // Show toast
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    // Auto hide after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3000);
    
    // Close button handler
    const closeBtn = toast.querySelector('.toast-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            toast.classList.remove('show');
            setTimeout(() => {
                toast.remove();
            }, 300);
        });
    }
}

// Initialize clubs distance chart
function initClubsChart(clubs = []) {
    // Destroy existing chart if it exists
    if (window.clubDistancesChart) {
        window.clubDistancesChart.destroy();
        window.clubDistancesChart = null;
    }
    
    const clubDistancesCanvas = document.getElementById('club-distances-chart');
    if (!clubDistancesCanvas) return;
    
    let labels = [];
    let distances = [];
    
    // If we have clubs, use their real data
    if (clubs.length > 0) {
        // Sort clubs by distance (descending)
        const sortedClubs = [...clubs].sort((a, b) => 
            (b.avg_distance_yards || 0) - (a.avg_distance_yards || 0)
        );
        
        // Extract labels and distances from clubs
        labels = sortedClubs.map(club => club.name);
        distances = sortedClubs.map(club => club.avg_distance_yards || 0);
    } else {
        // Use example data if no clubs exist
        labels = ['Driver', '3 Wood', '5 Wood', '4 Iron', '5 Iron', '6 Iron', '7 Iron', '8 Iron', '9 Iron', 'PW', 'GW', 'SW', 'LW'];
        distances = [265, 240, 225, 210, 195, 185, 170, 160, 150, 135, 120, 105, 90];
    }
    
    window.clubDistancesChart = new Chart(clubDistancesCanvas, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Average Distance (yards)',
                data: distances,
                backgroundColor: 'rgba(44, 140, 88, 0.7)',
                borderColor: 'rgba(44, 140, 88, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    min: Math.max(0, Math.min(...distances) - 10),
                    title: {
                        display: true,
                        text: 'Distance (yards)'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.raw} yards`;
                        }
                    }
                }
            }
        }
    });
}

// Initialize goals tracking chart
function initGoalsChart() {
    // Check if chart is already initialized
    if (window.goalTrackingChart) return;
    
    const goalTrackingCanvas = document.getElementById('goal-tracking-chart');
    if (goalTrackingCanvas) {
        window.goalTrackingChart = new Chart(goalTrackingCanvas, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Handicap Index',
                    data: [14.2, 13.9, 13.5, 13.1, 12.7, 12.4],
                    borderColor: 'rgba(25, 118, 210, 0.8)',
                    backgroundColor: 'rgba(25, 118, 210, 0.1)',
                    fill: true,
                    tension: 0.3
                },
                {
                    label: 'Fairways Hit %',
                    data: [57, 59, 61, 62, 63, 64],
                    borderColor: 'rgba(46, 125, 50, 0.8)',
                    backgroundColor: 'rgba(46, 125, 50, 0.1)',
                    fill: true,
                    tension: 0.3,
                    hidden: true
                },
                {
                    label: 'Putts/Round',
                    data: [34, 33.5, 33, 32.5, 32.2, 32],
                    borderColor: 'rgba(194, 24, 91, 0.8)',
                    backgroundColor: 'rgba(194, 24, 91, 0.1)',
                    fill: true,
                    tension: 0.3,
                    hidden: true
                },
                {
                    label: 'GIR %',
                    data: [39, 41, 42, 43, 44, 45],
                    borderColor: 'rgba(230, 81, 0, 0.8)',
                    backgroundColor: 'rgba(230, 81, 0, 0.1)',
                    fill: true,
                    tension: 0.3,
                    hidden: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    },
                    legend: {
                        position: 'top',
                        labels: {
                            boxWidth: 12,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }
}

// Load dashboard data
async function loadDashboardData() {
    // Show loading state
    showLoadingState();
    
    try {
        // Get user profile
        let userProfile;
        try {
            userProfile = await ApiService.getUserProfile();
            if (userProfile && userProfile.user) {
                updateUserInfo(userProfile.user);
            } else {
                console.warn('User profile data is incomplete or missing');
            }
        } catch (userError) {
            console.error('Error loading user profile:', userError);
            // Continue with other data loading despite user profile error
        }
        
        // Get integration status
        try {
            const integrationStatus = await ApiService.getIntegrationStatus();
            if (integrationStatus && integrationStatus.integrations) {
                // Update integration status in the UI
                Object.keys(integrationStatus.integrations).forEach(service => {
                    updateIntegrationStatus(
                        service, 
                        integrationStatus.integrations[service].connected
                    );
                });
            }
        } catch (integrationError) {
            console.error('Error loading integration status:', integrationError);
            // Continue with other data loading despite integration error
        }
        
        // Get statistics
        const timeframe = document.getElementById('date-range')?.value || 'all';
        let statsData;
        try {
            statsData = await ApiService.getStats(timeframe);
            
            if (statsData && statsData.stats) {
                // Update dashboard with real data
                updateDashboardStats(statsData.stats);
                
                // Initialize charts with real data
                initChartsWithData(statsData.stats);
            } else {
                console.warn('Stats data is incomplete or missing');
            }
        } catch (statsError) {
            console.error('Error loading stats data:', statsError);
            // Continue with other data loading despite stats error
        }
        
        // Get recent rounds
        try {
            const roundsData = await ApiService.getRounds({limit: 5});
            if (roundsData && roundsData.rounds) {
                updateRecentRounds(roundsData.rounds);
            } else {
                console.warn('Rounds data is incomplete or missing');
            }
        } catch (roundsError) {
            console.error('Error loading rounds data:', roundsError);
        }
        
        // Show empty state if we have no meaningful data
        if ((!statsData || !statsData.stats) && 
            (!userProfile || !userProfile.user)) {
            showEmptyState();
        }
        
        // Check if any onboarding needed
        checkIntegrationOnboarding();
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showErrorState(error);
    } finally {
        // Hide loading state
        hideLoadingState();
    }
}

// Check if integration onboarding is needed and display guidance
function checkIntegrationOnboarding() {
    // Check if user has any integrations connected
    const hasConnectedIntegrations = document.querySelector('.integration-status.connected');
    
    if (!hasConnectedIntegrations) {
        // Display onboarding guidance
        const dashboardDetails = document.querySelector('.dashboard-details');
        if (dashboardDetails) {
            const onboardingGuidance = document.createElement('div');
            onboardingGuidance.className = 'onboarding-guidance';
            onboardingGuidance.innerHTML = `
                <div class="guidance-header">
                    <i class="fas fa-plug"></i>
                    <h3>Connect Your Golf Platforms</h3>
                    <button class="close-guidance">&times;</button>
                </div>
                <p>Connect your Trackman, Arccos, or SkyTrak accounts to automatically import your golf data.</p>
                <button class="setup-integrations-btn">Set Up Integrations</button>
            `;
            
            // Insert before the first child
            dashboardDetails.insertBefore(onboardingGuidance, dashboardDetails.firstChild);
            
            // Add event listeners
            const closeBtn = onboardingGuidance.querySelector('.close-guidance');
            const setupBtn = onboardingGuidance.querySelector('.setup-integrations-btn');
            
            closeBtn.addEventListener('click', function() {
                onboardingGuidance.remove();
            });
            
            setupBtn.addEventListener('click', function() {
                // Navigate to integrations settings
                const settingsLink = document.querySelector('a[href="#settings"]');
                if (settingsLink) {
                    settingsLink.click();
                    
                    // Select integrations tab
                    setTimeout(() => {
                        const integrationsTab = document.querySelector('.settings-nav li[data-section="integrations"]');
                        if (integrationsTab) {
                            integrationsTab.click();
                        }
                    }, 100);
                }
            });
        }
    }
}

// Update user information in the sidebar
function updateUserInfo(user) {
    const nameElement = document.querySelector('.user-name');
    const handicapElement = document.querySelector('.user-handicap');
    const profileCompletionElement = document.querySelector('.profile-completion');
    
    // Update name with default if empty
    if (nameElement) {
        nameElement.textContent = user.full_name || 'Golf Enthusiast';
        
        // Add a class if name is default to style differently
        if (!user.full_name) {
            nameElement.classList.add('incomplete-profile');
        } else {
            nameElement.classList.remove('incomplete-profile');
        }
    }
    
    // Update handicap with a prompt if empty
    if (handicapElement) {
        if (user.handicap) {
            handicapElement.textContent = `Handicap: ${user.handicap}`;
            handicapElement.classList.remove('incomplete-profile');
        } else {
            handicapElement.textContent = 'Set your handicap';
            handicapElement.classList.add('incomplete-profile');
        }
    }
    
    // Show profile completion indicator if needed
    if (profileCompletionElement) {
        // Calculate profile completion percentage
        const fields = ['full_name', 'handicap', 'preferred_units'];
        const completedFields = fields.filter(field => user[field]).length;
        const completionPercentage = Math.round((completedFields / fields.length) * 100);
        
        if (completionPercentage < 100) {
            profileCompletionElement.style.display = 'block';
            profileCompletionElement.innerHTML = `
                <div class="completion-bar">
                    <div class="completion-progress" style="width: ${completionPercentage}%"></div>
                </div>
                <p>Profile ${completionPercentage}% complete</p>
                <button class="complete-profile-btn">Complete Profile</button>
            `;
            
            // Add click handler for complete profile button
            const completeProfileBtn = profileCompletionElement.querySelector('.complete-profile-btn');
            if (completeProfileBtn) {
                completeProfileBtn.addEventListener('click', () => {
                    // Navigate to settings tab
                    const settingsLink = document.querySelector('.sidebar-nav a[href="#settings"]');
                    if (settingsLink) {
                        settingsLink.click();
                    }
                });
            }
        } else {
            profileCompletionElement.style.display = 'none';
        }
    }
}

// Update dashboard statistics
function updateDashboardStats(stats) {
    // Update average score
    const avgScoreElement = document.querySelector('.stats-card:nth-child(2) .big-number');
    if (avgScoreElement && stats.average_score) {
        avgScoreElement.textContent = stats.average_score;
    }
    
    // Update fairways hit percentage
    const fairwaysElement = document.querySelector('.stats-card:nth-child(3) .big-number');
    if (fairwaysElement && stats.fairways_percentage) {
        fairwaysElement.innerHTML = `${stats.fairways_percentage}<span class="percentage">%</span>`;
    }
    
    // Update GIR percentage
    const girElement = document.querySelector('.stats-card:nth-child(4) .big-number');
    if (girElement && stats.gir_percentage) {
        girElement.innerHTML = `${stats.gir_percentage}<span class="percentage">%</span>`;
    }
    
    // Update performance index (calculated value based on various metrics)
    const perfIndexElement = document.querySelector('.performance-index .progress-value');
    if (perfIndexElement) {
        // Calculate a performance index score (0-100)
        let perfScore = 50; // Default middle value
        
        if (stats.average_score) {
            // Better scores produce higher index (rough calculation - adjust as needed)
            perfScore = Math.max(0, Math.min(100, 100 - ((stats.average_score - 70) * 2)));
        }
        
        perfIndexElement.textContent = Math.round(perfScore);
        
        // Update the circular progress
        const progressElement = document.querySelector('.circular-progress');
        if (progressElement) {
            progressElement.setAttribute('data-value', Math.round(perfScore));
            updateCircularProgress();
        }
    }
    
    // Update strengths and weaknesses
    updateGameAnalysis(stats);
}

// Update game analysis (strengths and weaknesses)
function updateGameAnalysis(stats) {
    // Update strengths
    const strengthsList = document.querySelector('.strengths ul');
    if (strengthsList && stats.strengths && stats.strengths.length > 0) {
        strengthsList.innerHTML = '';
        
        stats.strengths.forEach(strength => {
            const li = document.createElement('li');
            li.innerHTML = `
                <span class="strength-label">${strength.label}</span>
                <div class="strength-bar" style="width: ${strength.percentage}%"></div>
                <span class="strength-value">${strength.percentage}%</span>
            `;
            strengthsList.appendChild(li);
        });
    }
    
    // Update weaknesses
    const weaknessesList = document.querySelector('.weaknesses ul');
    if (weaknessesList && stats.weaknesses && stats.weaknesses.length > 0) {
        weaknessesList.innerHTML = '';
        
        stats.weaknesses.forEach(weakness => {
            const li = document.createElement('li');
            li.innerHTML = `
                <span class="weakness-label">${weakness.label}</span>
                <div class="weakness-bar" style="width: ${weakness.percentage}%"></div>
                <span class="weakness-value">${weakness.percentage}%</span>
            `;
            weaknessesList.appendChild(li);
        });
    }
}

// Update circular progress indicator
function updateCircularProgress() {
    const progressElement = document.querySelector('.circular-progress');
    if (!progressElement) return;
    
    const value = parseInt(progressElement.getAttribute('data-value'));
    const radius = 40;
    const circumference = 2 * Math.PI * radius;
    const dashoffset = circumference * (1 - value / 100);
    
    // If the SVG doesn't exist yet, create it
    if (!progressElement.querySelector('svg')) {
        progressElement.innerHTML = `
            <svg width="120" height="120" viewBox="0 0 120 120">
                <circle class="progress-bg" cx="60" cy="60" r="${radius}" stroke-width="8" fill="none" />
                <circle class="progress-bar" cx="60" cy="60" r="${radius}" stroke-width="8" fill="none"
                    stroke-dasharray="${circumference}" stroke-dashoffset="${dashoffset}" />
            </svg>
            <div class="progress-value">${value}</div>
        `;
    } else {
        // Just update the progress bar
        const progressBar = progressElement.querySelector('.progress-bar');
        progressBar.setAttribute('stroke-dashoffset', dashoffset);
        progressElement.querySelector('.progress-value').textContent = value;
    }
}

// Update recent rounds table
function updateRecentRounds(rounds) {
    const tbody = document.querySelector('.rounds-table tbody');
    if (!tbody || !rounds || rounds.length === 0) return;
    
    tbody.innerHTML = '';
    
    rounds.forEach(round => {
        // Format date
        const date = new Date(round.date);
        const formattedDate = date.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric' 
        });
        
        // Calculate to par
        const toPar = round.total_score - round.course_par;
        const toParDisplay = toPar > 0 ? `+${toPar}` : toPar;
        
        // Create table row
        const tr = document.createElement('tr');
        tr.setAttribute('data-round-id', round.id);
        tr.innerHTML = `
            <td>${formattedDate}</td>
            <td>${round.course}</td>
            <td>${round.total_score}</td>
            <td>${toParDisplay}</td>
            <td>${round.fairways_hit_percentage || '0'}%</td>
            <td>${round.gir_percentage || '0'}%</td>
            <td>${round.total_putts || '0'}</td>
            <td><button class="view-round-btn">View</button></td>
        `;
        
        tbody.appendChild(tr);
    });
    
    // Reattach event listeners
    attachRoundViewListeners();
}

// Initialize charts with real data
function initChartsWithData(stats) {
    // Reference to the chart container
    const chartContainer = document.getElementById('score-trend-chart');
    
    if (chartContainer && stats.rounds_dates && stats.scores && stats.rounds_dates.length > 0) {
        const placeholder = chartContainer.querySelector('.chart-placeholder');
        if (placeholder) {
            placeholder.remove();
        }
        
        // Clear any existing canvas
        chartContainer.innerHTML = '';
        
        // Create canvas for Chart.js
        const canvas = document.createElement('canvas');
        chartContainer.appendChild(canvas);
        
        // Format dates for display
        const labels = stats.rounds_dates.map(dateStr => {
            const date = new Date(dateStr);
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        });
        
        // Get scores
        const scores = stats.scores;
        
        // Create chart
        window.scoreChart = new Chart(canvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Score',
                    data: scores,
                    fill: false,
                    borderColor: '#2c8c58',
                    tension: 0.1,
                    pointBackgroundColor: '#2c8c58',
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        reverse: true, // Lower scores are better in golf
                        min: Math.max(60, Math.min(...scores) - 5),
                        max: Math.min(120, Math.max(...scores) + 5),
                        ticks: {
                            stepSize: 5
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title: function(context) {
                                return `Round: ${context[0].label}`;
                            },
                            label: function(context) {
                                return `Score: ${context.raw}`;
                            }
                        }
                    }
                }
            }
        });
        
        // Set up chart controls
        const chartControls = document.querySelectorAll('.chart-control');
        chartControls.forEach(control => {
            control.addEventListener('click', function() {
                chartControls.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                // Update chart based on selected period
                const period = this.dataset.period;
                updateChartPeriod(period);
            });
        });
    }
}

// Update chart based on selected period
function updateChartPeriod(period) {
    if (!window.scoreChart) return;
    
    // Show loading state for the chart
    const chartContainer = document.getElementById('score-trend-chart');
    if (chartContainer) {
        chartContainer.classList.add('loading');
    }
    
    // Get stats for the selected period
    ApiService.getStats(period === 'round' ? 'all' : period)
        .then(data => {
            if (!data || !data.stats || !data.stats.rounds_dates || !data.stats.scores) return;
            
            const stats = data.stats;
            
            // Format dates based on period
            const labels = stats.rounds_dates.map(dateStr => {
                const date = new Date(dateStr);
                if (period === 'month') {
                    return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
                } else {
                    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                }
            });
            
            // Update chart data
            window.scoreChart.data.labels = labels;
            window.scoreChart.data.datasets[0].data = stats.scores;
            
            // Update y-axis scale
            window.scoreChart.options.scales.y.min = Math.max(60, Math.min(...stats.scores) - 5);
            window.scoreChart.options.scales.y.max = Math.min(120, Math.max(...stats.scores) + 5);
            
            // Update chart
            window.scoreChart.update();
        })
        .catch(error => {
            console.error('Error updating chart period:', error);
        })
        .finally(() => {
            // Hide loading state
            if (chartContainer) {
                chartContainer.classList.remove('loading');
            }
        });
}

// Attach event listeners to round view buttons
function attachRoundViewListeners() {
    const viewRoundButtons = document.querySelectorAll('.view-round-btn');
    viewRoundButtons.forEach(button => {
        button.addEventListener('click', function() {
            const row = this.closest('tr');
            const roundId = this.getAttribute('data-round-id') || row.getAttribute('data-round-id');
            
            if (roundId) {
                // Navigate to round details
                viewRoundDetails(roundId);
            } else {
                console.error("No round ID found for this button");
            }
        });
    });
}

// View round details
function viewRoundDetails(roundId) {
    console.log(`Loading round details for ID: ${roundId}`);
    
    // Show the round detail modal
    const roundDetailModal = document.getElementById('round-detail-modal');
    const loadingContainer = document.getElementById('round-detail-loading');
    const contentContainer = document.getElementById('round-detail-content');
    const errorContainer = document.getElementById('round-detail-error');
    
    if (roundDetailModal) {
        // Reset the modal state
        loadingContainer.style.display = 'flex';
        contentContainer.style.display = 'none';
        errorContainer.style.display = 'none';
        
        // Show the modal
        roundDetailModal.classList.add('visible');
        
        // Fetch round details from the API
        fetchRoundDetails(roundId)
            .then(data => {
                // Hide loading indicator
                loadingContainer.style.display = 'none';
                
                // Populate round details
                populateRoundDetails(data);
                
                // Show content
                contentContainer.style.display = 'block';
            })
            .catch(error => {
                console.error('Error fetching round details:', error);
                loadingContainer.style.display = 'none';
                errorContainer.style.display = 'block';
            });
    }
}

// Get authentication token from local storage
function getAuthToken() {
    return localStorage.getItem('auth_token') || '';
}

// Fetch round details from API
async function fetchRoundDetails(roundId) {
    // Get the authentication token
    const token = getAuthToken();
    
    try {
        // Make API request to get round details
        const response = await fetch(`/api/rounds/${roundId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error fetching round details:', error);
        throw error;
    }
}

// Populate round details in the modal
function populateRoundDetails(data) {
    // Set course and date information
    document.getElementById('detail-course-name').textContent = data.course || 'Unknown Course';
    document.getElementById('detail-round-date').textContent = formatDate(data.date) || 'Unknown Date';
    
    // Set score information
    document.getElementById('detail-total-score').textContent = data.total_score || '--';
    
    // Calculate to par display
    let toPar = '';
    if (data.total_score && data.course_par) {
        const diff = data.total_score - data.course_par;
        toPar = diff === 0 ? 'E' : (diff > 0 ? `+${diff}` : diff.toString());
    }
    document.getElementById('detail-to-par').textContent = toPar ? `(${toPar})` : '';
    
    // Set stats information
    const fairwaysDisplay = data.fairways_hit ? 
        `${data.fairways_hit}/${data.total_fairways} (${data.fairways_hit_percentage}%)` : 
        'N/A';
    document.getElementById('detail-fairways').textContent = fairwaysDisplay;
    
    const girDisplay = data.greens_hit ? 
        `${data.greens_hit}/18 (${data.gir_percentage}%)` : 
        'N/A';
    document.getElementById('detail-gir').textContent = girDisplay;
    
    document.getElementById('detail-putts').textContent = data.total_putts || 'N/A';
    document.getElementById('detail-weather').textContent = data.weather || 'N/A';
    
    // Set notes if available
    const notesContainer = document.getElementById('detail-notes');
    if (data.notes) {
        notesContainer.innerHTML = `<h4>Notes</h4><p>${data.notes}</p>`;
    } else {
        notesContainer.innerHTML = `<h4>Notes</h4><p>No notes for this round.</p>`;
    }
    
    // Populate scorecard if available
    if (data.scorecard) {
        populateScorecard(data.scorecard);
    }
    
    // Populate shot details if available
    if (data.shots && data.shots.length > 0) {
        populateShotDetails(data.shots);
    } else {
        document.getElementById('shot-details-container').innerHTML = 
            '<p class="no-shots-message">No detailed shot data available for this round.</p>';
    }
}

// Format date for display
function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

// Populate scorecard with data
function populateScorecard(scorecard) {
    // Skip if no scorecard data
    if (!scorecard || !Array.isArray(scorecard.holes)) return;
    
    // Set par and score for each hole
    let frontNinePar = 0;
    let frontNineScore = 0;
    let backNinePar = 0;
    let backNineScore = 0;
    
    scorecard.holes.forEach((hole, index) => {
        const holeNumber = index + 1;
        const parElement = document.getElementById(`par-${holeNumber}`);
        const scoreElement = document.getElementById(`score-${holeNumber}`);
        
        if (parElement && scoreElement) {
            parElement.textContent = hole.par || '--';
            scoreElement.textContent = hole.score || '--';
            
            // Add color classes based on score
            if (hole.score && hole.par) {
                scoreElement.classList.remove('birdie', 'par', 'bogey', 'double-bogey');
                
                if (hole.score < hole.par) {
                    scoreElement.classList.add('birdie');
                } else if (hole.score === hole.par) {
                    scoreElement.classList.add('par');
                } else if (hole.score === hole.par + 1) {
                    scoreElement.classList.add('bogey');
                } else if (hole.score > hole.par + 1) {
                    scoreElement.classList.add('double-bogey');
                }
            }
            
            // Calculate front/back nine totals
            if (holeNumber <= 9) {
                frontNinePar += Number(hole.par || 0);
                frontNineScore += Number(hole.score || 0);
            } else {
                backNinePar += Number(hole.par || 0);
                backNineScore += Number(hole.score || 0);
            }
        }
    });
    
    // Set front nine totals
    document.getElementById('par-out').textContent = frontNinePar || '--';
    document.getElementById('score-out').textContent = frontNineScore || '--';
    
    // Set back nine totals
    document.getElementById('par-in').textContent = backNinePar || '--';
    document.getElementById('score-in').textContent = backNineScore || '--';
    
    // Set total
    document.getElementById('par-total').textContent = (frontNinePar + backNinePar) || '--';
    document.getElementById('score-total').textContent = (frontNineScore + backNineScore) || '--';
}

// Populate shot details
function populateShotDetails(shots) {
    const container = document.getElementById('shot-details-container');
    
    // Clear existing content
    container.innerHTML = '';
    
    if (!shots || shots.length === 0) {
        container.innerHTML = '<p class="no-shots-message">No detailed shot data available for this round.</p>';
        return;
    }
    
    // Group shots by hole
    const shotsByHole = {};
    shots.forEach(shot => {
        if (!shotsByHole[shot.hole]) {
            shotsByHole[shot.hole] = [];
        }
        shotsByHole[shot.hole].push(shot);
    });
    
    // Create shot details for each hole
    for (const hole in shotsByHole) {
        const holeShots = shotsByHole[hole];
        
        const holeElement = document.createElement('div');
        holeElement.className = 'hole-shots';
        holeElement.innerHTML = `<h4>Hole ${hole}</h4>`;
        
        const shotsList = document.createElement('ul');
        shotsList.className = 'shots-list';
        
        holeShots.forEach((shot, index) => {
            const shotItem = document.createElement('li');
            shotItem.className = 'shot-item';
            
            // Format shot details based on available data
            let shotDetails = `Shot ${index + 1}: `;
            
            if (shot.club) {
                shotDetails += `${shot.club}, `;
            }
            
            if (shot.distance) {
                shotDetails += `${shot.distance} yards, `;
            }
            
            if (shot.result) {
                shotDetails += `${shot.result}`;
            }
            
            shotItem.textContent = shotDetails;
            shotsList.appendChild(shotItem);
        });
        
        holeElement.appendChild(shotsList);
        container.appendChild(holeElement);
    }
}

// Initialize the round detail modal
function initRoundDetailModal() {
    const modal = document.getElementById('round-detail-modal');
    
    if (modal) {
        // Close button
        const closeBtn = modal.querySelector('.close-modal');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                modal.classList.remove('visible');
            });
        }
        
        // Close when clicking outside the modal content
        modal.addEventListener('click', function(event) {
            if (event.target === modal) {
                modal.classList.remove('visible');
            }
        });
    }
}

// Integration modal
function showIntegrationModal(service) {
    // Get service display name
    const serviceNames = {
        'trackman': 'Trackman',
        'arccos': 'Arccos',
        'skytrak': 'SkyTrak'
    };
    
    const serviceName = serviceNames[service] || service;
    
    // Create modal if it doesn't exist
    if (!document.getElementById('integration-modal')) {
        const modal = document.createElement('div');
        modal.id = 'integration-modal';
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content integration-modal-content">
                <div class="modal-header">
                    <h2>Connect <span class="service-name">${serviceName}</span></h2>
                    <button class="close-modal">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="loading-container" style="display: none;">
                        <div class="loading-spinner"></div>
                        <p>Connecting to ${serviceName}...</p>
                    </div>
                    <div class="error-container" style="display: none;">
                        <div class="error-icon">
                            <i class="fas fa-exclamation-circle"></i>
                        </div>
                        <div class="error-message"></div>
                        <button class="try-again-btn">Try Again</button>
                    </div>
                    <form id="integration-form">
                        <div class="form-group" id="username-field">
                            <label for="integration-username">Username/Email</label>
                            <input type="text" id="integration-username" name="username" required>
                        </div>
                        <div class="form-group">
                            <label for="integration-password">Password</label>
                            <input type="password" id="integration-password" name="password" required>
                        </div>
                        <div class="form-options">
                            <div class="remember-credentials">
                                <input type="checkbox" id="remember-credentials" name="remember" checked>
                                <label for="remember-credentials">Remember my credentials securely</label>
                            </div>
                        </div>
                        <div class="security-callout">
                            <i class="fas fa-lock"></i>
                            <span>Your credentials are securely encrypted and stored using industry-standard security practices.</span>
                        </div>
                        <div class="form-buttons">
                            <button type="button" class="btn-secondary cancel-integration-btn">Cancel</button>
                            <button type="submit" class="btn-primary connect-btn">Connect</button>
                        </div>
                    </form>
                    <div class="success-container" style="display: none;">
                        <div class="success-icon">
                            <i class="fas fa-check-circle"></i>
                        </div>
                        <h3>Connection Successful!</h3>
                        <p>Your <span class="service-name">${serviceName}</span> account has been successfully connected.</p>
                        <button class="done-btn">Done</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        
        // Add event listeners
        const closeBtn = modal.querySelector('.close-modal');
        const cancelBtn = modal.querySelector('.cancel-integration-btn');
        const form = modal.querySelector('#integration-form');
        const tryAgainBtn = modal.querySelector('.try-again-btn');
        const doneBtn = modal.querySelector('.done-btn');
        
        // Close modal functions
        function closeIntegrationModal() {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
        
        closeBtn.addEventListener('click', closeIntegrationModal);
        cancelBtn.addEventListener('click', closeIntegrationModal);
        
        // Close when clicking outside the modal content
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeIntegrationModal();
            }
        });
        
        // Handle form submission
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Show loading state
            const loadingContainer = modal.querySelector('.loading-container');
            const formContainer = form;
            
            formContainer.style.display = 'none';
            loadingContainer.style.display = 'flex';
            
            try {
                // Get form data
                const formData = new FormData(form);
                const credentials = {
                    service: service,
                    username: formData.get('username'),
                    password: formData.get('password'),
                    remember: formData.get('remember') === 'on'
                };
                
                // Special case for Arccos which uses email instead of username
                if (service === 'arccos') {
                    credentials.email = credentials.username;
                    delete credentials.username;
                }
                
                // Send to API with retry logic
                const result = await ApiService.connectIntegration(credentials);
                
                if (result.success) {
                    // Show success state
                    loadingContainer.style.display = 'none';
                    const successContainer = modal.querySelector('.success-container');
                    successContainer.style.display = 'flex';
                    
                    // Update UI to show connected state
                    updateIntegrationStatus(service, true);
                    
                    // Close modal after delay if user doesn't click Done
                    setTimeout(() => {
                        if (modal.style.display !== 'none') {
                            closeIntegrationModal();
                        }
                    }, 3000);
                    
                    // Handle done button
                    doneBtn.addEventListener('click', closeIntegrationModal);
                } else {
                    throw new Error(result.message || 'Connection failed');
                }
            } catch (error) {
                console.error(`Error connecting to ${serviceName}:`, error);
                
                // Show error state
                loadingContainer.style.display = 'none';
                const errorContainer = modal.querySelector('.error-container');
                const errorMessage = modal.querySelector('.error-message');
                
                errorMessage.textContent = `Unable to connect to your ${serviceName} account. Please check your credentials and try again.`;
                errorContainer.style.display = 'flex';
                
                // Try again button resets the form
                tryAgainBtn.addEventListener('click', function() {
                    errorContainer.style.display = 'none';
                    formContainer.style.display = 'block';
                });
            }
        });
    } else {
        // Update existing modal
        const modal = document.getElementById('integration-modal');
        const serviceNameEl = modal.querySelectorAll('.service-name');
        serviceNameEl.forEach(el => {
            el.textContent = serviceName;
        });
        
        // Reset form
        const form = modal.querySelector('#integration-form');
        form.reset();
        form.style.display = 'block';
        
        // Hide other containers
        modal.querySelector('.loading-container').style.display = 'none';
        modal.querySelector('.error-container').style.display = 'none';
        modal.querySelector('.success-container').style.display = 'none';
        
        // Update username field label for Arccos (uses email)
        const usernameField = modal.querySelector('#username-field');
        if (usernameField) {
            const label = usernameField.querySelector('label');
            const input = usernameField.querySelector('input');
            
            if (service === 'arccos') {
                label.textContent = 'Email Address';
                input.type = 'email';
            } else {
                label.textContent = 'Username';
                input.type = 'text';
            }
        }
    }
    
    // Display the modal
    const modal = document.getElementById('integration-modal');
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden'; // Prevent background scrolling
}

// Update integration status in the UI
function updateIntegrationStatus(service, isConnected) {
    const integrationItem = document.getElementById(`${service}-integration`);
    if (!integrationItem) return;
    
    const statusEl = integrationItem.querySelector('.integration-status');
    const buttonEl = integrationItem.querySelector('.connect-integration-btn');
    
    if (isConnected) {
        statusEl.textContent = 'Connected';
        statusEl.classList.remove('disconnected');
        statusEl.classList.add('connected');
        
        buttonEl.textContent = 'Manage Connection';
    } else {
        statusEl.textContent = 'Disconnected';
        statusEl.classList.remove('connected');
        statusEl.classList.add('disconnected');
        
        buttonEl.textContent = 'Connect Account';
    }
}

// Loading state functions
function showLoadingState() {
    // Add loading class to main content
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.classList.add('loading');
    }
    
    // Create loading overlay if it doesn't exist
    if (!document.querySelector('.loading-overlay')) {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-spinner"></div>
            <p>Loading your golf data...</p>
        `;
        document.body.appendChild(overlay);
    }
}

function hideLoadingState() {
    // Remove loading class from main content
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.classList.remove('loading');
    }
    
    // Remove loading overlay
    const overlay = document.querySelector('.loading-overlay');
    if (overlay) {
        overlay.remove();
    }
}

// Empty state function
function showEmptyState() {
    // Update dashboard with empty state message
    const dashboard = document.getElementById('dashboard-view');
    if (dashboard) {
        dashboard.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-golf-ball fa-4x"></i>
                <h2>No golf data yet</h2>
                <p>You haven't recorded any rounds yet. Click the "New Round" button to get started.</p>
                <button class="new-round-btn">
                    <i class="fas fa-plus"></i> Add Your First Round
                </button>
            </div>
        `;
        
        // Reattach event listener for new round button
        const newRoundBtn = dashboard.querySelector('.new-round-btn');
        if (newRoundBtn) {
            newRoundBtn.addEventListener('click', function() {
                const modalOpenBtn = document.querySelector('header .new-round-btn');
                if (modalOpenBtn) {
                    modalOpenBtn.click();
                }
            });
        }
    }
}

// Error state function
function showErrorState(error) {
    // Update dashboard with error message
    const dashboard = document.getElementById('dashboard-view');
    if (dashboard) {
        dashboard.innerHTML = `
            <div class="error-state">
                <i class="fas fa-exclamation-triangle fa-4x"></i>
                <h2>Oops! Something went wrong</h2>
                <p>We couldn't load your golf data. Please try again later.</p>
                <p class="error-details">${error.message || 'Unknown error'}</p>
                <button class="retry-btn">Retry</button>
            </div>
        `;
        
        // Attach retry button listener
        const retryBtn = dashboard.querySelector('.retry-btn');
        if (retryBtn) {
            retryBtn.addEventListener('click', function() {
                loadDashboardData();
            });
        }
    }
}

// Helper function to get the current user session
async function getSessionUser() {
    try {
        const response = await fetch('/api/auth/me', {
            credentials: 'include'
        });
        
        if (!response.ok) {
            return null;
        }
        
        const data = await response.json();
        return data.user || null;
    } catch (error) {
        console.error('Error fetching user session:', error);
        return null;
    }
}

// API service
const ApiService = {
    // Base URL for the backend API
    baseUrl: '/api',
    
    // Maximum number of retry attempts
    maxRetries: 3,
    
    // Helper method to handle API requests with retry logic
    async fetchWithRetry(url, options = {}, retries = 0) {
        try {
            // Add Authorization header with token if not already present
            if (!options.headers || !options.headers['Authorization']) {
                const currentUser = await getSessionUser();
                const token = currentUser?.token;
                
                if (token) {
                    // Create or update headers with Authorization
                    options.headers = {
                        ...options.headers,
                        'Authorization': `Bearer ${token}`
                    };
                }
            }
            
            console.log(`Fetching ${url}, attempt ${retries + 1}`);
            const response = await fetch(url, options);
            
            if (!response.ok) {
                // Special handling for different status codes
                if (response.status === 401) {
                    console.error('Authentication error - user not logged in');
                    // Redirect to login page
                    window.location.href = '/login.html';
                    return { error: 'Authentication required' };
                }
                
                if (response.status === 404) {
                    console.error(`Resource not found: ${url}`);
                    return { error: 'Resource not found' };
                }
                
                if (response.status >= 500) {
                    // Server error, might be worth retrying
                    if (retries < this.maxRetries) {
                        console.warn(`Server error (${response.status}), retrying... (${retries + 1}/${this.maxRetries})`);
                        // Exponential backoff: 300ms, 900ms, 2700ms
                        const delay = Math.pow(3, retries) * 300;
                        await new Promise(resolve => setTimeout(resolve, delay));
                        return this.fetchWithRetry(url, options, retries + 1);
                    }
                }
                
                throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
            }
            
            try {
                return await response.json();
            } catch (jsonError) {
                console.error('Error parsing JSON response:', jsonError);
                return { error: 'Invalid response format' };
            }
        } catch (error) {
            if (retries < this.maxRetries && error.message.includes('fetch')) {
                // Network error, retry
                console.warn(`Network error, retrying... (${retries + 1}/${this.maxRetries})`);
                const delay = Math.pow(2, retries) * 500;
                await new Promise(resolve => setTimeout(resolve, delay));
                return this.fetchWithRetry(url, options, retries + 1);
            }
            throw error;
        }
    },
    
    // Connect to golf service integrations
    async connectIntegration(credentials) {
        try {
            // Extra validation based on service type
            if (credentials.service === 'arccos' && !credentials.email) {
                return { success: false, message: 'Email is required for Arccos' };
            } else if ((credentials.service === 'trackman' || credentials.service === 'skytrak') && !credentials.username) {
                return { success: false, message: 'Username is required' };
            }
            
            if (!credentials.password) {
                return { success: false, message: 'Password is required' };
            }
            
            const response = await this.fetchWithRetry(`${this.baseUrl}/integrations/connect`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify(credentials)
            });
            
            if (response.error) {
                return { success: false, message: response.error };
            }
            
            return response;
        } catch (error) {
            console.error('Error connecting integration:', error);
            return { 
                success: false, 
                message: error.message || 'Failed to connect to the service. Please try again.'
            };
        }
    },
    
    // Get status of integrations
    async getIntegrationStatus() {
        try {
            const response = await this.fetchWithRetry(`${this.baseUrl}/integrations/status`, {
                credentials: 'include'
            });
            
            if (response.error) {
                return { integrations: {} };
            }
            
            return response;
        } catch (error) {
            console.error('Error getting integration status:', error);
            return { integrations: {} };
        }
    },
    
    // Test integration connection
    async testIntegration(service) {
        try {
            const response = await this.fetchWithRetry(`${this.baseUrl}/integrations/test/${service}`, {
                method: 'POST',
                credentials: 'include'
            });
            
            return response;
        } catch (error) {
            console.error(`Error testing ${service} integration:`, error);
            return { success: false, message: error.message };
        }
    },
    
    // Get user profile
    async getUserProfile() {
        try {
            return await this.fetchWithRetry(`${this.baseUrl}/user`, {
                credentials: 'include' // Important for session cookies
            });
        } catch (error) {
            console.error('Error fetching user profile:', error);
            return null;
        }
    },
    
    // Get rounds with optional filters
    async getRounds(filters = {}) {
        try {
            let url = `${this.baseUrl}/rounds`;
            if (Object.keys(filters).length > 0) {
                const params = new URLSearchParams(filters);
                url += `?${params.toString()}`;
            }
            
            const result = await this.fetchWithRetry(url, {
                credentials: 'include'
            });
            
            // If result contains an error property, return empty rounds
            if (result.error) {
                console.warn('Error getting rounds:', result.error);
                return { rounds: [] };
            }
            
            return result;
        } catch (error) {
            console.error('Error fetching rounds:', error);
            return { rounds: [] };
        }
    },
    
    // Save a new round
    async saveRound(roundData) {
        try {
            return await this.fetchWithRetry(`${this.baseUrl}/rounds`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify(roundData)
            });
        } catch (error) {
            console.error('Error saving round:', error);
            throw error;
        }
    },
    
    // Get statistics for a user
    async getStats(timeframe = 'all') {
        try {
            const result = await this.fetchWithRetry(`${this.baseUrl}/stats?timeframe=${timeframe}`, {
                credentials: 'include'
            });
            
            // If result contains an error property, handle it
            if (result.error) {
                console.warn('Error getting stats:', result.error);
                return { stats: {} };
            }
            
            return result;
        } catch (error) {
            console.error('Error fetching stats:', error);
            return { stats: {} };
        }
    },
    
    // Get clubs for current user
    async getClubs() {
        try {
            const result = await this.fetchWithRetry(`${this.baseUrl}/clubs`, {
                credentials: 'include'
            });
            
            // If result contains an error property, handle it
            if (result.error) {
                console.warn('Error getting clubs:', result.error);
                return { clubs: [] };
            }
            
            return result;
        } catch (error) {
            console.error('Error fetching clubs:', error);
            return { clubs: [] };
        }
    },
    
    // Get a specific club
    async getClub(clubId) {
        try {
            const result = await this.fetchWithRetry(`${this.baseUrl}/clubs/${clubId}`, {
                credentials: 'include'
            });
            
            if (result.error) {
                console.warn(`Error getting club ${clubId}:`, result.error);
                return { club: null };
            }
            
            return result;
        } catch (error) {
            console.error(`Error fetching club ${clubId}:`, error);
            return { club: null };
        }
    },
    
    // Create a new club
    async saveClub(clubData) {
        try {
            const result = await this.fetchWithRetry(`${this.baseUrl}/clubs`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify(clubData)
            });
            
            return result;
        } catch (error) {
            console.error('Error saving club:', error);
            return { error: 'Failed to save club' };
        }
    },
    
    // Update an existing club
    async updateClub(clubId, clubData) {
        try {
            const result = await this.fetchWithRetry(`${this.baseUrl}/clubs/${clubId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify(clubData)
            });
            
            return result;
        } catch (error) {
            console.error(`Error updating club ${clubId}:`, error);
            return { error: 'Failed to update club' };
        }
    },
    
    // Delete a club
    async deleteClub(clubId) {
        try {
            const result = await this.fetchWithRetry(`${this.baseUrl}/clubs/${clubId}`, {
                method: 'DELETE',
                credentials: 'include'
            });
            
            return result;
        } catch (error) {
            console.error(`Error deleting club ${clubId}:`, error);
            return { error: 'Failed to delete club' };
        }
    }
};