/**
 * Complete Assets JavaScript - Full replacement to fix all issues
 * Aligned with simplified asset schema and expense category system
 */

/**
 * Enhanced function to save asset (replaces existing saveAsset function completely)
 */
function saveAsset() {
    console.log('💾 Saving asset with expense categories...');
    
    const form = document.getElementById('assetForm');
    if (!form || !form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    // Get all form values (only fields that exist in simplified schema)
    const assetData = {
        name: document.getElementById('assetName').value.trim(),
        asset_type: document.getElementById('assetType').value.trim(),
        purchase_date: document.getElementById('assetPurchaseDate').value,
        purchase_price: parseFloat(document.getElementById('assetPurchasePrice').value),
        expense_category: document.getElementById('assetExpenseCategory').value,
        expense_sub_category: document.getElementById('assetExpenseSubCategory').value,
        account_name: document.getElementById('assetAccountName').value,
        description: document.getElementById('assetDescription').value.trim(),
        is_active: document.getElementById('assetStatus').value === '1'
    };
    
    // Validate required fields
    if (!assetData.name || !assetData.asset_type || !assetData.purchase_date || 
        !assetData.purchase_price || !assetData.expense_category) {
        showAlert('Please fill in all required fields', 'danger');
        return;
    }
    
    // Check if editing existing asset
    const assetId = document.getElementById('assetId').value;
    const isEditing = assetId && assetId.trim() !== '';
    
    // Prepare API call
    const url = isEditing ? `/api/assets/${assetId}` : '/api/assets';
    const method = isEditing ? 'PUT' : 'POST';
    
    // Show loading state
    const saveButton = document.getElementById('saveAssetText');
    const originalText = saveButton.textContent;
    saveButton.textContent = 'Saving...';
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(assetData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('✅ Asset saved successfully:', data);
            
            // Show success message
            showAlert(data.message || `Asset ${isEditing ? 'updated' : 'added'} successfully!`, 'success');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('assetModal'));
            if (modal) modal.hide();
            
            // Reload assets table or page
            if (typeof loadAssets === 'function') {
                loadAssets();
            } else {
                // Fallback: reload page if loadAssets function doesn't exist
                setTimeout(() => window.location.reload(), 1000);
            }
            
            // Reset form
            form.reset();
            document.getElementById('assetId').value = '';
            
        } else {
            console.error('❌ Error saving asset:', data.error);
            showAlert(data.error || 'Error saving asset', 'danger');
        }
    })
    .catch(error => {
        console.error('❌ Network error saving asset:', error);
        showAlert('Network error. Please try again.', 'danger');
    })
    .finally(() => {
        // Restore button text
        saveButton.textContent = originalText;
    });
}

/**
 * Populate asset sub-categories based on expense category selection
 */
function populateAssetSubCategories() {
    const categorySelect = document.getElementById('assetExpenseCategory');
    const subCategorySelect = document.getElementById('assetExpenseSubCategory');
    
    if (!categorySelect || !subCategorySelect) return;
    
    const selectedCategory = categorySelect.value;
    
    // Sub-category mapping (matches the expense modal)
    const subCategoryMap = {
        "Cost of Goods Sold": [
            "Inventory Purchase",
            "Raw Materials",
            "Direct Labor",
            "Manufacturing Costs"
        ],
        "Marketing & Advertising": [
            "Online Advertising",
            "Print Advertising", 
            "Social Media Marketing",
            "Website & SEO",
            "Business Cards",
            "Promotional Materials"
        ],
        "Operations": [
            "Rent & Utilities",
            "Office Supplies",
            "Venue Rental",
            "Storage Costs",
            "Maintenance & Repairs"
        ],
        "Equipment & Supplies": [
            "Computer Equipment",
            "Office Furniture", 
            "POS Systems",
            "Software Licenses",
            "Tools & Equipment",
            "Asset Purchase"
        ],
        "Professional Services": [
            "Legal Services",
            "Accounting Services", 
            "Consulting",
            "Banking Fees",
            "Insurance"
        ],
        "Travel & Transport": [
            "Business Travel",
            "Vehicle Expenses",
            "Shipping & Delivery",
            "Transportation"
        ],
        "Other Expenses": [
            "Miscellaneous",
            "One-time Costs",
            "Unexpected Expenses"
        ]
    };
    
    // Clear existing sub-categories
    subCategorySelect.innerHTML = '<option value="">Select sub-category...</option>';
    
    if (selectedCategory && subCategoryMap[selectedCategory]) {
        const subCategories = subCategoryMap[selectedCategory];
        
        subCategories.forEach(subCategory => {
            const option = document.createElement('option');
            option.value = subCategory;
            option.textContent = subCategory;
            subCategorySelect.appendChild(option);
        });
        
        // Auto-select "Asset Purchase" if available for Equipment & Supplies
        if (selectedCategory === "Equipment & Supplies") {
            subCategorySelect.value = "Asset Purchase";
        }
    }
}

