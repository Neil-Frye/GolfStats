// GolfStats Frontend Application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    console.log('GolfStats frontend initialized');
    initNavigation();
    initNewRoundModal();
    initCharts();
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
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // In a real app, you would collect form data and send to the server
        const formData = new FormData(form);
        const roundData = {};
        
        formData.forEach((value, key) => {
            roundData[key] = value;
        });
        
        console.log('New round data:', roundData);
        
        // For now, just simulate success and close the modal
        alert('Round saved successfully!');
        closeModal();
        form.reset();
        dateInput.value = today;
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
        // In a real app, this would update all the stats and charts based on the selected date range
    });
    
    // Handle notification bell clicks
    const notificationBell = document.querySelector('.notification-bell');
    notificationBell.addEventListener('click', function() {
        console.log('Notification bell clicked');
        // In a real app, this would open a notifications panel
    });
}

// API service (for demonstration, not actually used yet)
const ApiService = {
    // Base URL for the backend API
    baseUrl: 'http://localhost:5000/api',
    
    // Get user profile
    async getUserProfile() {
        try {
            const response = await fetch(`${this.baseUrl}/user`);
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
            const response = await fetch(url);
            return await response.json();
        } catch (error) {
            console.error('Error fetching rounds:', error);
            return [];
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
                body: JSON.stringify(roundData)
            });
            return await response.json();
        } catch (error) {
            console.error('Error saving round:', error);
            return null;
        }
    },
    
    // Get statistics for a user
    async getStats(timeframe = 'all') {
        try {
            const response = await fetch(`${this.baseUrl}/stats?timeframe=${timeframe}`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching stats:', error);
            return null;
        }
    }
};