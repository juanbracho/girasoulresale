/**
 * Inventory Modal Manager - Handles dynamic loading and add new functionality
 */

class InventoryModalManager {
    constructor() {
        this.apiBaseUrl = '/api';
        this.categories = [];
        this.conditions = [];
        this.isEditMode = false;
        this.currentItemId = null;
        
        this.init();
    }

    /**
     * Initialize the modal manager
     */
    async init() {
        try {
            await this.loadCategoriesAndConditions();
            this.setupEventListeners();
            this.setupFormValidation();
            console.log('✅ Inventory Modal Manager initialized');
        } catch (error) {
            console.error('❌ Error initializing Inventory Modal Manager:', error);
        }
    }

    /**
     * Load categories and conditions from API
     */
    async loadCategoriesAndConditions() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/categories-and-conditions`);
            const data = await response.json();
            
            if (data.success) {
                this.categories = data.categories || [];
                this.conditions = data.conditions || [];
                
                this.populateCategoryDropdown();
                this.populateConditionDropdown();
                
                console.log(`✅ Loaded ${this.categories.length} categories and ${this.conditions.length} conditions`);
            } else {
                throw new Error(data.error || 'Failed to load categories and conditions');
            }
        } catch (error) {
            console.error('❌ Error loading categories and conditions:', error);
            this.showError('Failed to load categories and conditions');
        }
    }

    /**
     * Populate category dropdown
     */
    populateCategoryDropdown() {
        const categorySelect = document.getElementById('inventoryCategory');
        if (!categorySelect) return;

        categorySelect.innerHTML = '<option value="">Select category...</option>';
        
        this.categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.name;
            option.textContent = category.name;
            categorySelect.appendChild(option);
        });
    }

    /**
     * Populate condition dropdown
     */
    populateConditionDropdown() {
        const conditionSelect = document.getElementById('inventoryCondition');
        if (!conditionSelect) return;

        conditionSelect.innerHTML = '<option value="">Select condition...</option>';
        
        this.conditions.forEach(condition => {
            const option = document.createElement('option');
            option.value = condition.name;
            option.textContent = condition.name;
            conditionSelect.appendChild(option);
        });
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Add new category link
        const addCategoryLink = document.getElementById('addNewCategoryLink');
        if (addCategoryLink) {
            addCategoryLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.showAddCategoryModal();
            });
        }

        // Add new condition link
        const addConditionLink = document.getElementById('addNewConditionLink');
        if (addConditionLink) {
            addConditionLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.showAddConditionModal();
            });
        }

        // Add category form submission
        const addCategoryForm = document.getElementById('addCategoryForm');
        if (addCategoryForm) {
            addCategoryForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleAddCategory();
            });
        }

        // Add condition form submission
        const addConditionForm = document.getElementById('addConditionForm');
        if (addConditionForm) {
            addConditionForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleAddCondition();
            });
        }

        // Profit calculation on price changes
        const costInput = document.getElementById('inventoryCostPerUnit');
        const priceInput = document.getElementById('inventorySellingPrice');
        
        if (costInput && priceInput) {
            costInput.addEventListener('input', () => this.calculateProfit());
            priceInput.addEventListener('input', () => this.calculateProfit());
        }

        // Character count for description
        const descriptionInput = document.getElementById('inventoryDescription');
        if (descriptionInput) {
            descriptionInput.addEventListener('input', () => this.updateCharacterCount());
        }

        // Main inventory form submission
        const inventoryForm = document.getElementById('inventoryForm');
        if (inventoryForm) {
            inventoryForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleInventorySubmission();
            });
        }
    }

    /**
     * Show add category modal
     */
    showAddCategoryModal() {
        const modal = new bootstrap.Modal(document.getElementById('addCategoryModal'));
        
        // Clear form
        document.getElementById('addCategoryForm').reset();
        document.getElementById('addCategoryForm').classList.remove('was-validated');
        
        modal.show();
    }

    /**
     * Show add condition modal
     */
    showAddConditionModal() {
        const modal = new bootstrap.Modal(document.getElementById('addConditionModal'));
        
        // Clear form
        document.getElementById('addConditionForm').reset();
        document.getElementById('addConditionForm').classList.remove('was-validated');
        
        modal.show();
    }

    /**
     * Handle add category
     */
    async handleAddCategory() {
        const form = document.getElementById('addCategoryForm');
        const submitBtn = document.getElementById('saveCategoryBtn');
        const spinner = submitBtn.querySelector('.spinner-border');
        
        if (!form.checkValidity()) {
            form.classList.add('was-validated');
            return;
        }

        const name = document.getElementById('newCategoryName').value.trim();
        const description = document.getElementById('newCategoryDescription').value.trim();

        try {
            // Show loading
            spinner.classList.remove('d-none');
            submitBtn.disabled = true;

            const response = await fetch(`${this.apiBaseUrl}/categories/inventory`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: name,
                    description: description || null
                })
            });

            const data = await response.json();

            if (data.success) {
                // Update categories list
                this.categories = data.categories || [];
                this.populateCategoryDropdown();
                
                // Select the new category
                const categorySelect = document.getElementById('inventoryCategory');
                if (categorySelect) {
                    categorySelect.value = name;
                }

                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('addCategoryModal'));
                modal.hide();

                this.showSuccess(`Category "${name}" added successfully`);
            } else {
                this.showError(data.error || 'Failed to add category');
            }
        } catch (error) {
            console.error('❌ Error adding category:', error);
            this.showError('Failed to add category');
        } finally {
            spinner.classList.add('d-none');
            submitBtn.disabled = false;
        }
    }

    /**
     * Handle add condition
     */
    async handleAddCondition() {
        const form = document.getElementById('addConditionForm');
        const submitBtn = document.getElementById('saveConditionBtn');
        const spinner = submitBtn.querySelector('.spinner-border');
        
        if (!form.checkValidity()) {
            form.classList.add('was-validated');
            return;
        }

        const name = document.getElementById('newConditionName').value.trim();
        const description = document.getElementById('newConditionDescription').value.trim();

        try {
            // Show loading
            spinner.classList.remove('d-none');
            submitBtn.disabled = true;

            const response = await fetch(`${this.apiBaseUrl}/conditions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: name,
                    description: description || null
                })
            });

            const data = await response.json();

            if (data.success) {
                // Update conditions list
                this.conditions = data.conditions || [];
                this.populateConditionDropdown();
                
                // Select the new condition
                const conditionSelect = document.getElementById('inventoryCondition');
                if (conditionSelect) {
                    conditionSelect.value = name;
                }

                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('addConditionModal'));
                modal.hide();

                this.showSuccess(`Condition "${name}" added successfully`);
            } else {
                this.showError(data.error || 'Failed to add condition');
            }
        } catch (error) {
            console.error('❌ Error adding condition:', error);
            this.showError('Failed to add condition');
        } finally {
            spinner.classList.add('d-none');
            submitBtn.disabled = false;
        }
    }

    /**
     * Calculate profit preview
     */
    calculateProfit() {
        const cost = parseFloat(document.getElementById('inventoryCostPerUnit').value) || 0;
        const price = parseFloat(document.getElementById('inventorySellingPrice').value) || 0;
        
        const profit = price - cost;
        const margin = price > 0 ? ((profit / price) * 100) : 0;
        const costWithTax = cost * 1.08; // Approximate 8% tax
        
        // Update display
        document.getElementById('profitAmount').textContent = `$${profit.toFixed(2)}`;
        document.getElementById('profitMargin').textContent = `${margin.toFixed(1)}%`;
        document.getElementById('costWithTax').textContent = `$${costWithTax.toFixed(2)}`;
        
        // Color coding
        const profitElement = document.getElementById('profitAmount');
        if (profit > 0) {
            profitElement.className = 'fw-bold text-success';
        } else if (profit < 0) {
            profitElement.className = 'fw-bold text-danger';
        } else {
            profitElement.className = 'fw-bold text-muted';
        }
    }

    /**
     * Update character count for description
     */
    updateCharacterCount() {
        const description = document.getElementById('inventoryDescription').value;
        const charCount = document.getElementById('descriptionCharCount');
        if (charCount) {
            charCount.textContent = description.length;
        }
    }

    /**
     * Setup form validation
     */
    setupFormValidation() {
        // Bootstrap validation styling
        const forms = document.querySelectorAll('.needs-validation, #inventoryForm, #addCategoryForm, #addConditionForm');
        forms.forEach(form => {
            form.addEventListener('submit', (event) => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });
    }

/**
 * Handle inventory form submission - integrate with existing system
 */
async handleInventorySubmission() {
    console.log('📦 Handling inventory form submission...');
    
    // First, ensure form data matches expected field names
    const formData = this.getFormData();
    
    // Check if we have the existing inventory modals manager
    if (window.inventoryModals && typeof window.inventoryModals.saveInventoryItem === 'function') {
        // Temporarily populate the existing form fields with our data
        this.populateExistingFormFields(formData);
        
        // Use the existing save function
        await window.inventoryModals.saveInventoryItem();
    } else {
        console.warn('⚠️ Existing inventory modals system not found, using direct API call');
        await this.directApiSubmission(formData);
    }
}

/**
 * Populate existing form fields to work with current system
 */
populateExistingFormFields(formData) {
    // Map our form data to whatever fields the existing system expects
    const fieldMappings = [
        { newId: 'inventoryName', existingId: 'inventoryName' },
        { newId: 'inventoryBrand', existingId: 'inventoryBrand' },
        { newId: 'inventoryItemType', existingId: 'inventoryItemType' },
        { newId: 'inventoryCategory', existingId: 'inventoryCategory' },
        { newId: 'inventorySize', existingId: 'inventorySize' },
        { newId: 'inventoryCondition', existingId: 'inventoryCondition' },
        { newId: 'inventoryCostPerUnit', existingId: 'inventoryCostPerUnit' },
        { newId: 'inventorySellingPrice', existingId: 'inventorySellingPrice' },
        { newId: 'inventoryCollectionDrop', existingId: 'inventoryCollectionDrop' },
        { newId: 'inventoryListingStatus', existingId: 'inventoryListingStatus' },
        { newId: 'inventoryLocation', existingId: 'inventoryLocation' },
        { newId: 'inventoryDescription', existingId: 'inventoryDescription' }
    ];
    
    fieldMappings.forEach(mapping => {
        const sourceField = document.getElementById(mapping.newId);
        const targetField = document.getElementById(mapping.existingId);
        
        if (sourceField && targetField && sourceField !== targetField) {
            targetField.value = sourceField.value;
        }
    });
}

/**
 * Direct API submission as fallback
 */
async directApiSubmission(formData) {
    const submitBtn = document.getElementById('saveInventoryBtn');
    const spinner = submitBtn.querySelector('.spinner-border');
    
    try {
        // Show loading
        spinner.classList.remove('d-none');
        submitBtn.disabled = true;

        const response = await fetch('/api/inventory', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (data.success) {
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('inventoryModal'));
            modal.hide();

            // Refresh page or update table
            if (window.inventoryManager && window.inventoryManager.refreshInventoryData) {
                await window.inventoryManager.refreshInventoryData();
            } else {
                location.reload();
            }

            this.showSuccess('Item saved successfully');
        } else {
            throw new Error(data.error || 'Failed to save item');
        }
    } catch (error) {
        console.error('❌ Error saving inventory item:', error);
        this.showError(error.message || 'Failed to save item');
    } finally {
        spinner.classList.add('d-none');
        submitBtn.disabled = false;
    }
}

/**
 * Basic inventory submission fallback
 */
async basicInventorySubmission() {
    const form = document.getElementById('inventoryForm');
    const submitBtn = document.getElementById('saveInventoryBtn');
    const spinner = submitBtn.querySelector('.spinner-border');
    
    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return;
    }

    try {
        // Show loading
        spinner.classList.remove('d-none');
        submitBtn.disabled = true;

        // Get form data
        const formData = this.getFormData();
        
        // Submit to API (you'll need to implement this endpoint)
        const response = await fetch('/api/inventory', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (data.success) {
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('inventoryModal'));
            modal.hide();

            // Refresh page or update table
            location.reload(); // Simple approach

            this.showSuccess('Item saved successfully');
        } else {
            this.showError(data.error || 'Failed to save item');
        }
    } catch (error) {
        console.error('❌ Error saving inventory item:', error);
        this.showError('Failed to save item');
    } finally {
        spinner.classList.add('d-none');
        submitBtn.disabled = false;
    }
}