/**
 * Show the add asset modal with proper defaults
 */
function showAddAssetModal() {
    console.log('➕ Opening enhanced add asset modal...');
    
    // Reset form
    const form = document.getElementById('assetForm');
    if (form) form.reset();
    
    // Clear hidden ID field
    const assetIdInput = document.getElementById('assetId');
    if (assetIdInput) assetIdInput.value = '';
    
    // Set default values
    setAssetFormDefaults();
    
    // Update modal title and button
    const modalLabel = document.getElementById('assetModalLabel');
    const saveButton = document.getElementById('saveAssetText');
    
    if (modalLabel) modalLabel.textContent = 'Add New Asset';
    if (saveButton) saveButton.textContent = 'Save Asset';
    
    // Show modal
    const modal = document.getElementById('assetModal');
    if (modal && typeof bootstrap !== 'undefined') {
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        // Focus on asset name field after modal opens
        modal.addEventListener('shown.bs.modal', function() {
            const nameInput = document.getElementById('assetName');
            if (nameInput) {
                setTimeout(() => nameInput.focus(), 100);
            }
        }, { once: true });
    }
}

/**
 * Set default form values
 */
function setAssetFormDefaults() {
    // Set today's date as default
    const dateInput = document.getElementById('assetPurchaseDate');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.value = today;
    }
    
    // Set default account name
    const accountSelect = document.getElementById('assetAccountName');
    if (accountSelect) {
        accountSelect.value = 'Business Checking';
    }
    
    // Set default status to active
    const statusField = document.getElementById('assetStatus');
    if (statusField) {
        statusField.value = '1';
    }
    
    // Set default expense category to Equipment & Supplies
    const categorySelect = document.getElementById('assetExpenseCategory');
    if (categorySelect) {
        categorySelect.value = 'Equipment & Supplies';
        // Trigger sub-category population
        populateAssetSubCategories();
    }
}

/**
 * Edit an asset (fetch data and populate form)
 */
function editAsset(assetId) {
    console.log(`✏️ Editing asset ${assetId}...`);
    
    // Fetch asset data first
    fetch(`/api/assets/${assetId}`)
    .then(response => response.json())
    .then(data => {
        if (data.success && data.asset) {
            const asset = data.asset;
            
            // Populate form with asset data
            document.getElementById('assetId').value = asset.id;
            document.getElementById('assetName').value = asset.name || '';
            document.getElementById('assetType').value = asset.asset_type || '';
            document.getElementById('assetPurchaseDate').value = asset.purchase_date || '';
            document.getElementById('assetPurchasePrice').value = asset.purchase_price || '';
            document.getElementById('assetExpenseCategory').value = asset.asset_category || '';
            document.getElementById('assetAccountName').value = 'Business Checking'; // Default since not stored
            document.getElementById('assetDescription').value = asset.description || '';
            document.getElementById('assetStatus').value = asset.is_active ? '1' : '0';
            
            // Populate sub-categories based on category
            populateAssetSubCategories();
            
            // Update modal title and button
            const modalLabel = document.getElementById('assetModalLabel');
            const saveButton = document.getElementById('saveAssetText');
            
            if (modalLabel) modalLabel.textContent = 'Edit Asset';
            if (saveButton) saveButton.textContent = 'Update Asset';
            
            // Show modal
            const modal = document.getElementById('assetModal');
            if (modal && typeof bootstrap !== 'undefined') {
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
            }
            
        } else {
            console.error('❌ Error fetching asset data:', data.error);
            showAlert('Error loading asset data', 'danger');
        }
    })
    .catch(error => {
        console.error('❌ Network error fetching asset:', error);
        showAlert('Network error loading asset', 'danger');
    });
}

