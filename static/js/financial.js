/* Financial Page JavaScript */
/* Handles financial dashboard functionality, charts, and data display */

// =============================================================================
// FINANCIAL PAGE INITIALIZATION
// =============================================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('💰 Loading business financial page...');
    
    // Initialize financial page components
    initializeFinancialPage();
    initializeTransactionForms();
    loadFinancialCharts();
    
    console.log('✅ Financial page initialization complete');
});

/**
 * Initialize main financial page functionality
 */
function initializeFinancialPage() {
    // Load financial data from hidden script tag
    loadFinancialData();
    
    // Initialize table interactions
    initializeTableInteractions();
    
    // Set up responsive behavior
    handleFinancialResponsiveChanges();
}

/**
 * Load financial data from the hidden JSON script
 */
function loadFinancialData() {
    try {
        const dataScript = document.getElementById('financialData');
        if (dataScript) {
            window.financialData = JSON.parse(dataScript.textContent);
            
            // NEW: Handle "all" year parameter for charts
            if (window.financialData.selectedYear === 'all') {
                // For "All Years", ensure we have valid numeric data
                const summary = window.financialData.summary || {};
                
                // Ensure all values are numbers, not undefined
                window.financialData.summary = {
                    monthly_revenue: parseFloat(summary.monthly_revenue) || 0,
                    monthly_expenses: parseFloat(summary.monthly_expenses) || 0,
                    ytd_revenue: parseFloat(summary.ytd_revenue) || 0,
                    ytd_expenses: parseFloat(summary.ytd_expenses) || 0
                };
                
                // Update chart titles for "All Years"
                window.financialData.chartTitle = 'All Years Data';
            }
            
            console.log('📊 Financial data loaded:', window.financialData);
        }
    } catch (error) {
        console.warn('Could not load financial data:', error);
        window.financialData = {
            summary: { monthly_revenue: 0, monthly_expenses: 0, ytd_revenue: 0, ytd_expenses: 0 },
            categoryBreakdown: [],
            selectedYear: new Date().getFullYear(),
            selectedMonth: 'all',
            chartTitle: 'Financial Data'
        };
    }
}

/**
 * Initialize table interactions and sorting
 */
function initializeTableInteractions() {
    const transactionsTable = document.getElementById('transactionsTable');
    if (transactionsTable) {
        // Add hover effects and sorting functionality if needed
        console.log('📋 Transactions table initialized');
    }
}

/**
 * Handle responsive changes for financial page
 */
function handleFinancialResponsiveChanges() {
    // Add responsive behavior for charts and tables
    window.addEventListener('resize', function() {
        // Debounce resize events
        clearTimeout(window.resizeTimeout);
        window.resizeTimeout = setTimeout(function() {
            // Resize charts if they exist - Plotly charts resize automatically
            if (document.getElementById('revenueExpenseChart')) {
                Plotly.Plots.resize(document.getElementById('revenueExpenseChart'));
            }
            if (document.getElementById('expenseCategoryChart')) {
                Plotly.Plots.resize(document.getElementById('expenseCategoryChart'));
            }
        }, 250);
    });
}

// =============================================================================
// TRANSACTION FORM FUNCTIONALITY
// =============================================================================

/**
 * Initialize transaction forms and modals
 */
