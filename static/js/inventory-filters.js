/**
 * Inventory Filters Manager - Complete Working Implementation
 * Handles both form-based and API-based filtering
 */

class InventoryFilters {
    constructor(apiManager = null) {
        this.apiManager = apiManager;
        this.apiBaseUrl = '/api/inventory';
        this.currentFilters = {
            search: '',
            status: '',
            category: '',
            condition: '',
            brand: '',
            drop: ''
        };
        this.categories = [];
        this.conditions = [];
        this.brands = [];
        this.drops = [];
        this.useFormBasedFiltering = true; // Default to form-based filtering
        
        this.init();
    }

    /**
     * Initialize the filters
     */
    async init() {
        try {
            console.log('📦 Initializing inventory filters...');
            
            // Load current filter state from URL
            this.loadCurrentFiltersFromURL();
            
            // Try to load dynamic filter data
            try {
                await this.loadFilterData();
                this.populateFilterDropdowns();
            } catch (error) {
                console.warn('Could not load dynamic filter data, using static options:', error);
            }
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Initialize filter display
            this.updateFilterDisplay();
            
            console.log('✅ Inventory filters initialized successfully');
            
        } catch (error) {
            console.error('❌ Error initializing inventory filters:', error);
            // Fallback to basic form functionality
            this.setupBasicFormFiltering();
        }
    }

    /**
     * Load current filter values from URL parameters
     */
    loadCurrentFiltersFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        
        this.currentFilters = {
            search: urlParams.get('search') || '',
            status: urlParams.get('status') || '',
            category: urlParams.get('category') || '',
            condition: urlParams.get('condition') || '',
            brand: urlParams.get('brand') || '',
            drop: urlParams.get('drop') || ''
        };
        
