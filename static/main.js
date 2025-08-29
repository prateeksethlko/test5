// Professional JavaScript for Zurich Assistant

// DOM Elements
const hamburgerToggle = document.getElementById('hamburgerToggle');
const hamburgerMenu = document.getElementById('hamburgerMenu');
const closeHamburger = document.getElementById('closeHamburger');
const chatWindow = document.getElementById('chat-window');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const chatError = document.getElementById('chat-error');
const sendButton = document.getElementById('send-button');

// Chat state
let chatHistory = [];
let isLoading = false;

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeHamburgerMenu();
    initializeDropdowns();
    initializeChat();
    chatInput.focus();
});

// Hamburger menu functionality
function initializeHamburgerMenu() {
    // Open hamburger menu
    hamburgerToggle.addEventListener('click', function() {
        hamburgerMenu.classList.add('open');
        document.body.style.overflow = 'hidden'; // Prevent background scroll
    });

    // Close hamburger menu
    closeHamburger.addEventListener('click', function() {
        hamburgerMenu.classList.remove('open');
        document.body.style.overflow = 'auto';
    });

    // Close on outside click
    hamburgerMenu.addEventListener('click', function(e) {
        if (e.target === hamburgerMenu) {
            hamburgerMenu.classList.remove('open');
            document.body.style.overflow = 'auto';
        }
    });

    // Close on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && hamburgerMenu.classList.contains('open')) {
            hamburgerMenu.classList.remove('open');
            document.body.style.overflow = 'auto';
        }
    });
}

// Dropdown functionality
function initializeDropdowns() {
    const dropdownButtons = document.querySelectorAll('.dropdown-btn');
    
    dropdownButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            
            const dropdownContent = button.nextElementSibling;
            const isOpen = dropdownContent.classList.contains('show');
            
            // Close all dropdowns
            document.querySelectorAll('.dropdown-content.show').forEach(content => {
                content.classList.remove('show');
            });
            
            // Toggle current dropdown
            if (!isOpen) {
                dropdownContent.classList.add('show');
            }
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown-content.show').forEach(content => {
                content.classList.remove('show');
            });
        }
    });
}

// Chat functionality
function initializeChat() {
    chatForm.addEventListener('submit', handleChatSubmit);
    
    // Auto-resize input
    chatInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });

    // Enter to send, Shift+Enter for new line
    chatInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!isLoading) {
                chatForm.dispatchEvent(new Event('submit'));
            }
        }
    });
}

async function handleChatSubmit(e) {
    e.preventDefault();
    
    const message = chatInput.value.trim();
    if (!message || isLoading) return;

    // Clear error and input
    clearError();
    chatInput.value = '';
    chatInput.style.height = 'auto';

    // Add user message
    appendMessage('user', message);
    chatHistory.push({ role: 'user', content: message });

    // Show loading state
    setLoadingState(true);

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ messages: chatHistory }),
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        const assistantMessage = data.choices?.[0]?.message?.content || 'I apologize, but I did not receive a proper response. Please try again.';

        // Add assistant response
        appendMessage('assistant', assistantMessage);
        chatHistory.push({ role: 'assistant', content: assistantMessage });

    } catch (error) {
        console.error('Chat error:', error);
        showError(`Unable to send message: ${error.message}. Please check your connection and try again.`);
        
        // Remove the user message from history on error
        chatHistory.pop();
    } finally {
        setLoadingState(false);
        chatInput.focus();
    }
}

function appendMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${role}`;
    
    // Create role header
    const roleDiv = document.createElement('div');
    roleDiv.className = role === 'user' ? 'chat-user' : 'chat-ai';
    roleDiv.textContent = role === 'user' ? 'You' : 'Assistant';
    
    // Create content
    const contentDiv = document.createElement('div');
    contentDiv.className = 'chat-content';
    contentDiv.textContent = content;
    
    messageDiv.appendChild(roleDiv);
    messageDiv.appendChild(contentDiv);
    
    // Add with animation
    messageDiv.style.opacity = '0';
    messageDiv.style.transform = 'translateY(20px)';
    chatWindow.appendChild(messageDiv);
    
    // Trigger animation
    requestAnimationFrame(() => {
        messageDiv.style.transition = 'all 0.3s ease';
        messageDiv.style.opacity = '1';
        messageDiv.style.transform = 'translateY(0)';
    });
    
    // Scroll to bottom
    chatWindow.scrollTo({
        top: chatWindow.scrollHeight,
        behavior: 'smooth'
    });
}

function setLoadingState(loading) {
    isLoading = loading;
    sendButton.disabled = loading;
    chatInput.disabled = loading;
    
    if (loading) {
        sendButton.textContent = 'Sending...';
        chatInput.placeholder = 'Sending message...';
    } else {
        sendButton.textContent = 'Send';
        chatInput.placeholder = 'Ask me about Informatica access, repositories, or myAccess groups...';
    }
}

function showError(message) {
    chatError.textContent = message;
    chatError.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(clearError, 5000);
}

function clearError() {
    chatError.textContent = '';
    chatError.style.display = 'none';
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
