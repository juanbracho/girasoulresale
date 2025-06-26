/* Girasoul Business Dashboard - Main JavaScript */
/* Global utilities and base functionality */

// =============================================================================
// GLOBAL NAMESPACE AND UTILITIES
// =============================================================================

window.BusinessApp = window.BusinessApp || {};

/**
 * Global utility functions for the business dashboard
 */
window.BusinessUtils = {
    /**
     * Format number as currency
     * @param {number} amount - Amount to format
     * @param {string} currency - Currency symbol (default: '$')
     * @returns {string} Formatted currency string
     */
    formatCurrency(amount, currency = '$') {
        try {
            const number = parseFloat(amount) || 0;
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD',
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }).format(number);
        } catch (error) {
            return `${currency}${parseFloat(amount || 0).toFixed(2)}`;
        }
    },

    /**
     * Format date to readable string
     * @param {string|Date} dateInput - Date to format
     * @param {string} format - Format type ('short', 'long', 'medium')
     * @returns {string} Formatted date string
     */
    formatDate(dateInput, format = 'medium') {
        try {
            const date = new Date(dateInput);
            if (isNaN(date.getTime())) return 'Invalid Date';

            const options = {
                short: { year: 'numeric', month: 'short', day: 'numeric' },
                medium: { year: 'numeric', month: 'short', day: 'numeric' },
                long: { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }
            };

            return date.toLocaleDateString('en-US', options[format] || options.medium);
        } catch (error) {
            return 'Invalid Date';
        }
    },

    /**
     * Format percentage with proper symbol
     * @param {number} value - Percentage value
     * @param {number} decimals - Number of decimal places
     * @returns {string} Formatted percentage
     */
    formatPercentage(value, decimals = 2) {
        const number = parseFloat(value) || 0;
        return `${number.toFixed(decimals)}%`;
    },

    /**
     * Show alert message to user
     * @param {string} message - Message to display
     * @param {string} type - Alert type ('success', 'danger', 'warning', 'info')
     * @param {number} duration - Auto-dismiss duration in ms (default: 5000)
     */
    showAlert(message, type = 'info', duration = 5000) {
        // Remove existing alerts of the same type
        const existingAlerts = document.querySelectorAll(`.alert.alert-${type}`);
        existingAlerts.forEach(alert => alert.remove());

        // Create new alert
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        // Insert at top of container
        const container = document.querySelector('.container');
        if (container) {
            container.insertBefore(alertDiv, container.firstChild);

            // Auto-dismiss
            if (duration > 0) {
                setTimeout(() => {
                    if (alertDiv.parentNode) {
                        alertDiv.remove();
                    }
                }, duration);
            }
        }
    },

    /**
     * Validate form fields
     * @param {string} formId - ID of form to validate
     * @returns {boolean} True if form is valid
     */
    validateForm(formId) {
        const form = document.getElementById(formId);
        if (!form) return false;

        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            const value = field.value.trim();
            
            if (!value) {
                field.classList.add('is-invalid');
                field.classList.remove('is-valid');
                isValid = false;
            } else {
                field.classList.remove('is-invalid');
                field.classList.add('is-valid');
            }
        });

        return isValid;
    },

    /**
     * Set loading state for an element
     * @param {string} elementId - ID of element
     * @param {boolean} isLoading - Loading state
     * @param {string} loadingText - Text to show while loading
     */
    setLoadingState(elementId, isLoading, loadingText = 'Loading...') {
        const element = document.getElementById(elementId);
        if (!element) return;

        if (isLoading) {
            element.dataset.originalContent = element.innerHTML;
            element.innerHTML = `
                <div class="d-flex justify-content-center align-items-center py-4">
                    <div class="spinner-border text-primary me-2" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <span>${loadingText}</span>
                </div>
            `;
        } else {
            if (element.dataset.originalContent) {
                element.innerHTML = element.dataset.originalContent;
                delete element.dataset.originalContent;
            }
        }
    },

    /**
     * Debounce function calls - FIXED: renamed timeout variable to avoid conflicts
     * @param {Function} func - Function to debounce
     * @param {number} wait - Wait time in milliseconds
     * @returns {Function} Debounced function
     */
    debounce(func, wait) {
        let timeoutId; // Changed from 'timeout' to 'timeoutId'
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeoutId);
                func.apply(this, args);
            };
            clearTimeout(timeoutId);
            timeoutId = setTimeout(later, wait);
        };
    },

    /**
     * Make API calls with improved error handling
     * @param {string} url - API endpoint
     * @param {Object} options - Fetch options
     * @returns {Promise} Response data
     */
    async apiCall(url, options = {}) {
        try {
            console.log(`🌐 API Call: ${options.method || 'GET'} ${url}`);
            
            const defaultOptions = {
                headers: {
                    'Content-Type': 'application/json',
                },
                ...options
            };

            const response = await fetch(url, defaultOptions);
            
            console.log(`📡 API Response: ${response.status} ${response.statusText}`);
            
            if (!response.ok) {
                // Try to get error message from response
                let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
                try {
                    const errorData = await response.json();
                    if (errorData.error) {
                        errorMessage = errorData.error;
                    }
                } catch (e) {
                    // If can't parse JSON, use default message
                }
                throw new Error(errorMessage);
            }

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const data = await response.json();
                console.log(`✅ API Success:`, data);
                return data;
            } else {
                return await response.text();
            }
        } catch (error) {
            console.error(`❌ API Error: ${options.method || 'GET'} ${url}`, error);
            throw error;
        }
    },

    /**
     * Safe HTML escaping to prevent XSS
     * @param {string} unsafe - Unsafe string
     * @returns {string} Escaped string
     */
    escapeHtml(unsafe) {
        if (!unsafe) return '';
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    },

    /**
     * Get query parameters from URL
     * @returns {Object} Query parameters as key-value pairs
     */
    getQueryParams() {
        const params = new URLSearchParams(window.location.search);
        const result = {};
        for (const [key, value] of params) {
            result[key] = value;
        }
        return result;
    }
};

