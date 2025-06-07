/**
 * Enhanced Clubs Module - Complete club management with all database fields
 */

// Enhanced club form HTML with all database fields
export function getEnhancedClubFormHTML(club = null) {
    const isEdit = club !== null;
    const title = isEdit ? 'Edit Club' : 'Add New Club';
    
    return `
        <form id="enhanced-club-form">
            ${isEdit ? `<input type="hidden" name="id" value="${club.id}">` : ''}
            
            <!-- Basic Information -->
            <div class="form-tabs">
                <button type="button" class="tab-btn active" data-tab="basic">Basic Info</button>
                <button type="button" class="tab-btn" data-tab="specs">Specifications</button>
                <button type="button" class="tab-btn" data-tab="shaft">Shaft & Grip</button>
                <button type="button" class="tab-btn" data-tab="fitting">Fitting Data</button>
                <button type="button" class="tab-btn" data-tab="purchase">Purchase Info</button>
            </div>
            
            <!-- Basic Info Tab -->
            <div class="tab-content active" id="basic-tab">
                <div class="form-row">
                    <div class="form-group">
                        <label for="club-name">Club Name <span class="required">*</span></label>
                        <input type="text" id="club-name" name="name" required 
                               value="${club ? club.name : ''}"
                               placeholder="e.g., 7 Iron, Driver, 56° Wedge">
                    </div>
                    <div class="form-group">
                        <label for="club-type">Club Type <span class="required">*</span></label>
                        <select id="club-type" name="club_type" required>
                            <option value="">Select Type</option>
                            <option value="driver" ${club?.club_type === 'driver' ? 'selected' : ''}>Driver</option>
                            <option value="wood" ${club?.club_type === 'wood' ? 'selected' : ''}>Fairway Wood</option>
                            <option value="hybrid" ${club?.club_type === 'hybrid' ? 'selected' : ''}>Hybrid</option>
                            <option value="iron" ${club?.club_type === 'iron' ? 'selected' : ''}>Iron</option>
                            <option value="wedge" ${club?.club_type === 'wedge' ? 'selected' : ''}>Wedge</option>
                            <option value="putter" ${club?.club_type === 'putter' ? 'selected' : ''}>Putter</option>
                        </select>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="club-brand">Brand</label>
                        <input type="text" id="club-brand" name="brand" 
                               value="${club ? club.brand || '' : ''}"
                               list="brand-list" placeholder="e.g., TaylorMade, Titleist">
                        <datalist id="brand-list">
                            <option value="TaylorMade">
                            <option value="Titleist">
                            <option value="Callaway">
                            <option value="Ping">
                            <option value="Mizuno">
                            <option value="Cobra">
                            <option value="Srixon">
                            <option value="Cleveland">
                            <option value="Wilson">
                            <option value="PXG">
                        </datalist>
                    </div>
                    <div class="form-group">
                        <label for="club-model">Model</label>
                        <input type="text" id="club-model" name="model" 
                               value="${club ? club.model || '' : ''}"
                               placeholder="e.g., Stealth 2, TSR3">
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="club-notes">Notes</label>
                    <textarea id="club-notes" name="notes" rows="3" 
                              placeholder="Any special notes about this club...">${club ? club.notes || '' : ''}</textarea>
                </div>
                
                <div class="form-group">
                    <label class="checkbox-label">
                        <input type="checkbox" name="is_active" ${!club || club.is_active !== false ? 'checked' : ''}>
                        <span>Active in bag</span>
                    </label>
                </div>
            </div>
            
            <!-- Specifications Tab -->
            <div class="tab-content" id="specs-tab">
                <div class="form-row">
                    <div class="form-group">
                        <label for="club-loft">Loft (degrees)</label>
                        <input type="number" id="club-loft" name="loft" 
                               value="${club ? club.loft || '' : ''}"
                               step="0.5" min="0" max="64" placeholder="e.g., 10.5">
                    </div>
                    <div class="form-group">
                        <label for="club-lie">Lie Angle (degrees)</label>
                        <input type="number" id="club-lie" name="lie_angle" 
                               value="${club ? club.lie_angle || '' : ''}"
                               step="0.5" min="50" max="70" placeholder="e.g., 62.5">
                    </div>
                    <div class="form-group">
                        <label for="club-length">Length (inches)</label>
                        <input type="number" id="club-length" name="length_inches" 
                               value="${club ? club.length_inches || '' : ''}"
                               step="0.25" min="30" max="48" placeholder="e.g., 37.5">
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="swing-weight">Swing Weight</label>
                        <input type="text" id="swing-weight" name="swing_weight" 
                               value="${club ? club.swing_weight || '' : ''}"
                               placeholder="e.g., D2" maxlength="3">
                    </div>
                    <div class="form-group">
                        <label for="total-weight">Total Weight (grams)</label>
                        <input type="number" id="total-weight" name="total_weight_grams" 
                               value="${club ? club.total_weight_grams || '' : ''}"
                               min="200" max="500" placeholder="e.g., 315">
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="avg-distance">Average Distance (yards)</label>
                        <input type="number" id="avg-distance" name="avg_distance_yards" 
                               value="${club ? club.avg_distance_yards || '' : ''}"
                               min="0" max="400" placeholder="e.g., 165">
                    </div>
                    <div class="form-group">
                        <label for="max-distance">Max Distance (yards)</label>
                        <input type="number" id="max-distance" name="max_distance_yards" 
                               value="${club ? club.max_distance_yards || '' : ''}"
                               min="0" max="400" placeholder="e.g., 175">
                    </div>
                </div>
            </div>
            
            <!-- Shaft & Grip Tab -->
            <div class="tab-content" id="shaft-tab">
                <h4>Shaft Information</h4>
                <div class="form-row">
                    <div class="form-group">
                        <label for="shaft-type">Shaft Type</label>
                        <select id="shaft-type" name="shaft_type">
                            <option value="">Select Type</option>
                            <option value="steel" ${club?.shaft_type === 'steel' ? 'selected' : ''}>Steel</option>
                            <option value="graphite" ${club?.shaft_type === 'graphite' ? 'selected' : ''}>Graphite</option>
                            <option value="composite" ${club?.shaft_type === 'composite' ? 'selected' : ''}>Composite</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="shaft-flex">Shaft Flex</label>
                        <select id="shaft-flex" name="shaft_flex">
                            <option value="">Select Flex</option>
                            <option value="L" ${club?.shaft_flex === 'L' ? 'selected' : ''}>Ladies (L)</option>
                            <option value="A" ${club?.shaft_flex === 'A' ? 'selected' : ''}>Senior (A)</option>
                            <option value="R" ${club?.shaft_flex === 'R' ? 'selected' : ''}>Regular (R)</option>
                            <option value="S" ${club?.shaft_flex === 'S' ? 'selected' : ''}>Stiff (S)</option>
                            <option value="X" ${club?.shaft_flex === 'X' ? 'selected' : ''}>Extra Stiff (X)</option>
                            <option value="XX" ${club?.shaft_flex === 'XX' ? 'selected' : ''}>Tour X (XX)</option>
                        </select>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="shaft-brand">Shaft Brand</label>
                        <input type="text" id="shaft-brand" name="shaft_brand" 
                               value="${club ? club.shaft_brand || '' : ''}"
                               placeholder="e.g., Project X, KBS, Fujikura">
                    </div>
                    <div class="form-group">
                        <label for="shaft-model">Shaft Model</label>
                        <input type="text" id="shaft-model" name="shaft_model" 
                               value="${club ? club.shaft_model || '' : ''}"
                               placeholder="e.g., HZRDUS Black, Dynamic Gold">
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="shaft-weight">Shaft Weight (grams)</label>
                    <input type="number" id="shaft-weight" name="shaft_weight_grams" 
                           value="${club ? club.shaft_weight_grams || '' : ''}"
                           min="40" max="130" placeholder="e.g., 65">
                </div>
                
                <h4>Grip Information</h4>
                <div class="form-row">
                    <div class="form-group">
                        <label for="grip-brand">Grip Brand</label>
                        <input type="text" id="grip-brand" name="grip_brand" 
                               value="${club ? club.grip_brand || '' : ''}"
                               placeholder="e.g., Golf Pride, Lamkin">
                    </div>
                    <div class="form-group">
                        <label for="grip-model">Grip Model</label>
                        <input type="text" id="grip-model" name="grip_model" 
                               value="${club ? club.grip_model || '' : ''}"
                               placeholder="e.g., MCC Plus4, Tour Velvet">
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="grip-size">Grip Size</label>
                    <select id="grip-size" name="grip_size">
                        <option value="">Select Size</option>
                        <option value="undersize" ${club?.grip_size === 'undersize' ? 'selected' : ''}>Undersize</option>
                        <option value="standard" ${club?.grip_size === 'standard' ? 'selected' : ''}>Standard</option>
                        <option value="midsize" ${club?.grip_size === 'midsize' ? 'selected' : ''}>Midsize</option>
                        <option value="jumbo" ${club?.grip_size === 'jumbo' ? 'selected' : ''}>Jumbo</option>
                    </select>
                </div>
            </div>
            
            <!-- Fitting Data Tab -->
            <div class="tab-content" id="fitting-tab">
                <div class="form-group">
                    <label class="checkbox-label">
                        <input type="checkbox" name="custom_fitting" ${club?.custom_fitting ? 'checked' : ''}>
                        <span>This club was custom fitted</span>
                    </label>
                </div>
                
                <div class="fitting-info">
                    <p><i class="fas fa-info-circle"></i> Record your custom fitting specifications here for future reference.</p>
                </div>
                
                <div class="form-group">
                    <label for="fitting-notes">Fitting Notes</label>
                    <textarea id="fitting-notes" name="fitting_notes" rows="4" 
                              placeholder="Fitting details, adjustments made, launch monitor data, etc.">${club ? club.fitting_notes || '' : ''}</textarea>
                </div>
            </div>
            
            <!-- Purchase Info Tab -->
            <div class="tab-content" id="purchase-tab">
                <div class="form-row">
                    <div class="form-group">
                        <label for="purchase-date">Purchase Date</label>
                        <input type="date" id="purchase-date" name="purchase_date" 
                               value="${club ? club.purchase_date || '' : ''}">
                    </div>
                    <div class="form-group">
                        <label for="purchase-price">Purchase Price ($)</label>
                        <input type="number" id="purchase-price" name="purchase_price" 
                               value="${club ? club.purchase_price || '' : ''}"
                               step="0.01" min="0" placeholder="e.g., 299.99">
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="purchase-location">Purchase Location</label>
                    <input type="text" id="purchase-location" name="purchase_location" 
                           value="${club ? club.purchase_location || '' : ''}"
                           placeholder="e.g., Golf Galaxy, Local Pro Shop">
                </div>
            </div>
            
            <div class="form-buttons">
                <button type="button" class="btn-secondary cancel-club">Cancel</button>
                ${isEdit ? '<button type="button" class="btn-danger delete-club">Delete Club</button>' : ''}
                <button type="submit" class="btn-primary">${isEdit ? 'Update' : 'Add'} Club</button>
            </div>
        </form>
    `;
}