function initializeTransactionForms() {
    const form = document.getElementById('transactionForm');
    if (!form) {
        console.warn('Transaction form not found');
        return;
    }
    
    // Set up category change listener for subcategories
    const categorySelect = document.getElementById('transactionCategory');
    if (categorySelect) {
        categorySelect.addEventListener('change', function() {
            populateSubCategories(this.value);
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
 * Show transaction modal for adding expense
 */
window.showAddExpenseModal = function() {
    console.log('💰 Opening add expense modal');
    
    // Reset edit mode flags
    isEditMode = false;
    currentEditId = null;
    
    showTransactionModal('Expense');
};

/**
 * Show transaction modal with specified type
 * @param {string} type - Transaction type ('Expense' only for financial page)
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
        if (form) form.reset();
        
        // Set transaction type to Expense only
        if (typeInput) typeInput.value = 'Expense';
        
        // Update modal title and button for add mode
        if (modalTitle) modalTitle.textContent = `Add Business ${type}`;
        if (saveText) saveText.textContent = `Save ${type}`;
        
        // Set today's date
        setTodaysDate();
        
        // Populate categories for expense type
        populateCategoriesByType('Expense');
        
        // Show modal
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        console.log(`✅ ${type} modal opened successfully`);
        
    } catch (error) {
        console.error(`❌ Error opening ${type} modal:`, error);
        showAlert(`Error opening ${type} form`, 'danger');
    }
}

/**
 * Set today's date in the transaction form
 */
function setTodaysDate() {
    const dateInput = document.getElementById('transactionDate');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.value = today;
    }
}

/**
 * Populate categories dropdown based on transaction type
 * @param {string} type - Transaction type
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
    
    // Expense categories for fashion business (reusing dashboard logic)
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
 * Populate subcategories based on main category selection (reused from dashboard)
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
 * Save transaction (handles both create and update)
 */
async function saveTransaction() {
    console.log('💾 Saving transaction...');
    
    const saveBtn = document.querySelector('#transactionModal .btn-primary');
    const originalText = saveBtn ? saveBtn.textContent : '';
    
    if (saveBtn) {
        saveBtn.textContent = isEditMode ? 'Updating...' : 'Saving...';
        saveBtn.disabled = true;
    }
    
    try {
        // Collect form data (reusing dashboard structure)
        const formData = {
            date: document.getElementById('transactionDate')?.value,
            description: document.getElementById('transactionDescription')?.value?.trim(),
            amount: parseFloat(document.getElementById('transactionAmount')?.value),
            category: document.getElementById('transactionCategory')?.value,
            sub_category: document.getElementById('transactionSubCategory')?.value || '',
            transaction_type: 'Expense', // Always expense for financial page
            account_name: document.getElementById('transactionAccount')?.value || 'Business Account',
            notes: document.getElementById('transactionNotes')?.value?.trim() || ''
        };
        
        // Validate required fields
        if (!formData.date || !formData.description || !formData.amount || !formData.category) {
            showAlert('Please fill in all required fields', 'warning');
            return;
        }
        
        if (formData.amount <= 0) {
            showAlert('Amount must be greater than 0', 'warning');
            return;
        }
        
        // Determine API endpoint and method
        let url = '/api/transactions';
        let method = 'POST';
        let successMessage = `Expense "${formData.description}" added successfully!`;
        
        if (isEditMode && currentEditId) {
            url = `/api/transactions/${currentEditId}`;
            method = 'PUT';
            successMessage = `Expense "${formData.description}" updated successfully!`;
        }
        
        console.log(`📡 ${method} request to ${url}`, formData);
        
        // Send to API
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(successMessage, 'success');
            
            // Reset edit mode flags
            isEditMode = false;
            currentEditId = null;
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('transactionModal'));
            if (modal) modal.hide();
            
            // Refresh page to update data
            setTimeout(() => {
                window.location.reload();
            }, 1000);
            
        } else {
            showAlert(`Error: ${result.error}`, 'danger');
        }
        
    } catch (error) {
        console.error('❌ Error saving transaction:', error);
        showAlert('Error saving transaction. Please try again.', 'danger');
    } finally {
        // Re-enable save button
        if (saveBtn) {
            saveBtn.textContent = originalText;
            saveBtn.disabled = false;
        }
    }
}

// =============================================================================
// TRANSACTION MANAGEMENT (View and Edit)
// =============================================================================

// Global variable to track if we're in edit mode
let isEditMode = false;
let currentEditId = null;

/**
 * Edit existing transaction
 * @param {number} transactionId - ID of transaction to edit
 */
window.editTransaction = async function(transactionId) {
    console.log(`✏️ Editing transaction ID: ${transactionId}`);
    
    try {
        // Fetch transaction data from API
        const response = await fetch(`/api/transactions/${transactionId}`);
        const result = await response.json();
        
        if (!result.success) {
            showAlert(`Error: ${result.error}`, 'danger');
            return;
        }
        
        const transaction = result.transaction;
        console.log('📄 Transaction data loaded:', transaction);
        
        // Set edit mode flags
        isEditMode = true;
        currentEditId = transactionId;
        
        // Show modal with transaction data
        showEditTransactionModal(transaction);
        
    } catch (error) {
        console.error('❌ Error fetching transaction:', error);
        showAlert('Error loading transaction data', 'danger');
    }
};

/**
 * Show transaction modal in edit mode with pre-populated data
 * @param {Object} transaction - Transaction data to populate
 */
function showEditTransactionModal(transaction) {
    console.log('📝 Opening edit transaction modal');
    
    const modal = document.getElementById('transactionModal');
    const modalTitle = document.getElementById('transactionModalLabel');
    const saveText = document.getElementById('saveTransactionText');
    const form = document.getElementById('transactionForm');
    
    if (!modal) {
        console.error('❌ Transaction modal not found');
        showAlert('Transaction form is not available', 'danger');
        return;
    }
    
    try {
        // Reset form first
        if (form) form.reset();
        
        // Update modal title and button for edit mode
        if (modalTitle) modalTitle.textContent = 'Edit Business Expense';
        if (saveText) saveText.textContent = 'Update Expense';
        
        // Populate form fields with transaction data
        populateFormWithTransaction(transaction);
        
        // Show modal
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        console.log('✅ Edit modal opened successfully');
        
    } catch (error) {
        console.error('❌ Error opening edit modal:', error);
        showAlert('Error opening edit form', 'danger');
    }
}

/**
 * Populate form fields with transaction data
 * @param {Object} transaction - Transaction data
 */
function populateFormWithTransaction(transaction) {
    console.log('📝 Populating form with transaction data');
    
    // Basic fields
    const dateField = document.getElementById('transactionDate');
    if (dateField && transaction.date) {
        dateField.value = transaction.date;
    }
    
    const descriptionField = document.getElementById('transactionDescription');
    if (descriptionField && transaction.description) {
        descriptionField.value = transaction.description;
    }
    
    const amountField = document.getElementById('transactionAmount');
    if (amountField && transaction.amount) {
        amountField.value = parseFloat(transaction.amount).toFixed(2);
    }
    
    const accountField = document.getElementById('transactionAccount');
    if (accountField && transaction.account_name) {
        accountField.value = transaction.account_name;
    }
    
    const notesField = document.getElementById('transactionNotes');
    if (notesField && transaction.notes) {
        notesField.value = transaction.notes;
    }
    
    // Set transaction type (always Expense for financial page)
    const typeField = document.getElementById('transactionType');
    if (typeField) {
        typeField.value = 'Expense';
    }
    
    // Populate category first
    populateCategoriesByType('Expense');
    
    // Wait a bit for categories to populate, then set the selected category
    setTimeout(() => {
        const categoryField = document.getElementById('transactionCategory');
        if (categoryField && transaction.category) {
            categoryField.value = transaction.category;
            
            // Trigger change event to populate subcategories
            populateSubCategories(transaction.category);
            
            // Set subcategory after subcategories are populated
            setTimeout(() => {
                const subCategoryField = document.getElementById('transactionSubCategory');
                if (subCategoryField && transaction.sub_category) {
                    subCategoryField.value = transaction.sub_category;
                }
            }, 100);
        }
    }, 100);
    
    console.log('✅ Form populated with transaction data');
}

/**
 * Delete transaction
 * @param {number} transactionId - ID of transaction to delete
 */
window.deleteTransaction = async function(transactionId) {
    console.log(`🗑️ Deleting transaction ID: ${transactionId}`);
    
    if (!confirm('Are you sure you want to delete this transaction? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/transactions/${transactionId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            if (typeof BusinessUtils !== 'undefined') {
                BusinessUtils.showAlert(result.message, 'success');
            } else {
                alert(result.message);
            }
            
            // Remove the row from table
            const row = document.querySelector(`tr[data-transaction-id="${transactionId}"]`);
            if (row) {
                row.remove();
            }
            
            // Refresh page to update metrics
            setTimeout(() => {
                window.location.reload();
            }, 1000);
            
        } else {
            if (typeof BusinessUtils !== 'undefined') {
                BusinessUtils.showAlert(`Error: ${result.error}`, 'danger');
            } else {
                alert(`Error: ${result.error}`);
            }
        }
        
    } catch (error) {
        console.error('❌ Error deleting transaction:', error);
        if (typeof BusinessUtils !== 'undefined') {
            BusinessUtils.showAlert('Error deleting transaction', 'danger');
        } else {
            alert('Error deleting transaction');
        }
    }
};

