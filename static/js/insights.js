/**
 * AI Insights Dashboard JavaScript
 * Handles dynamic functionality, chart updates, and API interactions
 */

class InsightsManager {
    constructor() {
        this.apiBaseUrl = '/api/insights';
        this.refreshInterval = 300000; // 5 minutes
        this.charts = {};
        this.refreshTimer = null;
        this.isLoading = false;
        
        console.log('🧠 InsightsManager initialized');
    }

    /**
     * Initialize the insights dashboard
     */
    init() {
        try {
            console.log('🧠 Initializing AI Insights dashboard...');
            
            // Setup auto-refresh
            this.setupAutoRefresh();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Initialize interactive elements
            this.initializeInteractiveElements();
            
            console.log('✅ AI Insights dashboard initialized successfully');
            
        } catch (error) {
            console.error('❌ Error initializing insights dashboard:', error);
        }
    }

    /**
     * Setup automatic refresh of insights
     */
    setupAutoRefresh() {
        // Clear any existing timer
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
        }
        
        // Set up new refresh timer (5 minutes)
        this.refreshTimer = setInterval(() => {
            console.log('🔄 Auto-refreshing insights...');
            this.refreshAllInsights();
        }, this.refreshInterval);
        
        console.log(`⏰ Auto-refresh set up for every ${this.refreshInterval / 1000} seconds`);
    }

    /**
     * Setup event listeners for interactive elements
     */
    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.querySelector('button[onclick="refreshInsights()"]');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.refreshAllInsights();
            });
        }
        
        // Insight action buttons
        document.querySelectorAll('button[onclick^="handleInsightAction"]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const action = btn.getAttribute('onclick').match(/'([^']+)'/)[1];
                this.handleInsightAction(action);
            });
        });
        
        // Chart hover effects
        this.setupChartInteractions();
        
        console.log('✅ Event listeners set up');
    }

    /**
     * Initialize interactive elements
     */
    initializeInteractiveElements() {
        // Add tooltips to elements
        this.initializeTooltips();
        
        // Add click handlers for expandable sections
        this.initializeExpandableSections();
        
        // Initialize progress bar animations
        this.animateProgressBars();
        
        console.log('✅ Interactive elements initialized');
    }

    /**
     * Refresh all insights data
     */
    async refreshAllInsights() {
        if (this.isLoading) {
            console.log('⚠️ Refresh already in progress');
            return;
        }

        try {
            this.isLoading = true;
            this.showLoadingOverlay();
            
            console.log('🔄 Refreshing all insights...');
            
            // Refresh health score
            await this.refreshHealthScore();
            
            // Refresh inventory insights
            await this.refreshInventoryInsights();
            
            // Refresh sales analytics
            await this.refreshSalesAnalytics();
            
            // Refresh profit optimization
            await this.refreshProfitOptimization();
            
            // Refresh trend analysis
            await this.refreshTrendAnalysis();
            
            // Update last refresh time
            this.updateLastRefreshTime();
            
            console.log('✅ All insights refreshed successfully');
            
        } catch (error) {
            console.error('❌ Error refreshing insights:', error);
            this.showErrorModal('Failed to refresh insights. Please try again.');
        } finally {
            this.isLoading = false;
            this.hideLoadingOverlay();
        }
    }

    /**
     * Refresh health score data
     */
    async refreshHealthScore() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health-score`);
            const data = await response.json();
            
            if (data.success) {
                this.updateHealthScoreDisplay(data.health_score);
                this.updateQuickInsights(data.quick_insights);
            } else {
                throw new Error(data.error);
            }
            
        } catch (error) {
            console.error('❌ Error refreshing health score:', error);
            throw error;
        }
    }

    /**
     * Refresh inventory insights
     */
    async refreshInventoryInsights() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/inventory-analysis`);
            const data = await response.json();
            
            if (data.success) {
                this.updateInventoryDisplay(data);
                this.updateInventoryChart(data.inventory_distribution);
            } else {
                throw new Error(data.error);
            }
            
        } catch (error) {
            console.error('❌ Error refreshing inventory insights:', error);
            throw error;
        }
    }

    /**
     * Refresh sales analytics
     */
    async refreshSalesAnalytics() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/sales-analytics`);
            const data = await response.json();
            
            if (data.success) {
                this.updateSalesDisplay(data);
                this.updateCategoryChart(data.category_performance);
            } else {
                throw new Error(data.error);
            }
            
        } catch (error) {
            console.error('❌ Error refreshing sales analytics:', error);
            throw error;
        }
    }

    /**
     * Refresh profit optimization
     */
    async refreshProfitOptimization() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/profit-optimization`);
            const data = await response.json();
            
            if (data.success) {
                this.updateProfitDisplay(data);
            } else {
                throw new Error(data.error);
            }
            
        } catch (error) {
            console.error('❌ Error refreshing profit optimization:', error);
            throw error;
        }
    }

    /**
     * Refresh trend analysis
     */
    async refreshTrendAnalysis() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/trend-analysis`);
            const data = await response.json();
            
            if (data.success) {
                this.updateTrendDisplay(data);
                this.updateSeasonalChart(data.seasonal_trends);
            } else {
                throw new Error(data.error);
            }
            
        } catch (error) {
            console.error('❌ Error refreshing trend analysis:', error);
            throw error;
        }
    }

    /**
     * Update health score display
     */
    updateHealthScoreDisplay(healthScore) {
        // Update score value
        const scoreValue = document.querySelector('.score-value');
        if (scoreValue) {
            this.animateNumber(scoreValue, healthScore.overall_score || 0);
        }
        
        // Update status
        const scoreStatus = document.querySelector('.score-status');
        if (scoreStatus) {
            scoreStatus.textContent = healthScore.status || 'Unknown';
            scoreStatus.className = `score-status ${(healthScore.status || '').toLowerCase()}`;
        }
        
        // Update component scores
        this.updateComponentScores(healthScore);
        
        // Update recommendations
        this.updateRecommendations(healthScore.recommendations || []);
    }

    /**
     * Update component scores with animations
     */
    updateComponentScores(healthScore) {
        const components = [
            { key: 'revenue_score', selector: '.score-component:nth-child(1)' },
            { key: 'inventory_score', selector: '.score-component:nth-child(2)' },
            { key: 'profit_score', selector: '.score-component:nth-child(3)' },
            { key: 'velocity_score', selector: '.score-component:nth-child(4)' }
        ];
        
        components.forEach(component => {
            const element = document.querySelector(component.selector);
            if (element) {
                const progressBar = element.querySelector('.progress-bar');
                const scoreText = element.querySelector('small');
                const score = healthScore[component.key] || 0;
                
                if (progressBar) {
                    this.animateProgressBar(progressBar, score);
                }
                
                if (scoreText) {
                    scoreText.textContent = `${score}/100`;
                }
            }
        });
    }

    /**
     * Update quick insights
     */
    updateQuickInsights(insights) {
        const insightsContainer = document.querySelector('.row:has(.insight-card) .row');
        if (!insightsContainer || !insights) return;
        
        // Clear existing insights
        insightsContainer.innerHTML = '';
        
        // Add new insights
        insights.slice(0, 3).forEach(insight => {
            const insightCard = this.createInsightCard(insight);
            insightsContainer.appendChild(insightCard);
        });
    }

    /**
     * Create insight card element
     */
    createInsightCard(insight) {
        const col = document.createElement('div');
        col.className = 'col-md-4 mb-3';
        
        const alertClass = insight.type === 'alert' ? 'danger' : 
                          (insight.type === 'warning' ? 'warning' : 'success');
        
        col.innerHTML = `
            <div class="alert alert-${alertClass} insight-card">
                <h6 class="alert-heading">${insight.title}</h6>
                <p class="mb-2">${insight.message}</p>
                <button class="btn btn-sm btn-outline-${alertClass}" 
                        onclick="handleInsightAction('${insight.action}')">
                    Take Action
                </button>
            </div>
        `;
        
        return col;
    }

    /**
     * Handle insight actions
     */
    handleInsightAction(action) {
        console.log(`🎯 Handling insight action: ${action}`);
        
        switch (action) {
            case 'review_inventory':
                this.scrollToSection('.col-lg-6:has(.fa-boxes)');
                break;
            case 'optimize_pricing':
                this.scrollToSection('.col-lg-6:has(.fa-dollar-sign)');
                break;
            case 'increase_margins':
                this.scrollToSection('.col-lg-6:has(.fa-dollar-sign)');
                break;
            case 'maintain_strategy':
                this.showSuccessMessage('Keep up the great work!');
                break;
            case 'retry':
                this.refreshAllInsights();
                break;
            default:
                console.log(`Unknown action: ${action}`);
        }
    }

    /**
     * Scroll to specific section
     */
    scrollToSection(selector) {
        const element = document.querySelector(selector);
        if (element) {
            element.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
            
            // Add highlight effect
            element.style.transition = 'box-shadow 0.3s ease';
            element.style.boxShadow = '0 0 20px rgba(0, 123, 255, 0.3)';
            
            setTimeout(() => {
                element.style.boxShadow = '';
            }, 2000);
        }
    }

    /**
     * Animate number changes
     */
    animateNumber(element, targetValue, duration = 1000) {
        const startValue = parseInt(element.textContent) || 0;
        const difference = targetValue - startValue;
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function
            const easeOutCubic = 1 - Math.pow(1 - progress, 3);
            const currentValue = Math.round(startValue + (difference * easeOutCubic));
            
            element.textContent = currentValue;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }

    /**
     * Animate progress bars
     */
    animateProgressBar(progressBar, targetWidth, duration = 1000) {
        const startWidth = parseFloat(progressBar.style.width) || 0;
        const difference = targetWidth - startWidth;
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const easeOutCubic = 1 - Math.pow(1 - progress, 3);
            const currentWidth = startWidth + (difference * easeOutCubic);
            
            progressBar.style.width = `${currentWidth}%`;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }

    /**
     * Animate all progress bars on page load
     */
    animateProgressBars() {
        document.querySelectorAll('.progress-bar').forEach(bar => {
            const targetWidth = parseFloat(bar.style.width) || 0;
            bar.style.width = '0%';
            
            setTimeout(() => {
                this.animateProgressBar(bar, targetWidth);
            }, 500);
        });
    }

    /**
     * Setup chart interactions
     */
    setupChartInteractions() {
        // Add chart hover effects and click handlers
        document.querySelectorAll('canvas').forEach(canvas => {
            canvas.addEventListener('mouseover', () => {
                canvas.style.cursor = 'pointer';
            });
            
            canvas.addEventListener('mouseout', () => {
                canvas.style.cursor = 'default';
            });
        });
    }

    /**
     * Initialize tooltips
     */
    initializeTooltips() {
        // Add tooltips to insight elements
        document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(element => {
            new bootstrap.Tooltip(element);
        });
    }

    /**
     * Initialize expandable sections
     */
    initializeExpandableSections() {
        // Add expand/collapse functionality to long lists
        document.querySelectorAll('.slow-moving-items, .category-performance, .pricing-recommendations').forEach(container => {
            if (container.scrollHeight > container.clientHeight) {
                this.addExpandButton(container);
            }
        });
    }

    /**
     * Add expand button to containers
     */
    addExpandButton(container) {
        const expandBtn = document.createElement('button');
        expandBtn.className = 'btn btn-sm btn-outline-primary mt-2';
        expandBtn.textContent = 'Show More';
        expandBtn.onclick = () => {
            if (container.style.maxHeight === 'none') {
                container.style.maxHeight = '';
                expandBtn.textContent = 'Show More';
            } else {
                container.style.maxHeight = 'none';
                expandBtn.textContent = 'Show Less';
            }
        };
        
        container.parentNode.appendChild(expandBtn);
    }

    /**
     * Show loading overlay
     */
    showLoadingOverlay() {
        const overlay = document.getElementById('insightsLoadingOverlay');
        if (overlay) {
            overlay.classList.remove('d-none');
        }
    }

    /**
     * Hide loading overlay
     */
    hideLoadingOverlay() {
        const overlay = document.getElementById('insightsLoadingOverlay');
        if (overlay) {
            overlay.classList.add('d-none');
        }
    }

    /**
     * Show error modal
     */
    showErrorModal(message) {
        const errorModal = document.getElementById('errorModal');
        const errorMessage = document.getElementById('errorMessage');
        
        if (errorModal && errorMessage) {
            errorMessage.textContent = message;
            const modal = new bootstrap.Modal(errorModal);
            modal.show();
        } else {
            alert(message); // Fallback
        }
    }

    /**
     * Show success message
     */
    showSuccessMessage(message) {
        // Create temporary success toast
        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white bg-success border-0 position-fixed';
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 10000;';
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                        data-bs-dismiss="toast"></button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
    }

    /**
     * Update last refresh time
     */
    updateLastRefreshTime() {
        const timeElements = document.querySelectorAll('small:contains("Last updated")');
        const currentTime = new Date().toLocaleString();
        
        timeElements.forEach(element => {
            if (element.textContent.includes('Last updated')) {
                element.textContent = `Last updated: ${currentTime}`;
            }
        });
    }

    /**
     * Update various display sections (placeholder methods)
     */
    updateInventoryDisplay(data) {
        console.log('📦 Updating inventory display', data);
        // Implementation for updating inventory section
    }

    updateSalesDisplay(data) {
        console.log('💰 Updating sales display', data);
        // Implementation for updating sales section
    }

    updateProfitDisplay(data) {
        console.log('📈 Updating profit display', data);
        // Implementation for updating profit section
    }

    updateTrendDisplay(data) {
        console.log('📊 Updating trend display', data);
        // Implementation for updating trend section
    }

    updateInventoryChart(data) {
        console.log('📊 Updating inventory chart', data);
        // Implementation for updating inventory chart
    }

    updateCategoryChart(data) {
        console.log('📊 Updating category chart', data);
        // Implementation for updating category chart
    }

    updateSeasonalChart(data) {
        console.log('📊 Updating seasonal chart', data);
        // Implementation for updating seasonal chart
    }

    updateRecommendations(recommendations) {
        console.log('💡 Updating recommendations', recommendations);
        // Implementation for updating recommendations section
    }

    /**
     * Cleanup method
     */
    destroy() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
        }
        
        // Destroy charts
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        
        console.log('🧠 InsightsManager destroyed');
    }
}

// Global instance
window.InsightsManager = InsightsManager;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (!window.insightsManager) {
        window.insightsManager = new InsightsManager();
        window.insightsManager.init();
    }
});

console.log('🧠 AI Insights JavaScript module loaded');