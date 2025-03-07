// GolfStats Signup Script

document.addEventListener('DOMContentLoaded', function() {
    // Initialize signup page functionality
    console.log('Signup page initialized');
    
    // Handle Google OAuth login
    const googleLoginBtn = document.getElementById('google-login');
    if (googleLoginBtn) {
        googleLoginBtn.addEventListener('click', function() {
            initiateGoogleLogin();
        });
    }
    
    // Handle signup form submission
    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const fullname = document.getElementById('fullname').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm-password').value;
            
            // Basic validation
            if (!fullname || !email || !password || !confirmPassword) {
                showSignupError('All fields are required');
                return;
            }
            
            if (password !== confirmPassword) {
                showSignupError('Passwords do not match');
                return;
            }
            
            if (password.length < 8) {
                showSignupError('Password must be at least 8 characters');
                return;
            }
            
            // All validation passed, proceed with signup
            signupWithEmailPassword(fullname, email, password);
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

// Function to signup with email and password
async function signupWithEmailPassword(name, email, password) {
    console.log('Attempting signup with email...');
    
    // Show loading state
    const submitBtn = document.querySelector('.login-btn');
    const originalText = submitBtn.textContent;
    submitBtn.innerHTML = '<div class="loading-spinner small"></div> Creating Account...';
    submitBtn.disabled = true;
    
    try {
        const response = await fetch('/api/auth/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include', // Important for session cookies
            body: JSON.stringify({ 
                name, 
                email, 
                password 
            })
        });
        
        const data = await response.json();
        
        if (response.ok && data.user) {
            // Signup successful
            console.log('Signup successful');
            window.location.href = '/';
        } else {
            // Signup failed
            console.error('Signup failed:', data.error || 'Unknown error');
            showSignupError(data.error || 'Could not create account. Please try again.');
        }
    } catch (error) {
        console.error('Signup error:', error);
        showSignupError('Could not connect to server. Please try again.');
    } finally {
        // Reset button state
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
}

// Show signup error message
function showSignupError(message) {
    const errorElement = document.querySelector('.form-error');
    const errorMessage = errorElement.querySelector('span');
    
    errorMessage.textContent = message || 'An error occurred';
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
        // If there's an error, stay on the signup page
    }
}