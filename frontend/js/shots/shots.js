/**
 * Shots Module - Handles the Range Shots functionality
 */
import ApiService from '../api/api.js';
import * as UI from '../ui/ui.js';

// Store the current session and shot data
let currentSessionId = null;
let currentShots = [];
let userClubs = [];

/**
 * Initialize the Shots view
 */
export function initShotsView() {
  // Set up tab navigation
  const tabButtons = document.querySelectorAll('.shots-tab-btn');
  const tabContents = document.querySelectorAll('.shots-tab-content');
  
  tabButtons.forEach(button => {
    button.addEventListener('click', () => {
      const tabName = button.dataset.tab;
      
      // Update active tab button
      tabButtons.forEach(btn => btn.classList.remove('active'));
      button.classList.add('active');
      
      // Update active tab content
      tabContents.forEach(content => {
        if (content.id === `${tabName}-tab`) {
          content.classList.add('active');
        } else {
          content.classList.remove('active');
        }
      });
      
      // Load data for the selected tab
      if (tabName === 'range-view') {
        loadRangeSessions();
      } else if (tabName === 'benchmarks') {
        loadClubBenchmarks();
      } else if (tabName === 'trends') {
        loadTrendData();
      }
    });
  });
  
  // Set up "New Session" button
  const newSessionBtn = document.getElementById('new-range-session-btn');
  if (newSessionBtn) {
    newSessionBtn.addEventListener('click', showNewSessionModal);
  }
  
  // Set up "Add Shot" and "Add First Shot" buttons
  const addShotBtn = document.getElementById('add-shot-btn');
  const addFirstShotBtn = document.getElementById('add-first-shot-btn');
  
  if (addShotBtn) {
    addShotBtn.addEventListener('click', () => showAddShotModal());
  }
  
  if (addFirstShotBtn) {
    addFirstShotBtn.addEventListener('click', () => showAddShotModal());
  }
  
  // Set up "Import Shots" button
  const importShotsBtn = document.getElementById('import-shots-btn');
  if (importShotsBtn) {
    importShotsBtn.addEventListener('click', showImportShotsModal);
  }
  
  // Set up "Add Club" button
  const addClubCard = document.querySelector('.club-card.add-club');
  if (addClubCard) {
    addClubCard.addEventListener('click', showAddClubModal);
  }
  
  // Initialize filter controls
  initFilters();
  
  // Initialize range session form
  initRangeSessionForm();
  
  // Initialize add shot form
  initAddShotForm();
  
  // Initialize add club form
  initAddClubForm();
  
  // Initialize import options
  initImportOptions();
  
  // Fetch clubs for shot form
  loadUserClubs();
}

/**
 * Initialize filter UI and event handlers
 */
function initFilters() {
  // Look for the filter controls element
  const filterControls = document.querySelector('.filter-controls');
  if (!filterControls) return;
  
  // Create filter UI
  const filterPanel = document.createElement('div');
  filterPanel.className = 'advanced-filters';
  filterPanel.innerHTML = `
    <button id="show-filters-btn" class="btn-secondary small">
      <i class="fas fa-filter"></i> Advanced Filters
    </button>
    
    <div id="filters-panel" class="filters-panel" style="display: none;">
      <div class="filters-header">
        <h3>Filter Shots</h3>
        <button id="close-filters-btn" class="btn-icon">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <div class="filter-group">
        <h4>Date Range</h4>
        <div class="filter-row">
          <div class="filter-field">
            <label for="filter-date-from">From</label>
            <input type="date" id="filter-date-from" class="filter-input">
          </div>
          <div class="filter-field">
            <label for="filter-date-to">To</label>
            <input type="date" id="filter-date-to" class="filter-input">
          </div>
        </div>
      </div>
      
      <div class="filter-group">
        <h4>Distance (Carry)</h4>
        <div class="filter-row">
          <div class="filter-field">
            <label for="filter-min-distance">Min (yards)</label>
            <input type="number" id="filter-min-distance" class="filter-input" min="0" max="400">
          </div>
          <div class="filter-field">
            <label for="filter-max-distance">Max (yards)</label>
            <input type="number" id="filter-max-distance" class="filter-input" min="0" max="400">
          </div>
        </div>
      </div>
      
      <div class="filter-group">
        <h4>Club Type</h4>
        <select id="filter-club" class="filter-select">
          <option value="all">All Clubs</option>
          <!-- Clubs will be loaded dynamically -->
        </select>
      </div>
      
      <div class="filter-group">
        <h4>Lie Type</h4>
        <select id="filter-lie-type" class="filter-select">
          <option value="all">All Lies</option>
          <option value="tee">Tee</option>
          <option value="fairway">Fairway</option>
          <option value="rough">Rough</option>
          <option value="sand">Sand/Bunker</option>
          <option value="green">Green</option>
        </select>
      </div>
      
      <div class="filter-group">
        <h4>Shot Type</h4>
        <select id="filter-shot-type" class="filter-select">
          <option value="all">All Types</option>
          <option value="range">Range</option>
          <option value="sim">Simulator</option>
          <option value="course">On Course</option>
        </select>
      </div>
      
      <div class="filter-actions">
        <button id="apply-filters-btn" class="btn-primary">Apply Filters</button>
        <button id="reset-filters-btn" class="btn-secondary">Reset</button>
      </div>
    </div>
    
    <div id="filter-stats" class="filter-stats"></div>
  `;
  
  // Add the filter panel to the filter controls
  filterControls.appendChild(filterPanel);
  
  // Set up event handlers
  const showFiltersBtn = document.getElementById('show-filters-btn');
  const closeFiltersBtn = document.getElementById('close-filters-btn');
  const filtersPanel = document.getElementById('filters-panel');
  const applyFiltersBtn = document.getElementById('apply-filters-btn');
  const resetFiltersBtn = document.getElementById('reset-filters-btn');
  
  // Show/hide filters panel
  showFiltersBtn.addEventListener('click', () => {
    filtersPanel.style.display = 'block';
  });
  
  closeFiltersBtn.addEventListener('click', () => {
    filtersPanel.style.display = 'none';
  });
  
  // Apply filters
  applyFiltersBtn.addEventListener('click', () => {
    if (currentShots.length > 0) {
      renderShotsTable(currentShots);
    }
    filtersPanel.style.display = 'none';
  });
  
  // Reset filters
  resetFiltersBtn.addEventListener('click', () => {
    // Reset date inputs
    const dateFrom = document.getElementById('filter-date-from');
    const dateTo = document.getElementById('filter-date-to');
    
    if (dateFrom) dateFrom.value = '';
    if (dateTo) dateTo.value = '';
    
    // Reset distance inputs
    const minDistance = document.getElementById('filter-min-distance');
    const maxDistance = document.getElementById('filter-max-distance');
    
    if (minDistance) minDistance.value = '';
    if (maxDistance) maxDistance.value = '';
    
    // Reset selects
    const selects = ['filter-club', 'filter-lie-type', 'filter-shot-type'];
    selects.forEach(id => {
      const select = document.getElementById(id);
      if (select) select.value = 'all';
    });
    
    // Re-render with reset filters
    if (currentShots.length > 0) {
      renderShotsTable(currentShots);
    }
  });
  
  // Set up club filter dropdown once clubs are loaded
  document.addEventListener('clubsLoaded', () => {
    populateClubFilter();
  });
}