        console.log('📦 Loaded filters from URL:', this.currentFilters);
    }

    /**
     * Load categories, conditions, and brands for filters
     */
    async loadFilterData() {
        try {
            // Try to load from API first
            const response = await fetch(`${this.apiBaseUrl}/filter-options`);
            if (response.ok) {
                const data = await response.json();
                
                if (data.success) {
                    this.categories = data.categories || [];
                    this.conditions = data.conditions || [];
                    this.brands = data.brands || [];
                    this.drops = data.drops || [];
                    console.log('✅ Loaded filter data from API');
                    return;
                }
            }
            
            // Fallback: extract from existing DOM
            this.extractFilterDataFromDOM();
            
        } catch (error) {
            console.warn('Failed to load filter data from API, using DOM fallback:', error);
            this.extractFilterDataFromDOM();
        }
    }

    /**
     * Extract filter data from existing DOM elements
     */
    extractFilterDataFromDOM() {
        // Category filter removed from system

        // Extract conditions from select options
        const conditionSelect = document.getElementById('conditionFilter');
        if (conditionSelect) {
            this.conditions = Array.from(conditionSelect.options)
                .map(option => option.value)
                .filter(value => value !== '');
        }

        // Extract brands from select options
        const brandSelect = document.getElementById('brandFilter');
        if (brandSelect) {
            this.brands = Array.from(brandSelect.options)
                .map(option => option.value)
                .filter(value => value !== '');
        }

        // Extract drops from select options
        const dropSelect = document.getElementById('dropFilter');
        if (dropSelect) {
            this.drops = Array.from(dropSelect.options)
                .map(option => option.value)
                .filter(value => value !== '');
        }

        console.log('📦 Extracted filter data from DOM');
    }

    /**
     * Populate filter dropdowns with dynamic data
     */
    populateFilterDropdowns() {
        // Only populate if we have new data and dropdowns are not already populated
        if (this.categories.length > 0) {
            this.populateCategoryFilter();
        }
        if (this.conditions.length > 0) {
            this.populateConditionFilter();
        }
        if (this.brands.length > 0) {
            this.populateBrandFilter();
        }
        if (this.drops.length > 0) {
            this.populateDropFilter();
        }
    }

    // Category filter removed from system

    /**
     * Populate condition filter dropdown
     */
    populateConditionFilter() {
        const conditionFilter = document.getElementById('conditionFilter');
        if (!conditionFilter) return;

        // Check if already populated
        if (conditionFilter.options.length > 1) return;

        // Clear existing options except "All Conditions"
        conditionFilter.innerHTML = '<option value="">All Conditions</option>';
        
        // Add condition options
        this.conditions.forEach(condition => {
            const option = document.createElement('option');
            option.value = condition;
            option.textContent = condition;
            if (condition === this.currentFilters.condition) {
                option.selected = true;
            }
            conditionFilter.appendChild(option);
        });
        
        console.log(`✅ Condition filter populated with ${this.conditions.length} conditions`);
    }

    /**
     * Populate brand filter dropdown
     */
    populateBrandFilter() {
        const brandFilter = document.getElementById('brandFilter');
        if (!brandFilter) return;

        // Check if already populated
        if (brandFilter.options.length > 1) return;

        // Clear existing options except "All Brands"
        brandFilter.innerHTML = '<option value="">All Brands</option>';
        
        // Add brand options
        this.brands.forEach(brand => {
            const option = document.createElement('option');
            option.value = brand;
            option.textContent = brand;
            if (brand === this.currentFilters.brand) {
                option.selected = true;
            }
            brandFilter.appendChild(option);
        });
        
        console.log(`✅ Brand filter populated with ${this.brands.length} brands`);
    }

    /**
     * Populate drop filter dropdown
     */
    populateDropFilter() {
        const dropFilter = document.getElementById('dropFilter');
        if (!dropFilter) return;

        // Check if already populated
        if (dropFilter.options.length > 1) return;

        // Clear existing options except "All Collections"
        dropFilter.innerHTML = '<option value="">All Collections</option>';
        
        // Add drop options
        this.drops.forEach(drop => {
            const option = document.createElement('option');
            option.value = drop;
            option.textContent = drop;
            if (drop === this.currentFilters.drop) {
                option.selected = true;
            }
            dropFilter.appendChild(option);
        });
        
        console.log(`✅ Drop filter populated with ${this.drops.length} drops`);
    }

    /**
     * Setup event listeners for filters
     */
    setupEventListeners() {
        // Search input with debounce
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            let searchTimeout;
            searchInput.value = this.currentFilters.search; // Set current value
            
            searchInput.addEventListener('input', () => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.currentFilters.search = searchInput.value.trim();
                    this.applyFilters();
                }, 500);
            });
        }

        // Filter dropdowns
        const filterElements = [
            { id: 'statusFilter', key: 'status' },
            { id: 'categoryFilter', key: 'category' },
            { id: 'conditionFilter', key: 'condition' },
            { id: 'brandFilter', key: 'brand' },
            { id: 'dropFilter', key: 'drop' }
        ];

        filterElements.forEach(({ id, key }) => {
            const element = document.getElementById(id);
            if (element) {
                // Set current value
                element.value = this.currentFilters[key];
                
                element.addEventListener('change', () => {
                    this.currentFilters[key] = element.value;
                    this.applyFilters();
                });
            }
        });

        // Clear search button
        const clearSearchBtn = document.getElementById('clearSearchBtn');
        if (clearSearchBtn) {
            clearSearchBtn.addEventListener('click', () => {
                this.currentFilters.search = '';
                const searchInput = document.getElementById('searchInput');
                if (searchInput) searchInput.value = '';
                this.applyFilters();
            });
        }

        // Clear all filters button
        const clearAllBtn = document.getElementById('clearAllFiltersBtn');
        if (clearAllBtn) {
            clearAllBtn.addEventListener('click', () => this.clearAllFilters());
        }

        // Setup form-based submission as fallback
        this.setupFormBasedFiltering();
    }

    /**
     * Setup form-based filtering as fallback
     */
    setupFormBasedFiltering() {
        const filterForm = document.getElementById('inventoryFilterForm');
        if (filterForm) {
            // Prevent default form submission if we're using API
            filterForm.addEventListener('submit', (e) => {
                if (!this.useFormBasedFiltering && this.apiManager) {
                    e.preventDefault();
                    this.applyFiltersViaAPI();
                }
            });
        }
    }

    /**
     * Setup basic form filtering (fallback)
     */
    setupBasicFormFiltering() {
        console.log('⚠️ Setting up basic form filtering fallback');
        
        const filterForm = document.getElementById('inventoryFilterForm');
        if (!filterForm) return;

        // Auto-submit form on changes
        const formElements = filterForm.querySelectorAll('select, input');
        formElements.forEach(element => {
            if (element.type === 'search' || element.id === 'searchInput') {
                let timeout;
                element.addEventListener('input', () => {
                    clearTimeout(timeout);
                    timeout = setTimeout(() => filterForm.submit(), 500);
                });
            } else {
                element.addEventListener('change', () => filterForm.submit());
            }
        });
    }

    /**
     * Apply current filters
     */
    applyFilters() {
        if (this.useFormBasedFiltering) {
            this.applyFiltersViaForm();
        } else if (this.apiManager && typeof this.apiManager.searchInventory === 'function') {
            this.applyFiltersViaAPI();
        } else {
            // Fallback to form-based filtering
            console.log('📦 Falling back to form-based filtering');
            this.applyFiltersViaForm();
        }
    }

    /**
     * Apply filters via form submission (URL navigation)
     */
    applyFiltersViaForm() {
        const params = new URLSearchParams();
        
        // Add non-empty filters to URL
        Object.keys(this.currentFilters).forEach(key => {
            if (this.currentFilters[key]) {
                params.set(key, this.currentFilters[key]);
            }
        });
        
        // Navigate to filtered URL
        const newURL = `${window.location.pathname}${params.toString() ? '?' + params.toString() : ''}`;
        window.location.href = newURL;
    }

    /**
     * Apply filters via API (AJAX)
     */
    applyFiltersViaAPI() {
        if (this.apiManager && typeof this.apiManager.searchInventory === 'function') {
            this.apiManager.searchInventory(this.currentFilters);
        } else {
            console.warn('API Manager not available, falling back to form submission');
            this.applyFiltersViaForm();
        }
    }

    /**
     * Clear all filters
     */
    clearAllFilters() {
        // Reset filter values
        this.currentFilters = {
            search: '',
            status: '',
            category: '',
            condition: '',
            brand: '',
            drop: ''
        };

        // Reset form elements
        const searchInput = document.getElementById('searchInput');
        if (searchInput) searchInput.value = '';

        const filterSelects = ['statusFilter', 'categoryFilter', 'conditionFilter', 'brandFilter', 'dropFilter'];
        filterSelects.forEach(id => {
            const select = document.getElementById(id);
            if (select) select.value = '';
        });

        // Apply cleared filters (go to base URL)
        window.location.href = window.location.pathname;
    }

    /**
     * Remove specific filter
     */
    removeFilter(filterName) {
        this.currentFilters[filterName] = '';
        
        // Update form element
        const element = document.getElementById(`${filterName}Filter`) || document.getElementById('searchInput');
        if (element) {
            element.value = '';
        }
        
        this.applyFilters();
    }

    /**
     * Update filter display
     */
    updateFilterDisplay() {
        // Update any filter status displays
        const filterSummary = this.getFilterSummary();
        console.log('📦 Active filters:', filterSummary);
    }

    /**
     * Refresh filter data (call when new categories/conditions are added)
     */
    async refresh() {
        try {
            await this.loadFilterData();
            this.populateFilterDropdowns();
            console.log('✅ Filter data refreshed');
        } catch (error) {
            console.error('❌ Error refreshing filter data:', error);
        }
    }

    /**
     * Get current filter summary
     */
    getFilterSummary() {
        const activeFilters = [];
        
        if (this.currentFilters.search) {
            activeFilters.push(`Search: "${this.currentFilters.search}"`);
        }
        if (this.currentFilters.status) {
            activeFilters.push(`Status: ${this.currentFilters.status}`);
        }
        // Category filter removed
        if (this.currentFilters.condition) {
            activeFilters.push(`Condition: ${this.currentFilters.condition}`);
        }
        if (this.currentFilters.brand) {
            activeFilters.push(`Brand: ${this.currentFilters.brand}`);
        }
        if (this.currentFilters.drop) {
            activeFilters.push(`Collection: ${this.currentFilters.drop}`);
        }
        
        return activeFilters;
    }

    /**
     * Set table view (if needed for compatibility)
     */
    setTableView(viewType) {
        console.log(`📦 Setting table view: ${viewType}`);
        // Implementation depends on your table view requirements
    }
}

// Global functions for backward compatibility
window.clearAllFilters = function() {
    if (window.inventoryFilters) {
        window.inventoryFilters.clearAllFilters();
    } else {
        // Fallback
        window.location.href = window.location.pathname;
    }
};

window.removeFilter = function(filterName) {
    if (window.inventoryFilters) {
        window.inventoryFilters.removeFilter(filterName);
    } else {
        // Fallback: remove from URL
        const url = new URL(window.location);
        url.searchParams.delete(filterName);
        window.location.href = url.toString();
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize filters (will be connected to API manager if available)
    window.inventoryFilters = new InventoryFilters(window.inventoryApiManager || null);
    console.log('✅ Inventory filters initialized globally');
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = InventoryFilters;
}

console.log('📦 Inventory filters module loaded');