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
    console.log('Updating UI with user info:', user);
    if (!user) {
        console.warn('No user data provided to updateUserInfo');
        return;
    }
    
    // Update sidebar user info
    const userNameElement = document.querySelector('.user-name');
    const userHandicapElement = document.querySelector('.user-handicap');
    const userAvatarImg = document.querySelector('.user-avatar img');
    
    // Get avatar URL from user or preferences
    const avatarUrl = user.avatar_url || 
                     (user.preferences && user.preferences.avatar_url) || 
                     user.profile_picture;
    console.log('Avatar URL:', avatarUrl);
    
    // Get user's display name with fallbacks
    const displayName = user.name || 
                      (user.preferences && user.preferences.display_name) || 
                      user.full_name || 
                      user.email.split('@')[0];
    console.log('Display name:', displayName);
    
    if (userNameElement) {
        userNameElement.textContent = displayName;
        console.log('Updated user name element to:', displayName);
    }
    
    if (userHandicapElement && user.preferences) {
        // Handle case where handicap might be empty string
        const handicap = user.preferences.handicap;
        userHandicapElement.textContent = `Handicap: ${handicap ? handicap : 'N/A'}`;
        console.log('Updated handicap element to:', handicap ? handicap : 'N/A');
    }
    
    // Update avatar in sidebar if available
    if (userAvatarImg && avatarUrl) {
        userAvatarImg.src = avatarUrl;
        console.log('Updated avatar image to:', avatarUrl);
    }
    
    // Update profile form fields
    const fullnameInput = document.getElementById('fullname');
    const emailInput = document.getElementById('email');
    const handicapInput = document.getElementById('handicap');
    const phoneInput = document.getElementById('phone');
    const homeCourseInput = document.getElementById('home-course');
    const profileImagePreview = document.getElementById('profile-image-preview');
    
    if (fullnameInput) {
        fullnameInput.value = displayName;
        console.log('Updated fullname input to:', displayName);
    }
    
    if (emailInput) {
        emailInput.value = user.email || '';
        console.log('Updated email input to:', user.email || '');
    }
    
    if (user.preferences) {
        if (phoneInput) {
            phoneInput.value = user.preferences.phone || '';
            console.log('Updated phone input to:', user.preferences.phone || '');
        }
        
        if (handicapInput) {
            handicapInput.value = user.preferences.handicap || '';
            console.log('Updated handicap input to:', user.preferences.handicap || '');
        }
        
        if (homeCourseInput) {
            homeCourseInput.value = user.preferences.home_course || '';
            console.log('Updated home course input to:', user.preferences.home_course || '');
        }
    }
    
    // Update profile image preview if available
    if (profileImagePreview && avatarUrl) {
        profileImagePreview.src = avatarUrl;
        console.log('Updated profile image preview to:', avatarUrl);
    }
    
    // Update profile completion indicator
    updateProfileCompletion(user);
    console.log('Profile UI update complete');
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
            
            // Add profile fields - always append values, even if empty
            // Log what we're sending for debugging
            console.log('Sending profile data:');
            
            const fullname = document.getElementById('fullname').value || '';
            console.log('Fullname:', fullname);
            formData.append('name', fullname);
            
            const email = document.getElementById('email').value || '';
            console.log('Email:', email);
            formData.append('email', email);
            
            const handicap = document.getElementById('handicap').value || '';
            console.log('Handicap:', handicap);
            formData.append('handicap', handicap);
            
            const phone = document.getElementById('phone').value || '';
            console.log('Phone:', phone);
            formData.append('phone', phone);
            
            const homeCourse = document.getElementById('home-course').value || '';
            console.log('Home Course:', homeCourse);
            formData.append('home_course', homeCourse);
            
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
            console.log('Sending request with token:', token ? 'yes' : 'no');
            
            const requestHeaders = token ? {
                'Authorization': `Bearer ${token}`
            } : {};
            console.log('Request headers:', requestHeaders);
            
            const response = await fetch('/api/auth/profile', {
                method: 'POST',
                credentials: 'include',
                headers: requestHeaders,
                body: formData
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Failed to update profile (${response.status})`);
            }
            
            const result = await response.json();
            console.log('Profile update response:', result);
            
            // Update UI with new user data
            if (result.user) {
                console.log('Updating UI with user data:', result.user);
                updateUserInfo(result.user);
                
                // Import showToast from UI module if needed
                const { showToast } = await import('../ui/ui.js').catch(() => {
                    console.log('Could not import showToast, using fallback');
                    return {};
                });
                
                // Show success toast
                if (typeof showToast === 'function') {
                    console.log('Using showToast for success message');
                    showToast('Profile updated successfully!', 'success');
                } else {
                    // Fallback if UI module not loaded
                    console.log('Using fallback success message');
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
            } else {
                console.warn('No user data in response:', result);
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