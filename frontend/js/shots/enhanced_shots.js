/**
 * Enhanced Shots Module - Adds comprehensive shot data input
 */

// Enhanced shot form HTML with all database fields
export function getEnhancedShotFormHTML() {
    return `
        <form id="enhanced-shot-form">
            <!-- Basic Information -->
            <div class="form-section">
                <h4>Basic Information</h4>
                <div class="form-row">
                    <div class="form-group">
                        <label for="shot-club">Club <span class="required">*</span></label>
                        <select id="shot-club" name="club" required>
                            <option value="">Select Club</option>
                            <!-- Populated dynamically -->
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="shot-date">Date <span class="required">*</span></label>
                        <input type="datetime-local" id="shot-date" name="shot_date" required>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="shot-type">Shot Type</label>
                        <select id="shot-type" name="shot_type">
                            <option value="range">Range</option>
                            <option value="course">Course</option>
                            <option value="simulator">Simulator</option>
                            <option value="approach">Approach</option>
                            <option value="chip">Chip</option>
                            <option value="pitch">Pitch</option>
                            <option value="putt">Putt</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="lie-type">Lie Type</label>
                        <select id="lie-type" name="lie_type">
                            <option value="tee">Tee</option>
                            <option value="fairway">Fairway</option>
                            <option value="rough">Rough</option>
                            <option value="sand">Sand/Bunker</option>
                            <option value="green">Green</option>
                            <option value="fringe">Fringe</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                </div>
            </div>
            
            <!-- Distance Metrics -->
            <div class="form-section">
                <h4>Distance Metrics</h4>
                <div class="form-row">
                    <div class="form-group">
                        <label for="carry-distance">Carry Distance (yards)</label>
                        <input type="number" id="carry-distance" name="carry_distance_yards" 
                               step="0.1" min="0" max="500">
                    </div>
                    <div class="form-group">
                        <label for="total-distance">Total Distance (yards)</label>
                        <input type="number" id="total-distance" name="total_distance_yards" 
                               step="0.1" min="0" max="500">
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="offline-distance">Offline Distance (yards)</label>
                        <input type="number" id="offline-distance" name="offline_distance_yards" 
                               step="0.1" min="-100" max="100">
                        <small>Negative = left, Positive = right</small>
                    </div>
                    <div class="form-group">
                        <label for="from-pin">Distance from Pin (yards)</label>
                        <input type="number" id="from-pin" name="from_pin_yards" 
                               step="0.1" min="0" max="100">
                    </div>
                </div>
            </div>
            
            <!-- Ball Flight Data -->
            <div class="form-section collapsible">
                <h4 class="section-toggle">Ball Flight Data <i class="fas fa-chevron-down"></i></h4>
                <div class="collapsible-content">
                    <div class="form-row">
                        <div class="form-group">
                            <label for="ball-speed">Ball Speed (mph)</label>
                            <input type="number" id="ball-speed" name="ball_speed" 
                                   step="0.1" min="0" max="200">
                        </div>
                        <div class="form-group">
                            <label for="club-speed">Club Speed (mph)</label>
                            <input type="number" id="club-speed" name="club_speed" 
                                   step="0.1" min="0" max="150">
                        </div>
                        <div class="form-group">
                            <label for="smash-factor">Smash Factor</label>
                            <input type="number" id="smash-factor" name="smash_factor" 
                                   step="0.01" min="1.0" max="1.6">
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="launch-angle">Launch Angle (°)</label>
                            <input type="number" id="launch-angle" name="launch_angle_degrees" 
                                   step="0.1" min="-10" max="60">
                        </div>
                        <div class="form-group">
                            <label for="launch-direction">Launch Direction (°)</label>
                            <input type="number" id="launch-direction" name="launch_direction_degrees" 
                                   step="0.1" min="-45" max="45">
                            <small>Negative = left, Positive = right</small>
                        </div>
                        <div class="form-group">
                            <label for="height-feet">Max Height (feet)</label>
                            <input type="number" id="height-feet" name="height_feet" 
                                   step="0.1" min="0" max="200">
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="spin-rate">Spin Rate (rpm)</label>
                            <input type="number" id="spin-rate" name="spin_rate" 
                                   step="1" min="0" max="15000">
                        </div>
                        <div class="form-group">
                            <label for="spin-axis">Spin Axis (°)</label>
                            <input type="number" id="spin-axis" name="spin_axis_degrees" 
                                   step="0.1" min="-90" max="90">
                            <small>Negative = draw, Positive = fade</small>
                        </div>
                        <div class="form-group">
                            <label for="backspin">Backspin (rpm)</label>
                            <input type="number" id="backspin" name="backspin_rpm" 
                                   step="1" min="0" max="15000">
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Club Data -->
            <div class="form-section collapsible">
                <h4 class="section-toggle">Club Data <i class="fas fa-chevron-down"></i></h4>
                <div class="collapsible-content">
                    <div class="form-row">
                        <div class="form-group">
                            <label for="club-path">Club Path (°)</label>
                            <input type="number" id="club-path" name="club_path_degrees" 
                                   step="0.1" min="-20" max="20">
                            <small>In-to-out = positive</small>
                        </div>
                        <div class="form-group">
                            <label for="face-angle">Face Angle (°)</label>
                            <input type="number" id="face-angle" name="face_angle_degrees" 
                                   step="0.1" min="-20" max="20">
                            <small>Open = positive</small>
                        </div>
                        <div class="form-group">
                            <label for="attack-angle">Attack Angle (°)</label>
                            <input type="number" id="attack-angle" name="attack_angle_degrees" 
                                   step="0.1" min="-15" max="15">
                            <small>Downward = negative</small>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="lie-angle">Dynamic Lie (°)</label>
                            <input type="number" id="lie-angle" name="lie_angle_degrees" 
                                   step="0.1" min="-10" max="10">
                        </div>
                        <div class="form-group">
                            <label for="loft-angle">Dynamic Loft (°)</label>
                            <input type="number" id="loft-angle" name="loft_angle_degrees" 
                                   step="0.1" min="0" max="60">
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Environmental Conditions -->
            <div class="form-section collapsible">
                <h4 class="section-toggle">Conditions <i class="fas fa-chevron-down"></i></h4>
                <div class="collapsible-content">
                    <div class="form-row">
                        <div class="form-group">
                            <label for="temperature">Temperature (°F)</label>
                            <input type="number" id="temperature" name="temperature_f" 
                                   min="-20" max="120">
                        </div>
                        <div class="form-group">
                            <label for="wind-speed">Wind Speed (mph)</label>
                            <input type="number" id="wind-speed" name="wind_speed_mph" 
                                   min="0" max="50">
                        </div>
                        <div class="form-group">
                            <label for="wind-direction">Wind Direction</label>
                            <select id="wind-direction" name="wind_direction">
                                <option value="">None</option>
                                <option value="headwind">Headwind</option>
                                <option value="tailwind">Tailwind</option>
                                <option value="crosswind-left">Crosswind Left</option>
                                <option value="crosswind-right">Crosswind Right</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="humidity">Humidity (%)</label>
                            <input type="number" id="humidity" name="humidity_percent" 
                                   min="0" max="100">
                        </div>
                        <div class="form-group">
                            <label for="altitude">Altitude (feet)</label>
                            <input type="number" id="altitude" name="altitude_feet" 
                                   min="-500" max="15000">
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Shot Details -->
            <div class="form-section collapsible">
                <h4 class="section-toggle">Shot Details <i class="fas fa-chevron-down"></i></h4>
                <div class="collapsible-content">
                    <div class="form-row">
                        <div class="form-group">
                            <label for="shot-shape">Shot Shape</label>
                            <select id="shot-shape" name="shot_shape">
                                <option value="">Straight</option>
                                <option value="draw">Draw</option>
                                <option value="fade">Fade</option>
                                <option value="hook">Hook</option>
                                <option value="slice">Slice</option>
                                <option value="push">Push</option>
                                <option value="pull">Pull</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="intended-shape">Intended Shape</label>
                            <select id="intended-shape" name="intended_shape">
                                <option value="">Straight</option>
                                <option value="draw">Draw</option>
                                <option value="fade">Fade</option>
                                <option value="punch">Punch</option>
                                <option value="flop">Flop</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="shot-result">Result</label>
                            <select id="shot-result" name="shot_result">
                                <option value="">Select</option>
                                <option value="excellent">Excellent</option>
                                <option value="good">Good</option>
                                <option value="average">Average</option>
                                <option value="poor">Poor</option>
                                <option value="terrible">Terrible</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="penalty-type">Penalty</label>
                            <select id="penalty-type" name="penalty_type">
                                <option value="">None</option>
                                <option value="water">Water</option>
                                <option value="ob">Out of Bounds</option>
                                <option value="lost">Lost Ball</option>
                                <option value="unplayable">Unplayable</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="recovery-shot">Recovery Shot</label>
                            <label class="checkbox-label">
                                <input type="checkbox" id="recovery-shot" name="is_recovery_shot">
                                <span>This was a recovery shot</span>
                            </label>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="shot-notes">Notes</label>
                        <textarea id="shot-notes" name="notes" rows="3" 
                                  placeholder="Any additional notes about this shot..."></textarea>
                    </div>
                </div>
            </div>
            
            <!-- Data Source -->
            <div class="form-section">
                <div class="form-group">
                    <label for="data-source">Data Source</label>
                    <select id="data-source" name="source">
                        <option value="manual">Manual Entry</option>
                        <option value="trackman">TrackMan</option>
                        <option value="arccos">Arccos</option>
                        <option value="skytrak">SkyTrak</option>
                        <option value="simulator">Other Simulator</option>
                    </select>
                </div>
            </div>
            
            <div class="form-buttons">
                <button type="button" class="btn-secondary cancel-shot">Cancel</button>
                <button type="submit" class="btn-primary">Save Shot</button>
            </div>
        </form>
    `;
}