// =============================================================================
// CHART FUNCTIONALITY
// =============================================================================

/**
 * Load and display financial charts
 */
function loadFinancialCharts() {
    console.log('📊 Loading financial charts...');
    
    // Load charts with financial data
    loadRevenueExpenseChart();
    loadExpenseCategoryChart();
}

/**
 * Load Revenue vs Expense chart
 */
function loadRevenueExpenseChart() {
    const chartContainer = document.getElementById('revenueExpenseChart');
    if (!chartContainer) {
        console.warn('Revenue expense chart container not found');
        return;
    }

    try {
        // Get data from window.financialData
        const data = window.financialData || {};
        const summary = data.summary || {};
        
        const chartData = [{
            x: ['Revenue', 'Expenses'],
            y: [
                summary.monthly_revenue || 0,
                summary.monthly_expenses || 0
            ],
            type: 'bar',
            marker: {
                color: ['#28a745', '#dc3545']
            },
            text: [
                `$${(summary.monthly_revenue || 0).toFixed(2)}`,
                `$${(summary.monthly_expenses || 0).toFixed(2)}`
            ],
            textposition: 'auto'
        }];

        const layout = {
            title: {
                text: 'Monthly Revenue vs Expenses',
                font: { size: 14 }
            },
            xaxis: { title: 'Type' },
            yaxis: { title: 'Amount ($)' },
            margin: { l: 50, r: 20, t: 40, b: 40 },
            height: 300,
            showlegend: false
        };

        const config = {
            responsive: true,
            displayModeBar: false
        };

        Plotly.newPlot(chartContainer, chartData, layout, config);
        console.log('✅ Revenue vs Expense chart loaded');
        
    } catch (error) {
        console.error('❌ Error loading Revenue vs Expense chart:', error);
        chartContainer.innerHTML = '<div class="text-center text-muted py-3">Chart data unavailable</div>';
    }
}

