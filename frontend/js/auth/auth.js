import ApiService from '../api/api.js';

// Check if user is authenticated
async function checkAuthentication() {
    // Don't check on login page to avoid redirect loops
    if (window.location.pathname.includes('login.html')) {
        return;
    }
    
    try {
        const response = await fetch('/api/auth/me', {
            credentials: 'include'
        });
        
        if (!response.ok) {
            // If not authenticated, redirect to login page
            window.location.href = '/login.html';
            return;
        }
        
        const data = await response.json();
        if (!data.user) {
            window.location.href = '/login.html';
            return;
        }
        
        // Update user info if available
        updateUserInfo(data.user);
    } catch (error) {
        console.error('Error checking authentication:', error);
        window.location.href = '/login.html';
    }
}

// Update user info in UI with data from API
function updateUserInfo(user) {
    if (!user) return;
    
    // Update sidebar user info
    const userNameElement = document.querySelector('.user-name');
    const userHandicapElement = document.querySelector('.user-handicap');
    const userAvatarImg = document.querySelector('.user-avatar img');
    
    if (userNameElement) {
        userNameElement.textContent = user.name || user.full_name || user.email.split('@')[0];
    }
    
    if (userHandicapElement && user.preferences) {
        userHandicapElement.textContent = `Handicap: ${user.preferences.handicap || 'N/A'}`;
    }
    
    // Update avatar in sidebar if available
    if (userAvatarImg && (user.avatar_url || user.profile_picture)) {
        userAvatarImg.src = user.avatar_url || user.profile_picture;
    }
    
    // Update profile form fields
    const fullnameInput = document.getElementById('fullname');
    const emailInput = document.getElementById('email');
    const handicapInput = document.getElementById('handicap');
    const phoneInput = document.getElementById('phone');
    const homeCourseInput = document.getElementById('home-course');
    const profileImagePreview = document.getElementById('profile-image-preview');
    
    if (fullnameInput) {
        fullnameInput.value = user.name || user.full_name || '';
    }
    
    if (emailInput) {
        emailInput.value = user.email || '';
    }
    
    if (phoneInput && user.preferences) {
        phoneInput.value = user.preferences.phone || '';
    }
    
    if (handicapInput && user.preferences) {
        handicapInput.value = user.preferences.handicap || '';
    }
    
    if (homeCourseInput && user.preferences) {
        homeCourseInput.value = user.preferences.home_course || '';
    }
    
    // Update profile image preview if available
    if (profileImagePreview && (user.avatar_url || user.profile_picture)) {
        profileImagePreview.src = user.avatar_url || user.profile_picture;
    }
    
    // Update profile completion indicator
    updateProfileCompletion(user);
}

// Initialize logout handler
function initLogoutHandler() {
    const logoutButton = document.getElementById('logout-button');
    if (logoutButton) {
        logoutButton.addEventListener('click', async function(e) {
            e.preventDefault();
            
            try {
                // Show loading state on button
                const originalText = this.textContent;
                this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Logging out...';
                this.disabled = true;
                
                const result = await ApiService.logout();
                if (result.success) {
                    // Clear any stored credentials
                    sessionStorage.clear();
                    localStorage.removeItem('user_session');
                    
                    // Redirect to login page
                    window.location.href = '/login.html';
                } else {
                    console.error('Logout failed');
                    this.innerHTML = originalText;
                    this.disabled = false;
                }
            } catch (error) {
                console.error('Error during logout:', error);
                logoutButton.innerHTML = originalText;
                logoutButton.disabled = false;
            }
        });
    }
}

// Get current user session with token
async function getSessionUser() {
    try {
        return await ApiService.getCurrentUser();
    } catch (error) {
        console.error('Error getting session user:', error);
        return null;
    }
}

// Login with email and password
async function loginWithEmailPassword(email, password) {
    console.log('Attempting login with email...');
    
    try {
        const result = await ApiService.login({ email, password });
        return { success: true, user: result.user };
    } catch (error) {
        console.error('Login error:', error);
        return { 
            success: false, 
            error: error.message || 'Could not connect to server. Please try again.' 
        };
    }
}

// Update profile completion indicator
function updateProfileCompletion(user) {
    if (!user) return;
    
    // Fields that should be completed for a "complete" profile
    const requiredFields = [
        'name',
        'email', 
        'avatar_url', 
        'preferences.handicap', 
        'preferences.home_course'
    ];
    
    // Count completed fields
    let completedFields = 0;
    
    // Check basic fields
    if (user.name || user.full_name) completedFields++;
    if (user.email) completedFields++;
    if (user.avatar_url || user.profile_picture) completedFields++;
    
    // Check preference fields 
    if (user.preferences) {
        if (user.preferences.handicap) completedFields++;
        if (user.preferences.home_course) completedFields++;
    }
    
    // Calculate completion percentage
    const completionPercentage = Math.round((completedFields / requiredFields.length) * 100);
    
    // Update UI elements
    const profileCompletionValue = document.querySelector('.profile-completion-progress .progress-value');
    const profileCompletionText = document.querySelector('.profile-completion-progress .progress-text');
    const profileCompletionAlert = document.getElementById('profile-completion-alert');
    
    if (profileCompletionValue) {
        profileCompletionValue.style.width = `${completionPercentage}%`;
    }
    
    if (profileCompletionText) {
        profileCompletionText.textContent = `${completionPercentage}% Complete`;
    }
    
    // Show/hide profile completion alert based on completion
    if (profileCompletionAlert) {
        if (completionPercentage < 100) {
            profileCompletionAlert.style.display = 'flex';
        } else {
            profileCompletionAlert.style.display = 'none';
        }
    }
}