/**
 * Load range sessions for the current user
 */
export async function loadRangeSessions() {
  const sessionsList = document.querySelector('.range-sessions-list');
  
  if (!sessionsList) return;
  
  // Show loading indicator
  sessionsList.innerHTML = `
    <div class="loading-indicator">
      <div class="loading-spinner small"></div>
      <span>Loading sessions...</span>
    </div>
  `;
  
  try {
    // Fetch sessions from API
    const response = await ApiService.getRangeSessions();
    
    if (response && response.sessions && response.sessions.length > 0) {
      // Render sessions list
      renderSessionsList(response.sessions);
    } else {
      // Show empty state
      sessionsList.innerHTML = `
        <div class="empty-state">
          <i class="fas fa-calendar-alt fa-2x"></i>
          <h3>No Range Sessions</h3>
          <p>Record your first range session to start tracking your shots.</p>
          <button id="create-first-session-btn" class="btn-primary">
            <i class="fas fa-plus"></i> Create First Session
          </button>
        </div>
      `;
      
      // Add event listener to "Create First Session" button
      const createFirstSessionBtn = document.getElementById('create-first-session-btn');
      if (createFirstSessionBtn) {
        createFirstSessionBtn.addEventListener('click', showNewSessionModal);
      }
    }
  } catch (error) {
    console.error('Error loading range sessions:', error);
    
    // Show error message
    sessionsList.innerHTML = `
      <div class="error-message">
        <i class="fas fa-exclamation-circle"></i>
        <p>Failed to load range sessions. Please try again.</p>
      </div>
    `;
  }
}

/**
 * Render the list of range sessions
 * @param {Array} sessions - List of range sessions
 */
function renderSessionsList(sessions) {
  const sessionsList = document.querySelector('.range-sessions-list');
  
  if (!sessionsList) return;
  
  // Sort sessions by date (newest first)
  sessions.sort((a, b) => new Date(b.date) - new Date(a.date));
  
  // Clear loading indicator
  sessionsList.innerHTML = '';
  
  // Create session items
  sessions.forEach(session => {
    const sessionDate = new Date(session.date);
    const formattedDate = sessionDate.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
    
    const sessionItem = document.createElement('div');
    sessionItem.className = 'session-item';
    sessionItem.dataset.sessionId = session.id;
    
    sessionItem.innerHTML = `
      <div class="session-date">${formattedDate}</div>
      <div class="session-location">${session.location}</div>
      <div class="session-actions">
        <button class="btn-icon view-session-btn" title="View Session">
          <i class="fas fa-eye"></i>
        </button>
        <button class="btn-icon delete-session-btn" title="Delete Session">
          <i class="fas fa-trash-alt"></i>
        </button>
      </div>
    `;
    
    // Add click event to view session
    sessionItem.addEventListener('click', (e) => {
      // Don't trigger if clicking on delete button
      if (!e.target.closest('.delete-session-btn')) {
        loadSessionShots(session.id);
      }
    });
    
    // Add click event to delete button
    const deleteBtn = sessionItem.querySelector('.delete-session-btn');
    if (deleteBtn) {
      deleteBtn.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent session click event
        confirmDeleteSession(session.id, formattedDate);
      });
    }
    
    sessionsList.appendChild(sessionItem);
  });
}

/**
 * Load shots for a specific range session
 * @param {number} sessionId - Range session ID
 */
async function loadSessionShots(sessionId) {
  // Set current session ID
  currentSessionId = sessionId;
  
  // Update UI to show we're loading a session
  document.getElementById('session-title').textContent = 'Loading session...';
  document.getElementById('session-details').style.display = 'none';
  
  // Clear shots table
  const shotsTable = document.getElementById('shots-table');
  if (shotsTable) {
    shotsTable.querySelector('tbody').innerHTML = `
      <tr class="loading-row">
        <td colspan="11">
          <div class="loading-indicator">
            <div class="loading-spinner small"></div>
            <span>Loading shots data...</span>
          </div>
        </td>
      </tr>
    `;
  }
  
  // Hide empty state if visible
  const emptyState = document.querySelector('.shots-empty-state');
  if (emptyState) {
    emptyState.style.display = 'none';
  }
  
  try {
    // Fetch session and shots from API
    const response = await ApiService.getRangeSession(sessionId);
    
    if (response && response.session) {
      // Update session details
      updateSessionDetails(response.session);
      
      // Check if there are shots
      if (response.shots && response.shots.length > 0) {
        // Store current shots
        currentShots = response.shots;
        
        // Render shots table
        renderShotsTable(response.shots);
      } else {
        // Show empty state for shots
        showEmptyShotsState();
      }
    } else {
      // Session not found
      document.getElementById('session-title').textContent = 'Session not found';
      document.getElementById('session-details').style.display = 'none';
      
      // Show error in shots table
      shotsTable.querySelector('tbody').innerHTML = `
        <tr class="error-row">
          <td colspan="11">
            <div class="error-message">
              <i class="fas fa-exclamation-circle"></i>
              <p>Session not found or access denied.</p>
            </div>
          </td>
        </tr>
      `;
    }
  } catch (error) {
    console.error('Error loading session shots:', error);
    
    // Show error in session title
    document.getElementById('session-title').textContent = 'Error loading session';
    
    // Show error in shots table
    shotsTable.querySelector('tbody').innerHTML = `
      <tr class="error-row">
        <td colspan="11">
          <div class="error-message">
            <i class="fas fa-exclamation-circle"></i>
            <p>Failed to load session data. Please try again.</p>
          </div>
        </td>
      </tr>
    `;
  }
}

