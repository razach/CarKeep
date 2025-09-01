// CarKeep Web Application - Enhanced JavaScript

// Global state
let currentTheme = 'light';
let animationsEnabled = true;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    addEventListeners();
    enableAnimations();
});

// Initialize the application
function initializeApp() {
    console.log('CarKeep Web App Initialized');
    
    // Add fade-in animations to cards
    animateCards();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Add loading states
    addLoadingStates();
}

// Add event listeners for interactive elements
function addEventListeners() {
    // Scenario card interactions
    const scenarioCards = document.querySelectorAll('.scenario-card');
    scenarioCards.forEach(card => {
        card.addEventListener('click', function(e) {
            if (!e.target.closest('.scenario-actions')) {
                // Add click effect
                this.style.transform = 'scale(0.98)';
                setTimeout(() => {
                    this.style.transform = '';
                }, 150);
            }
        });
        
        // Add hover sound effect (optional)
        card.addEventListener('mouseenter', function() {
            this.style.zIndex = '10';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.zIndex = '1';
        });
    });
    
    // Button interactions
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Add ripple effect
            createRipple(e, this);
            
            // Add loading state for action buttons
            if (this.classList.contains('btn-primary') || this.classList.contains('btn-success')) {
                addLoadingState(this);
            }
        });
    });
    
    // Form interactions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
    
    // Navigation interactions
    const navLinks = document.querySelectorAll('.nav-menu a');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            // Add active state
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

// Animate scenario cards with staggered entrance
function animateCards() {
    const cards = document.querySelectorAll('.scenario-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// Create ripple effect on button clicks
function createRipple(event, button) {
    const ripple = document.createElement('span');
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.classList.add('ripple');
    
    button.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

// Add loading state to buttons
function addLoadingState(button) {
    const originalText = button.textContent;
    button.textContent = 'Loading...';
    button.classList.add('loading');
    button.disabled = true;
    
    // Simulate loading (replace with actual async operation)
    setTimeout(() => {
        button.textContent = originalText;
        button.classList.remove('loading');
        button.disabled = false;
    }, 2000);
}

// Handle form submissions
function handleFormSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    
    // Add loading state
    submitButton.textContent = 'Creating...';
    submitButton.disabled = true;
    
    // Simulate form processing
    setTimeout(() => {
        showNotification('Scenario created successfully!', 'success');
        submitButton.textContent = 'Create Scenario';
        submitButton.disabled = false;
        form.reset();
    }, 1500);
}

// Show notification messages
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        z-index: 10000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    `;
    
    // Set background color based on type
    const colors = {
        success: '#27ae60',
        error: '#e74c3c',
        warning: '#f39c12',
        info: '#3498db'
    };
    
    notification.style.backgroundColor = colors[type] || colors.info;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Initialize tooltips
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

// Show tooltip
function showTooltip(event) {
    const element = event.target;
    const tooltipText = element.getAttribute('data-tooltip');
    
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = tooltipText;
    tooltip.style.cssText = `
        position: absolute;
        background: #2c3e50;
        color: white;
        padding: 0.5rem 0.75rem;
        border-radius: 6px;
        font-size: 0.8rem;
        z-index: 1000;
        pointer-events: none;
        white-space: nowrap;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    `;
    
    document.body.appendChild(tooltip);
    
    // Position tooltip
    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
    
    element.tooltip = tooltip;
}

// Hide tooltip
function hideTooltip(event) {
    const element = event.target;
    if (element.tooltip) {
        element.tooltip.remove();
        element.tooltip = null;
    }
}

// Enable/disable animations
function enableAnimations() {
    if (!animationsEnabled) {
        document.body.classList.add('no-animations');
    }
}

// Toggle theme (for future dark mode support)
function toggleTheme() {
    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.body.setAttribute('data-theme', currentTheme);
    localStorage.setItem('theme', currentTheme);
}

// Enhanced scenario management functions
function editScenario(scenarioName) {
    showNotification(`Editing scenario: ${scenarioName}`, 'info');
    // TODO: Implement edit functionality
}

function deleteScenario(scenarioName) {
    if (confirm(`Are you sure you want to delete the scenario "${scenarioName}"?`)) {
        showNotification(`Deleting scenario: ${scenarioName}`, 'warning');
        // TODO: Implement delete functionality
    }
}

function duplicateScenario(scenarioName) {
    showNotification(`Duplicating scenario: ${scenarioName}`, 'info');
    // TODO: Implement duplicate functionality
}

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatNumber(number) {
    return new Intl.NumberFormat('en-US').format(number);
}

// Add CSS for new interactive elements
function addDynamicStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .ripple {
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.6);
            transform: scale(0);
            animation: ripple-animation 0.6s linear;
            pointer-events: none;
        }
        
        @keyframes ripple-animation {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        
        .notification {
            animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
            from { transform: translateX(100%); }
            to { transform: translateX(0); }
        }
        
        .tooltip {
            animation: fadeIn 0.2s ease;
        }
        
        .no-animations * {
            animation: none !important;
            transition: none !important;
        }
        
        .active {
            background-color: rgba(255,255,255,0.3) !important;
            transform: scale(1.05);
        }
    `;
    document.head.appendChild(style);
}

// Initialize dynamic styles
addDynamicStyles();

// Export functions for global access
window.CarKeep = {
    editScenario,
    deleteScenario,
    duplicateScenario,
    showNotification,
    toggleTheme,
    formatCurrency,
    formatNumber
};
