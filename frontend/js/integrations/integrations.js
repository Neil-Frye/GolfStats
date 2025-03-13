// Integrations Module
import ApiService from '../api/api.js';

// Constants for integration types
const INTEGRATION_TYPES = {
  TRACKMAN: 'trackman',
  ARCCOS: 'arccos',
  SKYTRAK: 'skytrak'
};

// Integration service to manage connections to external golf data providers
const IntegrationsService = {
  // Initialize integrations
  async initialize() {
    try {
      // Load current integration status
      await this.loadIntegrationStatus();
      
      // Set up UI event listeners
      this._setupEventListeners();
    } catch (error) {
      console.error('Error initializing integrations:', error);
    }
  },
  
  // Load integration status from the server
  async loadIntegrationStatus() {
    try {
      const result = await ApiService.getIntegrationStatus();
      
      if (result && result.integrations) {
        // Update UI for each integration
        for (const [service, status] of Object.entries(result.integrations)) {
          this.updateIntegrationUI(service, status.connected);
        }
      }
    } catch (error) {
      console.error('Error loading integration status:', error);
    }
  },
  
  // Update the UI to reflect connection status
  updateIntegrationUI(service, isConnected) {
    const integrationEl = document.getElementById(`${service}-integration`);
    if (!integrationEl) return;
    
    const statusEl = integrationEl.querySelector('.integration-status');
    const connectBtn = integrationEl.querySelector('.connect-integration-btn');
    
    if (isConnected) {
      // Update status indicator
      statusEl.textContent = 'Connected';
      statusEl.classList.remove('disconnected');
      statusEl.classList.add('connected');
      
      // Update button
      connectBtn.textContent = 'Disconnect';
      connectBtn.classList.add('disconnect-btn');
      
      // Add test sync button if it doesn't exist
      if (!integrationEl.querySelector('.test-integration-btn')) {
        const testBtn = document.createElement('button');
        testBtn.className = 'test-integration-btn';
        testBtn.textContent = 'Sync Now';
        testBtn.setAttribute('data-service', service);
        
        // Insert before the disconnect button
        connectBtn.parentNode.insertBefore(testBtn, connectBtn);
        
        // Add event listener
        testBtn.addEventListener('click', (e) => {
          const service = e.target.getAttribute('data-service');
          this.testIntegration(service);
        });
      }
    } else {
      // Update status indicator
      statusEl.textContent = 'Disconnected';
      statusEl.classList.remove('connected');
      statusEl.classList.add('disconnected');
      
      // Update button
      connectBtn.textContent = 'Connect Account';
      connectBtn.classList.remove('disconnect-btn');
      
      // Remove test sync button if it exists
      const testBtn = integrationEl.querySelector('.test-integration-btn');
      if (testBtn) {
        testBtn.remove();
      }
    }
  },
  
  // Connect to an integration service
  async connectIntegration(service, credentials) {
    try {
      const result = await ApiService.connectIntegration(credentials);
      
      if (result && result.success) {
        this.updateIntegrationUI(service, true);
        return { success: true, message: result.message };
      } else {
        return { success: false, message: result.error || 'Unknown error occurred' };
      }
    } catch (error) {
      console.error(`Error connecting to ${service}:`, error);
      return { success: false, message: error.message };
    }
  },
  
  // Disconnect from an integration service
  async disconnectIntegration(service) {
    try {
      // Show confirmation dialog
      if (!confirm(`Are you sure you want to disconnect your ${this._getServiceDisplayName(service)} account?`)) {
        return;
      }
      
      const result = await ApiService.disconnectIntegration(service);
      
      if (result && result.success) {
        this.updateIntegrationUI(service, false);
        // Show success message
        alert(`Successfully disconnected from ${this._getServiceDisplayName(service)}`);
      } else {
        // Show error message
        alert(`Failed to disconnect from ${this._getServiceDisplayName(service)}: ${result.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error(`Error disconnecting from ${service}:`, error);
      alert(`Error disconnecting from ${this._getServiceDisplayName(service)}: ${error.message}`);
    }
  },
  
  // Test an integration by triggering a sync
  async testIntegration(service) {
    try {
      // Show loading state
      const integrationEl = document.getElementById(`${service}-integration`);
      const testBtn = integrationEl?.querySelector('.test-integration-btn');
      
      if (testBtn) {
        const originalText = testBtn.textContent;
        testBtn.textContent = 'Syncing...';
        testBtn.disabled = true;
        
        // Call API to test connection
        const result = await ApiService.testIntegration(service);
        
        // Reset button
        testBtn.textContent = originalText;
        testBtn.disabled = false;
        
        if (result && result.success) {
          // Show success message
          alert(`${this._getServiceDisplayName(service)} sync completed successfully!`);
        } else {
          // Show error message
          alert(`${this._getServiceDisplayName(service)} sync failed: ${result.error || 'Unknown error'}`);
        }
      }
    } catch (error) {
      console.error(`Error testing ${service} integration:`, error);
      alert(`Error syncing with ${this._getServiceDisplayName(service)}: ${error.message}`);
      
      // Reset button if it exists
      const integrationEl = document.getElementById(`${service}-integration`);
      const testBtn = integrationEl?.querySelector('.test-integration-btn');
      if (testBtn) {
        testBtn.textContent = 'Sync Now';
        testBtn.disabled = false;
      }
    }
  },
  
  // Set up event listeners for integration buttons
  _setupEventListeners() {
    // Connect/disconnect buttons
    document.querySelectorAll('.connect-integration-btn').forEach(button => {
      button.addEventListener('click', (e) => {
        const service = e.target.getAttribute('data-service');
        
        if (e.target.classList.contains('disconnect-btn')) {
          // Disconnect flow
          this.disconnectIntegration(service);
        } else {
          // Connect flow - show modal
          const connectFn = window.showIntegrationModal;
          if (typeof connectFn === 'function') {
            connectFn(service);
          } else {
            console.error('showIntegrationModal function not found');
          }
        }
      });
    });
  },
  
  // Get formatted service name for display
  _getServiceDisplayName(service) {
    const serviceNames = {
      'trackman': 'Trackman',
      'arccos': 'Arccos',
      'skytrak': 'SkyTrak'
    };
    
    return serviceNames[service] || service;
  }
};

// Export the service
export default IntegrationsService;