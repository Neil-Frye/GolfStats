// GolfStats Login Script

document.addEventListener('DOMContentLoaded', function() {
    // Initialize login page functionality
    console.log('Login page initialized');
    
    // Handle Google OAuth login
    const googleLoginBtn = document.getElementById('google-login');
    if (googleLoginBtn) {
        googleLoginBtn.addEventListener('click', function() {
            initiateGoogleLogin();
        });
    }
    
    // Handle email/password login
    const emailLoginForm = document.getElementById('email-login-form');
    if (emailLoginForm) {
        emailLoginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            if (email && password) {
                loginWithEmailPassword(email, password);
            }
        });
    }
    
    // Handle signup link
    const signupLink = document.getElementById('signup-link');
    if (signupLink) {
        signupLink.addEventListener('click', function(e) {
            e.preventDefault();
            window.location.href = '/signup.html';
        });
    }
    
    // Handle forgot password link
    const forgotPasswordLink = document.querySelector('.forgot-password');
    if (forgotPasswordLink) {
        forgotPasswordLink.addEventListener('click', function(e) {
            e.preventDefault();
            window.location.href = '/reset-password.html';
        });
    }
    
    // Check if user is already logged in
    checkLoginStatus();
});

// Function to initiate Google OAuth login
function initiateGoogleLogin() {
    console.log('Initiating Google login...');
    
    // Show loading state
    const googleBtn = document.getElementById('google-login');
    const originalText = googleBtn.innerHTML;
    googleBtn.innerHTML = '<div class="loading-spinner small"></div> Connecting...';
    googleBtn.disabled = true;
    
    // Redirect to the Google OAuth endpoint
    window.location.href = '/api/auth/google/login';
}

// Function to login with email and password
async function loginWithEmailPassword(email, password) {
    console.log('Attempting login with email...');
    
    // Show loading state
    const submitBtn = document.querySelector('.login-btn');
    const originalText = submitBtn.textContent;
    submitBtn.innerHTML = '<div class="loading-spinner small"></div> Signing In...';
    submitBtn.disabled = true;
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include', // Important for session cookies
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            // Login successful
            console.log('Login successful');
            window.location.href = '/';
        } else {
            // Login failed
            console.error('Login failed:', data.message || 'Unknown error');
            showLoginError(data.message || 'Invalid email or password');
        }
    } catch (error) {
        console.error('Login error:', error);
        showLoginError('Could not connect to server. Please try again.');
    } finally {
        // Reset button state
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
}

// Show login error message
function showLoginError(message) {
    const errorElement = document.querySelector('.form-error');
    const errorMessage = errorElement.querySelector('span');
    
    errorMessage.textContent = message || 'Invalid email or password';
    errorElement.style.display = 'flex';
    
    // Hide the error message after 5 seconds
    setTimeout(() => {
        errorElement.style.display = 'none';
    }, 5000);
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
        // If there's an error, stay on the login page
    }
}