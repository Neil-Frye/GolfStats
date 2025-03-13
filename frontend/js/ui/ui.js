// Navigation handling
function initNavigation() {
    const navLinks = document.querySelectorAll('.sidebar-nav a');
    const contentSections = document.querySelectorAll('.content-section');
    const pageTitle = document.getElementById('page-title');
    const mobileToggle = document.getElementById('mobile-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    // Initialize settings tabs
    initSettingsTabs();
    
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

// Format date for display
function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

// Show a toast notification message
function showToast(message, type = 'info', duration = 3000) {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    // Add close button
    const closeBtn = document.createElement('button');
    closeBtn.className = 'toast-close';
    closeBtn.innerHTML = '&times;';
    closeBtn.addEventListener('click', () => {
        toast.remove();
    });
    
    toast.appendChild(closeBtn);
    toastContainer.appendChild(toast);
    
    // Show the toast with animation
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    // Hide and remove after duration
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300); // Wait for transition to complete
    }, duration);
}

// Show loading state
function showLoadingState(elementId, message = 'Loading...') {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    // Store original content in data attribute to restore later
    element.dataset.originalContent = element.innerHTML;
    
    // Insert loading spinner and message
    element.innerHTML = `
        <div class="loading-state">
            <div class="loading-spinner"></div>
            <span class="loading-message">${message}</span>
        </div>
    `;
    
    // Add loading class for styling
    element.classList.add('is-loading');
}

// Hide loading state
function hideLoadingState(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    // Restore original content if it exists
    if (element.dataset.originalContent) {
        element.innerHTML = element.dataset.originalContent;
        delete element.dataset.originalContent;
    } else {
        // Just remove the loading spinner
        const loadingState = element.querySelector('.loading-state');
        if (loadingState) {
            loadingState.remove();
        }
    }
    
    // Remove loading class
    element.classList.remove('is-loading');
}

// Show empty state message
function showEmptyState(containerId, message, iconClass = 'fa-flag-checkered', actionButton = null) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // Clear container
    container.innerHTML = '';
    
    // Create empty state element
    const emptyState = document.createElement('div');
    emptyState.className = 'empty-state';
    
    // Add icon
    const icon = document.createElement('i');
    icon.className = `fas ${iconClass} fa-3x`;
    emptyState.appendChild(icon);
    
    // Add message
    const messageElement = document.createElement('h3');
    messageElement.textContent = message;
    emptyState.appendChild(messageElement);
    
    // Add action button if provided
    if (actionButton) {
        const { label, callback, className = 'btn-primary' } = actionButton;
        
        const button = document.createElement('button');
        button.className = `btn ${className}`;
        button.textContent = label;
        button.addEventListener('click', callback);
        
        emptyState.appendChild(button);
    }
    
    // Add to container
    container.appendChild(emptyState);
}

// Show error state
function showErrorState(containerId, message, retryCallback = null) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // Clear container
    container.innerHTML = '';
    
    // Create error state element
    const errorState = document.createElement('div');
    errorState.className = 'error-state';
    
    // Add icon
    const icon = document.createElement('i');
    icon.className = 'fas fa-exclamation-circle fa-3x';
    errorState.appendChild(icon);
    
    // Add message
    const messageElement = document.createElement('h3');
    messageElement.textContent = message;
    errorState.appendChild(messageElement);
    
    // Add retry button if callback provided
    if (retryCallback) {
        const button = document.createElement('button');
        button.className = 'btn btn-primary';
        button.textContent = 'Try Again';
        button.addEventListener('click', retryCallback);
        
        errorState.appendChild(button);
    }
    
    // Add to container
    container.appendChild(errorState);
}

// Initialize modal
function initModal(modalId, options = {}) {
    const modal = document.getElementById(modalId);
    if (!modal) return;
    
    const closeButtons = modal.querySelectorAll('.close-modal, .cancel-btn');
    
    // Close modal when clicking close button
    closeButtons.forEach(button => {
        button.addEventListener('click', () => {
            closeModal(modalId);
            
            if (options.onClose) {
                options.onClose();
            }
        });
    });
    
    // Close modal when clicking outside (if enabled)
    if (options.closeOnOutsideClick !== false) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal(modalId);
                
                if (options.onClose) {
                    options.onClose();
                }
            }
        });
    }
    
    // Close on escape key (if enabled)
    if (options.closeOnEscape !== false) {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.classList.contains('visible')) {
                closeModal(modalId);
                
                if (options.onClose) {
                    options.onClose();
                }
            }
        });
    }
    
    return {
        open: () => openModal(modalId, options.onOpen),
        close: () => closeModal(modalId, options.onClose)
    };
}

// Open modal
function openModal(modalId, onOpenCallback) {
    const modal = document.getElementById(modalId);
    if (!modal) return;
    
    modal.classList.add('visible');
    document.body.classList.add('modal-open');
    
    if (onOpenCallback) {
        onOpenCallback();
    }
}

// Close modal
function closeModal(modalId, onCloseCallback) {
    const modal = document.getElementById(modalId);
    if (!modal) return;
    
    modal.classList.remove('visible');
    document.body.classList.remove('modal-open');
    
    // Reset form if present
    const form = modal.querySelector('form');
    if (form) {
        form.reset();
    }
    
    if (onCloseCallback) {
        onCloseCallback();
    }
}

// Set up all event listeners
function setupEventListeners() {
    // Date filter change handler
    const dateRange = document.getElementById('date-range');
    if (dateRange) {
        dateRange.addEventListener('change', function() {
            const selectedValue = this.value;
            console.log(`Date range changed to: ${selectedValue}`);
            
            // TODO: Implement date range filtering
        });
    }
    
    // New round button handler
    const newRoundBtns = document.querySelectorAll('.new-round-btn');
    newRoundBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Show new round modal
            openModal('new-round-modal');
        });
    });
    
    // New goal button handler
    const newGoalBtns = document.querySelectorAll('.goals-view .add-btn');
    newGoalBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Show toast notification since goal functionality is not implemented yet
            showToast('Goal functionality coming soon!', 'info');
        });
    });
    
    // Set up chart controls
    setupChartControls();
}

// Set up chart controls
function setupChartControls() {
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

// Export UI module functions
export {
    initNavigation,
    initSettingsTabs,
    navigateToProfileSettings,
    updateProfileAlert,
    updateCircularProgress,
    formatDate,
    showToast,
    showLoadingState,
    hideLoadingState,
    showEmptyState,
    showErrorState,
    initModal,
    openModal,
    closeModal,
    setupEventListeners,
    setupChartControls
};