/**
 * Update session details in the UI
 * @param {Object} session - Range session data
 */
function updateSessionDetails(session) {
  // Format session date
  const sessionDate = new Date(session.date);
  const formattedDate = sessionDate.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
  
  // Set session title
  document.getElementById('session-title').textContent = `Range Session: ${session.location}`;
  
  // Update session details
  document.getElementById('session-date').textContent = formattedDate;
  document.getElementById('session-location').textContent = session.location;
  
  // Set duration (if available)
  const durationElement = document.getElementById('session-duration');
  if (session.duration_minutes) {
    durationElement.textContent = `${session.duration_minutes} minutes`;
  } else {
    durationElement.textContent = 'N/A';
  }
  
  // Show session details
  document.getElementById('session-details').style.display = 'flex';
}

/**
 * Apply filters to shots
 * @param {Array} shots - List of shots
 * @param {Object} filters - Filter criteria
 * @returns {Array} - Filtered shots
 */
function applyFilters(shots, filters) {
  if (!filters || Object.keys(filters).length === 0) {
    return shots;
  }
  
  return shots.filter(shot => {
    // Date range filter
    if (filters.dateFrom && filters.dateTo) {
      const shotDate = new Date(shot.created_at || shot.shot_date);
      const fromDate = new Date(filters.dateFrom);
      const toDate = new Date(filters.dateTo);
      toDate.setHours(23, 59, 59, 999); // End of the selected day
      
      if (shotDate < fromDate || shotDate > toDate) {
        return false;
      }
    }
    
    // Distance threshold filter
    if (filters.minDistance && shot.carry_distance_yards < filters.minDistance) {
      return false;
    }
    
    if (filters.maxDistance && shot.carry_distance_yards > filters.maxDistance) {
      return false;
    }
    
    // Club filter
    if (filters.club && filters.club !== 'all' && shot.club !== filters.club) {
      return false;
    }
    
    // Lie type filter
    if (filters.lieType && filters.lieType !== 'all' && 
       (shot.from_location !== filters.lieType)) {
      return false;
    }
    
    // Shot type filter (range, sim, course)
    if (filters.shotType && filters.shotType !== 'all' && 
       (shot.shot_type !== filters.shotType)) {
      return false;
    }
    
    return true;
  });
}

/**
 * Render the shots table
 * @param {Array} shots - List of shots
 */
function renderShotsTable(shots) {
  const tbody = document.getElementById('shots-table').querySelector('tbody');
  
  // Get current filters
  const filters = getCurrentFilters();
  
  // Apply filters
  const filteredShots = applyFilters(shots, filters);
  
  // Sort shots by shot number
  filteredShots.sort((a, b) => a.shot_number - b.shot_number);
  
  // Clear table body
  tbody.innerHTML = '';
  
  // If no shots after filtering, show message
  if (filteredShots.length === 0) {
    tbody.innerHTML = `
      <tr class="no-data-row">
        <td colspan="12">No shots match the current filters</td>
      </tr>
    `;
    return;
  }
  
  // Add rows for each shot
  filteredShots.forEach(shot => {
    const row = document.createElement('tr');
    
    // Format values and handle nulls
    const formatValue = (value, unit = '', decimals = 1) => {
      if (value === null || value === undefined) return '--';
      return `${parseFloat(value).toFixed(decimals)}${unit}`;
    };
    
    // Format shot type for display
    const formatShotType = (type) => {
      if (!type) return '--';
      return type.charAt(0).toUpperCase() + type.slice(1);
    };
    
    row.innerHTML = `
      <td>${shot.shot_number}</td>
      <td>${shot.club || '--'}</td>
      <td>${formatShotType(shot.shot_type)}</td>
      <td>${formatValue(shot.carry_distance_yards)}</td>
      <td>${formatValue(shot.total_distance_yards)}</td>
      <td>${formatValue(shot.ball_speed_mph)}</td>
      <td>${formatValue(shot.height_feet)}</td>
      <td>${formatValue(shot.launch_angle_degrees, '°')}</td>
      <td>${formatValue(shot.launch_direction_degrees, '°')}</td>
      <td>${formatValue(shot.carry_side_feet)}</td>
      <td>${formatValue(shot.from_pin_yards)}</td>
      <td>
        <button class="btn-icon edit-shot-btn" title="Edit Shot" data-shot-id="${shot.id}">
          <i class="fas fa-edit"></i>
        </button>
        <button class="btn-icon delete-shot-btn" title="Delete Shot" data-shot-id="${shot.id}">
          <i class="fas fa-trash-alt"></i>
        </button>
      </td>
    `;
    
    // Add event listeners to edit and delete buttons
    const editBtn = row.querySelector('.edit-shot-btn');
    const deleteBtn = row.querySelector('.delete-shot-btn');
    
    if (editBtn) {
      editBtn.addEventListener('click', () => {
        showAddShotModal(shot);
      });
    }
    
    if (deleteBtn) {
      deleteBtn.addEventListener('click', () => {
        confirmDeleteShot(shot.id, shot.shot_number);
      });
    }
    
    tbody.appendChild(row);
  });
  
  // Update filter stats
  updateFilterStats(filteredShots, shots.length);
  
  // Hide empty state
  const emptyState = document.querySelector('.shots-empty-state');
  if (emptyState) {
    emptyState.style.display = 'none';
  }
}