/**
 * Get form data for submission
 */
getFormData() {
    return {
        // Basic item info
        name: document.getElementById('inventoryName').value.trim(),
        brand: document.getElementById('inventoryBrand').value.trim(),
        item_type: document.getElementById('inventoryItemType').value.trim(),
        category: document.getElementById('inventoryCategory').value,
        size: document.getElementById('inventorySize').value.trim(),
        condition: document.getElementById('inventoryCondition').value,
        
        // Pricing - CORRECTED FIELD NAME
        cost_of_item: parseFloat(document.getElementById('inventoryCostPerUnit').value) || 0,  // Changed from cost_per_unit
        selling_price: parseFloat(document.getElementById('inventorySellingPrice').value) || 0,
        
        // Optional fields with defaults
        collection_drop: document.getElementById('inventoryCollectionDrop').value.trim() || '',
        listing_status: document.getElementById('inventoryListingStatus').value || 'inventory',
        location: document.getElementById('inventoryLocation').value.trim() || '',  // Required field
        description: document.getElementById('inventoryDescription').value.trim() || ''  // Required field
    };
}

    /**
     * Show success message
     */
    showSuccess(message) {
        // You can integrate this with your existing notification system
        console.log('✅', message);
        // Example: show a toast notification
        this.showNotification(message, 'success');
    }

    /**
     * Show error message
     */
    showError(message) {
        // You can integrate this with your existing notification system
        console.error('❌', message);
        this.showNotification(message, 'error');
    }

    /**
     * Show notification (placeholder for your notification system)
     */
    showNotification(message, type) {
        // This is a simple implementation - replace with your preferred notification system
        const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
        const alertHtml = `
            <div class="alert ${alertClass} alert-dismissible fade show position-fixed" 
                 style="top: 20px; right: 20px; z-index: 9999; max-width: 300px;">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = alertHtml;
        document.body.appendChild(tempDiv.firstElementChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            const alert = document.querySelector('.alert');
            if (alert) {
                alert.remove();
            }
        }, 5000);
    }

    /**
     * Refresh categories and conditions
     */
    async refresh() {
        await this.loadCategoriesAndConditions();
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.inventoryModalManager = new InventoryModalManager();
});