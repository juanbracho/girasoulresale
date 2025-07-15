from flask import Blueprint, render_template, request
from blueprints.services.insights_service import InsightsService
from datetime import datetime

# Create insights blueprint
insights_bp = Blueprint('insights', __name__)

@insights_bp.route('/insights')
def ai_insights():
    """AI-powered business insights dashboard"""
    
    print("🧠 Loading AI Insights dashboard...")
    
    try:
        # Get comprehensive business insights
        business_overview = InsightsService.get_business_overview()
        inventory_insights = InsightsService.get_inventory_insights()
        sales_analytics = InsightsService.get_sales_analytics()
        profit_optimization = InsightsService.get_profit_optimization()
        trend_analysis = InsightsService.get_trend_analysis()
        
        # Prepare dashboard data
        dashboard_data = {
            'health_score': business_overview.get('health_score', {}),
            'key_metrics': business_overview.get('key_metrics', {}),
            'quick_insights': business_overview.get('quick_insights', []),
            
            # Inventory Intelligence
            'slow_moving_items': inventory_insights.get('slow_moving_items', [])[:10],  # Top 10
            'inventory_distribution': inventory_insights.get('inventory_distribution', {}),
            'inventory_recommendations': inventory_insights.get('recommendations', []),
            'inventory_summary': inventory_insights.get('summary', {}),
            
            # Sales Analytics
            'category_performance': sales_analytics.get('category_performance', [])[:8],  # Top 8
            'price_range_analysis': sales_analytics.get('price_range_analysis', []),
            'top_performers': sales_analytics.get('top_performers', {}),
            'sales_insights': sales_analytics.get('insights', []),
            
            # Profit Optimization
            'pricing_recommendations': profit_optimization.get('pricing_recommendations', [])[:8],  # Top 8
            'margin_analysis': profit_optimization.get('margin_analysis', {}),
            'profit_insights': profit_optimization.get('profit_insights', []),
            
            # Trend Analysis
            'seasonal_trends': trend_analysis.get('seasonal_trends', []),
            'brand_trends': trend_analysis.get('brand_trends', [])[:10],  # Top 10
            'trend_insights': trend_analysis.get('trend_insights', [])
        }
        
        # Calculate summary statistics for the dashboard
        summary_stats = {
            'total_recommendations': (
                len(inventory_insights.get('recommendations', [])) +
                len(profit_optimization.get('pricing_recommendations', []))
            ),
            'health_status': business_overview.get('health_score', {}).get('status', 'Unknown'),
            'top_category': sales_analytics.get('category_performance', [{}])[0].get('category', 'N/A') if sales_analytics.get('category_performance') else 'N/A',
            'inventory_efficiency': inventory_insights.get('summary', {}).get('listing_efficiency', 0),
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print(f"✅ AI Insights loaded successfully - Health Score: {dashboard_data['health_score'].get('overall_score', 0)}")
        
        return render_template('insights.html',
                             dashboard_data=dashboard_data,
                             summary_stats=summary_stats,
                             page_title="AI Business Insights")
                             
    except Exception as e:
        print(f"❌ Error loading AI insights dashboard: {e}")
        import traceback
        traceback.print_exc()
        
        # Return safe fallback data
        fallback_data = {
            'health_score': {
                'overall_score': 0,
                'status': 'Error',
                'recommendations': ['Unable to load insights at this time']
            },
            'key_metrics': {
                'monthly_revenue': 0,
                'active_listings': 0,
                'inventory_value': 0,
                'items_sold_month': 0
            },
            'quick_insights': [{
                'type': 'error',
                'title': 'Insights Unavailable',
                'message': 'Unable to load AI insights. Please try again later.',
                'action': 'retry'
            }],
            'slow_moving_items': [],
            'inventory_distribution': {'by_category': [], 'by_condition': []},
            'inventory_recommendations': [],
            'inventory_summary': {},
            'category_performance': [],
            'price_range_analysis': [],
            'top_performers': {'top_brands': []},
            'sales_insights': [],
            'pricing_recommendations': [],
            'margin_analysis': {'by_category': []},
            'profit_insights': [],
            'seasonal_trends': [],
            'brand_trends': [],
            'trend_insights': []
        }
        
        fallback_stats = {
            'total_recommendations': 0,
            'health_status': 'Error',
            'top_category': 'N/A',
            'inventory_efficiency': 0,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return render_template('insights.html',
                             dashboard_data=fallback_data,
                             summary_stats=fallback_stats,
                             page_title="AI Business Insights",
                             error=str(e))