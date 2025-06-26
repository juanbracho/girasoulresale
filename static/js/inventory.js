/**
 * Inventory Manager - Main controller for inventory functionality
 * CORRECTED VERSION: Fixed all syntax errors and string literal issues
 */

class InventoryManager {
    constructor() {
        console.log('📦 InventoryManager initializing...');
        this.apiManager = null;
        this.modalsManager = null;
        this.filtersManager = null;
        this.isInitialized = false;
        this.inventoryData = [];
        this.initRetryCount = 0;
        this.maxRetries = 5;
    }

    async init() {
        try {
            console.log('📦 Initializing inventory system...');
            
            this.initializeApiManager();
            this.initializeComponentsWhenReady();
            await this.loadInitialData();
            this.setupGlobalFunctions();
            
            this.isInitialized = true;
            console.log('✅ Inventory system fully initialized');
            
        } catch (error) {
            console.error('❌ Error initializing inventory system:', error);
            this.handleInitializationError(error);
        }
    }

    initializeApiManager() {
        if (window.inventoryApi) {
            this.apiManager = window.inventoryApi;
            console.log('✅ Inventory API Manager linked');
        } else {
            console.warn('⚠️ InventoryApi not available yet, will retry...');
            if (this.initRetryCount < this.maxRetries) {
                this.initRetryCount++;
                setTimeout(() => this.initializeApiManager(), 100);
            } else {
                console.error('❌ Failed to initialize API Manager after maximum retries');
            }
        }
    }

    initializeComponentsWhenReady() {
        const self = this;
        
        const checkComponents = () => {
            if (window.InventoryModals && !self.modalsManager) {
                try {
                    self.modalsManager = new window.InventoryModals();
                    self.modalsManager.apiManager = self.apiManager;
                    self.modalsManager.inventoryManager = self;
                    console.log('✅ Inventory Modals Manager initialized');
                } catch (error) {
                    console.error('❌ Error initializing modals manager:', error);
                }
            }

            if (window.InventoryFilters && !self.filtersManager) {
                try {
                    self.filtersManager = new window.InventoryFilters();
                    self.filtersManager.apiManager = self.apiManager;
                    self.filtersManager.inventoryManager = self;
                    console.log('✅ Inventory Filters Manager initialized');
                } catch (error) {
                    console.error('❌ Error initializing filters manager:', error);
                }
            }

            if (!self.modalsManager || !self.filtersManager) {
                setTimeout(() => checkComponents(), 200);
            }
        };

        checkComponents();
    }

