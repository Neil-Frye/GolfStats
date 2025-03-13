// API Service Module
const ApiService = {
  // Authentication
  async login(credentials) {
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(credentials)
      });
      
      return await this._handleResponse(response);
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },
  
  async logout() {
    try {
      const response = await fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include'
      });
      
      return await this._handleResponse(response);
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  },
  
  async getCurrentUser() {
    try {
      const response = await fetch('/api/auth/me', {
        credentials: 'include'
      });
      
      return await this._handleResponse(response);
    } catch (error) {
      console.error('Get current user error:', error);
      throw error;
    }
  },
  
  async updateProfile(profileData) {
    try {
      // For FormData (multipart/form-data) requests, don't set Content-Type
      // The browser will set it automatically with the correct boundary
      const headers = {};
      const token = await this._getAuthToken();
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch('/api/auth/profile', {
        method: 'POST',
        credentials: 'include',
        headers: headers,
        body: profileData // Assuming profileData is a FormData object
      });
      
      return await this._handleResponse(response);
    } catch (error) {
      console.error('Update profile error:', error);
      throw error;
    }
  },
  
  // Rounds
  async getRounds(params = {}) {
    try {
      const { filter = 'all', limit = 10, page = 1 } = params;
      const queryParams = new URLSearchParams({
        filter,
        limit,
        page
      }).toString();
      
      const response = await fetch(`/api/rounds?${queryParams}`, {
        credentials: 'include'
      });
      
      return await this._handleResponse(response);
    } catch (error) {
      console.error('Get rounds error:', error);
      throw error;
    }
  },
  
  async getRound(roundId) {
    try {
      const response = await fetch(`/api/rounds/${roundId}`, {
        credentials: 'include'
      });
      
      return await this._handleResponse(response);
    } catch (error) {
      console.error('Get round error:', error);
      throw error;
    }
  },
  
  async saveRound(roundData) {
    try {
      const response = await fetch('/api/rounds', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(roundData)
      });
      
      return await this._handleResponse(response);
    } catch (error) {
      console.error('Save round error:', error);
      throw error;
    }
  },
  
  async updateRound(roundId, roundData) {
    try {
      const response = await fetch(`/api/rounds/${roundId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(roundData)
      });
      
      return await this._handleResponse(response);
    } catch (error) {
      console.error('Update round error:', error);
      throw error;
    }
  },
  
  async deleteRound(roundId) {
    try {
      const response = await fetch(`/api/rounds/${roundId}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      
      return await this._handleResponse(response);
    } catch (error) {
      console.error('Delete round error:', error);
      throw error;
    }
  },
  
  // Stats
  async getStats(timeframe = 'all') {
    try {
      const response = await fetch(`/api/stats?timeframe=${timeframe}`, {
        credentials: 'include'
      });
      
      return await this._handleResponse(response);
    } catch (error) {
      console.error('Get stats error:', error);
      throw error;
    }
  },
  
  // Clubs
  async getClubs() {
    try {
      const response = await fetch('/api/clubs', {
        credentials: 'include'
      });
      
      return await this._handleResponse(response);
    } catch (error) {
      console.error('Get clubs error:', error);
      throw error;
    }
  },
  
  async getClub(clubId) {
    try {
      const response = await fetch(`/api/clubs/${clubId}`, {
        credentials: 'include'
      });
      
      return await this._handleResponse(response);
    } catch (error) {
      console.error('Get club error:', error);
      throw error;
    }
  },
  
  async saveClub(clubData) {
    try {
      const response = await fetch('/api/clubs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(clubData)
      });
      
      return await this._handleResponse(response);
    } catch (error) {
      console.error('Save club error:', error);
      throw error;
    }
  },
  
  async updateClub(clubId, clubData) {
    try {
      const response = await fetch(`/api/clubs/${clubId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(clubData)
      });
      
      return await this._handleResponse(response);
    } catch (error) {
      console.error('Update club error:', error);
      throw error;
    }
  },
  
  async deleteClub(clubId) {
    try {
      const response = await fetch(`/api/clubs/${clubId}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      
      return await this._handleResponse(response);
    } catch (error) {
      console.error('Delete club error:', error);
      throw error;
    }
  },
  
  // Range Sessions and Shots
  async getRangeSessions(params = {}) {
    try {
      const { limit = 50 } = params;
      const queryParams = new URLSearchParams({
        limit
      }).toString();
      
      const response = await fetch(`/api/range-sessions?${queryParams}`, {
        credentials: 'include'
      });
      
      return await this._handleResponse(response);
    } catch (error) {
      console.error('Get range sessions error:', error);
      throw error;
    }
  },
  
  async getRangeSession(sessionId) {
    try {
      const response = await fetch(`/api/range-sessions/${sessionId}`, {
        credentials: 'include'
      });
      
      return await this._handleResponse(response);
    } catch (error) {
      console.error('Get range session error:', error);
      throw error;
    }
  },
  
  async createRangeSession(sessionData) {
    try {
      const response = await fetch('/api/range-sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(sessionData)
      });
      
      return await this._handleResponse(response);
    } catch (error) {
      console.error('Create range session error:', error);
      throw error;
    }
  },
  
  async updateRangeSession(sessionId, sessionData) {
    try {
      const response = await fetch(`/api/range-sessions/${sessionId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(sessionData)
      });
      
      return await this._handleResponse(response);
    } catch (error) {
      console.error('Update range session error:', error);
      throw error;
    }
  },
  
  async deleteRangeSession(sessionId) {
    try {
      const response = await fetch(`/api/range-sessions/${sessionId}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      
      return await this._handleResponse(response);
    } catch (error) {
      console.error('Delete range session error:', error);
      throw error;
    }
  },
  
  async getRangeShots(sessionId) {
    try {
      const response = await fetch(`/api/range-sessions/${sessionId}/shots`, {
        credentials: 'include'
      });
      
      return await this._handleResponse(response);
    } catch (error) {
      console.error('Get range shots error:', error);
      throw error;
    }
  },
  
  async addRangeShot(sessionId, shotData) {
    try {
      const response = await fetch(`/api/range-sessions/${sessionId}/shots`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(shotData)
      });
      
      return await this._handleResponse(response);
    } catch (error) {
      console.error('Add range shot error:', error);
      throw error;
    }
  },
  
  async addRangeShots(sessionId, shotsData) {
    try {
      const response = await fetch(`/api/range-sessions/${sessionId}/shots/batch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(shotsData)
      });
      
      return await this._handleResponse(response);
    } catch (error) {
      console.error('Add range shots error:', error);
      throw error;
    }
  },
  
  async getClubBenchmarks() {
    try {
      const response = await fetch('/api/club-benchmarks', {
        credentials: 'include'
      });
      
      return await this._handleResponse(response);
    } catch (error) {
      console.error('Get club benchmarks error:', error);
      throw error;
    }
  },
  
  async getClubBenchmark(club) {
    try {
      const response = await fetch(`/api/club-benchmarks/${encodeURIComponent(club)}`, {
        credentials: 'include'
      });
      
      return await this._handleResponse(response);
    } catch (error) {
      console.error('Get club benchmark error:', error);
      throw error;
    }
  },

  // Helper methods
  async _getAuthToken() {
    // Get the current user session with token
    try {
      const user = await this.getCurrentUser();
      return user?.token;
    } catch (error) {
      console.error('Error getting auth token:', error);
      return null;
    }
  },
  
  async _handleResponse(response) {
    if (!response.ok) {
      // Try to get error message from response
      try {
        const errorData = await response.json();
        throw new Error(errorData.message || `Request failed with status ${response.status}`);
      } catch (e) {
        throw new Error(`Request failed with status ${response.status}`);
      }
    }
    
    // Check if response is empty
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }
    
    return { success: true };
  }
};

// Export the service
export default ApiService;