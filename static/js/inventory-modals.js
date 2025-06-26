/**
 * Inventory Modals Manager - Handles modal operations for inventory
 */

class InventoryModals {
    constructor() {
        console.log('📦 InventoryModals initializing...');
        this.apiManager = null;
        this.inventoryManager = null;
        this.currentEditSku = null;
        this.isEditMode = false;
    }

    /**
     * Show add item modal
     */
    showAddItemModal() {
        console.log('📦 Opening add item modal...');
        
        this.isEditMode = false;
        this.currentEditSku = null;
        
        // Reset form
        this.resetInventoryForm();
        
        // Update modal title
        const modalTitle = document.getElementById('inventoryModalLabel');
        if (modalTitle) {
            modalTitle.textContent = 'Add New Inventory Item';
        }
        
        // Update button text
        const saveButton = document.getElementById('saveButtonText');
        if (saveButton) {
            saveButton.textContent = 'Save Item';
        }
        
        // Show modal
        const modal = document.getElementById('inventoryModal');
        if (modal) {
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
        }
    }

    /**
     * Edit existing item
     */
    async editItem(sku) {
        console.log(`📦 Opening edit modal for SKU: ${sku}`);
        
        if (!this.apiManager) {
            console.error('❌ API Manager not available');
            return;
        }

        try {
            // Get item data
            const item = await this.apiManager.getInventoryItem(sku);
            
            this.isEditMode = true;
            this.currentEditSku = sku;
            
            // Populate form with item data
            this.populateInventoryForm(item);
            
            // Update modal title
            const modalTitle = document.getElementById('inventoryModalLabel');
            if (modalTitle) {
                modalTitle.textContent = `Edit Item - SKU ${sku}`;
            }
            
            // Update button text
            const saveButton = document.getElementById('saveButtonText');
            if (saveButton) {
                saveButton.textContent = 'Update Item';
            }
            
            // Show modal
            const modal = document.getElementById('inventoryModal');
            if (modal) {
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
            }
            
        } catch (error) {
            console.error('❌ Error loading item for edit:', error);
            this.showMessage('Error loading item data', 'danger');
        }
    }

    /**
     * Show sell modal
     */
    async showSellModal(sku) {
        console.log(`📦 Opening sell modal for SKU: ${sku}`);
        
        if (!this.apiManager) {
            console.error('❌ API Manager not available');
            return;
        }

        try {
            // Get item data
            const item = await this.apiManager.getInventoryItem(sku);
            
            // Populate sell modal
            if (window.populateSellModal) {
                window.populateSellModal(item);
            }
            
            // Show modal
            const modal = document.getElementById('inventorySellModal');
            if (modal) {
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
            }
            
        } catch (error) {
            console.error('❌ Error loading item for sell:', error);
            this.showMessage('Error loading item data', 'danger');
        }
    }