// Initialize enhanced club form with all event handlers
export function initializeEnhancedClubForm(formElement, onSubmit, onDelete) {
    // Initialize tab switching
    const tabButtons = formElement.querySelectorAll('.tab-btn');
    const tabContents = formElement.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;
            
            // Update active button
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // Update active content
            tabContents.forEach(content => {
                if (content.id === `${tabName}-tab`) {
                    content.classList.add('active');
                } else {
                    content.classList.remove('active');
                }
            });
        });
    });
    
    // Handle form submission
    formElement.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(formElement);
        const clubData = {};
        
        // Convert form data to object
        for (let [key, value] of formData.entries()) {
            if (value && value !== '') {
                // Handle checkboxes
                if (formElement.querySelector(`[name="${key}"]`).type === 'checkbox') {
                    clubData[key] = formElement.querySelector(`[name="${key}"]`).checked;
                } else {
                    clubData[key] = value;
                }
            }
        }
        
        // Ensure required fields
        if (!clubData.name || !clubData.club_type) {
            alert('Please fill in all required fields');
            return;
        }
        
        // Set default for is_active if not provided
        if (!('is_active' in clubData)) {
            clubData.is_active = true;
        }
        
        if (onSubmit) {
            await onSubmit(clubData);
        }
    });
    
    // Cancel button
    const cancelBtn = formElement.querySelector('.cancel-club');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
            if (confirm('Are you sure you want to cancel? Any unsaved data will be lost.')) {
                formElement.reset();
                // Trigger any cancel callback
                if (window.closeClubModal) {
                    window.closeClubModal();
                }
            }
        });
    }
    
    // Delete button (for edit mode)
    const deleteBtn = formElement.querySelector('.delete-club');
    if (deleteBtn && onDelete) {
        deleteBtn.addEventListener('click', () => {
            if (confirm('Are you sure you want to delete this club? This action cannot be undone.')) {
                const clubId = formElement.querySelector('input[name="id"]').value;
                onDelete(clubId);
            }
        });
    }
    
    // Auto-suggest swing weight based on club type
    const clubTypeSelect = formElement.querySelector('#club-type');
    const swingWeightInput = formElement.querySelector('#swing-weight');
    
    if (clubTypeSelect && swingWeightInput) {
        clubTypeSelect.addEventListener('change', () => {
            if (!swingWeightInput.value) {
                const suggestions = {
                    'driver': 'D2',
                    'wood': 'D1',
                    'hybrid': 'D0',
                    'iron': 'D0',
                    'wedge': 'D3',
                    'putter': 'E0'
                };
                
                if (suggestions[clubTypeSelect.value]) {
                    swingWeightInput.placeholder = `e.g., ${suggestions[clubTypeSelect.value]}`;
                }
            }
        });
    }
}

