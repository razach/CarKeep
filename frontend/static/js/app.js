// Main application JavaScript
document.addEventListener('DOMContentLoaded', () => {
    console.log('CarKeep application loaded');
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize any existing notification cleanup
    cleanupOldNotifications();

    // Listen for htmx-driven toasts
    document.body.addEventListener('htmx:afterRequest', (evt) => {
        try {
            const trigger = evt?.detail?.xhr?.getResponseHeader('HX-Trigger');
            if (!trigger) return;
            const data = JSON.parse(trigger);
            if (data.toast) {
                const { type = 'info', message = '' } = data.toast;
                if (message) showNotification(message, type);
            }
        } catch (e) {
            // ignore parsing errors
        }
    });
});

// Scenario Management Functions
function duplicateScenario(scenarioName) {
    // TODO: Implement scenario duplication
    showNotification('Scenario duplication feature coming soon!', 'info');
}

function deleteScenario(scenarioName, description) {
    if (confirm(`Are you sure you want to delete "${description}"?\n\nThis action cannot be undone.`)) {
        // Show loading state
        const deleteBtn = event.target;
        const originalText = deleteBtn.innerHTML;
        deleteBtn.innerHTML = '🗑️ Deleting...';
        deleteBtn.disabled = true;
        
        console.log('Deleting scenario:', scenarioName);
        
        // Make delete request
        fetch(`/scenario/${scenarioName}/delete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => {
            console.log('Response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Response data:', data);
            if (data.success) {
                // Remove the scenario card from the UI
                const scenarioCard = document.querySelector(`[data-scenario="${scenarioName}"]`);
                if (scenarioCard) {
                    scenarioCard.style.opacity = '0';
                    scenarioCard.style.transform = 'translateY(-20px)';
                    setTimeout(() => {
                        scenarioCard.remove();
                        updateScenarioCounts();
                    }, 300);
                    console.log('Scenario card removed from UI');
                } else {
                    console.log('Scenario card not found in UI');
                }
                
                // Show success message
                showNotification('Scenario deleted successfully!', 'success');
                
                // Refresh the page to ensure UI is in sync
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                showNotification(data.message || 'Failed to delete scenario', 'error');
            }
        })
        .catch(error => {
            console.error('Error deleting scenario:', error);
            showNotification('An error occurred while deleting the scenario', 'error');
        })
        .finally(() => {
            // Reset button state
            deleteBtn.innerHTML = originalText;
            deleteBtn.disabled = false;
        });
    }
}

// UI Helper Functions
function updateScenarioCounts() {
    // Update the total scenarios count
    const scenarioCards = document.querySelectorAll('.scenario-card');
    const totalScenarios = document.querySelector('.stat-card .stat-number');
    if (totalScenarios) {
        totalScenarios.textContent = scenarioCards.length;
    }
    
    // Update lease/loan counts
    const leaseCount = document.querySelectorAll('.scenario-card .type.lease').length;
    const loanCount = document.querySelectorAll('.scenario-card .type.loan').length;
    
    const statNumbers = document.querySelectorAll('.stat-card .stat-number');
    if (statNumbers.length >= 3) {
        statNumbers[1].textContent = leaseCount;
        statNumbers[2].textContent = loanCount;
    }
}

function showNotification(message, type = 'info') {
    // Remove any existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" aria-label="Close notification">×</button>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}

function initializeTooltips() {
    // Enhanced tooltip handling for better accessibility
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
        element.addEventListener('focus', showTooltip);
        element.addEventListener('blur', hideTooltip);
    });
}

function showTooltip(event) {
    const element = event.target;
    const tooltipText = element.getAttribute('data-tooltip');
    
    if (!tooltipText) return;
    
    // Remove any existing tooltips
    hideTooltip();
    
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip-popup';
    tooltip.textContent = tooltipText;
    tooltip.id = 'active-tooltip';
    
    document.body.appendChild(tooltip);
    
    // Position the tooltip
    const rect = element.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();
    
    tooltip.style.left = `${rect.left + rect.width / 2 - tooltipRect.width / 2}px`;
    tooltip.style.top = `${rect.top - tooltipRect.height - 8}px`;
}

function hideTooltip() {
    const tooltip = document.getElementById('active-tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

function cleanupOldNotifications() {
    // Clean up any notifications that might have been left from previous page loads
    const oldNotifications = document.querySelectorAll('.notification');
    oldNotifications.forEach(notification => {
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 100);
    });
}

// Form Enhancement Functions (for future use)
function enhanceForm(formSelector) {
    const form = document.querySelector(formSelector);
    if (!form) return;
    
    // Add loading states to form submissions
    form.addEventListener('submit', function(event) {
        const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
        if (submitBtn) {
            const originalText = submitBtn.textContent || submitBtn.value;
            submitBtn.disabled = true;
            submitBtn.textContent = 'Processing...';
            
            // Reset after a delay if form doesn't redirect
            setTimeout(() => {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }, 5000);
        }
    });
}

// API Helper Functions (for future API migration)
class CarKeepAPI {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
    }
    
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        const response = await fetch(url, { ...defaultOptions, ...options });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return response.json();
    }
    
    async getScenarios() {
        return this.request('/api/scenarios');
    }
    
    async deleteScenario(scenarioName) {
        return this.request(`/api/scenarios/${scenarioName}`, {
            method: 'DELETE'
        });
    }
    
    async createScenario(scenarioData) {
        return this.request('/api/scenarios', {
            method: 'POST',
            body: JSON.stringify(scenarioData)
        });
    }
    
    async updateScenario(scenarioName, scenarioData) {
        return this.request(`/api/scenarios/${scenarioName}`, {
            method: 'PUT',
            body: JSON.stringify(scenarioData)
        });
    }
    
    // Add method to fetch comparison results
    async fetchComparisonResults() {
        try {
            const response = await this.request('/api/comparison-results');
            return response;
        } catch (error) {
            console.error('Error fetching comparison results:', error);
            throw error;
        }
    }
}

// Initialize API client for future use
const api = new CarKeepAPI();

// Fetch and render comparison results on page load
document.addEventListener('DOMContentLoaded', async () => {
    // If the server already rendered scenario rows, skip the client fetch to avoid overwriting
    const existingRows = document.querySelectorAll('.comparison-table tbody tr');
    if (existingRows && existingRows.length > 0) {
        console.debug('Server-rendered comparison rows detected; skipping client-side fetch.');
        return;
    }

    const api = new CarKeepAPI('http://127.0.0.1:5050');

    try {
        const comparisonResults = await api.fetchComparisonResults();
        renderComparisonResults(comparisonResults);
    } catch (error) {
        console.error('Failed to load comparison results:', error);
        showNotification('Failed to load comparison results. Please try again later.', 'error');
    }
});

// Update renderComparisonResults to safely access fields and use template-compatible values
function renderComparisonResults(results) {
    const comparisonTableBody = document.querySelector('.comparison-table tbody');

    if (!comparisonTableBody) {
        console.error('Comparison table body not found in the DOM.');
        return;
    }

    if (!results || Object.keys(results).length === 0) {
        comparisonTableBody.innerHTML = '<tr><td colspan="6">No comparison data available.</td></tr>';
        return;
    }

    let html = '';
    for (const [key, scenario] of Object.entries(results)) {
        // Prefer server-style structured values when available
        const vehicleName = (scenario.scenario && scenario.scenario.vehicle && scenario.scenario.vehicle.name) || (scenario.results && scenario.results.summary && scenario.results.summary.data && scenario.results.summary.data[0] && scenario.results.summary.data[0][1]) || '';
        const msrp = (scenario.scenario && scenario.scenario.vehicle && scenario.scenario.vehicle.msrp) || '';
        const monthlyPayment = (scenario.scenario && scenario.scenario.financing && scenario.scenario.financing.monthly_payment) || (scenario.results && scenario.results.monthly_payment && scenario.results.monthly_payment.data && scenario.results.monthly_payment.data[0] && scenario.results.monthly_payment.data[0][1]) || '';
        const state = scenario.state || 'VA';
        const description = scenario.description || key;

        html += `<tr>
            <td>
                <strong>${description}</strong>
                <small class="scenario-name">${key}</small>
            </td>
            <td>${vehicleName}</td>
            <td>${msrp ? '$' + Number(msrp).toLocaleString() : ''}</td>
            <td>${monthlyPayment}</td>
            <td>${state}</td>
            <td>
                <a href="/scenario/${key}" class="btn btn-sm btn-outline">View</a>
                <a href="/scenario/${key}/edit" class="btn btn-sm btn-warning">Edit</a>
            </td>
        </tr>`;
    }

    comparisonTableBody.innerHTML = html;
}