/**
 * Load Expense Category chart
 */
function loadExpenseCategoryChart() {
    const chartContainer = document.getElementById('expenseCategoryChart');
    if (!chartContainer) {
        console.warn('Expense category chart container not found');
        return;
    }

    try {
        // Get data from window.financialData
        const data = window.financialData || {};
        const categoryBreakdown = data.categoryBreakdown || [];
        
        // Filter for categories with expenses
        const expenseCategories = categoryBreakdown.filter(cat => cat.expenses > 0);
        
        if (expenseCategories.length === 0) {
            chartContainer.innerHTML = '<div class="alert alert-info"><i class="fas fa-info-circle"></i> No expense data available</div>';
            console.log('ℹ️ No expense data for category chart');
            return;
        }

        const chartData = [{
            values: expenseCategories.map(cat => cat.expenses),
            labels: expenseCategories.map(cat => cat.name),
            type: 'pie',
            textinfo: 'label+percent',
            textposition: 'auto',
            hovertemplate: '<b>%{label}</b><br>Amount: $%{value:.2f}<br>Percentage: %{percent}<extra></extra>'
        }];

        const layout = {
            title: {
                text: 'Expenses by Category',
                font: { size: 14 }
            },
            margin: { l: 20, r: 20, t: 40, b: 20 },
            height: 300,
            showlegend: true,
            legend: {
                orientation: 'v',
                x: 1,
                y: 0.5
            }
        };

        const config = {
            responsive: true,
            displayModeBar: false
        };

        Plotly.newPlot(chartContainer, chartData, layout, config);
        console.log('✅ Expense category chart loaded');
        
    } catch (error) {
        console.error('❌ Error loading Expense category chart:', error);
        chartContainer.innerHTML = '<div class="text-center text-muted py-3">Chart data unavailable</div>';
    }
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Format currency for display
 * @param {number} amount - Amount to format
 * @returns {string} Formatted currency string
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount || 0);
}