// Create a club card element for display
export function createClubCard(club) {
    const avgDistance = club.avg_distance_yards ? `${club.avg_distance_yards} yds` : 'No data';
    const isInactive = !club.is_active;
    
    return `
        <div class="club-card ${isInactive ? 'inactive' : ''}" data-club-id="${club.id}">
            ${isInactive ? '<div class="inactive-badge">Inactive</div>' : ''}
            <div class="club-header">
                <h3 class="club-name">${club.name}</h3>
                <button class="btn-icon edit-club-btn" data-club-id="${club.id}">
                    <i class="fas fa-edit"></i>
                </button>
            </div>
            <div class="club-details">
                ${club.brand || club.model ? `
                    <p class="club-model">${[club.brand, club.model].filter(Boolean).join(' ')}</p>
                ` : ''}
                <div class="club-stats">
                    <div class="stat">
                        <span class="stat-label">Avg Distance</span>
                        <span class="stat-value">${avgDistance}</span>
                    </div>
                    ${club.loft ? `
                        <div class="stat">
                            <span class="stat-label">Loft</span>
                            <span class="stat-value">${club.loft}°</span>
                        </div>
                    ` : ''}
                    ${club.shaft_flex ? `
                        <div class="stat">
                            <span class="stat-label">Flex</span>
                            <span class="stat-value">${club.shaft_flex}</span>
                        </div>
                    ` : ''}
                </div>
                ${club.custom_fitting ? '<div class="custom-fitted-badge"><i class="fas fa-check-circle"></i> Custom Fitted</div>' : ''}
            </div>
        </div>
    `;
}