/**
 * Get current filter values from the filter UI
 * @returns {Object} - Filter values
 */
function getCurrentFilters() {
  const filters = {};
  
  // Date range filter
  const dateFrom = document.getElementById('filter-date-from');
  const dateTo = document.getElementById('filter-date-to');
  
  if (dateFrom && dateFrom.value) {
    filters.dateFrom = dateFrom.value;
  }
  
  if (dateTo && dateTo.value) {
    filters.dateTo = dateTo.value;
  }
  
  // Distance threshold filter
  const minDistance = document.getElementById('filter-min-distance');
  const maxDistance = document.getElementById('filter-max-distance');
  
  if (minDistance && minDistance.value) {
    filters.minDistance = parseFloat(minDistance.value);
  }
  
  if (maxDistance && maxDistance.value) {
    filters.maxDistance = parseFloat(maxDistance.value);
  }
  
  // Club filter
  const clubSelect = document.getElementById('filter-club');
  if (clubSelect && clubSelect.value !== 'all') {
    filters.club = clubSelect.value;
  }
  
  // Lie type filter
  const lieTypeSelect = document.getElementById('filter-lie-type');
  if (lieTypeSelect && lieTypeSelect.value !== 'all') {
    filters.lieType = lieTypeSelect.value;
  }
  
  // Shot type filter
  const shotTypeSelect = document.getElementById('filter-shot-type');
  if (shotTypeSelect && shotTypeSelect.value !== 'all') {
    filters.shotType = shotTypeSelect.value;
  }
  
  return filters;
}

/**
 * Update filter stats UI
 * @param {Array} filteredShots - Shots after filtering
 * @param {number} totalShots - Total shots before filtering
 */
function updateFilterStats(filteredShots, totalShots) {
  const filterStats = document.getElementById('filter-stats');
  if (filterStats) {
    filterStats.textContent = `Showing ${filteredShots.length} of ${totalShots} shots`;
  }
}

/**
 * Show empty state for shots
 */
function showEmptyShotsState() {
  // Hide loading indicator in shots table
  const shotsTable = document.getElementById('shots-table');
  if (shotsTable) {
    shotsTable.querySelector('tbody').innerHTML = `
      <tr class="no-data-row">
        <td colspan="11">No shots recorded for this session</td>
      </tr>
    `;
  }
  
  // Show empty state
  const emptyState = document.querySelector('.shots-empty-state');
  if (emptyState) {
    emptyState.style.display = 'flex';
  }
}

/**
 * Initialize the range session form
 */
function initRangeSessionForm() {
  const form = document.getElementById('range-session-form');
  
  if (!form) return;
  
  // Set default date to today
  const today = new Date().toISOString().split('T')[0];
  document.getElementById('session-date-input').value = today;
  
  // Form submission handler
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Disable submit button and show loading
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...';
    
    try {
      // Get form data
      const formData = new FormData(form);
      const sessionData = {};
      
      // Convert form data to session data object
      formData.forEach((value, key) => {
        // Parse numeric values
        if (key === 'duration_minutes' && value) {
          sessionData[key] = parseInt(value);
        } else if (value) {
          sessionData[key] = value;
        }
      });
      
      // Create range session
      const response = await ApiService.createRangeSession(sessionData);
      
      if (response && response.session) {
        // Close modal
        UI.closeModal('range-session-modal');
        
        // Show success message
        UI.showToast('Range session created successfully!', 'success');
        
        // Reset form
        form.reset();
        document.getElementById('session-date-input').value = today;
        
        // Reload sessions
        loadRangeSessions();
        
        // Load the new session shots
        loadSessionShots(response.session.id);
      } else {
        throw new Error('Failed to create range session');
      }
    } catch (error) {
      console.error('Error creating range session:', error);
      UI.showToast(`Error: ${error.message || 'Failed to create range session'}`, 'error');
    } finally {
      // Re-enable submit button
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
    }
  });
  
  // Cancel button handler
  const cancelBtn = form.querySelector('.cancel-btn');
  if (cancelBtn) {
    cancelBtn.addEventListener('click', () => {
      UI.closeModal('range-session-modal');
      form.reset();
      document.getElementById('session-date-input').value = today;
    });
  }
}

/**
 * Show the new range session modal
 */
function showNewSessionModal() {
  UI.openModal('range-session-modal');
}

/**
 * Load user clubs for the shot form
 */
async function loadUserClubs() {
  try {
    const response = await ApiService.getClubs();
    
    if (response && response.clubs) {
      userClubs = response.clubs;
      
      // Populate club select in shot form
      const clubSelect = document.getElementById('shot-club');
      if (clubSelect) {
        // Clear current options (except the default)
        while (clubSelect.options.length > 1) {
          clubSelect.remove(1);
        }
        
        // Add "No Club / Unknown" option
        const unknownOption = document.createElement('option');
        unknownOption.value = "unknown";
        unknownOption.textContent = "No Club / Unknown";
        clubSelect.appendChild(unknownOption);
        
        // Add standard club options if user has no clubs
        if (!userClubs || userClubs.length === 0) {
          addStandardClubOptions(clubSelect);
        }
        
        // Add user's custom clubs
        userClubs.forEach(club => {
          const option = document.createElement('option');
          option.value = club.name;
          option.textContent = club.name;
          clubSelect.appendChild(option);
        });
      }
      
      // Dispatch event to notify clubs have been loaded
      document.dispatchEvent(new CustomEvent('clubsLoaded'));
    }
  } catch (error) {
    console.error('Error loading user clubs:', error);
  }
}

/**
 * Populate club filter dropdown with user clubs
 */