// =============================================================================
// GLOBAL EVENT HANDLERS
// =============================================================================

/**
 * Settings menu functions (called from navigation dropdown)
 */
window.exportData = function() {
    BusinessUtils.showAlert('Export functionality will be implemented in a future update', 'info');
};

window.backupDatabase = function() {
    BusinessUtils.showAlert('Database backup functionality will be implemented in a future update', 'info');
};

window.showAbout = function() {
    const aboutText = `
        <strong>Girasoul Business Dashboard v1.0</strong><br>
        Standalone Business Management System<br>
        Built with Flask & Bootstrap<br><br>
        <small>© 2025 Girasoul Business Solutions</small>
    `;
    
    // Create modal for about info
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">About Girasoul Business Dashboard</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body text-center">
                    ${aboutText}
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-primary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    // Remove modal when hidden
    modal.addEventListener('hidden.bs.modal', () => {
        modal.remove();
    });
};

// =============================================================================
// INITIALIZATION AND EVENT LISTENERS
// =============================================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('💼 Girasoul Business Dashboard - Main JS loaded');

    // Initialize tooltips
    initializeTooltips();

    // Initialize form enhancements
    initializeFormEnhancements();

    // Initialize global keyboard shortcuts
    initializeKeyboardShortcuts();

    // Initialize loading states
    initializeLoadingStates();

    console.log('✅ Main JavaScript initialization complete');
});

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    try {
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
            console.log('✅ Tooltips initialized');
        }
    } catch (error) {
        console.warn('⚠️ Tooltip initialization failed:', error);
    }
}

/**
 * Initialize form enhancements
 */
function initializeFormEnhancements() {
    // Auto-format currency inputs
    const currencyInputs = document.querySelectorAll('input[type="number"][step="0.01"]');
    currencyInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value) {
                const value = parseFloat(this.value);
                if (!isNaN(value)) {
                    this.value = value.toFixed(2);
                }
            }
        });
    });

    // Set today's date for date inputs that are empty
    const dateInputs = document.querySelectorAll('input[type="date"]');
    const today = new Date().toISOString().split('T')[0];
    dateInputs.forEach(input => {
        if (!input.value && input.classList.contains('auto-today')) {
            input.value = today;
        }
    });

    // Add real-time validation feedback
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateSingleField(this);
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    validateSingleField(this);
                }
            });
        });
    });

    console.log('✅ Form enhancements initialized');
}

/**
 * Validate a single form field
 * @param {HTMLElement} field - Form field to validate
 */
function validateSingleField(field) {
    const value = field.value.trim();
    const isRequired = field.hasAttribute('required');
    
    if (isRequired && !value) {
        field.classList.add('is-invalid');
        field.classList.remove('is-valid');
    } else if (value) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
    } else {
        field.classList.remove('is-invalid', 'is-valid');
    }
}

/**
 * Initialize keyboard shortcuts
 */
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + S to save (prevent browser save dialog)
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            const saveButton = document.querySelector('.btn[onclick*="save"], .btn[type="submit"]');
            if (saveButton && !saveButton.disabled) {
                saveButton.click();
            }
        }

        // Escape to close modals
        if (e.key === 'Escape') {
            const openModals = document.querySelectorAll('.modal.show');
            openModals.forEach(modal => {
                if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                    const bsModal = bootstrap.Modal.getInstance(modal);
                    if (bsModal) {
                        bsModal.hide();
                    }
                }
            });
        }

        // Ctrl/Cmd + N for new item (if add button exists)
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            const addButton = document.querySelector('.btn[onclick*="Add"], .btn[onclick*="showAdd"]');
            if (addButton) {
                addButton.click();
            }
        }
    });

    console.log('✅ Keyboard shortcuts initialized');
}

/**
 * Initialize loading states and error handling
 */
