// GolfStats Frontend Application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    console.log('GolfStats frontend initialized');
    initNavigation();
    initNewRoundModal();
    loadDashboardData();
    setupEventListeners();
});

// Navigation handling
function initNavigation() {
    const navLinks = document.querySelectorAll('.sidebar-nav a');
    const contentSections = document.querySelectorAll('.content-section');
    const pageTitle = document.getElementById('page-title');
    const mobileToggle = document.getElementById('mobile-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    // Handle navigation clicks
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get the target section ID from the href
            const targetId = this.getAttribute('href').substring(1);
            const targetSection = document.getElementById(`${targetId}-view`);
            
            if (!targetSection) return;
            
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
        });
    });
    
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
                course: roundData.course_name,
                tee_color: roundData.tee_color,
                total_score: roundData.total_score,
                notes: roundData.round_notes || '',
                course_par: 72, // Default par value
                stats: {
                    fairways_hit: roundData.fairways_hit || 0,
                    fairways_total: 14, // Default for 18 holes
                    greens_hit: roundData.greens_hit || 0,
                    greens_total: 18,
                    total_putts: roundData.total_putts || 0
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
    }}
    
    // Handle notification bell clicks
    const notificationBell = document.querySelector('.notification-bell');
    notificationBell.addEventListener('click', function() {
        console.log('Notification bell clicked');
        // In a real app, this would open a notifications panel
    });
}

// Load dashboard data
async function loadDashboardData() {
    // Show loading state
    showLoadingState();
    
    try {
        // Get user profile
        const userProfile = await ApiService.getUserProfile();
        if (userProfile && userProfile.user) {
            updateUserInfo(userProfile.user);
        }
        
        // Get statistics
        const timeframe = document.getElementById('date-range').value;
        const statsData = await ApiService.getStats(timeframe);
        
        if (statsData && statsData.stats) {
            // Update dashboard with real data
            updateDashboardStats(statsData.stats);
            
            // Get recent rounds
            const roundsData = await ApiService.getRounds({limit: 5});
            if (roundsData && roundsData.rounds) {
                updateRecentRounds(roundsData.rounds);
            }
            
            // Initialize charts with real data
            initChartsWithData(statsData.stats);
        } else {
            // Handle empty data state
            showEmptyState();
        }
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showErrorState(error);
    } finally {
        // Hide loading state
        hideLoadingState();
    }
}

// Update user information in the sidebar
function updateUserInfo(user) {
    const nameElement = document.querySelector('.user-name');
    const handicapElement = document.querySelector('.user-handicap');
    
    if (nameElement && user.full_name) {
        nameElement.textContent = user.full_name;
    }
    
    if (handicapElement && user.handicap) {
        handicapElement.textContent = `Handicap: ${user.handicap}`;
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
            const roundId = row.getAttribute('data-round-id');
            
            // Navigate to round details
            viewRoundDetails(roundId);
        });
    });
}

// View round details
function viewRoundDetails(roundId) {
    console.log(`Viewing round details for ID: ${roundId}`);
    
    // Navigate to rounds view
    const roundsLink = document.querySelector('a[href="#rounds"]');
    if (roundsLink) {
        roundsLink.click();
        
        // In a real app, you would load the specific round details here
        // For now, we'll just show a message
        const roundsView = document.getElementById('rounds-view');
        if (roundsView) {
            roundsView.innerHTML = `
                <div class="section-placeholder">
                    <h2>Round Details</h2>
                    <p>Loading details for round ID: ${roundId}...</p>
                </div>
            `;
        }
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

// API service
const ApiService = {
    // Base URL for the backend API
    baseUrl: 'http://localhost:5000/api',
    
    // Get user profile
    async getUserProfile() {
        try {
            const response = await fetch(`${this.baseUrl}/user`, {
                credentials: 'include' // Important for session cookies
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            
            return await response.json();
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
            
            const response = await fetch(url, {
                credentials: 'include'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching rounds:', error);
            return { rounds: [] };
        }
    },
    
    // Save a new round
    async saveRound(roundData) {
        try {
            const response = await fetch(`${this.baseUrl}/rounds`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify(roundData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error saving round:', error);
            throw error;
        }
    },
    
    // Get statistics for a user
    async getStats(timeframe = 'all') {
        try {
            const response = await fetch(`${this.baseUrl}/stats?timeframe=${timeframe}`, {
                credentials: 'include'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching stats:', error);
            throw error;
        }
    }
};