// Initialize enhanced shot form with all event handlers
export function initializeEnhancedShotForm(formElement, onSubmit) {
    // Set default date to now
    const dateInput = formElement.querySelector('#shot-date');
    if (dateInput) {
        const now = new Date();
        dateInput.value = now.toISOString().slice(0, 16);
    }
    
    // Initialize collapsible sections
    const toggles = formElement.querySelectorAll('.section-toggle');
    toggles.forEach(toggle => {
        toggle.addEventListener('click', () => {
            const content = toggle.nextElementSibling;
            const icon = toggle.querySelector('i');
            
            if (content.style.display === 'none' || !content.style.display) {
                content.style.display = 'block';
                icon.classList.remove('fa-chevron-down');
                icon.classList.add('fa-chevron-up');
            } else {
                content.style.display = 'none';
                icon.classList.remove('fa-chevron-up');
                icon.classList.add('fa-chevron-down');
            }
        });
    });
    
    // Auto-calculate smash factor
    const ballSpeedInput = formElement.querySelector('#ball-speed');
    const clubSpeedInput = formElement.querySelector('#club-speed');
    const smashFactorInput = formElement.querySelector('#smash-factor');
    
    function calculateSmashFactor() {
        const ballSpeed = parseFloat(ballSpeedInput.value);
        const clubSpeed = parseFloat(clubSpeedInput.value);
        
        if (ballSpeed && clubSpeed && clubSpeed > 0) {
            const smashFactor = (ballSpeed / clubSpeed).toFixed(2);
            smashFactorInput.value = smashFactor;
        }
    }
    
    if (ballSpeedInput && clubSpeedInput) {
        ballSpeedInput.addEventListener('input', calculateSmashFactor);
        clubSpeedInput.addEventListener('input', calculateSmashFactor);
    }
    
    // Handle form submission
    formElement.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(formElement);
        const shotData = {};
        
        // Convert form data to object, handling empty values
        for (let [key, value] of formData.entries()) {
            if (value && value !== '') {
                // Handle checkboxes
                if (formElement.querySelector(`[name="${key}"]`).type === 'checkbox') {
                    shotData[key] = formElement.querySelector(`[name="${key}"]`).checked;
                } else {
                    shotData[key] = value;
                }
            }
        }
        
        // Ensure required fields are present
        if (!shotData.club || !shotData.shot_date) {
            alert('Please fill in all required fields');
            return;
        }
        
        if (onSubmit) {
            await onSubmit(shotData);
        }
    });
    
    // Cancel button
    const cancelBtn = formElement.querySelector('.cancel-shot');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
            if (confirm('Are you sure you want to cancel? Any unsaved data will be lost.')) {
                formElement.reset();
                // Trigger any cancel callback if needed
                if (window.closeAddShotModal) {
                    window.closeAddShotModal();
                }
            }
        });
    }
}

// Export function to populate club dropdown
export function populateClubDropdown(selectElement, clubs) {
    // Clear existing options except the first one
    selectElement.innerHTML = '<option value="">Select Club</option>';
    
    // Group clubs by type
    const clubTypes = {
        'driver': 'Drivers',
        'wood': 'Woods',
        'hybrid': 'Hybrids',
        'iron': 'Irons',
        'wedge': 'Wedges',
        'putter': 'Putters'
    };
    
    const groupedClubs = {};
    
    clubs.forEach(club => {
        const type = club.club_type || 'other';
        if (!groupedClubs[type]) {
            groupedClubs[type] = [];
        }
        groupedClubs[type].push(club);
    });
    
    // Add clubs by group
    Object.entries(clubTypes).forEach(([type, label]) => {
        if (groupedClubs[type] && groupedClubs[type].length > 0) {
            const optgroup = document.createElement('optgroup');
            optgroup.label = label;
            
            groupedClubs[type].forEach(club => {
                const option = document.createElement('option');
                option.value = club.name;
                option.textContent = club.name;
                optgroup.appendChild(option);
            });
            
            selectElement.appendChild(optgroup);
        }
    });
}