function initializeLoadingStates() {
    // Add loading states to all forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButton = this.querySelector('button[type="submit"], input[type="submit"]');
            if (submitButton && !submitButton.disabled) {
                const originalText = submitButton.textContent;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Saving...';
                submitButton.disabled = true;

                // Re-enable after 10 seconds as fallback
                setTimeout(() => {
                    if (submitButton.disabled) {
                        submitButton.textContent = originalText;
                        submitButton.disabled = false;
                    }
                }, 10000);
            }
        });
    });

    // Add loading states to AJAX buttons
    const ajaxButtons = document.querySelectorAll('.btn[data-ajax="true"]');
    ajaxButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (!this.disabled) {
                const originalText = this.textContent;
                this.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
                this.disabled = true;

                // Store original text for restoration
                this.dataset.originalText = originalText;
            }
        });
    });

    console.log('✅ Loading states initialized');
}

// =============================================================================
// GLOBAL HELPER FUNCTIONS
// =============================================================================

/**
 * Restore button state after AJAX call - FIXED: improved safety
 * @param {HTMLElement} button - Button to restore
 * @param {string} newText - Optional new text for button
 */
window.restoreButtonState = function(button, newText = null) {
    if (button && button.disabled) {
        const originalText = newText || button.dataset.originalText || 'Submit';
        button.textContent = originalText;
        button.disabled = false;
        delete button.dataset.originalText;
    }
};

/**
 * Safe setTimeout wrapper to prevent undefined errors
 * @param {Function} callback - Callback function
 * @param {number} delay - Delay in milliseconds
 * @returns {number} Timeout ID
 */
window.safeSetTimeout = function(callback, delay) {
    if (typeof callback === 'function' && typeof delay === 'number') {
        return setTimeout(callback, delay);
    }
    console.warn('⚠️ Invalid setTimeout parameters:', callback, delay);
    return null;
};

/**
 * Confirm dialog with custom styling
 * @param {string} message - Confirmation message
 * @param {string} title - Dialog title
 * @returns {Promise<boolean>} User confirmation
 */
window.confirmDialog = function(message, title = 'Confirm Action') {
    return new Promise((resolve) => {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${BusinessUtils.escapeHtml(title)}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>${BusinessUtils.escapeHtml(message)}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-danger" id="confirmButton">Confirm</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const bsModal = new bootstrap.Modal(modal);
            
            modal.querySelector('#confirmButton').addEventListener('click', () => {
                bsModal.hide();
                resolve(true);
            });
            
            modal.addEventListener('hidden.bs.modal', () => {
                modal.remove();
                resolve(false);
            });
            
            bsModal.show();
        } else {
            // Fallback if Bootstrap is not available
            const confirmed = confirm(message);
            modal.remove();
            resolve(confirmed);
        }
    });
};

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>} Success status
 */
window.copyToClipboard = async function(text) {
    try {
        await navigator.clipboard.writeText(text);
        BusinessUtils.showAlert('Copied to clipboard!', 'success', 2000);
        return true;
    } catch (error) {
        console.error('Failed to copy text:', error);
        BusinessUtils.showAlert('Failed to copy to clipboard', 'danger', 3000);
        return false;
    }
};

/**
 * Download data as file
 * @param {string} data - Data to download
 * @param {string} filename - Filename
 * @param {string} type - MIME type
 */
window.downloadFile = function(data, filename, type = 'text/plain') {
    const blob = new Blob([data], { type });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
};

/**
 * Format number with thousand separators
 * @param {number} num - Number to format
 * @returns {string} Formatted number
 */
window.formatNumber = function(num) {
    return new Intl.NumberFormat('en-US').format(num);
};

/**
 * Calculate percentage change
 * @param {number} oldValue - Original value
 * @param {number} newValue - New value
 * @returns {number} Percentage change
 */
window.calculatePercentageChange = function(oldValue, newValue) {
    if (oldValue === 0) return newValue === 0 ? 0 : 100;
    return ((newValue - oldValue) / oldValue) * 100;
};

/**
 * Scroll to element smoothly
 * @param {string} elementId - ID of element to scroll to
 * @param {number} offset - Offset from top (default: 100px for navbar)
 */
window.scrollToElement = function(elementId, offset = 100) {
    const element = document.getElementById(elementId);
    if (element) {
        const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
        const offsetPosition = elementPosition - offset;
        
        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });
    }
};

// =============================================================================
// ERROR HANDLING AND DEBUGGING
// =============================================================================

// Global error handler for unhandled promises
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    BusinessUtils.showAlert('An unexpected error occurred. Please try again.', 'danger');
});

// Global error handler for JavaScript errors
window.addEventListener('error', function(event) {
    console.error('JavaScript error:', event.error);
    
    // Don't show error messages in production for security
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        BusinessUtils.showAlert(`JavaScript Error: ${event.message}`, 'danger');
    }
});

// Console welcome message
console.log(`
🌻 Girasoul Business Dashboard
==========================================
Version: 1.0.0
Environment: ${window.location.hostname === 'localhost' ? 'Development' : 'Production'}
Loaded at: ${new Date().toLocaleString()}
==========================================

Available utilities:
- BusinessUtils.* - General utilities
- confirmDialog() - Custom confirmation dialogs
- copyToClipboard() - Clipboard operations
- downloadFile() - File downloads
- restoreButtonState() - UI state management

For help, visit: https://github.com/your-repo/girasoul-business
`);

// Export BusinessUtils globally for other modules
window.BusinessUtils = BusinessUtils;