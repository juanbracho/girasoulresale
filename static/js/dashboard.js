/**
 * Dashboard JavaScript - Complete File
 * Handles expense transaction management and dashboard functionality
 * Updated to remove income functionality and focus on expense-only workflow
 */

// Global variables
let dashboardCharts = {};

/**
 * Initialize dashboard functionality
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('📊 Dashboard initializing...');
    
    try {
        // Initialize core functionality
        initializeTransactionForm();
        initializeDateInputs();
        initializeBusinessUtils();
        
        // Initialize charts if data is available
        initializeDashboardCharts();
        
        // Set up periodic data refresh
        setupDataRefresh();
        
        console.log('✅ Dashboard initialized successfully');
        
    } catch (error) {
        console.error('❌ Error initializing dashboard:', error);
        showAlert('Dashboard initialization error. Please refresh the page.', 'warning');
    }
});

/**
 * Initialize business utilities for consistent UX
 */
function initializeBusinessUtils() {
    // Create global BusinessUtils if it doesn't exist
    if (typeof window.BusinessUtils === 'undefined') {
        window.BusinessUtils = {
            showAlert: function(message, type = 'info') {
                showAlert(message, type);
            },
            
            formatCurrency: function(amount) {
                return new Intl.NumberFormat('en-US', {
                    style: 'currency',
                    currency: 'USD'
                }).format(amount || 0);
            },
            
            formatDate: function(dateString) {
                if (!dateString) return '';
                const date = new Date(dateString);
                return date.toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric'
                });
            }
        };
    }
}

/**
 * Show alert messages to user
 */
function showAlert(message, type = 'info') {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.dashboard-alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show dashboard-alert`;
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.style.minWidth = '300px';
    
    const iconMap = {
        'success': 'fas fa-check-circle',
        'danger': 'fas fa-exclamation-circle',
        'warning': 'fas fa-exclamation-triangle',
        'info': 'fas fa-info-circle'
    };
    
    alertDiv.innerHTML = `
        <i class="${iconMap[type] || iconMap.info} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv && alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

/**
 * Initialize date inputs with today's date
 */
function initializeDateInputs() {
    const today = new Date().toISOString().split('T')[0];
    const dateInputs = document.querySelectorAll('.auto-today');
    
    dateInputs.forEach(input => {
        if (!input.value) {
            input.value = today;
        }
    });
}

/**
 * Set today's date in specific elements
 */
function setTodaysDate() {
    const today = new Date().toISOString().split('T')[0];
    const transactionDate = document.getElementById('transactionDate');
    
    if (transactionDate && !transactionDate.value) {
        transactionDate.value = today;
    }
}

/**
 * Initialize transaction form functionality
 */
function initializeTransactionForm() {
    const form = document.getElementById('transactionForm');
    if (!form) return;
    
    console.log('📝 Initializing transaction form...');
    
    // Set up category change handler
    const categorySelect = document.getElementById('transactionCategory');
    if (categorySelect) {
        categorySelect.addEventListener('change', function() {
            populateSubCategories(this.value);
        });
    }
    
    // Set up amount formatting
    const amountInput = document.getElementById('transactionAmount');
    if (amountInput) {
        amountInput.addEventListener('input', function() {
            // Remove any non-numeric characters except decimal point
            this.value = this.value.replace(/[^0-9.]/g, '');
            
            // Ensure only one decimal point
            const parts = this.value.split('.');
            if (parts.length > 2) {
                this.value = parts[0] + '.' + parts.slice(1).join('');
            }
        });
        
        amountInput.addEventListener('blur', function() {
            if (this.value) {
                const value = parseFloat(this.value);
                if (!isNaN(value) && value > 0) {
                    this.value = value.toFixed(2);
                }
            }
        });
    }
    
    // Set up form validation
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        saveTransaction();
    });
    
    console.log('✅ Transaction form initialized');
}

/**
 * Show transaction modal for adding expense (primary function)
 */
window.showAddExpenseModal = function() {
    console.log('💰 Opening add expense modal');
    showTransactionModal('Expense');
};

/**
 * Show transaction modal with specified type
 * @param {string} type - Transaction type (now only 'Expense')
 */
function showTransactionModal(type = 'Expense') {
    console.log(`💰 Opening add ${type.toLowerCase()} modal`);
    
    const modal = document.getElementById('transactionModal');
    const modalTitle = document.getElementById('transactionModalLabel');
    const saveText = document.getElementById('saveTransactionText');
    const typeInput = document.getElementById('transactionType');
    const form = document.getElementById('transactionForm');
    
    if (!modal) {
        console.error('❌ Transaction modal not found');
        showAlert('Transaction form is not available', 'danger');
        return;
    }
    
    try {
        // Reset form
        if (form) {
            form.reset();
        }
        
        // Set transaction type to Expense
        if (typeInput) typeInput.value = 'Expense';
        
        // Update modal title and button
        if (modalTitle) modalTitle.textContent = `Add Business ${type}`;
        if (saveText) saveText.textContent = `Save ${type}`;
        
        // Set today's date
        setTodaysDate();
        
        // Populate categories for expense type
        populateCategoriesByType('Expense');
        
        // Show modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        // Focus on description field after modal is shown
        modal.addEventListener('shown.bs.modal', function() {
            const descriptionInput = document.getElementById('transactionDescription');
            if (descriptionInput) {
                setTimeout(() => descriptionInput.focus(), 100);
            }
        }, { once: true });
        
    } catch (error) {
        console.error('❌ Error opening transaction modal:', error);
        showAlert('Error opening transaction form', 'danger');
    }
}

