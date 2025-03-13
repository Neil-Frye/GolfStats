import ApiService from '../api/api.js';
import { formatDate, showToast, openModal, closeModal, showLoadingState, hideLoadingState, showErrorState } from '../ui/ui.js';

// Function to load rounds data
function loadRoundsData(filter = 'all') {
    const tableBody = document.getElementById('rounds-table-body');
    const roundsContainer = document.querySelector('.rounds-list-container');
    if (!tableBody) return;
    
    // Show enhanced loading state - both in table and as section overlay
    if (roundsContainer) {
        showLoadingState('rounds-list-container', 'Loading your rounds...');
    }
    
    // Show loading state in table
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
            // Hide loading state if we used the enhanced loading
            if (roundsContainer) {
                hideLoadingState('rounds-list-container');
            }
            
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
            
            // Hide loading state if we used the enhanced loading
            if (roundsContainer) {
                hideLoadingState('rounds-list-container');
            }
            
            // Show more detailed error message
            const errorMessage = error.message || 'Failed to load rounds data';
            tableBody.innerHTML = `
                <tr>
                    <td colspan="9" class="error-message">
                        <i class="fas fa-exclamation-circle"></i>
                        ${errorMessage}
                        <button class="retry-btn" onclick="window.GolfStatsApp.rounds.loadRoundsData('${filter}')">
                            <i class="fas fa-sync-alt"></i> Try Again
                        </button>
                    </td>
                </tr>
            `;
            
            // Show toast notification with error
            showToast(`Error loading rounds: ${errorMessage}`, 'error');
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
    const emptyState = document.querySelector('.rounds-empty-state');
    if (emptyState) {
        emptyState.style.display = 'none';
    }
    
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
    const emptyState = document.querySelector('.rounds-empty-state');
    if (emptyState) {
        emptyState.style.display = 'flex';
    }
    
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
    const filter = document.getElementById('rounds-filter')?.value || 'all';
    const roundsContainer = document.querySelector('.rounds-list-container');
    
    // Show enhanced loading state with overlay
    if (roundsContainer) {
        showLoadingState('rounds-list-container', `Loading page ${page}...`);
    }
    
    // Show loading state in table
    const tableBody = document.getElementById('rounds-table-body');
    if (tableBody) {
        tableBody.innerHTML = `
            <tr class="loading-row">
                <td colspan="9">
                    <div class="loading-indicator">
                        <div class="loading-spinner small"></div>
                        <span>Loading page ${page}...</span>
                    </div>
                </td>
            </tr>
        `;
    }
    
    // Fetch data for the specified page
    ApiService.getRounds({ filter: filter, limit: 10, page: page })
        .then(data => {
            // Hide loading state if we used the enhanced loading
            if (roundsContainer) {
                hideLoadingState('rounds-list-container');
            }
            
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
            
            // Hide loading state if we used the enhanced loading
            if (roundsContainer) {
                hideLoadingState('rounds-list-container');
            }
            
            if (tableBody) {
                // Show more detailed error message with retry button
                const errorMessage = error.message || 'Failed to load rounds data';
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="9" class="error-message">
                            <i class="fas fa-exclamation-circle"></i>
                            ${errorMessage}
                            <button class="retry-btn" onclick="window.GolfStatsApp.rounds.navigateToPage(${page})">
                                <i class="fas fa-sync-alt"></i> Try Again
                            </button>
                        </td>
                    </tr>
                `;
                
                // Show toast notification with error
                showToast(`Error loading page ${page}: ${errorMessage}`, 'error');
            }
        });
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
        openModal('round-detail-modal');
        
        // Fetch round details from the API
        ApiService.getRound(roundId)
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
                
                // Show detailed error message
                const errorMessage = error.message || 'Unable to load round details';
                errorContainer.innerHTML = `
                    <div class="error-icon">
                        <i class="fas fa-exclamation-circle"></i>
                    </div>
                    <h3>Error Loading Round Details</h3>
                    <p>${errorMessage}</p>
                    <button class="retry-btn" data-round-id="${roundId}">
                        <i class="fas fa-sync-alt"></i> Try Again
                    </button>
                `;
                
                // Add event listener to the retry button
                const retryBtn = errorContainer.querySelector('.retry-btn');
                if (retryBtn) {
                    retryBtn.addEventListener('click', function() {
                        // Get the round ID from the button's data attribute
                        const roundId = this.getAttribute('data-round-id');
                        if (roundId) {
                            // Retry loading the round details
                            viewRoundDetails(roundId);
                        }
                    });
                }
                
                errorContainer.style.display = 'block';
                
                // Show a toast notification with the error
                UI.showToast(`Error: ${errorMessage}`, 'error');
            });
    }
}

// Populate round details in the modal
function populateRoundDetails(data) {
    // Set course and date information
    document.getElementById('detail-course-name').textContent = data.course || data.course_name || 'Unknown Course';
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
                closeModal('round-detail-modal');
            });
        }
        
        // Close when clicking outside the modal content
        modal.addEventListener('click', function(event) {
            if (event.target === modal) {
                closeModal('round-detail-modal');
            }
        });
    }
}

// Initialize new round modal
function initNewRoundModal() {
    const modal = document.getElementById('new-round-modal');
    
    if (!modal) return;
    
    // Set default date to today
    const dateInput = document.getElementById('round-date');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.value = today;
    }
    
    // Set up cancel button explicitly
    const cancelBtn = modal.querySelector('.cancel-btn');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', function() {
            closeModal('new-round-modal');
        });
    }
    
    // Close button (X in the corner)
    const closeBtn = modal.querySelector('.close-modal');
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            closeModal('new-round-modal');
        });
    }
    
    // Close when clicking outside the modal
    modal.addEventListener('click', function(event) {
        if (event.target === modal) {
            closeModal('new-round-modal');
        }
    });
    
    // Handle form submission
    const form = document.getElementById('new-round-form');
    if (form) {
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
                    showToast('Round saved successfully!', 'success');
                    
                    // Close modal and reset form
                    closeModal('new-round-modal');
                    form.reset();
                    
                    // Set date to today
                    if (dateInput) {
                        const today = new Date().toISOString().split('T')[0];
                        dateInput.value = today;
                    }
                    
                    // Trigger reload of dashboard data
                    document.dispatchEvent(new CustomEvent('roundSaved'));
                } else {
                    throw new Error('Failed to save round');
                }
            } catch (error) {
                console.error('Error saving round:', error);
                showToast(`Error: ${error.message || 'Failed to save round'}`, 'error');
            } finally {
                // Reset button state
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    }
}

// Initialize pagination handlers
function initPaginationHandlers() {
    const prevButton = document.querySelector('.pagination-prev');
    const nextButton = document.querySelector('.pagination-next');
    
    if (prevButton) {
        prevButton.addEventListener('click', function() {
            if (!this.hasAttribute('disabled')) {
                const currentPage = parseInt(document.querySelector('.current-page').textContent);
                navigateToPage(currentPage - 1);
            }
        });
    }
    
    if (nextButton) {
        nextButton.addEventListener('click', function() {
            if (!this.hasAttribute('disabled')) {
                const currentPage = parseInt(document.querySelector('.current-page').textContent);
                navigateToPage(currentPage + 1);
            }
        });
    }
}

// Initialize rounds filter
function initRoundsFilter() {
    const filterSelect = document.getElementById('rounds-filter');
    if (filterSelect) {
        filterSelect.addEventListener('change', function() {
            const filter = this.value;
            loadRoundsData(filter);
        });
    }
}

// Initialize rounds view
function initRoundsView() {
    // Initialize round detail modal
    initRoundDetailModal();
    
    // Initialize new round modal
    initNewRoundModal();
    
    // Initialize pagination
    initPaginationHandlers();
    
    // Initialize filter
    initRoundsFilter();
    
    // Load initial data
    loadRoundsData();
}

// Export the rounds module functions
export {
    initRoundsView,
    loadRoundsData,
    updateRoundsTable,
    navigateToPage,
    updateRecentRounds,
    viewRoundDetails,
    initRoundDetailModal,
    initNewRoundModal,
    attachRoundViewListeners,
    populateRoundDetails,
    populateScorecard,
    populateShotDetails,
    showRoundsEmptyState
};