function populateClubFilter() {
  const clubFilter = document.getElementById('filter-club');
  if (!clubFilter) return;
  
  // Clear current options (except "All Clubs")
  while (clubFilter.options.length > 1) {
    clubFilter.remove(1);
  }
  
  // Standard club types for grouping
  const clubTypes = {
    'driver': 'Drivers',
    'wood': 'Woods',
    'hybrid': 'Hybrids',
    'iron': 'Irons',
    'wedge': 'Wedges',
    'putter': 'Putters',
    'other': 'Other'
  };
  
  // Create club type optgroups
  const optgroups = {};
  Object.keys(clubTypes).forEach(type => {
    const optgroup = document.createElement('optgroup');
    optgroup.label = clubTypes[type];
    optgroups[type] = optgroup;
    clubFilter.appendChild(optgroup);
  });
  
  // Helper function to determine club type
  const getClubType = (club) => {
    const clubName = club.name.toLowerCase();
    
    if (clubName.includes('driver')) return 'driver';
    if (clubName.includes('wood')) return 'wood';
    if (clubName.includes('hybrid')) return 'hybrid';
    if (clubName.includes('iron')) return 'iron';
    if (clubName.includes('wedge') || 
        clubName.includes('pw') || 
        clubName.includes('sw') || 
        clubName.includes('lw') || 
        clubName.includes('gw')) return 'wedge';
    if (clubName.includes('putter')) return 'putter';
    
    return 'other';
  };
  
  // Add user's custom clubs
  if (userClubs && userClubs.length > 0) {
    userClubs.forEach(club => {
      const option = document.createElement('option');
      option.value = club.name;
      option.textContent = club.name;
      
      const clubType = getClubType(club);
      optgroups[clubType].appendChild(option);
    });
  } else {
    // Add standard clubs if user has none
    const standardClubs = [
      { name: "Driver", type: 'driver' },
      { name: "3 Wood", type: 'wood' },
      { name: "5 Wood", type: 'wood' },
      { name: "2 Hybrid", type: 'hybrid' },
      { name: "3 Hybrid", type: 'hybrid' },
      { name: "4 Hybrid", type: 'hybrid' },
      { name: "3 Iron", type: 'iron' },
      { name: "4 Iron", type: 'iron' },
      { name: "5 Iron", type: 'iron' },
      { name: "6 Iron", type: 'iron' },
      { name: "7 Iron", type: 'iron' },
      { name: "8 Iron", type: 'iron' },
      { name: "9 Iron", type: 'iron' },
      { name: "PW", type: 'wedge' },
      { name: "GW", type: 'wedge' },
      { name: "SW", type: 'wedge' },
      { name: "LW", type: 'wedge' },
      { name: "Putter", type: 'putter' }
    ];
    
    standardClubs.forEach(club => {
      const option = document.createElement('option');
      option.value = club.name;
      option.textContent = club.name;
      optgroups[club.type].appendChild(option);
    });
  }
  
  // Remove empty optgroups
  Object.keys(optgroups).forEach(type => {
    if (optgroups[type].children.length === 0) {
      clubFilter.removeChild(optgroups[type]);
    }
  });
}

/**
 * Initialize the add shot form
 */
function initAddShotForm() {
  const form = document.getElementById('add-shot-form');
  
  if (!form) return;
  
  // Form submission handler
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Disable submit button and show loading
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
    
    try {
      // Get form data
      const formData = new FormData(form);
      const shotData = {};
      
      // Convert form data to shot data object
      formData.forEach((value, key) => {
        // Handle club field specially
        if (key === 'club') {
          if (value === 'unknown') {
            // Don't add club if "unknown" is selected
            // Backend will record it as null
          } else if (value) {
            shotData[key] = value;
          }
        }
        // Convert numeric values to numbers
        else if (key !== 'session_id' && value) {
          shotData[key] = parseFloat(value);
        } else if (value) {
          shotData[key] = value;
        }
      });
      
      // Check if we have a shot ID (editing existing shot)
      const shotId = form.dataset.shotId;
      
      if (shotId) {
        // Update existing shot - not implemented in the API yet
        UI.showToast('Shot editing is not supported yet', 'info');
      } else {
        // Add new shot
        const response = await ApiService.addRangeShot(currentSessionId, shotData);
        
        if (response && response.shot) {
          // Close modal
          UI.closeModal('add-shot-modal');
          
          // Show success message
          UI.showToast('Shot added successfully!', 'success');
          
          // Reset form
          form.reset();
          form.dataset.shotId = '';
          
          // Reload session shots
          loadSessionShots(currentSessionId);
        } else {
          throw new Error('Failed to add shot');
        }
      }
    } catch (error) {
      console.error('Error saving shot:', error);
      UI.showToast(`Error: ${error.message || 'Failed to save shot'}`, 'error');
    } finally {
      // Re-enable submit button
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
    }
  });
  
  // Cancel button handler
  const cancelBtn = form.querySelector('.cancel-btn');
  if (cancelBtn) {
    cancelBtn.addEventListener('click', () => {
      UI.closeModal('add-shot-modal');
      form.reset();
      form.dataset.shotId = '';
    });
  }
}

/**
 * Show the add shot modal
 * @param {Object} shot - Existing shot data (for editing)
 */
function showAddShotModal(shot = null) {
  const form = document.getElementById('add-shot-form');
  
  if (!form) return;
  
  // Reset form
  form.reset();
  
  // Set session ID
  document.getElementById('shot-session-id').value = currentSessionId;
  
  if (shot) {
    // Editing existing shot
    form.dataset.shotId = shot.id;
    document.querySelector('#add-shot-modal .modal-header h2').textContent = 'Edit Shot';
    
    // Set form values
    document.getElementById('shot-number').value = shot.shot_number;
    
    // Set club select
    const clubSelect = document.getElementById('shot-club');
    if (clubSelect) {
      for (let i = 0; i < clubSelect.options.length; i++) {
        if (clubSelect.options[i].value === shot.club) {
          clubSelect.selectedIndex = i;
          break;
        }
      }
    }
    
    // Set shot type
    const shotTypeSelect = document.getElementById('shot-type');
    if (shotTypeSelect && shot.shot_type) {
      for (let i = 0; i < shotTypeSelect.options.length; i++) {
        if (shotTypeSelect.options[i].value === shot.shot_type) {
          shotTypeSelect.selectedIndex = i;
          break;
        }
      }
    }
    
    // Set numeric values
    const numericFields = [
      'carry_distance_yards', 'total_distance_yards', 'ball_speed_mph',
      'height_feet', 'launch_angle_degrees', 'launch_direction_degrees',
      'carry_side_feet', 'from_pin_yards'
    ];
    
    numericFields.forEach(field => {
      const input = document.getElementById(`shot-${field.replace(/_/g, '-')}`);
      if (input && shot[field] !== null && shot[field] !== undefined) {
        input.value = shot[field];
      }
    });
    
    // Change submit button text
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
      submitBtn.textContent = 'Update Shot';
    }
  } else {
    // Adding new shot
    form.dataset.shotId = '';
    document.querySelector('#add-shot-modal .modal-header h2').textContent = 'Add Shot';
    
    // Set next shot number
    const nextShotNumber = currentShots.length > 0 ? Math.max(...currentShots.map(s => s.shot_number)) + 1 : 1;
    document.getElementById('shot-number').value = nextShotNumber;
    
    // Change submit button text
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
      submitBtn.textContent = 'Add Shot';
    }
  }
  
  UI.openModal('add-shot-modal');
}