    /**
     * Save inventory item (create or update)
     */
    async saveInventoryItem() {
        console.log('📦 Saving inventory item...');
        
        if (!this.apiManager) {
            console.error('❌ API Manager not available');
            return;
        }

        try {
            // Get form data
            const formData = this.getInventoryFormData();
            
            // Validate form
            if (!this.validateInventoryForm(formData)) {
                return;
            }

            let result;
            
            if (this.isEditMode && this.currentEditSku) {
                // Update existing item
                result = await this.apiManager.updateInventoryItem(this.currentEditSku, formData);
            } else {
                // Create new item
                result = await this.apiManager.createInventoryItem(formData);
            }
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('inventoryModal'));
            if (modal) {
                modal.hide();
            }
            
            // Refresh inventory data
            if (this.inventoryManager) {
                await this.inventoryManager.refreshInventoryData();
            }
            
            // Show success message
            this.showMessage(result.message || 'Item saved successfully', 'success');
            
        } catch (error) {
            console.error('❌ Error saving inventory item:', error);
            this.showMessage(error.message || 'Error saving item', 'danger');
        }
    }

    /**
     * Confirm sell item
     */
    async confirmSellItem() {
        console.log('📦 Confirming item sale...');
        
        if (!this.apiManager) {
            console.error('❌ API Manager not available');
            return;
        }

        try {
            // Validate sell form
            if (!window.validateSellForm || !window.validateSellForm()) {
                return;
            }

            // Get sell form data
            const sellData = window.getSellFormData ? window.getSellFormData() : {};
            
            if (!sellData.sku) {
                this.showMessage('Error: No item selected', 'danger');
                return;
            }

            // Mark item as sold
            const result = await this.apiManager.sellInventoryItem(sellData.sku, sellData);
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('inventorySellModal'));
            if (modal) {
                modal.hide();
            }
            
            // Refresh inventory data
            if (this.inventoryManager) {
                await this.inventoryManager.refreshInventoryData();
            }
            
            // Show success message
            this.showMessage(result.message || 'Item sold successfully', 'success');
            
        } catch (error) {
            console.error('❌ Error selling item:', error);
            this.showMessage(error.message || 'Error selling item', 'danger');
        }
    }

    /**
     * Reset inventory form
     */
    resetInventoryForm() {
        const form = document.getElementById('inventoryForm');
        if (form) {
            form.reset();
            
            // Clear hidden fields
            document.getElementById('inventorySku').value = '';
            document.getElementById('inventoryEditMode').value = 'false';
            
            // Remove validation classes
            const inputs = form.querySelectorAll('.form-control, .form-select');
            inputs.forEach(input => {
                input.classList.remove('is-valid', 'is-invalid');
            });
        }
    }

    /**
     * Populate form with item data
     */
    populateInventoryForm(item) {
        // Set form values
        document.getElementById('inventorySku').value = item.sku || '';
        document.getElementById('inventoryEditMode').value = 'true';
        document.getElementById('inventoryBrand').value = item.brand || '';
        document.getElementById('inventoryItemType').value = item.item_type || '';
        document.getElementById('inventoryCategory').value = item.category || '';
        document.getElementById('inventorySize').value = item.size || '';
        document.getElementById('inventoryCondition').value = item.condition || '';
        document.getElementById('inventoryCostPerUnit').value = item.cost_of_item || '';
        document.getElementById('inventorySellingPrice').value = item.selling_price || '';
        document.getElementById('inventoryCollectionDrop').value = item.collection_drop || '';
        document.getElementById('inventoryListingStatus').value = item.listing_status || '';
        document.getElementById('inventoryLocation').value = item.location || '';
        document.getElementById('inventoryName').value = item.name || '';
        document.getElementById('inventoryDescription').value = item.description || '';
    }

    /**
     * Get form data
     */
    getInventoryFormData() {
        return {
            name: document.getElementById('inventoryName').value.trim(),
            brand: document.getElementById('inventoryBrand').value.trim(),
            item_type: document.getElementById('inventoryItemType').value.trim(),
            category: document.getElementById('inventoryCategory').value,
            size: document.getElementById('inventorySize').value.trim(),
            condition: document.getElementById('inventoryCondition').value,
            cost_of_item: document.getElementById('inventoryCostPerUnit').value,
            selling_price: document.getElementById('inventorySellingPrice').value,
            collection_drop: document.getElementById('inventoryCollectionDrop').value.trim(),
            listing_status: document.getElementById('inventoryListingStatus').value,
            location: document.getElementById('inventoryLocation').value.trim(),
            description: document.getElementById('inventoryDescription').value.trim()
        };
    }

    /**
     * Validate form data
     */
    validateInventoryForm(data) {
        let isValid = true;
        
        // Required fields
        const requiredFields = [
            { id: 'inventoryName', value: data.name, name: 'Item name' },
            { id: 'inventoryBrand', value: data.brand, name: 'Brand' },
            { id: 'inventoryItemType', value: data.item_type, name: 'Item type' },
            { id: 'inventoryCategory', value: data.category, name: 'Category' },
            { id: 'inventorySize', value: data.size, name: 'Size' },
            { id: 'inventoryCondition', value: data.condition, name: 'Condition' },
            { id: 'inventoryListingStatus', value: data.listing_status, name: 'Status' }
        ];
        
        requiredFields.forEach(field => {
            const element = document.getElementById(field.id);
            if (!field.value) {
                element.classList.add('is-invalid');
                isValid = false;
            } else {
                element.classList.remove('is-invalid');
                element.classList.add('is-valid');
            }
        });
        
        // Validate numeric fields
        const costElement = document.getElementById('inventoryCostPerUnit');
        const cost = parseFloat(data.cost_of_item);
        if (isNaN(cost) || cost < 0.01) {
            costElement.classList.add('is-invalid');
            isValid = false;
        } else {
            costElement.classList.remove('is-invalid');
            costElement.classList.add('is-valid');
        }
        
        const priceElement = document.getElementById('inventorySellingPrice');
        const price = parseFloat(data.selling_price);
        if (isNaN(price) || price < 0.01) {
            priceElement.classList.add('is-invalid');
            isValid = false;
        } else {
            priceElement.classList.remove('is-invalid');
            priceElement.classList.add('is-valid');
        }
        
        if (!isValid) {
            this.showMessage('Please fill in all required fields correctly', 'warning');
        }
        
        return isValid;
    }

    /**
     * Show message to user
     */
    showMessage(message, type = 'info', duration = 3000) {
        if (this.inventoryManager && this.inventoryManager.showMessage) {
            this.inventoryManager.showMessage(message, type, duration);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
}

// Create global class
window.InventoryModals = InventoryModals;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ InventoryModals class available');
});