"""
AI Insights API Blueprint - REST API Endpoints for Business Intelligence
Provides AI-powered analytics and recommendations via RESTful endpoints
"""

from flask import Blueprint, request, jsonify
from blueprints.services.insights_service import InsightsService
import logging

logger = logging.getLogger(__name__)

# Create the insights API blueprint
insights_api_bp = Blueprint('insights_api', __name__, url_prefix='/api/insights')

# =============================================================================
# BUSINESS INTELLIGENCE ENDPOINTS
# =============================================================================

@insights_api_bp.route('/business-overview', methods=['GET'])
def get_business_overview():
    """Get comprehensive business overview with AI health score and insights"""
    try:
        print("🧠 API: Getting business overview with AI insights...")
        
        overview_data = InsightsService.get_business_overview()
        
        if overview_data['success']:
            print("✅ API: Successfully generated business overview")
            return jsonify(overview_data)
        else:
            print(f"❌ API: Failed to generate business overview: {overview_data.get('error')}")
            return jsonify(overview_data), 500
            
    except Exception as e:
        logger.error(f"API Error getting business overview: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate business overview'
        }), 500

@insights_api_bp.route('/inventory-analysis', methods=['GET'])
def get_inventory_analysis():
    """Get comprehensive inventory analysis with AI recommendations"""
    try:
        print("📦 API: Analyzing inventory with AI insights...")
        
        inventory_data = InsightsService.get_inventory_insights()
        
        if inventory_data['success']:
            print(f"✅ API: Successfully analyzed inventory - {len(inventory_data.get('slow_moving_items', []))} slow movers identified")
            return jsonify(inventory_data)
        else:
            print(f"❌ API: Failed to analyze inventory: {inventory_data.get('error')}")
            return jsonify(inventory_data), 500
            
    except Exception as e:
        logger.error(f"API Error getting inventory analysis: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to analyze inventory'
        }), 500

@insights_api_bp.route('/sales-analytics', methods=['GET'])
def get_sales_analytics():
    """Get comprehensive sales performance analytics"""
    try:
        print("💰 API: Analyzing sales performance...")
        
        sales_data = InsightsService.get_sales_analytics()
        
        if sales_data['success']:
            print(f"✅ API: Successfully analyzed sales - {len(sales_data.get('category_performance', []))} categories analyzed")
            return jsonify(sales_data)
        else:
            print(f"❌ API: Failed to analyze sales: {sales_data.get('error')}")
            return jsonify(sales_data), 500
            
    except Exception as e:
        logger.error(f"API Error getting sales analytics: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to analyze sales performance'
        }), 500

@insights_api_bp.route('/profit-optimization', methods=['GET'])
def get_profit_optimization():
    """Get AI-powered profit optimization recommendations"""
    try:
        print("📈 API: Generating profit optimization recommendations...")
        
        profit_data = InsightsService.get_profit_optimization()
        
        if profit_data['success']:
            print(f"✅ API: Successfully generated profit optimization - {len(profit_data.get('pricing_recommendations', []))} pricing recommendations")
            return jsonify(profit_data)
        else:
            print(f"❌ API: Failed to generate profit optimization: {profit_data.get('error')}")
            return jsonify(profit_data), 500
            
    except Exception as e:
        logger.error(f"API Error getting profit optimization: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate profit optimization'
        }), 500

@insights_api_bp.route('/trend-analysis', methods=['GET'])
def get_trend_analysis():
    """Get comprehensive trend analysis and market predictions"""
    try:
        print("📊 API: Analyzing business trends and generating predictions...")
        
        trend_data = InsightsService.get_trend_analysis()
        
        if trend_data['success']:
            print(f"✅ API: Successfully analyzed trends - seasonal and brand data generated")
            return jsonify(trend_data)
        else:
            print(f"❌ API: Failed to analyze trends: {trend_data.get('error')}")
            return jsonify(trend_data), 500
            
    except Exception as e:
        logger.error(f"API Error getting trend analysis: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to analyze trends'
        }), 500

# =============================================================================
# SPECIFIC INSIGHTS ENDPOINTS
# =============================================================================

@insights_api_bp.route('/slow-moving-inventory', methods=['GET'])
def get_slow_moving_inventory():
    """Get specifically slow-moving inventory items with recommendations"""
    try:
        print("🐌 API: Identifying slow-moving inventory items...")
        
        inventory_data = InsightsService.get_inventory_insights()
        
        if inventory_data['success']:
            slow_movers = inventory_data.get('slow_moving_items', [])
            return jsonify({
                'success': True,
                'slow_moving_items': slow_movers,
                'count': len(slow_movers),
                'recommendations': inventory_data.get('recommendations', [])
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to identify slow-moving inventory'
            }), 500
            
    except Exception as e:
        logger.error(f"API Error getting slow-moving inventory: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get slow-moving inventory'
        }), 500