/**
 * Initialize import options
 */
function initImportOptions() {
  const importSourceRadios = document.querySelectorAll('input[name="import-source"]');
  const csvUploadDiv = document.querySelector('.csv-upload');
  const startImportBtn = document.getElementById('start-import-btn');
  
  if (!importSourceRadios || !csvUploadDiv || !startImportBtn) return;
  
  // Toggle CSV upload div based on selected import source
  importSourceRadios.forEach(radio => {
    radio.addEventListener('change', () => {
      if (radio.value === 'csv') {
        csvUploadDiv.style.display = 'block';
      } else {
        csvUploadDiv.style.display = 'none';
      }
    });
  });
  
  // File input change handler
  const fileInput = document.getElementById('csv-file-input');
  const fileNameSpan = document.querySelector('.selected-file-name');
  
  if (fileInput && fileNameSpan) {
    fileInput.addEventListener('change', () => {
      if (fileInput.files.length > 0) {
        fileNameSpan.textContent = fileInput.files[0].name;
      } else {
        fileNameSpan.textContent = 'No file selected';
      }
    });
  }
  
  // Start import button handler
  if (startImportBtn) {
    startImportBtn.addEventListener('click', () => {
      const selectedSource = document.querySelector('input[name="import-source"]:checked').value;
      
      if (selectedSource === 'csv') {
        if (fileInput && fileInput.files.length > 0) {
          importFromCsv(fileInput.files[0]);
        } else {
          UI.showToast('Please select a CSV file to import', 'error');
        }
      } else if (selectedSource === 'trackman') {
        UI.showToast('TrackMan import will be available soon', 'info');
        UI.closeModal('import-shots-modal');
      } else if (selectedSource === 'skytrak') {
        UI.showToast('SkyTrak import will be available soon', 'info');
        UI.closeModal('import-shots-modal');
      }
    });
  }
}

/**
 * Show the import shots modal
 */
function showImportShotsModal() {
  // Check if we have a current session
  if (!currentSessionId) {
    UI.showToast('Please select a session first', 'error');
    return;
  }
  
  UI.openModal('import-shots-modal');
}

/**
 * Import shots from a CSV file
 * @param {File} file - CSV file
 */
async function importFromCsv(file) {
  // Basic CSV parsing (would need more robust implementation for production)
  const reader = new FileReader();
  
  reader.onload = async (e) => {
    try {
      const contents = e.target.result;
      const lines = contents.split('\n');
      
      // Assume first line is header
      const header = lines[0].split(',');
      
      // Map column indices
      const columnMap = {};
      header.forEach((column, index) => {
        columnMap[column.trim().toLowerCase()] = index;
      });
      
      // Required fields
      const requiredFields = ['club', 'carry_distance_yards'];
      const missingFields = requiredFields.filter(field => 
        !Object.keys(columnMap).some(col => col === field)
      );
      
      if (missingFields.length > 0) {
        UI.showToast(`Missing required fields: ${missingFields.join(', ')}`, 'error');
        return;
      }
      
      // Parse data rows
      const shots = [];
      for (let i = 1; i < lines.length; i++) {
        // Skip empty lines
        if (!lines[i].trim()) continue;
        
        const columns = lines[i].split(',');
        
        // Create shot object
        const shot = {
          session_id: currentSessionId,
          shot_number: currentShots.length + i,
        };
        
        // Map CSV columns to shot fields
        Object.keys(columnMap).forEach(column => {
          const value = columns[columnMap[column]].trim();
          
          // Skip empty values
          if (!value) return;
          
          // Map to shot fields (adjust field names if needed)
          let fieldName = column.replace(/\s+/g, '_').toLowerCase();
          
          // Handle special cases
          if (fieldName === 'carry' || fieldName === 'carry_yards') {
            fieldName = 'carry_distance_yards';
          } else if (fieldName === 'total' || fieldName === 'total_yards') {
            fieldName = 'total_distance_yards';
          }
          
          // Convert numeric values
          if (fieldName !== 'club') {
            shot[fieldName] = parseFloat(value);
          } else {
            shot[fieldName] = value;
          }
        });
        
        shots.push(shot);
      }
      
      // Check if we have any shots
      if (shots.length === 0) {
        UI.showToast('No valid shots found in CSV', 'error');
        return;
      }
      
      // Import shots in batches
      UI.closeModal('import-shots-modal');
      UI.showToast(`Importing ${shots.length} shots...`, 'info');
      
      const response = await ApiService.addRangeShots(currentSessionId, shots);
      
      if (response && response.shots) {
        UI.showToast(`Successfully imported ${response.shots.length} shots`, 'success');
        
        // Reload session shots
        loadSessionShots(currentSessionId);
      } else {
        throw new Error('Failed to import shots');
      }
    } catch (error) {
      console.error('Error importing shots:', error);
      UI.showToast(`Error: ${error.message || 'Failed to import shots'}`, 'error');
    }
  };
  
  reader.onerror = () => {
    UI.showToast('Error reading CSV file', 'error');
  };
  
  reader.readAsText(file);
}