/**
 * Delete an asset with confirmation
 */
function deleteAsset(assetId) {
    if (!confirm('Are you sure you want to delete this asset? This action cannot be undone.')) {
        return;
    }
    
    console.log(`🗑️ Deleting asset ${assetId}...`);
    
    fetch(`/api/assets/${assetId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('✅ Asset deleted successfully');
            showAlert(data.message || 'Asset deleted successfully', 'success');
            
            // Reload assets table
            if (typeof loadAssets === 'function') {
                loadAssets();
            } else {
                // Fallback: reload page
                setTimeout(() => window.location.reload(), 1000);
            }
        } else {
            console.error('❌ Error deleting asset:', data.error);
            showAlert(data.error || 'Error deleting asset', 'danger');
        }
    })
    .catch(error => {
        console.error('❌ Network error deleting asset:', error);
        showAlert('Network error. Please try again.', 'danger');
    });
}

/**
 * Show asset details in modal (simplified for new schema)
 */
function showAssetDetails(assetId) {
    console.log(`👁️ Showing details for asset ${assetId}...`);
    
    fetch(`/api/assets/${assetId}`)
    .then(response => response.json())
    .then(data => {
        if (data.success && data.asset) {
            const asset = data.asset;
            
            // Build asset details HTML (simplified for new schema)
            const detailsHtml = `
                <div class="asset-details">
                    <div class="row mb-3">
                        <div class="col-sm-4"><strong>Name:</strong></div>
                        <div class="col-sm-8">${asset.name}</div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-sm-4"><strong>Type:</strong></div>
                        <div class="col-sm-8">${asset.asset_type}</div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-sm-4"><strong>Category:</strong></div>
                        <div class="col-sm-8">${asset.asset_category}</div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-sm-4"><strong>Purchase Date:</strong></div>
                        <div class="col-sm-8">${new Date(asset.purchase_date).toLocaleDateString()}</div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-sm-4"><strong>Purchase Price:</strong></div>
                        <div class="col-sm-8">$${parseFloat(asset.purchase_price).toFixed(2)}</div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-sm-4"><strong>Status:</strong></div>
                        <div class="col-sm-8">
                            <span class="badge ${asset.is_active ? 'bg-success' : 'bg-secondary'}">
                                ${asset.is_active ? 'Active' : 'Disposed'}
                            </span>
                        </div>
                    </div>
                    ${asset.description ? `
                    <div class="row mb-3">
                        <div class="col-sm-4"><strong>Description:</strong></div>
                        <div class="col-sm-8">${asset.description}</div>
                    </div>
                    ` : ''}
                </div>
            `;
            
            // Show in modal
            document.getElementById('assetDetailsContent').innerHTML = detailsHtml;
            
            const modal = document.getElementById('assetDetailsModal');
            if (modal && typeof bootstrap !== 'undefined') {
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
            }
            
        } else {
            console.error('❌ Error fetching asset details:', data.error);
            showAlert('Error loading asset details', 'danger');
        }
    })
    .catch(error => {
        console.error('❌ Network error fetching asset details:', error);
        showAlert('Network error loading asset details', 'danger');
    });
}

/**
 * Utility function to show alerts
 */
function showAlert(message, type = 'info') {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Find a good place to show the alert
    let container = document.querySelector('.alert-container');
    if (!container) {
        container = document.querySelector('.container-fluid') || document.body;
    }
    
    // Insert at the top
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('🏢 Assets JavaScript loaded and ready');
});