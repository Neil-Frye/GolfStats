import ApiService from '../api/api.js';
import { updateCircularProgress, navigateToProfileSettings, formatDate } from '../ui/ui.js';
import { viewRoundDetails } from '../rounds/rounds.js';

// Load dashboard data
async function loadDashboardData() {
    // Show loading state
    showLoadingState();
    
    try {
        // Get user profile
        let userProfile;
        try {
            userProfile = await ApiService.getCurrentUser();
            if (userProfile && userProfile.user) {
                // Update user info if a function to do so exists
                if (typeof updateUserInfo === 'function') {
                    updateUserInfo(userProfile.user);
                }
            } else {
                console.warn('User profile data is incomplete or missing');
            }
        } catch (userError) {
            console.error('Error loading user profile:', userError);
            // Continue with other data loading despite user profile error
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
                initScoreTrendChart(statsData.stats);
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
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showErrorState(error);
    } finally {
        // Hide loading state
        hideLoadingState();
    }
}

// Initialize score trend chart
function initScoreTrendChart(stats) {
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
    
    // Use real data if available, otherwise use sample data
    let labels = ['Apr 2', 'Apr 16', 'May 1', 'May 14', 'May 28', 'Jun 12'];
    let scores = [93, 92, 90, 91, 89, 85];
    let pars = [72, 72, 72, 72, 72, 72];
    
    // If we have real data, use it
    if (stats && stats.rounds_dates && stats.scores && stats.pars) {
        labels = stats.rounds_dates.map(dateStr => {
            const date = new Date(dateStr);
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        });
        
        scores = stats.scores;
        pars = stats.pars;
    }
    
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
            
            if (window.scoreTrendChart) {
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

// Update recent rounds in the dashboard
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
        const toPar = round.total_score - (round.course_par || 72);
        const toParDisplay = toPar > 0 ? `+${toPar}` : toPar;
        
        // Create table row
        const tr = document.createElement('tr');
        tr.setAttribute('data-round-id', round.id);
        tr.innerHTML = `
            <td>${formattedDate}</td>
            <td>${round.course || 'N/A'}</td>
            <td>${round.total_score || 'N/A'}</td>
            <td>${toParDisplay}</td>
            <td>${round.fairways_hit_percentage || 'N/A'}%</td>
            <td>${round.gir_percentage || 'N/A'}%</td>
            <td>${round.total_putts || 'N/A'}</td>
            <td><button class="view-round-btn" data-round-id="${round.id}">View</button></td>
        `;
        
        tbody.appendChild(tr);
    });
    
    // Attach event listeners to view buttons
    attachRoundViewListeners();
}

// Attach event listeners to round view buttons
function attachRoundViewListeners() {
    const viewRoundButtons = document.querySelectorAll('.view-round-btn');
    viewRoundButtons.forEach(button => {
        button.addEventListener('click', function() {
            const roundId = this.getAttribute('data-round-id') || 
                            this.closest('tr')?.getAttribute('data-round-id');
            
            if (roundId) {
                viewRoundDetails(roundId);
            } else {
                console.error("No round ID found for this button");
            }
        });
    });
}

// Show empty state when no data is available
function showEmptyState() {
    const dashboardOverview = document.querySelector('.dashboard-overview');
    if (!dashboardOverview) return;
    
    // Check if we already have the empty state
    if (dashboardOverview.querySelector('.empty-dashboard-state')) return;
    
    // Create empty state
    const emptyState = document.createElement('div');
    emptyState.className = 'empty-dashboard-state';
    emptyState.innerHTML = `
        <div class="empty-state-icon">
            <i class="fas fa-golf-ball"></i>
        </div>
        <h3>Welcome to GolfStats!</h3>
        <p>Track your golf game and improve your performance with detailed statistics and analysis.</p>
        <div class="empty-state-actions">
            <button class="btn-primary add-first-round-btn">Add Your First Round</button>
        </div>
    `;
    
    // Add event listeners
    const addRoundBtn = emptyState.querySelector('.add-first-round-btn');
    
    addRoundBtn.addEventListener('click', () => {
        const newRoundBtn = document.querySelector('.new-round-btn');
        if (newRoundBtn) {
            newRoundBtn.click();
        }
    });
    
    // Add to dashboard
    dashboardOverview.appendChild(emptyState);
}

// Show error state
function showErrorState(error) {
    const dashboardOverview = document.querySelector('.dashboard-overview');
    if (!dashboardOverview) return;
    
    // Create error state
    const errorState = document.createElement('div');
    errorState.className = 'dashboard-error-state';
    errorState.innerHTML = `
        <div class="error-icon">
            <i class="fas fa-exclamation-circle"></i>
        </div>
        <h3>Something went wrong</h3>
        <p>${error.message || 'There was an error loading your dashboard data.'}</p>
        <button class="btn-primary retry-btn">Try Again</button>
    `;
    
    // Add retry action
    const retryBtn = errorState.querySelector('.retry-btn');
    retryBtn.addEventListener('click', () => {
        // Remove error state
        errorState.remove();
        
        // Reload dashboard data
        loadDashboardData();
    });
    
    // Add to dashboard
    dashboardOverview.appendChild(errorState);
}

// Show loading state for dashboard
function showLoadingState() {
    const statsCards = document.querySelectorAll('.stats-card .big-number');
    statsCards.forEach(card => {
        card.dataset.originalContent = card.innerHTML;
        card.innerHTML = '<div class="skeleton-loader"></div>';
    });
    
    // Add loading indicator to chart
    const chartContainer = document.getElementById('score-trend-chart');
    if (chartContainer) {
        chartContainer.innerHTML = `
            <div class="chart-loading">
                <div class="skeleton-loader chart-skeleton"></div>
            </div>
        `;
    }
    
    // Add loading indicator to recent rounds
    const tableBody = document.querySelector('.rounds-table tbody');
    if (tableBody) {
        tableBody.innerHTML = `
            <tr class="loading-row">
                <td colspan="8">
                    <div class="loading-indicator">
                        <div class="loading-spinner small"></div>
                        <span>Loading rounds...</span>
                    </div>
                </td>
            </tr>
        `;
    }
}

// Hide loading state
function hideLoadingState() {
    // Restore stat cards
    const statsCards = document.querySelectorAll('.stats-card .big-number');
    statsCards.forEach(card => {
        if (card.dataset.originalContent) {
            card.innerHTML = card.dataset.originalContent;
        }
    });
}

// Initialize dashboard
function initDashboard() {
    // Set up date filter change handler
    const dateRangeSelect = document.getElementById('date-range');
    if (dateRangeSelect) {
        dateRangeSelect.addEventListener('change', function() {
            const timeframe = this.value;
            loadDashboardData(timeframe);
        });
    }
    
    // Set up chart controls
    setupChartControls();
    
    // Set up profile completion alert
    updateProfileAlert(50); // Default 50% completion - should be calculated based on user profile
    
    // Load dashboard data
    loadDashboardData();
    
    // Listen for round saved event
    document.addEventListener('roundSaved', function() {
        loadDashboardData();
    });
}

// Export dashboard module functions
export {
    initDashboard,
    loadDashboardData,
    updateDashboardStats,
    updateGameAnalysis,
    updateRecentRounds,
    updateProfileAlert
};