/**
 * Show alert message (fallback if BusinessUtils not available)
 * @param {string} message - Message to show
 * @param {string} type - Alert type (success, danger, info, warning)
 */
function showAlert(message, type = 'info') {
    if (typeof BusinessUtils !== 'undefined') {
        BusinessUtils.showAlert(message, type);
    } else {
        alert(message);
    }
}

// =============================================================================
// PAGINATION ENHANCEMENTS
// =============================================================================

/**
 * Initialize pagination interactions
 */
function initializePagination() {
    // Add loading states to pagination links
    const paginationLinks = document.querySelectorAll('.pagination .page-link');
    
    paginationLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Don't prevent default - let the link work normally
            // Just add visual feedback
            if (!this.closest('.page-item').classList.contains('disabled') && 
                !this.closest('.page-item').classList.contains('active')) {
                
                // Add loading state
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                
                // Remove loading state after a short delay (page will reload anyway)
                setTimeout(() => {
                    this.innerHTML = originalText;
                }, 500);
            }
        });
    });
}

/**
 * Update transaction table interactions for paginated results
 */
function updateTableInteractions() {
    // Re-initialize table interactions after page load
    initializeTableInteractions();
    
    // Add row click handlers for better UX
    const transactionRows = document.querySelectorAll('#transactionsTable tbody tr');
    
    transactionRows.forEach(row => {
        row.addEventListener('click', function(e) {
            // Don't trigger if clicking on action buttons
            if (e.target.closest('.btn-group')) {
                return;
            }
            
            // Add visual feedback for row selection
            transactionRows.forEach(r => r.classList.remove('table-active'));
            this.classList.add('table-active');
        });
    });
}

/**
 * Smooth scroll to top after pagination
 */
function scrollToTransactionsTable() {
    const tableElement = document.getElementById('transactionsTable');
    if (tableElement) {
        tableElement.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }
}

// =============================================================================
// ENHANCED FILTER FUNCTIONALITY
// =============================================================================

/**
 * Initialize enhanced filter functionality
 */
function initializeEnhancedFilters() {
    const yearSelect = document.getElementById('yearSelect');
    const monthSelect = document.getElementById('monthSelect');
    
    if (yearSelect) {
        yearSelect.addEventListener('change', function() {
            // Auto-submit form when year changes
            this.closest('form').submit();
        });
    }
    
    if (monthSelect) {
        monthSelect.addEventListener('change', function() {
            // Auto-submit form when month changes
            this.closest('form').submit();
        });
    }
}

/**
 * Show loading state during filter changes
 */
function showFilterLoading() {
    const filterButton = document.querySelector('.filter-controls .btn-primary');
    if (filterButton) {
        const originalText = filterButton.innerHTML;
        filterButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        filterButton.disabled = true;
        
        // Re-enable after form submission
        setTimeout(() => {
            filterButton.innerHTML = originalText;
            filterButton.disabled = false;
        }, 1000);
    }
}

// =============================================================================
// UPDATE INITIALIZATION
// =============================================================================

// Update the main initialization to include pagination
document.addEventListener('DOMContentLoaded', function() {
    console.log('💰 Loading enhanced business financial page...');
    
    // Initialize financial page components
    initializeFinancialPage();
    initializeTransactionForms();
    loadFinancialCharts();
    
    // Initialize pagination features
    initializePagination();
    updateTableInteractions();
    initializeEnhancedFilters();
    
    // Scroll to table if coming from pagination
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('page') && parseInt(urlParams.get('page')) > 1) {
        setTimeout(scrollToTransactionsTable, 100);
    }
    
    console.log('✅ Enhanced financial page initialization complete');
});

/**
 * Handle filter form submission with loading states
 */
function handleFilterSubmission() {
    const filterForm = document.querySelector('.filter-controls form');
    if (filterForm) {
        filterForm.addEventListener('submit', function() {
            showFilterLoading();
        });
    }
}

// Initialize filter submission handling
document.addEventListener('DOMContentLoaded', handleFilterSubmission);

// =============================================================================
// INITIALIZATION COMPLETE
// =============================================================================

console.log('💰 Financial page JavaScript loaded successfully');