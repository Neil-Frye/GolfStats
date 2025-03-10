// GolfStats Reset Password Confirmation Script

document.addEventListener('DOMContentLoaded', function() {
    // Initialize reset password confirmation page
    console.log('Reset password confirmation page initialized');
    
    // Get token from URL
    const urlParams = new URLSearchParams(window.location.hash.substring(1));
    const accessToken = urlParams.get('access_token');
    const refreshToken = urlParams.get('refresh_token');
    const expiresIn = urlParams.get('expires_in');
    const type = urlParams.get('type');
    
    // If no token is found, show error
    if (!accessToken || type !== 'recovery') {
        showErrorMessage('Invalid or missing reset token. Please request a new password reset link.');
        disableForm();
        return;
    }
    
    // Store token in session storage
    sessionStorage.setItem('resetToken', accessToken);
    
    // Handle form submission
    const resetPasswordForm = document.getElementById('reset-password-confirm-form');
    if (resetPasswordForm) {
        resetPasswordForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm-password').value;
            
            // Validate passwords
            if (!password || password.length < 8) {
                showErrorMessage('Password must be at least 8 characters long');
                return;
            }
            
            if (password !== confirmPassword) {
                showErrorMessage('Passwords do not match');
                return;
            }
            
            // Get token from session storage
            const token = sessionStorage.getItem('resetToken');
            if (!token) {
                showErrorMessage('Reset token not found. Please try again.');
                return;
            }
            
            // Reset password
            resetPassword(token, password);
        });
    }
});

// Function to reset password
async function resetPassword(token, password) {
    console.log('Resetting password...');
    
    // Show loading state
    const submitBtn = document.querySelector('.login-btn');
    const originalText = submitBtn.textContent;
    submitBtn.innerHTML = '<div class="loading-spinner small"></div> Updating...';
    submitBtn.disabled = true;
    
    try {
        const response = await fetch('/api/auth/reset-password-confirm', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Success - show message
            showSuccessMessage('Password has been reset successfully! You can now login with your new password.');
            
            // Clear form and disable it
            document.getElementById('password').value = '';
            document.getElementById('confirm-password').value = '';
            disableForm();
            
            // Clear token from session storage
            sessionStorage.removeItem('resetToken');
            
            // Add login button
            const successMessage = document.querySelector('.form-message.success');
            if (successMessage) {
                const loginButton = document.createElement('button');
                loginButton.className = 'login-btn';
                loginButton.style.marginTop = '15px';
                loginButton.textContent = 'Go to Login';
                loginButton.addEventListener('click', function() {
                    window.location.href = '/login.html';
                });
                
                successMessage.appendChild(loginButton);
            }
        } else {
            // Error
            console.error('Password reset failed:', data.message || 'Unknown error');
            showErrorMessage(data.message || 'Failed to reset password. Please try again.');
        }
    } catch (error) {
        console.error('Password reset error:', error);
        showErrorMessage('Could not connect to server. Please try again.');
    } finally {
        // Reset button state
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
}

// Show success message
function showSuccessMessage(message) {
    const successElement = document.querySelector('.form-message.success');
    const successMessage = successElement.querySelector('span');
    
    successMessage.textContent = message;
    successElement.style.display = 'flex';
    
    // Hide the error message if it's visible
    const errorElement = document.querySelector('.form-error');
    if (errorElement) {
        errorElement.style.display = 'none';
    }
}

// Show error message
function showErrorMessage(message) {
    const errorElement = document.querySelector('.form-error');
    const errorMessage = errorElement.querySelector('span');
    
    errorMessage.textContent = message;
    errorElement.style.display = 'flex';
    
    // Hide the success message if it's visible
    const successElement = document.querySelector('.form-message.success');
    if (successElement) {
        successElement.style.display = 'none';
    }
}

// Disable form
function disableForm() {
    const form = document.getElementById('reset-password-confirm-form');
    const inputs = form.querySelectorAll('input');
    const submitBtn = form.querySelector('button[type="submit"]');
    
    inputs.forEach(input => {
        input.disabled = true;
    });
    
    submitBtn.disabled = true;
    submitBtn.style.display = 'none';
}