/**
 * Confirm deletion of a range session
 * @param {number} sessionId - Range session ID
 * @param {string} sessionDate - Formatted session date for display
 */
function confirmDeleteSession(sessionId, sessionDate) {
  if (confirm(`Are you sure you want to delete the range session from ${sessionDate}? This will delete all associated shots and cannot be undone.`)) {
    deleteRangeSession(sessionId);
  }
}

/**
 * Delete a range session
 * @param {number} sessionId - Range session ID
 */
async function deleteRangeSession(sessionId) {
  try {
    const response = await ApiService.deleteRangeSession(sessionId);
    
    if (response && response.success) {
      // Show success message
      UI.showToast('Range session deleted successfully', 'success');
      
      // Reload sessions
      loadRangeSessions();
      
      // Clear current session if it's the one we deleted
      if (currentSessionId === sessionId) {
        currentSessionId = null;
        currentShots = [];
        
        // Update UI
        document.getElementById('session-title').textContent = 'Select a Session';
        document.getElementById('session-details').style.display = 'none';
        
        // Update shots table
        const shotsTable = document.getElementById('shots-table');
        if (shotsTable) {
          shotsTable.querySelector('tbody').innerHTML = `
            <tr class="no-data-row">
              <td colspan="11">Select a session to view shots data</td>
            </tr>
          `;
        }
        
        // Hide empty state
        const emptyState = document.querySelector('.shots-empty-state');
        if (emptyState) {
          emptyState.style.display = 'none';
        }
      }
    } else {
      throw new Error('Failed to delete range session');
    }
  } catch (error) {
    console.error('Error deleting range session:', error);
    UI.showToast(`Error: ${error.message || 'Failed to delete range session'}`, 'error');
  }
}

/**
 * Confirm deletion of a shot
 * @param {number} shotId - Shot ID
 * @param {number} shotNumber - Shot number for display
 */
function confirmDeleteShot(shotId, shotNumber) {
  if (confirm(`Are you sure you want to delete shot #${shotNumber}? This cannot be undone.`)) {
    UI.showToast('Shot deletion will be available soon', 'info');
    // deleteShot(shotId); - Not implemented in the API yet
  }
}

/**
 * Load club benchmarks
 * @param {string} shotType - Optional shot type to filter by
 */
async function loadClubBenchmarks(shotType = null) {
  const benchmarksTable = document.getElementById('benchmarks-table');
  
  if (!benchmarksTable) return;
  
  // Get table body
  const tbody = benchmarksTable.querySelector('tbody');
  
  // Show loading state
  tbody.innerHTML = `
    <tr class="loading-row">
      <td colspan="12">
        <div class="loading-indicator">
          <div class="loading-spinner small"></div>
          <span>Loading benchmarks...</span>
        </div>
      </td>
    </tr>
  `;
  
  // Add shot type filter UI if it doesn't exist
  if (!document.querySelector('.shot-type-filters')) {
    const benchmarksHeader = document.querySelector('.benchmarks-header');
    if (benchmarksHeader) {
      const filtersDiv = document.createElement('div');
      filtersDiv.className = 'shot-type-filters';
      filtersDiv.innerHTML = `
        <div class="filter-section">
          <label>Filter by shot type:</label>
          <div class="filter-buttons">
            <button class="shot-type-filter-btn active" data-shot-type="">All Shots</button>
            <button class="shot-type-filter-btn" data-shot-type="range">Range</button>
            <button class="shot-type-filter-btn" data-shot-type="sim">Simulator</button>
            <button class="shot-type-filter-btn" data-shot-type="course">On Course</button>
          </div>
        </div>
      `;
      
      // Insert filters after the header
      benchmarksHeader.after(filtersDiv);
      
      // Add event listeners to filter buttons
      const filterButtons = filtersDiv.querySelectorAll('.shot-type-filter-btn');
      filterButtons.forEach(button => {
        button.addEventListener('click', () => {
          // Update active state
          filterButtons.forEach(btn => btn.classList.remove('active'));
          button.classList.add('active');
          
          // Load benchmarks with selected filter
          loadClubBenchmarks(button.dataset.shotType || null);
        });
      });
    }
  } else if (shotType !== null) {
    // Update active filter button if already exists
    const filterButtons = document.querySelectorAll('.shot-type-filter-btn');
    filterButtons.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.shotType === shotType);
    });
  }
  
  try {
    // Fetch benchmarks with shot type filter
    const response = await ApiService.getClubBenchmarks(shotType);
    
    if (response && response.benchmarks && response.benchmarks.length > 0) {
      // Render benchmarks table
      renderBenchmarksTable(response.benchmarks);
    } else {
      // Show empty state
      showEmptyBenchmarksState();
    }
  } catch (error) {
    console.error('Error loading club benchmarks:', error);
    
    // Show error in table
    tbody.innerHTML = `
      <tr class="error-row">
        <td colspan="12">
          <div class="error-message">
            <i class="fas fa-exclamation-circle"></i>
            <p>Failed to load benchmarks. Please try again.</p>
          </div>
        </td>
      </tr>
    `;
  }
}

/**
 * Render the benchmarks table
 * @param {Array} benchmarks - List of club benchmarks
 */