// Initialize profile form submission
async function initProfileFormSubmission() {
    const profileForm = document.querySelector('#profile-settings form');
    
    if (!profileForm) return;
    
    profileForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Show loading state
        const submitBtn = profileForm.querySelector('.btn-primary');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
        
        // Remove any existing error messages
        const existingErrorMsg = profileForm.querySelector('.error-message');
        if (existingErrorMsg) {
            existingErrorMsg.remove();
        }
        
        try {
            // Get image file if selected
            const imageFile = document.getElementById('profile-image-upload').files[0];
            
            // Create FormData object for multipart form submission (for file upload)
            const formData = new FormData();
            
            // Add profile fields
            formData.append('name', document.getElementById('fullname').value);
            formData.append('email', document.getElementById('email').value);
            formData.append('handicap', document.getElementById('handicap').value);
            formData.append('phone', document.getElementById('phone').value);
            formData.append('home_course', document.getElementById('home-course').value);
            
            // Add image if available
            if (imageFile) {
                console.log("Selected file:", imageFile.name, imageFile.type, imageFile.size);
                
                // Verify it's an image file
                if (!imageFile.type.match('image.*')) {
                    throw new Error('Please select a valid image file (JPEG, PNG, GIF, etc.)');
                }
                
                // Verify file size (limit to 5MB)
                if (imageFile.size > 5 * 1024 * 1024) {
                    throw new Error('Image file size must be less than 5MB');
                }
                formData.append('profile_image', imageFile);
            }
            
            // Get authentication token for API request
            const token = await ApiService._getAuthToken();
            
            // Update profile with proper authorization
            const response = await fetch('/api/auth/profile', {
                method: 'POST',
                credentials: 'include',
                headers: token ? {
                    'Authorization': `Bearer ${token}`
                } : {},
                body: formData
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Failed to update profile (${response.status})`);
            }
            
            const result = await response.json();
            
            // Update UI with new user data
            if (result.user) {
                updateUserInfo(result.user);
                // Import showToast from UI module if needed
                const { showToast } = await import('../ui/ui.js').catch(() => ({}));
                
                // Show success toast
                if (typeof showToast === 'function') {
                    showToast('Profile updated successfully!', 'success');
                } else {
                    // Fallback if UI module not loaded
                    const successMsg = document.createElement('div');
                    successMsg.className = 'success-message';
                    successMsg.textContent = 'Profile updated successfully!';
                    profileForm.appendChild(successMsg);
                    
                    // Remove success message after 3 seconds
                    setTimeout(() => {
                        if (profileForm.contains(successMsg)) {
                            profileForm.removeChild(successMsg);
                        }
                    }, 3000);
                }
            }
        } catch (error) {
            console.error('Error updating profile:', error);
            
            // Import showToast from UI module if needed
            const { showToast } = await import('../ui/ui.js').catch(() => ({}));
            
            // Check for specific error types
            let errorMessage = error.message || 'Failed to update profile';
            
            // Check for connection errors
            if (error.name === 'TypeError' && errorMessage.includes('Failed to fetch')) {
                errorMessage = 'Connection error. Please check your internet connection.';
            }
            
            // Check for auth errors
            if (errorMessage.includes('401') || errorMessage.includes('403')) {
                errorMessage = 'Authentication error. Please login again.';
                // Force logout after delay
                setTimeout(() => {
                    window.location.href = '/login.html';
                }, 3000);
            }
            
            // Show error toast or message
            if (typeof showToast === 'function') {
                showToast(errorMessage, 'error');
            } else {
                // Fallback if UI module not loaded
                const errorMsg = document.createElement('div');
                errorMsg.className = 'error-message';
                errorMsg.textContent = errorMessage;
                profileForm.appendChild(errorMsg);
                
                // Remove error after delay
                setTimeout(() => {
                    if (profileForm.contains(errorMsg)) {
                        profileForm.removeChild(errorMsg);
                    }
                }, 5000);
            }
        } finally {
            // Reset button state
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    });
}

// Initialize profile image upload preview
function initProfileImageUpload() {
    const imageUpload = document.getElementById('profile-image-upload');
    const imagePreview = document.getElementById('profile-image-preview');
    const avatarUploadLabel = document.querySelector('.change-avatar');
    
    if (!imageUpload || !imagePreview) return;
    
    // Add click handler to the "Change Photo" label to trigger file input
    if (avatarUploadLabel) {
        avatarUploadLabel.addEventListener('click', function(e) {
            e.preventDefault();
            imageUpload.click();
        });
    }
    
    imageUpload.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            // Check if file is an image
            if (!file.type.match('image.*')) {
                showToast('Please select an image file (JPEG, PNG, GIF)', 'error');
                return;
            }
            
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.src = e.target.result;
            }
            reader.readAsDataURL(file);
        }
    });
}

// Export the auth module functions
export {
    checkAuthentication,
    updateUserInfo,
    initLogoutHandler,
    getSessionUser,
    loginWithEmailPassword,
    updateProfileCompletion,
    initProfileFormSubmission,
    initProfileImageUpload
};