/**
 * Populate category dropdown for expense transactions
 * @param {string} type - Transaction type (now only 'Expense')
 */
function populateCategoriesByType(type) {
    const categorySelect = document.getElementById('transactionCategory');
    if (!categorySelect) return;
    
    // Clear existing options except the first one
    const firstOption = categorySelect.firstElementChild;
    categorySelect.innerHTML = '';
    if (firstOption) {
        categorySelect.appendChild(firstOption);
    }
    
    // Expense categories for fashion business
    const expenseCategories = [
        'Cost of Goods Sold',
        'Operations', 
        'Marketing',
        'Administrative',
        'Technology',
        'Travel',
        'Professional Services',
        'Equipment',
        'Utilities',
        'Office Expenses',
        'Insurance',
        'Other'
    ];
    
    expenseCategories.forEach(category => {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = category;
        categorySelect.appendChild(option);
    });
}

/**
 * Populate subcategories based on main category selection
 * @param {string} category - Selected main category
 */
function populateSubCategories(category) {
    const subCategorySelect = document.getElementById('transactionSubCategory');
    if (!subCategorySelect) return;
    
    // Clear existing subcategories
    subCategorySelect.innerHTML = '<option value="">Select Subcategory</option>';
    
    const subcategoryMap = {
        'Cost of Goods Sold': [
            'Inventory Purchase',
            'Product Materials',
            'Shipping & Fulfillment',
            'Packaging Materials',
            'Product Photography',
            'Alterations & Repairs'
        ],
        'Operations': [
            'Venue Rental',
            'Market Fees',
            'Storage',
            'Equipment Rental',
            'Pop-up Shop Costs',
            'Event Fees'
        ],
        'Marketing': [
            'Social Media Ads',
            'Photography',
            'Website & E-commerce',
            'Print Materials',
            'Influencer Collaborations',
            'Content Creation',
            'Brand Development'
        ],
        'Administrative': [
            'Banking Fees',
            'Legal & Professional',
            'Office Supplies',
            'Software Subscriptions',
            'Accounting Services',
            'Business Registration'
        ],
        'Technology': [
            'POS System',
            'Website Hosting',
            'Software Licenses',
            'Equipment Purchase',
            'App Subscriptions',
            'Tech Support'
        ],
        'Travel': [
            'Mileage',
            'Parking & Tolls',
            'Accommodation',
            'Meals',
            'Transportation',
            'Trade Show Travel'
        ],
        'Professional Services': [
            'Accounting',
            'Legal Consultation',
            'Business Consulting',
            'Photography Services',
            'Design Services',
            'Marketing Consulting'
        ],
        'Equipment': [
            'Display Equipment',
            'Storage Solutions',
            'POS Equipment',
            'Photography Equipment',
            'Packaging Supplies',
            'Tools & Accessories'
        ],
        'Utilities': [
            'Internet',
            'Phone',
            'Electricity',
            'Water',
            'Cloud Storage',
            'Communication Tools'
        ],
        'Office Expenses': [
            'Supplies',
            'Furniture',
            'Printing',
            'Stationery',
            'Organization Tools'
        ],
        'Insurance': [
            'Business Insurance',
            'Product Liability',
            'Equipment Insurance',
            'Health Insurance'
        ]
    };
    
    const subcategories = subcategoryMap[category] || [];
    subcategories.forEach(subcat => {
        const option = document.createElement('option');
        option.value = subcat;
        option.textContent = subcat;
        subCategorySelect.appendChild(option);
    });
    
    console.log(`📝 Populated ${subcategories.length} subcategories for ${category}`);
}

/**
 * Save transaction (expense only) - UPDATED for new database schema
 */
