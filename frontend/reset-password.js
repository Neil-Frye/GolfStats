// GolfStats Reset Password Script

document.addEventListener('DOMContentLoaded', function() {
    // Initialize reset password page functionality
    console.log('Reset password page initialized');
    
    // Handle reset password form submission
    const resetPasswordForm = document.getElementById('reset-password-form');
    if (resetPasswordForm) {
        resetPasswordForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = document.getElementById('email').value;
            
            if (email) {
                requestPasswordReset(email);
            }
        });
    }
    
    // Check if user is already logged in
    checkLoginStatus();
});

// Function to request password reset
async function requestPasswordReset(email) {
    console.log('Requesting password reset for:', email);
    
    // Show loading state
    const submitBtn = document.querySelector('.login-btn');
    const originalText = submitBtn.textContent;
    submitBtn.innerHTML = '<div class="loading-spinner small"></div> Sending...';
    submitBtn.disabled = true;
    
    try {
        const response = await fetch('/api/auth/reset-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Success
            console.log('Password reset email sent');
            showSuccessMessage('Password reset email sent! Check your inbox.');
            
            // Clear the form
            document.getElementById('email').value = '';
        } else {
            // Error
            console.error('Password reset request failed:', data.message || 'Unknown error');
            showErrorMessage(data.message || 'Error sending reset email. Please try again.');
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

// Check if user is already logged in
async function checkLoginStatus() {
    try {
        const response = await fetch('/api/auth/me', {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            
            if (data.user) {
                // User is already logged in, redirect to main app
                console.log('User already logged in:', data.user);
                window.location.href = '/';
            }
        }
    } catch (error) {
        console.error('Error checking login status:', error);
        // If there's an error, stay on the reset password page
    }
}