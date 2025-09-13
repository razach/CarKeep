// CarKeep Web Application - Simplified JavaScript

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('CarKeep Web App Initialized');
    addEventListeners();
});

// Add event listeners for interactive elements
function addEventListeners() {
    // Scenario card interactions
    const scenarioCards = document.querySelectorAll('.scenario-card');
    scenarioCards.forEach(card => {
        card.addEventListener('click', function(e) {
            if (!e.target.closest('.scenario-actions')) {
                // Simple click effect
                this.style.transform = 'scale(0.98)';
                setTimeout(() => {
                    this.style.transform = '';
                }, 150);
            }
        });
    });
    
    // Button interactions
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
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

// Add loading state to buttons
function addLoadingState(button) {
    const originalText = button.textContent;
    button.textContent = 'Loading...';
    button.disabled = true;
    
    setTimeout(() => {
        button.textContent = originalText;
        button.disabled = false;
    }, 2000);
}

// Handle form submissions
function handleFormSubmit(event) {
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    
    // If it's the edit form
    if (form.id === 'editForm') {
        event.preventDefault();
        
        // Add loading state
        if (submitButton) {
            addLoadingState(submitButton);
        }
        
        // Get form data
        const formData = new FormData(form);
        const data = {};
        for (let [key, value] of formData.entries()) {
            // Convert numeric strings to numbers
            if (!isNaN(value) && value !== '') {
                data[key] = parseFloat(value);
            } else {
                data[key] = value;
            }
        }
        
        // Send POST request
        fetch(form.action, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                // Redirect after successful update
                setTimeout(() => {
                    window.location.href = `/scenario/${data.scenario_name}`;
                }, 1500);
            } else {
                showNotification(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('An error occurred while saving changes', 'error');
        })
        .finally(() => {
            if (submitButton) {
                submitButton.textContent = 'Save Changes';
                submitButton.disabled = false;
            }
        });
    } else {
        // For other forms, add loading state only
        if (submitButton) {
            addLoadingState(submitButton);
        }
    }
}

// Enhanced scenario management functions
function editScenario(scenarioName) {
    showNotification(`Editing scenario: ${scenarioName}`, 'info');
}

function deleteScenario(scenarioName) {
    if (confirm(`Are you sure you want to delete the scenario "${scenarioName}"?`)) {
        showNotification(`Deleting scenario: ${scenarioName}`, 'warning');
    }
}

function duplicateScenario(scenarioName) {
    showNotification(`Duplicating scenario: ${scenarioName}`, 'info');
}

// Show notifications
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Remove notification after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
        padding: 12px 24px;
        background-color: white;
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    `;
    
    // Add color based on type
    switch(type) {
        case 'success':
            notification.style.borderLeft = '4px solid #28a745';
            break;
        case 'error':
            notification.style.borderLeft = '4px solid #dc3545';
            break;
        case 'warning':
            notification.style.borderLeft = '4px solid #ffc107';
            break;
        default:
            notification.style.borderLeft = '4px solid #17a2b8';
    }
    
    document.body.appendChild(notification);
    
    // Remove notification after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}
        padding: 1rem 1.5rem;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        z-index: 10000;
        animation: slideIn 0.3s ease;
        max-width: 300px;
    `;
    
    // Set background color based on type
    switch(type) {
        case 'success':
            notification.style.background = '#27ae60';
            break;
        case 'warning':
            notification.style.background = '#f39c12';
            break;
        case 'error':
            notification.style.background = '#e74c3c';
            break;
        default:
            notification.style.background = '#3498db';
    }
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add CSS for notifications
function addDynamicStyles() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
        
        .active {
            background-color: rgba(255,255,255,0.3) !important;
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
    showNotification
};