function renderBenchmarksTable(benchmarks) {
  const tbody = document.getElementById('benchmarks-table').querySelector('tbody');
  
  // Sort benchmarks (driver first, then woods, then irons by number, then wedges)
  benchmarks.sort((a, b) => {
    // Helper to get club type and number
    const getClubInfo = (club) => {
      if (club.toLowerCase().includes('driver')) {
        return { type: 1, num: 0 };
      } else if (club.toLowerCase().includes('wood')) {
        const match = club.match(/(\d+)/);
        return { type: 2, num: match ? parseInt(match[1]) : 0 };
      } else if (club.toLowerCase().includes('iron')) {
        const match = club.match(/(\d+)/);
        return { type: 3, num: match ? parseInt(match[1]) : 0 };
      } else if (club.toLowerCase().includes('wedge') || 
                club.toLowerCase().includes('pw') || 
                club.toLowerCase().includes('sw') || 
                club.toLowerCase().includes('lw') || 
                club.toLowerCase().includes('gw')) {
        return { type: 4, num: 0 };
      } else {
        return { type: 5, num: 0 };
      }
    };
    
    const aInfo = getClubInfo(a.club);
    const bInfo = getClubInfo(b.club);
    
    if (aInfo.type !== bInfo.type) {
      return aInfo.type - bInfo.type;
    }
    
    if (aInfo.type === 2 || aInfo.type === 3) {
      // Sort woods and irons by number
      return aInfo.num - bInfo.num;
    }
    
    return a.club.localeCompare(b.club);
  });
  
  // Clear table body
  tbody.innerHTML = '';
  
  // Add rows for each benchmark
  benchmarks.forEach(benchmark => {
    const row = document.createElement('tr');
    
    // Format values and handle nulls
    const formatValue = (value, unit = '', decimals = 1) => {
      if (value === null || value === undefined) return '--';
      return `${parseFloat(value).toFixed(decimals)}${unit}`;
    };
    
    // Consistency score color class (red to green based on score)
    let consistencyClass = '';
    if (benchmark.consistency_score) {
      if (benchmark.consistency_score >= 90) {
        consistencyClass = 'high-consistency';
      } else if (benchmark.consistency_score >= 75) {
        consistencyClass = 'medium-consistency';
      } else {
        consistencyClass = 'low-consistency';
      }
    }
    
    row.innerHTML = `
      <td>${benchmark.club}</td>
      <td>${formatValue(benchmark.avg_carry_yards)}</td>
      <td>${formatValue(benchmark.avg_total_yards)}</td>
      <td>${formatValue(benchmark.consistency_yards)}</td>
      <td>${formatValue(benchmark.avg_ball_speed_mph)}</td>
      <td>${formatValue(benchmark.avg_height_feet)}</td>
      <td>${formatValue(benchmark.avg_launch_angle_degrees, '°')}</td>
      <td>${formatValue(benchmark.avg_launch_direction_degrees, '°')}</td>
      <td>${formatValue(benchmark.avg_carry_side_feet)}</td>
      <td>${formatValue(benchmark.avg_from_pin_yards)}</td>
      <td>${formatValue(benchmark.avg_carry_efficiency)}</td>
      <td class="${consistencyClass}">${formatValue(benchmark.consistency_score)}</td>
    `;
    
    tbody.appendChild(row);
  });
  
  // Hide empty state
  const emptyState = document.querySelector('.benchmarks-empty-state');
  if (emptyState) {
    emptyState.style.display = 'none';
  }
}

/**
 * Show empty state for benchmarks
 */
function showEmptyBenchmarksState() {
  // Hide loading indicator in benchmarks table
  const benchmarksTable = document.getElementById('benchmarks-table');
  if (benchmarksTable) {
    benchmarksTable.querySelector('tbody').innerHTML = `
      <tr class="no-data-row">
        <td colspan="12">No benchmark data available</td>
      </tr>
    `;
  }
  
  // Show empty state
  const emptyState = document.querySelector('.benchmarks-empty-state');
  if (emptyState) {
    emptyState.style.display = 'flex';
    
    // Add event listener to "Create Range Session" button
    const createSessionBtn = document.getElementById('create-session-btn');
    if (createSessionBtn) {
      createSessionBtn.addEventListener('click', showNewSessionModal);
    }
  }
}

/**
 * Add standard club options to the club select dropdown
 * @param {HTMLSelectElement} selectElement - The club select dropdown
 */
function addStandardClubOptions(selectElement) {
  const standardClubs = [
    "Driver",
    "3 Wood",
    "5 Wood",
    "2 Hybrid",
    "3 Hybrid",
    "4 Hybrid",
    "3 Iron",
    "4 Iron",
    "5 Iron",
    "6 Iron",
    "7 Iron",
    "8 Iron",
    "9 Iron",
    "PW",
    "GW",
    "SW",
    "LW",
    "Putter"
  ];
  
  standardClubs.forEach(club => {
    const option = document.createElement('option');
    option.value = club;
    option.textContent = club;
    selectElement.appendChild(option);
  });
}

/**
 * Load trend data for charts
 */
function loadTrendData() {
  // This is a placeholder - trends would require more data and time series analysis
  const trendChart = document.getElementById('trend-chart');
  const emptyState = document.querySelector('#trends-tab .trends-empty-state');
  
  if (trendChart && emptyState) {
    // For now, just show the empty state
    emptyState.style.display = 'flex';
    
    // In a real implementation, we would fetch time series data and render charts
    // using a library like Chart.js
  }
}

/**
 * Initialize the add club form
 */
function initAddClubForm() {
  const form = document.getElementById('add-club-form');
  
  if (!form) return;
  
  // Form submission handler
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Disable submit button and show loading
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
    
    try {
      // Get form data
      const formData = new FormData(form);
      const clubData = {};
      
      // Convert form data to club data object
      formData.forEach((value, key) => {
        if (key === 'loft' && value) {
          clubData[key] = parseFloat(value);
        } else if (value) {
          clubData[key] = value;
        }
      });
      
      // Create club
      const response = await ApiService.saveClub(clubData);
      
      if (response && response.club) {
        // Close modal
        UI.closeModal('add-club-modal');
        
        // Show success message
        UI.showToast('Club added successfully!', 'success');
        
        // Reset form
        form.reset();
        
        // Reload clubs
        loadUserClubs();
      } else {
        throw new Error('Failed to add club');
      }
    } catch (error) {
      console.error('Error adding club:', error);
      UI.showToast(`Error: ${error.message || 'Failed to add club'}`, 'error');
    } finally {
      // Re-enable submit button
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
    }
  });
  
  // Cancel button handler
  const cancelBtn = form.querySelector('.cancel-btn');
  if (cancelBtn) {
    cancelBtn.addEventListener('click', () => {
      UI.closeModal('add-club-modal');
      form.reset();
    });
  }
}

/**
 * Show the add club modal
 */
function showAddClubModal() {
  UI.openModal('add-club-modal');
}

// Export functions
export default {
  initShotsView,
  loadRangeSessions,
  loadClubBenchmarks
};