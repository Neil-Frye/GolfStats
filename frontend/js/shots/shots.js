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
  
  // Initialize range session form
  initRangeSessionForm();
  
  // Initialize add shot form
  initAddShotForm();
  
  // Initialize import options
  initImportOptions();
  
  // Fetch clubs for shot form
  loadUserClubs();
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
 * Render the shots table
 * @param {Array} shots - List of shots
 */
function renderShotsTable(shots) {
  const tbody = document.getElementById('shots-table').querySelector('tbody');
  
  // Sort shots by shot number
  shots.sort((a, b) => a.shot_number - b.shot_number);
  
  // Clear table body
  tbody.innerHTML = '';
  
  // Add rows for each shot
  shots.forEach(shot => {
    const row = document.createElement('tr');
    
    // Format values and handle nulls
    const formatValue = (value, unit = '', decimals = 1) => {
      if (value === null || value === undefined) return '--';
      return `${parseFloat(value).toFixed(decimals)}${unit}`;
    };
    
    row.innerHTML = `
      <td>${shot.shot_number}</td>
      <td>${shot.club || '--'}</td>
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
  
  // Hide empty state
  const emptyState = document.querySelector('.shots-empty-state');
  if (emptyState) {
    emptyState.style.display = 'none';
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
        
        // Add club options
        userClubs.forEach(club => {
          const option = document.createElement('option');
          option.value = club.name;
          option.textContent = club.name;
          clubSelect.appendChild(option);
        });
      }
    }
  } catch (error) {
    console.error('Error loading user clubs:', error);
  }
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
        // Convert numeric values to numbers
        if (key !== 'club' && key !== 'session_id' && value) {
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
 */
async function loadClubBenchmarks() {
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
  
  try {
    // Fetch benchmarks
    const response = await ApiService.getClubBenchmarks();
    
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

// Export functions
export default {
  initShotsView,
  loadRangeSessions,
  loadClubBenchmarks
};