// Create club summary statistics
export function createClubStatsSummary(clubs) {
    const activeClubs = clubs.filter(c => c.is_active);
    const byType = {};
    
    activeClubs.forEach(club => {
        const type = club.club_type || 'other';
        byType[type] = (byType[type] || 0) + 1;
    });
    
    return `
        <div class="club-stats-summary">
            <h3>Bag Summary</h3>
            <div class="summary-stats">
                <div class="stat">
                    <span class="stat-value">${activeClubs.length}</span>
                    <span class="stat-label">Active Clubs</span>
                </div>
                <div class="stat">
                    <span class="stat-value">${byType.driver || 0}</span>
                    <span class="stat-label">Drivers</span>
                </div>
                <div class="stat">
                    <span class="stat-value">${(byType.wood || 0) + (byType.hybrid || 0)}</span>
                    <span class="stat-label">Woods/Hybrids</span>
                </div>
                <div class="stat">
                    <span class="stat-value">${byType.iron || 0}</span>
                    <span class="stat-label">Irons</span>
                </div>
                <div class="stat">
                    <span class="stat-value">${byType.wedge || 0}</span>
                    <span class="stat-label">Wedges</span>
                </div>
                <div class="stat">
                    <span class="stat-value">${byType.putter || 0}</span>
                    <span class="stat-label">Putters</span>
                </div>
            </div>
        </div>
    `;
}