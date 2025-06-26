/**
 * Inventory API Manager - Handles all AJAX requests for inventory operations
 */

class InventoryApi {
    constructor() {
        console.log('📦 InventoryApi initialized');
        this.baseUrl = '/api/inventory';
    }

    /**
     * Get all inventory items
     */
    async getAllInventory() {
        try {
            console.log('📦 API: Fetching all inventory items...');
            
            const response = await fetch(this.baseUrl);
            const data = await response.json();
            
            if (data.success) {
                console.log(`📦 API: Successfully retrieved ${data.items.length} items`);
                return data.items;
            } else {
                console.error('❌ API: Failed to get inventory:', data.error);
                throw new Error(data.error);
            }
        } catch (error) {
            console.error('❌ API: Error fetching inventory:', error);
            throw error;
        }
    }

    /**
     * Get single inventory item by SKU
     */
    async getInventoryItem(sku) {
        try {
            console.log(`📦 API: Fetching item with SKU: ${sku}`);
            
            const response = await fetch(`${this.baseUrl}/${sku}`);
            const data = await response.json();
            
            if (data.success) {
                console.log(`📦 API: Successfully retrieved item ${sku}`);
                return data.item;
            } else {
                console.error(`❌ API: Failed to get item ${sku}:`, data.error);
                throw new Error(data.error);
            }
        } catch (error) {
            console.error(`❌ API: Error fetching item ${sku}:`, error);
            throw error;
        }
    }

    /**
     * Create new inventory item
     */
    async createInventoryItem(itemData) {
        try {
            console.log('📦 API: Creating new inventory item...');
            
            const response = await fetch(this.baseUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(itemData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                console.log(`📦 API: Successfully created item with SKU: ${data.item.sku}`);
                return data;
            } else {
                console.error('❌ API: Failed to create item:', data.error);
                throw new Error(data.error);
            }
        } catch (error) {
            console.error('❌ API: Error creating item:', error);
            throw error;
        }
    }

    /**
     * Update existing inventory item
     */
    async updateInventoryItem(sku, itemData) {
        try {
            console.log(`📦 API: Updating item with SKU: ${sku}`);
            
            const response = await fetch(`${this.baseUrl}/${sku}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(itemData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                console.log(`📦 API: Successfully updated item ${sku}`);
                return data;
            } else {
                console.error(`❌ API: Failed to update item ${sku}:`, data.error);
                throw new Error(data.error);
            }
        } catch (error) {
            console.error(`❌ API: Error updating item ${sku}:`, error);
            throw error;
        }
    }

    /**
     * Mark item as sold
     */
    async sellInventoryItem(sku, saleData) {
        try {
            console.log(`📦 API: Selling item with SKU: ${sku}`);
            
            const response = await fetch(`${this.baseUrl}/${sku}/sell`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(saleData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                console.log(`📦 API: Successfully sold item ${sku}`);
                return data;
            } else {
                console.error(`❌ API: Failed to sell item ${sku}:`, data.error);
                throw new Error(data.error);
            }
        } catch (error) {
            console.error(`❌ API: Error selling item ${sku}:`, error);
            throw error;
        }
    }

    /**
     * Delete inventory item
     */
    async deleteInventoryItem(sku) {
        try {
            console.log(`📦 API: Deleting item with SKU: ${sku}`);
            
            const response = await fetch(`${this.baseUrl}/${sku}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (data.success) {
                console.log(`📦 API: Successfully deleted item ${sku}`);
                return data;
            } else {
                console.error(`❌ API: Failed to delete item ${sku}:`, data.error);
                throw new Error(data.error);
            }
        } catch (error) {
            console.error(`❌ API: Error deleting item ${sku}:`, error);
            throw error;
        }
    }

    /**
     * Search inventory with filters
     */
    async searchInventory(filters) {
        try {
            console.log('📦 API: Searching inventory with filters:', filters);
            
            const response = await fetch(`${this.baseUrl}/search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(filters)
            });
            
            const data = await response.json();
            
            if (data.success) {
                console.log(`📦 API: Search returned ${data.items.length} items`);
                return data.items;
            } else {
                console.error('❌ API: Search failed:', data.error);
                throw new Error(data.error);
            }
        } catch (error) {
            console.error('❌ API: Error searching inventory:', error);
            throw error;
        }
    }

    /**
     * Get inventory summary statistics
     */
    async getInventorySummary() {
        try {
            console.log('📦 API: Fetching inventory summary...');
            
            const response = await fetch(`${this.baseUrl}/summary`);
            const data = await response.json();
            
            if (data.success) {
                console.log('📦 API: Successfully retrieved inventory summary');
                return data.summary;
            } else {
                console.error('❌ API: Failed to get inventory summary:', data.error);
                // Return fallback data instead of throwing error
                return {
                    total_items: 0,
                    available_items: 0,
                    sold_items: 0,
                    total_cost: 0,
                    total_value: 0,
                    potential_profit: 0
                };
            }
        } catch (error) {
            console.error('❌ API: Error fetching inventory summary:', error);
            // Return fallback data instead of throwing error
            return {
                total_items: 0,
                available_items: 0,
                sold_items: 0,
                total_cost: 0,
                total_value: 0,
                potential_profit: 0
            };
        }
    }

    /**
     * Get list of brands for filtering
     */
    async getBrandsList() {
        try {
            console.log('📦 API: Fetching brands list...');
            
            const response = await fetch(`${this.baseUrl}/brands`);
            const data = await response.json();
            
            if (data.success) {
                console.log(`📦 API: Retrieved ${data.brands.length} brands`);
                return data.brands;
            } else {
                console.error('❌ API: Failed to get brands list:', data.error);
                return [];
            }
        } catch (error) {
            console.error('❌ API: Error fetching brands list:', error);
            return [];
        }
    }

    /**
     * Check if item can be edited
     */
    async checkEditPermissions(sku) {
        try {
            console.log(`📦 API: Checking edit permissions for SKU: ${sku}`);
            
            const response = await fetch(`${this.baseUrl}/check-edit-permissions/${sku}`);
            const data = await response.json();
            
            if (data.success) {
                console.log(`📦 API: Edit permissions checked for ${sku}:`, data.can_edit);
                return data.can_edit;
            } else {
                console.error(`❌ API: Failed to check edit permissions for ${sku}:`, data.error);
                return false;
            }
        } catch (error) {
            console.error(`❌ API: Error checking edit permissions for ${sku}:`, error);
            return false;
        }
    }

    /**
     * Show user-friendly error messages
     */
    showMessage(message, type = 'info', duration = 3000) {
        // Create a simple toast notification
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} position-fixed`;
        toast.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border-radius: 4px;
        `;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        // Auto-remove after duration
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, duration);
    }
}

// Create global instance
window.InventoryApi = InventoryApi;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (!window.inventoryApi) {
        window.inventoryApi = new InventoryApi();
        console.log('✅ Global InventoryApi instance created');
    }
});