window.saveTransaction = function() {
    console.log('💾 Attempting to save transaction...');
    
    const form = document.getElementById('transactionForm');
    if (!form) {
        console.error('❌ Transaction form not found');
        showAlert('Transaction form not found', 'danger');
        return;
    }
    
    // Validate form
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    // Collect form data (UPDATED: Removed vendor, invoice_number, tax_deductible fields)
    const formData = {
        date: document.getElementById('transactionDate')?.value,
        description: document.getElementById('transactionDescription')?.value?.trim(),
        amount: parseFloat(document.getElementById('transactionAmount')?.value),
        category: document.getElementById('transactionCategory')?.value,
        sub_category: document.getElementById('transactionSubCategory')?.value || '',
        transaction_type: 'Expense', // Always expense
        account_name: document.getElementById('transactionAccount')?.value,
        notes: document.getElementById('transactionNotes')?.value?.trim() || ''
    };
    
    console.log('📊 Form data collected:', formData);
    
    // Validate required fields
    const missingFields = [];
    if (!formData.date) missingFields.push('Date');
    if (!formData.description) missingFields.push('Description');
    if (!formData.amount || formData.amount <= 0) missingFields.push('Valid Amount');
    if (!formData.category) missingFields.push('Category');
    if (!formData.account_name) missingFields.push('Payment Method');
    
    if (missingFields.length > 0) {
        showAlert(`Please fill in: ${missingFields.join(', ')}`, 'danger');
        return;
    }
    
    // Validate amount
    if (isNaN(formData.amount) || formData.amount <= 0) {
        showAlert('Amount must be a valid number greater than zero', 'danger');
        return;
    }
    
    console.log('💾 Saving expense transaction:', formData);
    
    // Disable save button to prevent double submission
    const saveButton = document.querySelector('#transactionModal .btn-primary, #transactionModal .btn-danger');
    const originalText = saveButton?.innerHTML;
    
    if (saveButton) {
        saveButton.disabled = true;
        saveButton.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Saving...';
    }
    
    // Submit to API
    fetch('/api/transactions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('📡 API Response:', data);
        
        if (data.success) {
            console.log('✅ Expense transaction saved successfully');
            showAlert(data.message || 'Expense saved successfully!', 'success');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('transactionModal'));
            if (modal) {
                modal.hide();
            }
            
            // Refresh dashboard data
            refreshDashboardData();
            
        } else {
            console.error('❌ Error saving expense transaction:', data.error);
            showAlert(data.error || 'Failed to save expense', 'danger');
        }
    })
    .catch(error => {
        console.error('❌ Network error saving expense transaction:', error);
        showAlert(`Network error: ${error.message}. Please check your connection and try again.`, 'danger');
    })
    .finally(() => {
        // Re-enable save button
        if (saveButton && originalText) {
            saveButton.disabled = false;
            saveButton.innerHTML = originalText;
        }
    });
};

/**
 * Refresh dashboard data after transaction save
 */
function refreshDashboardData() {
    console.log('🔄 Refreshing dashboard data...');
    
    // Option 1: Reload the page (simplest)
    setTimeout(() => {
        window.location.reload();
    }, 1500);
    
    // Option 2: Refresh specific sections via AJAX (more advanced)
    // This could be implemented to update only changed sections
}

/**
 * Initialize dashboard charts if chart data is available
 */
function initializeDashboardCharts() {
    try {
        // Check if Chart.js is available
        if (typeof Chart === 'undefined') {
            console.log('📊 Chart.js not available, skipping chart initialization');
            return;
        }
        
        // Initialize expense chart
        initializeExpenseChart();
        
        // Initialize revenue chart (from inventory sales)
        initializeRevenueChart();
        
        console.log('📊 Dashboard charts initialized');
        
    } catch (error) {
        console.error('❌ Error initializing charts:', error);
    }
}

/**
 * Initialize expense chart
 */
function initializeExpenseChart() {
    const expenseChartCanvas = document.getElementById('expenseChart');
    if (!expenseChartCanvas) return;
    
    // Sample chart - replace with actual data
    const ctx = expenseChartCanvas.getContext('2d');
    dashboardCharts.expenseChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Cost of Goods', 'Marketing', 'Operations', 'Administrative'],
            datasets: [{
                data: [40, 25, 20, 15],
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB', 
                    '#FFCE56',
                    '#4BC0C0'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

/**
 * Initialize revenue chart
 */
function initializeRevenueChart() {
    const revenueChartCanvas = document.getElementById('revenueChart');
    if (!revenueChartCanvas) return;
    
    // Sample chart - replace with actual data
    const ctx = revenueChartCanvas.getContext('2d');
    dashboardCharts.revenueChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Revenue',
                data: [1200, 1900, 3000, 2500, 2200, 3000],
                borderColor: '#28a745',
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

/**
 * Setup periodic data refresh
 */
function setupDataRefresh() {
    // Refresh dashboard data every 5 minutes if page is active
    setInterval(() => {
        if (!document.hidden) {
            console.log('🔄 Periodic dashboard refresh...');
            // Could implement AJAX refresh here instead of full reload
        }
    }, 300000); // 5 minutes
}

/**
 * Handle window resize for responsive charts
 */
window.addEventListener('resize', function() {
    Object.values(dashboardCharts).forEach(chart => {
        if (chart && typeof chart.resize === 'function') {
            chart.resize();
        }
    });
});

/**
 * Cleanup function for when leaving the page
 */
window.addEventListener('beforeunload', function() {
    // Destroy charts to prevent memory leaks
    Object.values(dashboardCharts).forEach(chart => {
        if (chart && typeof chart.destroy === 'function') {
            chart.destroy();
        }
    });
    
    console.log('🧹 Dashboard cleanup completed');
});

// Export functions for testing or external use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showAddExpenseModal,
        saveTransaction,
        populateSubCategories,
        showAlert
    };
}

console.log('📊 Dashboard.js loaded successfully');