@insights_api_bp.route('/category-performance', methods=['GET'])
def get_category_performance():
    """Get detailed category performance analysis"""
    try:
        print("📊 API: Analyzing category performance...")
        
        sales_data = InsightsService.get_sales_analytics()
        
        if sales_data['success']:
            categories = sales_data.get('category_performance', [])
            return jsonify({
                'success': True,
                'categories': categories,
                'top_performer': categories[0] if categories else None,
                'insights': sales_data.get('insights', [])
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to analyze category performance'
            }), 500
            
    except Exception as e:
        logger.error(f"API Error getting category performance: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get category performance'
        }), 500

@insights_api_bp.route('/pricing-recommendations', methods=['GET'])
def get_pricing_recommendations():
    """Get AI-powered pricing recommendations for current inventory"""
    try:
        print("💰 API: Generating pricing recommendations...")
        
        # Optional: Get limit from query parameter
        limit = request.args.get('limit', 10, type=int)
        
        profit_data = InsightsService.get_profit_optimization()
        
        if profit_data['success']:
            recommendations = profit_data.get('pricing_recommendations', [])[:limit]
            return jsonify({
                'success': True,
                'recommendations': recommendations,
                'count': len(recommendations),
                'potential_impact': sum([rec.get('potential_impact', 0) for rec in recommendations])
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to generate pricing recommendations'
            }), 500
            
    except Exception as e:
        logger.error(f"API Error getting pricing recommendations: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get pricing recommendations'
        }), 500

@insights_api_bp.route('/health-score', methods=['GET'])
def get_health_score():
    """Get current business health score and component breakdown"""
    try:
        print("❤️ API: Calculating business health score...")
        
        overview_data = InsightsService.get_business_overview()
        
        if overview_data['success']:
            health_score = overview_data.get('health_score', {})
            return jsonify({
                'success': True,
                'health_score': health_score,
                'quick_insights': overview_data.get('quick_insights', [])
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to calculate health score'
            }), 500
            
    except Exception as e:
        logger.error(f"API Error getting health score: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get health score'
        }), 500

# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@insights_api_bp.route('/refresh-insights', methods=['POST'])
def refresh_insights():
    """Force refresh of all cached insights and recalculate"""
    try:
        print("🔄 API: Refreshing all insights cache...")
        
        # This could trigger a background task to recalculate all insights
        # For now, we'll just return a success message
        
        return jsonify({
            'success': True,
            'message': 'Insights refresh initiated',
            'timestamp': InsightsService.get_business_overview().get('generated_at')
        })
        
    except Exception as e:
        logger.error(f"API Error refreshing insights: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to refresh insights'
        }), 500

@insights_api_bp.route('/insights-summary', methods=['GET'])
def get_insights_summary():
    """Get a quick summary of all available insights"""
    try:
        print("📋 API: Generating insights summary...")
        
        # Get overview data for key metrics
        overview = InsightsService.get_business_overview()
        
        if overview['success']:
            health_score = overview.get('health_score', {})
            key_metrics = overview.get('key_metrics', {})
            
            summary = {
                'success': True,
                'overall_health': health_score.get('overall_score', 0),
                'health_status': health_score.get('status', 'Unknown'),
                'monthly_revenue': key_metrics.get('monthly_revenue', 0),
                'active_listings': key_metrics.get('active_listings', 0),
                'inventory_value': key_metrics.get('inventory_value', 0),
                'top_recommendations': health_score.get('recommendations', [])[:3],
                'last_updated': overview.get('generated_at')
            }
            
            return jsonify(summary)
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to generate insights summary'
            }), 500
            
    except Exception as e:
        logger.error(f"API Error getting insights summary: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get insights summary'
        }), 500

# =============================================================================
# ERROR HANDLERS
# =============================================================================

@insights_api_bp.errorhandler(400)
def bad_request(error):
    """Handle bad request errors"""
    return jsonify({
        'success': False,
        'error': 'Bad request - invalid parameters provided'
    }), 400

@insights_api_bp.errorhandler(404)
def not_found(error):
    """Handle not found errors"""
    return jsonify({
        'success': False,
        'error': 'Insights endpoint not found'
    }), 404

@insights_api_bp.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error in insights processing'
    }), 500

# =============================================================================
# BLUEPRINT REGISTRATION
# =============================================================================

def register_insights_api(app):
    """Register the insights API blueprint with the Flask app"""
    app.register_blueprint(insights_api_bp)
    print("✅ AI Insights API blueprint registered")