    async loadInitialData() {
        try {
            console.log('📦 Loading initial inventory data...');
            
            // NEW: Check if page has server-side filters
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.toString().length > 0) {
                console.log('📦 Server filters detected, skipping API load');
                await this.updateInventoryMetrics();
                return;
            }
            
            if (!this.apiManager) {
                console.warn('⚠️ API Manager not ready, using fallback data');
                return;
            }

            try {
                this.inventoryData = await this.apiManager.getAllInventory();
                console.log('📦 Loaded ' + this.inventoryData.length + ' inventory items');
            } catch (error) {
                console.error('❌ Error loading inventory items:', error);
                this.inventoryData = [];
            }

            this.updateInventoryTable();
            await this.updateInventoryMetrics();
            
        } catch (error) {
            console.error('❌ Error loading initial data:', error);
        }
    }

    updateInventoryTable() {
    try {
        console.log('📦 Updating inventory table...');
        
        // NEW: Check if page has server-side filters
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.toString().length > 0) {
            console.log('📦 Server filters active, keeping existing table');
            return;
        }
        
        const tableBody = document.getElementById('inventoryTableBody');
        if (!tableBody) {
            console.warn('⚠️ Inventory table body not found');
            return;
        }

        if (!this.inventoryData || this.inventoryData.length === 0) {
            const emptyRowHtml = '<tr><td colspan="11" class="text-center py-4">' +
                '<div class="text-muted">' +
                '<i class="fas fa-boxes fa-3x mb-3"></i>' +
                '<p class="mb-0">No inventory items found</p>' +
                '<button type="button" class="btn btn-primary mt-2" onclick="showAddItemModal()">' +
                '<i class="fas fa-plus me-1"></i>Add Your First Item' +
                '</button>' +
                '</div>' +
                '</td></tr>';
            tableBody.innerHTML = emptyRowHtml;
            return;
        }

        const rows = this.inventoryData.map(item => this.generateTableRow(item)).join('');
        tableBody.innerHTML = rows;
        
        const itemCount = document.getElementById('itemCount');
        if (itemCount) {
            itemCount.textContent = 'Showing ' + this.inventoryData.length + ' items';
        }
        
        console.log('✅ Table updated with ' + this.inventoryData.length + ' items');
        
    } catch (error) {
        console.error('❌ Error updating inventory table:', error);
    }
}

    generateTableRow(item) {
        try {
            const statusBadgeClass = this.getStatusBadgeClass(item.listing_status);
            const conditionBadgeClass = this.getConditionBadgeClass(item.condition);
            const canSell = item.listing_status !== 'sold';
            
            const editButton = '<button type="button" class="btn btn-outline-primary" onclick="editItem(\'' + item.sku + '\')" title="Edit Item">' +
                '<i class="fas fa-edit"></i>' +
                '</button>';
            
            const sellButton = canSell ? 
                '<button type="button" class="btn btn-outline-success" onclick="showSellModal(\'' + item.sku + '\')" title="Mark as Sold">' +
                '<i class="fas fa-shopping-cart"></i>' +
                '</button>' : '';
            
            const deleteButton = '<button type="button" class="btn btn-outline-danger" onclick="deleteItem(\'' + item.sku + '\')" title="Delete Item">' +
                '<i class="fas fa-trash"></i>' +
                '</button>';
            
            const categoryText = (item.category || '');
            const categoryDisplay = categoryText.charAt(0).toUpperCase() + categoryText.slice(1);
            
            const statusText = (item.listing_status || '');
            const statusDisplay = statusText.charAt(0).toUpperCase() + statusText.slice(1);
            
            let row = '<tr data-sku="' + item.sku + '" data-status="' + item.listing_status + '">';
            row += '<td><span class="badge bg-primary">' + item.sku + '</span></td>';
            row += '<td><div class="fw-medium">' + this.escapeHtml(item.name) + '</div></td>';
            row += '<td>' + this.escapeHtml(item.brand || '') + '</td>';
            row += '<td><span class="badge bg-secondary">' + this.escapeHtml(categoryDisplay) + '</span></td>';
            row += '<td>' + this.escapeHtml(item.size || '') + '</td>';
            row += '<td><span class="badge ' + conditionBadgeClass + '">' + this.escapeHtml(item.condition || '') + '</span></td>';
            row += '<td class="text-end">$' + parseFloat(item.cost_of_item || 0).toFixed(2) + '</td>';
            row += '<td class="text-end">$' + parseFloat(item.selling_price || 0).toFixed(2) + '</td>';
            row += '<td><span class="badge ' + statusBadgeClass + '">' + this.escapeHtml(statusDisplay) + '</span></td>';
            row += '<td>' + (item.date_added ? new Date(item.date_added).toLocaleDateString() : '-') + '</td>';
            row += '<td><div class="btn-group btn-group-sm" role="group">' + editButton + sellButton + deleteButton + '</div></td>';
            row += '</tr>';
            
            return row;
            
        } catch (error) {
            console.error('❌ Error generating table row:', error);
            return '<tr><td colspan="11" class="text-danger">Error displaying item</td></tr>';
        }
    }

    getStatusBadgeClass(status) {
        switch (status) {
            case 'sold': return 'bg-success';
            case 'listed': return 'bg-info';
            case 'inventory': return 'bg-primary';
            case 'kept': return 'bg-warning';
            default: return 'bg-secondary';
        }
    }
    
    getConditionBadgeClass(condition) {
        switch (condition) {
            case 'NWT': return 'bg-success';
            case 'NWOT': return 'bg-info';
            case 'good': return 'bg-primary';
            case 'fair': return 'bg-warning';
            case 'poor': return 'bg-danger';
            default: return 'bg-secondary';
        }
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    async updateInventoryMetrics() {
        try {
            console.log('📦 Updating inventory metrics...');
            
            if (!this.apiManager) {
                console.warn('⚠️ API Manager not ready for metrics update');
                return;
            }

            const summary = await this.apiManager.getInventorySummary();
            
            this.updateMetricCard('totalItemsCount', summary.total_items || 0);
            this.updateMetricCard('availableItemsCount', summary.available_items || 0);
            this.updateMetricCard('totalValueAmount', '$' + (summary.total_value || 0).toFixed(2));
            this.updateMetricCard('potentialProfitAmount', '$' + (summary.potential_profit || 0).toFixed(2));
            
            console.log('✅ Inventory metrics updated');
            
        } catch (error) {
            console.error('❌ Error updating inventory metrics:', error);
            
            this.updateMetricCard('totalItemsCount', '0');
            this.updateMetricCard('availableItemsCount', '0');
            this.updateMetricCard('totalValueAmount', '$0.00');
            this.updateMetricCard('potentialProfitAmount', '$0.00');
        }
    }

    updateMetricCard(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    async refreshInventoryData() {
        try {
            console.log('📦 Refreshing inventory data...');
            
            this.showLoadingState();
            await this.loadInitialData();
            this.hideLoadingState();
            this.showMessage('Inventory data refreshed successfully', 'success');
            
        } catch (error) {
            console.error('❌ Error refreshing inventory data:', error);
            this.hideLoadingState();
            this.showMessage('Error refreshing inventory data', 'danger');
        }
    }

    showLoadingState() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.remove('d-none');
        }
    }

    hideLoadingState() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.add('d-none');
        }
    }

    showMessage(message, type, duration) {
        type = type || 'info';
        duration = duration || 3000;
        
        const toast = document.createElement('div');
        toast.className = 'alert alert-' + type + ' position-fixed';
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border-radius: 4px;';
        
        const iconClass = type === 'success' ? 'check' : type === 'danger' ? 'exclamation-triangle' : 'info';
        toast.innerHTML = '<i class="fas fa-' + iconClass + ' me-2"></i>' + this.escapeHtml(message);
        
        document.body.appendChild(toast);
        
        setTimeout(function() {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, duration);
    }

    setupGlobalFunctions() {
        console.log('📦 Setting up global functions...');
        
        const self = this;
        
        window.showAddItemModal = function() {
            console.log('📦 showAddItemModal called');
            if (self.modalsManager && self.modalsManager.showAddItemModal) {
                self.modalsManager.showAddItemModal();
            } else {
                self.showMessage('Modal system is loading. Please try again in a moment.', 'info');
            }
        };
        
        window.editItem = function(sku) {
            console.log('📦 editItem called for SKU: ' + sku);
            if (self.modalsManager && self.modalsManager.editItem) {
                self.modalsManager.editItem(sku);
            } else {
                self.showMessage('Edit functionality is loading. Please try again in a moment.', 'info');
            }
        };
        
        window.showSellModal = function(sku) {
            console.log('📦 showSellModal called for SKU: ' + sku);
            if (self.modalsManager && self.modalsManager.showSellModal) {
                self.modalsManager.showSellModal(sku);
            } else {
                self.showMessage('Sell functionality is loading. Please try again in a moment.', 'info');
            }
        };
        
        window.deleteItem = async function(sku) {
            console.log('📦 deleteItem called for SKU: ' + sku);
            
            try {
                const confirmed = await window.confirmDialog(
                    'Are you sure you want to delete this item? This action cannot be undone.',
                    'Delete Item'
                );
                
                if (!confirmed) {
                    return;
                }
                
                if (self.apiManager) {
                    try {
                        await self.apiManager.deleteInventoryItem(sku);
                        await self.refreshInventoryData();
                        self.showMessage('Item deleted successfully', 'success');
                    } catch (error) {
                        console.error('❌ Error deleting item:', error);
                        self.showMessage('Error deleting item. Please try again.', 'danger');
                    }
                } else {
                    self.showMessage('System is loading. Please try again in a moment.', 'info');
                }
            } catch (error) {
                console.error('❌ Error in deleteItem function:', error);
                self.showMessage('Error processing delete request.', 'danger');
            }
        };
        
        window.saveInventoryItem = function() {
            console.log('📦 saveInventoryItem called');
            if (self.modalsManager && self.modalsManager.saveInventoryItem) {
                self.modalsManager.saveInventoryItem();
            } else {
                self.showMessage('Save functionality is loading. Please try again in a moment.', 'info');
            }
        };
        
        window.confirmSellItem = function() {
            console.log('📦 confirmSellItem called');
            if (self.modalsManager && self.modalsManager.confirmSellItem) {
                self.modalsManager.confirmSellItem();
            } else {
                self.showMessage('Sell functionality is loading. Please try again in a moment.', 'info');
            }
        };
        
        window.refreshInventoryData = function() {
            self.refreshInventoryData();
        };
        
        window.clearAllFilters = function() {
        console.log('📦 clearAllFilters called');
        if (self.filtersManager && self.filtersManager.clearAllFilters) {
            self.filtersManager.clearAllFilters();
        } else {
            // NEW: Form-based fallback for server filtering
            window.location.href = window.location.pathname;
        }
    };
        window.setTableView = function(viewType) {
            if (self.filtersManager && self.filtersManager.setTableView) {
                self.filtersManager.setTableView(viewType);
            }
        };
        
        console.log('✅ Global functions set up successfully');
    }

    handleInitializationError(error) {
        console.error('❌ Inventory system initialization failed:', error);
        this.showMessage('Error loading inventory system. Please refresh the page.', 'danger', 5000);
        this.setupBasicFallbackFunctions();
    }

    setupBasicFallbackFunctions() {
        console.log('⚠️ Setting up fallback functions...');
        
        const self = this;
        
        window.showAddItemModal = function() {
            self.showMessage('System is loading. Please refresh the page and try again.', 'warning');
        };
        
        window.editItem = function() {
            self.showMessage('System is loading. Please refresh the page and try again.', 'warning');
        };
        
        window.showSellModal = function() {
            self.showMessage('System is loading. Please refresh the page and try again.', 'warning');
        };
        
        window.deleteItem = function() {
            self.showMessage('System is loading. Please refresh the page and try again.', 'warning');
        };
        
        window.refreshInventoryData = function() {
            location.reload();
        };
    }
}

window.InventoryManager = InventoryManager;

document.addEventListener('DOMContentLoaded', function() {
    if (!window.inventoryManager) {
        window.inventoryManager = new InventoryManager();
        console.log('✅ Global InventoryManager instance created');
    }
});