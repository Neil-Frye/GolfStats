/**
 * Enhanced Integrations Module - Real-time sync, progress tracking, and webhook support
 */
import ApiService from '../api/api.js';

// Enhanced Integration Service with real-time features
export const EnhancedIntegrationsService = {
    // Active sync processes
    activeSyncs: new Map(),
    
    // WebSocket connection for real-time updates
    wsConnection: null,
    
    /**
     * Initialize enhanced integration features
     */
    async initialize() {
        try {
            // Load current integration status
            await this.loadIntegrationStatus();
            
            // Set up WebSocket for real-time updates
            this.initializeWebSocket();
            
            // Set up UI event listeners
            this._setupEventListeners();
            
            // Check for pending syncs
            await this.checkPendingSyncs();
        } catch (error) {
            console.error('Error initializing enhanced integrations:', error);
        }
    },
    
    /**
     * Initialize WebSocket connection for real-time sync updates
     */
    initializeWebSocket() {
        const wsUrl = window.location.protocol === 'https:' 
            ? `wss://${window.location.host}/ws/integrations`
            : `ws://${window.location.host}/ws/integrations`;
        
        try {
            this.wsConnection = new WebSocket(wsUrl);
            
            this.wsConnection.onopen = () => {
                console.log('WebSocket connected for integration updates');
                this.sendWebSocketMessage({ type: 'subscribe', services: ['trackman', 'arccos', 'skytrak'] });
            };
            
            this.wsConnection.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };
            
            this.wsConnection.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
            
            this.wsConnection.onclose = () => {
                console.log('WebSocket disconnected, attempting reconnect in 5s...');
                setTimeout(() => this.initializeWebSocket(), 5000);
            };
        } catch (error) {
            console.error('Failed to initialize WebSocket:', error);
        }
    },
    
    /**
     * Handle WebSocket messages
     */
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'sync_started':
                this.handleSyncStarted(data);
                break;
            case 'sync_progress':
                this.handleSyncProgress(data);
                break;
            case 'sync_completed':
                this.handleSyncCompleted(data);
                break;
            case 'sync_error':
                this.handleSyncError(data);
                break;
            case 'new_data_available':
                this.handleNewDataAvailable(data);
                break;
        }
    },
    
    /**
     * Send message through WebSocket
     */
    sendWebSocketMessage(message) {
        if (this.wsConnection && this.wsConnection.readyState === WebSocket.OPEN) {
            this.wsConnection.send(JSON.stringify(message));
        }
    },
    
    /**
     * Perform full sync with progress tracking
     */
    async performFullSync(service, options = {}) {
        const syncId = `${service}_${Date.now()}`;
        
        // Create sync progress modal
        const progressModal = this.createSyncProgressModal(service, syncId);
        document.body.appendChild(progressModal);
        
        // Show modal
        setTimeout(() => progressModal.classList.add('show'), 10);
        
        // Store sync info
        this.activeSyncs.set(syncId, {
            service,
            modal: progressModal,
            startTime: Date.now(),
            progress: 0,
            status: 'initializing'
        });
        
        try {
            // Start sync via API
            const response = await ApiService.startIntegrationSync(service, {
                ...options,
                syncId,
                includeHistory: options.includeHistory || false,
                daysBack: options.daysBack || 90
            });
            
            if (!response.success) {
                throw new Error(response.error || 'Failed to start sync');
            }
            
            // Progress will be updated via WebSocket
            return response;
        } catch (error) {
            this.handleSyncError({
                syncId,
                service,
                error: error.message
            });
            throw error;
        }
    },
    
    /**
     * Create sync progress modal
     */
    createSyncProgressModal(service, syncId) {
        const modal = document.createElement('div');
        modal.className = 'modal sync-progress-modal';
        modal.id = `sync-modal-${syncId}`;
        modal.innerHTML = `
            <div class="modal-content sync-modal-content">
                <div class="sync-header">
                    <div class="sync-icon ${service}">
                        <img src="/images/integrations/${service}-logo.png" 
                             alt="${service}" 
                             onerror="this.style.display='none'">
                    </div>
                    <h2>Syncing ${this._getServiceDisplayName(service)}</h2>
                </div>
                
                <div class="sync-body">
                    <div class="sync-status">
                        <span class="status-text">Initializing sync...</span>
                        <span class="status-time">0:00</span>
                    </div>
                    
                    <div class="progress-container">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 0%"></div>
                        </div>
                        <span class="progress-percent">0%</span>
                    </div>
                    
                    <div class="sync-details">
                        <div class="sync-metric">
                            <span class="metric-label">Sessions Found:</span>
                            <span class="metric-value" data-metric="sessions">0</span>
                        </div>
                        <div class="sync-metric">
                            <span class="metric-label">Shots Imported:</span>
                            <span class="metric-value" data-metric="shots">0</span>
                        </div>
                        <div class="sync-metric">
                            <span class="metric-label">Duplicates Skipped:</span>
                            <span class="metric-value" data-metric="duplicates">0</span>
                        </div>
                        <div class="sync-metric">
                            <span class="metric-label">Errors:</span>
                            <span class="metric-value error" data-metric="errors">0</span>
                        </div>
                    </div>
                    
                    <div class="sync-log">
                        <div class="log-header">
                            <span>Activity Log</span>
                            <button class="btn-icon toggle-log" data-expanded="false">
                                <i class="fas fa-chevron-down"></i>
                            </button>
                        </div>
                        <div class="log-content" style="display: none;">
                            <ul class="log-entries"></ul>
                        </div>
                    </div>
                </div>
                
                <div class="sync-footer">
                    <button class="btn-secondary cancel-sync" data-sync-id="${syncId}">
                        Cancel Sync
                    </button>
                    <button class="btn-primary close-sync" style="display: none;">
                        Close
                    </button>
                </div>
            </div>
        `;
        
        // Set up event handlers
        this._setupSyncModalHandlers(modal, syncId);
        
        return modal;
    },
    
    /**
     * Handle sync started event
     */
    handleSyncStarted(data) {
        const syncInfo = this.activeSyncs.get(data.syncId);
        if (!syncInfo) return;
        
        syncInfo.status = 'syncing';
        const modal = syncInfo.modal;
        
        // Update status text
        const statusText = modal.querySelector('.status-text');
        statusText.textContent = 'Connecting to service...';
        
        // Add log entry
        this.addSyncLogEntry(modal, 'Sync process started', 'info');
    },
    
    /**
     * Handle sync progress update
     */
    handleSyncProgress(data) {
        const syncInfo = this.activeSyncs.get(data.syncId);
        if (!syncInfo) return;
        
        const modal = syncInfo.modal;
        
        // Update progress bar
        const progressFill = modal.querySelector('.progress-fill');
        const progressPercent = modal.querySelector('.progress-percent');
        progressFill.style.width = `${data.progress}%`;
        progressPercent.textContent = `${data.progress}%`;
        
        // Update status text
        const statusText = modal.querySelector('.status-text');
        statusText.textContent = data.message || 'Syncing data...';
        
        // Update metrics
        if (data.metrics) {
            Object.entries(data.metrics).forEach(([key, value]) => {
                const metricElement = modal.querySelector(`[data-metric="${key}"]`);
                if (metricElement) {
                    metricElement.textContent = value.toLocaleString();
                }
            });
        }
        
        // Update elapsed time
        this.updateSyncTime(syncInfo);
        
        // Add log entry if provided
        if (data.logEntry) {
            this.addSyncLogEntry(modal, data.logEntry, data.logType || 'info');
        }
    },
    
    /**
     * Handle sync completed
     */
    handleSyncCompleted(data) {
        const syncInfo = this.activeSyncs.get(data.syncId);
        if (!syncInfo) return;
        
        const modal = syncInfo.modal;
        syncInfo.status = 'completed';
        
        // Update UI to completed state
        const progressFill = modal.querySelector('.progress-fill');
        const progressPercent = modal.querySelector('.progress-percent');
        progressFill.style.width = '100%';
        progressPercent.textContent = '100%';
        progressFill.classList.add('complete');
        
        // Update status
        const statusText = modal.querySelector('.status-text');
        statusText.textContent = 'Sync completed successfully!';
        statusText.classList.add('success');
        
        // Show completion summary
        if (data.summary) {
            this.addSyncLogEntry(modal, 
                `Sync completed: ${data.summary.totalShots} shots imported, ` +
                `${data.summary.duplicatesSkipped} duplicates skipped`, 
                'success'
            );
        }
        
        // Update buttons
        const cancelBtn = modal.querySelector('.cancel-sync');
        const closeBtn = modal.querySelector('.close-sync');
        cancelBtn.style.display = 'none';
        closeBtn.style.display = 'block';
        
        // Show notification
        this.showNotification(`${this._getServiceDisplayName(syncInfo.service)} sync completed!`, 'success');
        
        // Reload integration status
        this.loadIntegrationStatus();
        
        // Clean up after delay
        setTimeout(() => {
            this.activeSyncs.delete(data.syncId);
        }, 60000); // Keep for 1 minute
    },
    
    /**
     * Handle sync error
     */
    handleSyncError(data) {
        const syncInfo = this.activeSyncs.get(data.syncId);
        if (!syncInfo) return;
        
        const modal = syncInfo.modal;
        syncInfo.status = 'error';
        
        // Update status
        const statusText = modal.querySelector('.status-text');
        statusText.textContent = `Error: ${data.error}`;
        statusText.classList.add('error');
        
        // Add error log
        this.addSyncLogEntry(modal, `Error: ${data.error}`, 'error');
        
        // Update buttons
        const cancelBtn = modal.querySelector('.cancel-sync');
        const closeBtn = modal.querySelector('.close-sync');
        cancelBtn.textContent = 'Retry';
        closeBtn.style.display = 'block';
        
        // Show notification
        this.showNotification(`${this._getServiceDisplayName(syncInfo.service)} sync failed: ${data.error}`, 'error');
    },
    
    /**
     * Handle new data available notification
     */
    handleNewDataAvailable(data) {
        this.showNotification(
            `New data available from ${this._getServiceDisplayName(data.service)}. Click to sync.`,
            'info',
            () => {
                this.performFullSync(data.service);
            }
        );
    },
    
    /**
     * Add entry to sync log
     */
    addSyncLogEntry(modal, message, type = 'info') {
        const logEntries = modal.querySelector('.log-entries');
        const entry = document.createElement('li');
        entry.className = `log-entry ${type}`;
        
        const timestamp = new Date().toLocaleTimeString();
        entry.innerHTML = `
            <span class="log-time">${timestamp}</span>
            <span class="log-message">${message}</span>
        `;
        
        logEntries.appendChild(entry);
        
        // Auto-scroll to bottom
        logEntries.scrollTop = logEntries.scrollHeight;
    },
    
    /**
     * Update sync elapsed time
     */
    updateSyncTime(syncInfo) {
        const elapsed = Date.now() - syncInfo.startTime;
        const minutes = Math.floor(elapsed / 60000);
        const seconds = Math.floor((elapsed % 60000) / 1000);
        
        const timeElement = syncInfo.modal.querySelector('.status-time');
        if (timeElement) {
            timeElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        }
    },
    
    /**
     * Setup sync modal event handlers
     */
    _setupSyncModalHandlers(modal, syncId) {
        // Toggle log
        const toggleBtn = modal.querySelector('.toggle-log');
        const logContent = modal.querySelector('.log-content');
        
        toggleBtn.addEventListener('click', () => {
            const isExpanded = toggleBtn.dataset.expanded === 'true';
            
            if (isExpanded) {
                logContent.style.display = 'none';
                toggleBtn.innerHTML = '<i class="fas fa-chevron-down"></i>';
                toggleBtn.dataset.expanded = 'false';
            } else {
                logContent.style.display = 'block';
                toggleBtn.innerHTML = '<i class="fas fa-chevron-up"></i>';
                toggleBtn.dataset.expanded = 'true';
            }
        });
        
        // Cancel/Retry button
        const cancelBtn = modal.querySelector('.cancel-sync');
        cancelBtn.addEventListener('click', async () => {
            const syncInfo = this.activeSyncs.get(syncId);
            
            if (syncInfo.status === 'error') {
                // Retry sync
                modal.remove();
                this.activeSyncs.delete(syncId);
                this.performFullSync(syncInfo.service);
            } else {
                // Cancel sync
                try {
                    await ApiService.cancelIntegrationSync(syncId);
                    this.handleSyncError({
                        syncId,
                        error: 'Sync cancelled by user'
                    });
                } catch (error) {
                    console.error('Error cancelling sync:', error);
                }
            }
        });
        
        // Close button
        const closeBtn = modal.querySelector('.close-sync');
        closeBtn.addEventListener('click', () => {
            modal.classList.remove('show');
            setTimeout(() => {
                modal.remove();
                this.activeSyncs.delete(syncId);
            }, 300);
        });
    },
    
    /**
     * Check for pending syncs on initialization
     */
    async checkPendingSyncs() {
        try {
            const pendingSyncs = await ApiService.getPendingSyncs();
            
            if (pendingSyncs && pendingSyncs.length > 0) {
                pendingSyncs.forEach(sync => {
                    // Recreate progress modal for pending sync
                    const progressModal = this.createSyncProgressModal(sync.service, sync.syncId);
                    document.body.appendChild(progressModal);
                    setTimeout(() => progressModal.classList.add('show'), 10);
                    
                    this.activeSyncs.set(sync.syncId, {
                        service: sync.service,
                        modal: progressModal,
                        startTime: new Date(sync.startTime).getTime(),
                        progress: sync.progress || 0,
                        status: sync.status
                    });
                    
                    // Update progress
                    this.handleSyncProgress({
                        syncId: sync.syncId,
                        progress: sync.progress,
                        message: sync.statusMessage,
                        metrics: sync.metrics
                    });
                });
            }
        } catch (error) {
            console.error('Error checking pending syncs:', error);
        }
    },
    
    /**
     * Show notification
     */
    showNotification(message, type = 'info', onClick = null) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close">&times;</button>
        `;
        
        if (onClick) {
            notification.style.cursor = 'pointer';
            notification.addEventListener('click', onClick);
        }
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => notification.classList.add('show'), 10);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 5000);
        
        // Close button
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        });
    },
    
    /**
     * Get service display name
     */
    _getServiceDisplayName(service) {
        const names = {
            'trackman': 'TrackMan',
            'arccos': 'Arccos',
            'skytrak': 'SkyTrak'
        };
        return names[service] || service;
    },
    
    /**
     * Load current integration status
     */
    async loadIntegrationStatus() {
        // Implementation from original IntegrationsService
        try {
            const result = await ApiService.getIntegrationStatus();
            
            if (result && result.integrations) {
                for (const [service, status] of Object.entries(result.integrations)) {
                    this.updateIntegrationUI(service, status.connected);
                }
            }
        } catch (error) {
            console.error('Error loading integration status:', error);
        }
    },
    
    /**
     * Update integration UI
     */
    updateIntegrationUI(service, isConnected) {
        // Implementation from original IntegrationsService
        const integrationEl = document.getElementById(`${service}-integration`);
        if (!integrationEl) return;
        
        const statusEl = integrationEl.querySelector('.integration-status');
        const connectBtn = integrationEl.querySelector('.connect-integration-btn');
        
        if (isConnected) {
            statusEl.textContent = 'Connected';
            statusEl.classList.remove('disconnected');
            statusEl.classList.add('connected');
            
            connectBtn.textContent = 'Disconnect';
            connectBtn.classList.add('disconnect-btn');
            
            // Add sync now button if it doesn't exist
            if (!integrationEl.querySelector('.sync-now-btn')) {
                const syncBtn = document.createElement('button');
                syncBtn.className = 'btn-primary sync-now-btn';
                syncBtn.textContent = 'Sync Now';
                syncBtn.setAttribute('data-service', service);
                
                connectBtn.parentNode.insertBefore(syncBtn, connectBtn);
                
                syncBtn.addEventListener('click', (e) => {
                    const service = e.target.getAttribute('data-service');
                    this.showSyncOptionsModal(service);
                });
            }
        } else {
            statusEl.textContent = 'Disconnected';
            statusEl.classList.remove('connected');
            statusEl.classList.add('disconnected');
            
            connectBtn.textContent = 'Connect Account';
            connectBtn.classList.remove('disconnect-btn');
            
            const syncBtn = integrationEl.querySelector('.sync-now-btn');
            if (syncBtn) {
                syncBtn.remove();
            }
        }
    },
    
    /**
     * Show sync options modal
     */
    showSyncOptionsModal(service) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Sync ${this._getServiceDisplayName(service)} Data</h2>
                    <button class="close-modal">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="sync-options-form">
                        <div class="form-group">
                            <label class="checkbox-label">
                                <input type="checkbox" name="includeHistory" checked>
                                <span>Include historical data</span>
                            </label>
                        </div>
                        
                        <div class="form-group">
                            <label for="days-back">Days to sync back</label>
                            <select id="days-back" name="daysBack">
                                <option value="7">Last 7 days</option>
                                <option value="30">Last 30 days</option>
                                <option value="90" selected>Last 90 days</option>
                                <option value="180">Last 180 days</option>
                                <option value="365">Last year</option>
                                <option value="0">All time</option>
                            </select>
                        </div>
                        
                        <div class="form-buttons">
                            <button type="button" class="btn-secondary cancel-modal">Cancel</button>
                            <button type="submit" class="btn-primary">Start Sync</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        setTimeout(() => modal.classList.add('show'), 10);
        
        // Event handlers
        const closeBtn = modal.querySelector('.close-modal');
        const cancelBtn = modal.querySelector('.cancel-modal');
        const form = modal.querySelector('#sync-options-form');
        
        const closeModal = () => {
            modal.classList.remove('show');
            setTimeout(() => modal.remove(), 300);
        };
        
        closeBtn.addEventListener('click', closeModal);
        cancelBtn.addEventListener('click', closeModal);
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(form);
            const options = {
                includeHistory: formData.get('includeHistory') === 'on',
                daysBack: parseInt(formData.get('daysBack'))
            };
            
            closeModal();
            
            // Start sync
            this.performFullSync(service, options);
        });
    },
    
    /**
     * Set up event listeners
     */
    _setupEventListeners() {
        // Delegate to handle dynamic buttons
        document.addEventListener('click', (e) => {
            const button = e.target.closest('.connect-integration-btn');
            if (button) {
                const service = button.getAttribute('data-service');
                
                if (button.classList.contains('disconnect-btn')) {
                    this.disconnectIntegration(service);
                } else {
                    // Use the global showIntegrationModal function
                    if (window.showIntegrationModal) {
                        window.showIntegrationModal(service);
                    }
                }
            }
        });
    },
    
    /**
     * Disconnect integration
     */
    async disconnectIntegration(service) {
        if (!confirm(`Are you sure you want to disconnect your ${this._getServiceDisplayName(service)} account?`)) {
            return;
        }
        
        try {
            const result = await ApiService.disconnectIntegration(service);
            
            if (result && result.success) {
                this.updateIntegrationUI(service, false);
                this.showNotification(`Disconnected from ${this._getServiceDisplayName(service)}`, 'success');
            } else {
                throw new Error(result.error || 'Disconnection failed');
            }
        } catch (error) {
            console.error(`Error disconnecting from ${service}:`, error);
            this.showNotification(`Failed to disconnect: ${error.message}`, 'error');
        }
    }
};

// Export default
export default EnhancedIntegrationsService;