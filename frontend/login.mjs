// GolfStats Login Script
import { createClient as supabaseCreateClient } from 'https://esm.sh/@supabase/supabase-js@2';

// --- Supabase Client Initialization for login.js ---
const SUPABASE_URL = 'https://rrrniscrqsrbtfahgguo.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJycm5pc2NycXNyYnRmYWhnZ3VvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDEyMDY1OTIsImV4cCI6MjA1Njc4MjU5Mn0.hnz96yUXBFlDzLzcptn9fLoR9tcbfvW-62YrMrEks1w';

let supabaseClient = null;

// Function to initialize Supabase client using ES Module import
function initializeSupabase() {
  console.log('=== Supabase Initialization with ES Module Import ===');
  try {
    if (typeof supabaseCreateClient === 'function') {
      supabaseClient = supabaseCreateClient(SUPABASE_URL, SUPABASE_ANON_KEY);
      console.log('✓ Supabase client initialized successfully via ES Module import!');
      
      // Setup auth state listener
      supabaseClient.auth.onAuthStateChange((event, session) => {
        console.log('Auth state changed (login.js via ES import):', event, session);
        if (event === 'SIGNED_IN' && session) {
          if (window.location.pathname.includes('login.html') || window.location.pathname.includes('signup.html')) {
            window.location.href = '/';
          }
        }
      });
      return true;
    } else {
      // This case should ideally not be hit if the import worked.
      console.error('✗ supabaseCreateClient (from import) is not a function.');
      return false;
    }
  } catch (error) {
    console.error('✗ Error initializing Supabase via ES Module import:', error);
    return false;
  }
}

// Initialize Supabase (no retry needed if import itself fails, as it's a static failure)
let supabaseInitialized = initializeSupabase();
if (!supabaseInitialized) {
    console.error('Failed to initialize Supabase on first attempt using ES module import.');
    // Optionally, could display an error to the user here if needed,
    // though initiateGoogleLogin will also show an error.
}

// --- End Supabase Client Initialization ---

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
async function initiateGoogleLogin() {
    console.log('=== Google Login Debug ===');
    console.log('initiateGoogleLogin called');
    console.log('supabaseClient available:', !!supabaseClient);
    console.log('supabaseInitialized:', supabaseInitialized);
    
    // Show loading state
    const googleBtn = document.getElementById('google-login');
    const originalText = googleBtn.innerHTML;
    googleBtn.innerHTML = '<div class="loading-spinner small"></div> Connecting...';
    googleBtn.disabled = true;
    
    try {
        // Check if Supabase is ready
        if (!supabaseClient || !supabaseInitialized) {
            console.error('✗ Supabase client not ready for Google login');
            showLoginError('Google login is not ready. Please refresh the page and try again.');
            googleBtn.innerHTML = originalText;
            googleBtn.disabled = false;
            return;
        }

        console.log('✓ Supabase client ready, initiating OAuth...');
        
        const { data, error } = await supabaseClient.auth.signInWithOAuth({
            provider: 'google',
            options: {
                redirectTo: window.location.origin
            }
        });

        if (error) {
            console.error('✗ OAuth error:', error.message);
            showLoginError(`Google login failed: ${error.message}`);
            googleBtn.innerHTML = originalText;
            googleBtn.disabled = false;
        } else {
            console.log('✓ OAuth initiated successfully');
            // Supabase handles the redirect
        }
    } catch (err) {
        console.error('✗ Unexpected error during Google login:', err);
        showLoginError('An unexpected error occurred during Google login.');
        googleBtn.innerHTML = originalText;
        googleBtn.disabled = false;
    }
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
        
        if (response.ok && (data.success || data.message === "Login successful")) {
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
