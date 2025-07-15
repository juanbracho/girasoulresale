"""
Business Insights Service - AI-Powered Analytics Engine
Orchestrates AI calculations and provides comprehensive business intelligence
"""

import logging
from datetime import datetime, date, timedelta
from blueprints.utils.ai_calculations import (
    BusinessIntelligence, 
    InventoryIntelligence, 
    SalesIntelligence, 
    ProfitOptimization, 
    TrendAnalysis
)
from models import db, BusinessInventory, BusinessTransaction
from sqlalchemy import func, extract, and_

logger = logging.getLogger(__name__)

class InsightsService:
    """Central service for all AI-powered business insights"""
    
    @staticmethod
    def get_business_overview():
        """Get comprehensive business overview with AI insights"""
        try:
            print("🧠 Generating business overview insights...")
            
            # Business health score
            health_data = BusinessIntelligence.calculate_business_health_score()
            
            # Key metrics
            key_metrics = InsightsService._calculate_key_metrics()
            
            # Quick insights
            quick_insights = InsightsService._generate_quick_insights()
            
            return {
                'success': True,
                'health_score': health_data,
                'key_metrics': key_metrics,
                'quick_insights': quick_insights,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating business overview: {e}")
            return {
                'success': False,
                'error': 'Failed to generate business overview',
                'health_score': {'overall_score': 0, 'status': 'Error'},
                'key_metrics': {},
                'quick_insights': []
            }
    
    @staticmethod
    def get_inventory_insights():
        """Get comprehensive inventory analysis and recommendations"""
        try:
            print("📦 Analyzing inventory performance...")
            
            # Slow moving inventory
            slow_movers = InventoryIntelligence.analyze_slow_moving_inventory()
            
            # Inventory distribution
            inventory_distribution = InsightsService._analyze_inventory_distribution()
            
            # Stock performance
            stock_performance = InsightsService._analyze_stock_performance()
            
            # Recommendations
            recommendations = InsightsService._generate_inventory_recommendations(slow_movers, inventory_distribution)
            
            return {
                'success': True,
                'slow_moving_items': slow_movers,
                'inventory_distribution': inventory_distribution,
                'stock_performance': stock_performance,
                'recommendations': recommendations,
                'summary': InsightsService._create_inventory_summary(inventory_distribution, stock_performance)
            }
            
        except Exception as e:
            logger.error(f"Error generating inventory insights: {e}")
            return {
                'success': False,
                'error': 'Failed to generate inventory insights',
                'slow_moving_items': [],
                'inventory_distribution': {},
                'recommendations': []
            }
    
    @staticmethod
    def get_sales_analytics():
        """Get comprehensive sales performance analysis"""
        try:
            print("💰 Analyzing sales performance...")
            
            # Category performance
            category_performance = SalesIntelligence.analyze_category_performance()
            
            # Price range analysis
            price_range_analysis = SalesIntelligence.analyze_price_range_performance()
            
            # Sales trends
            sales_trends = InsightsService._analyze_sales_trends()
            
            # Top performers
            top_performers = InsightsService._identify_top_performers()
            
            return {
                'success': True,
                'category_performance': category_performance,
                'price_range_analysis': price_range_analysis,
                'sales_trends': sales_trends,
                'top_performers': top_performers,
                'insights': InsightsService._generate_sales_insights(category_performance, price_range_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error generating sales analytics: {e}")
            return {
                'success': False,
                'error': 'Failed to generate sales analytics',
                'category_performance': [],
                'price_range_analysis': [],
                'sales_trends': {},
                'top_performers': {}
            }
    
    @staticmethod
    def get_profit_optimization():
        """Get profit optimization recommendations"""
        try:
            print("📈 Generating profit optimization insights...")
            
            # Pricing recommendations
            pricing_recommendations = ProfitOptimization.get_pricing_recommendations()
            
            # Margin analysis
            margin_analysis = InsightsService._analyze_profit_margins()
            
            # Cost optimization
            cost_optimization = InsightsService._analyze_cost_optimization()
            
            return {
                'success': True,
                'pricing_recommendations': pricing_recommendations,
                'margin_analysis': margin_analysis,
                'cost_optimization': cost_optimization,
                'profit_insights': InsightsService._generate_profit_insights(margin_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error generating profit optimization: {e}")
            return {
                'success': False,
                'error': 'Failed to generate profit optimization',
                'pricing_recommendations': [],
                'margin_analysis': {},
                'cost_optimization': []
            }
    
    @staticmethod
    def get_trend_analysis():
        """Get comprehensive trend analysis and forecasting"""
        try:
            print("📊 Analyzing business trends...")
            
            # Seasonal trends
            seasonal_trends = TrendAnalysis.analyze_seasonal_trends()
            
            # Brand trends
            brand_trends = TrendAnalysis.analyze_brand_trends()
            
            # Market predictions
            market_predictions = InsightsService._generate_market_predictions()
            
            return {
                'success': True,
                'seasonal_trends': seasonal_trends,
                'brand_trends': brand_trends,
                'market_predictions': market_predictions,
                'trend_insights': InsightsService._generate_trend_insights(seasonal_trends, brand_trends)
            }
            
        except Exception as e:
            logger.error(f"Error generating trend analysis: {e}")
            return {
                'success': False,
                'error': 'Failed to generate trend analysis',
                'seasonal_trends': [],
                'brand_trends': [],
                'market_predictions': []
            }
    
    # Helper methods for detailed analysis
    
    @staticmethod
    def _calculate_key_metrics():
        """Calculate key business metrics"""
        try:
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            # Total inventory value
            inventory_value = db.session.query(func.sum(BusinessInventory.cost_of_item)).filter(
                BusinessInventory.listing_status != 'sold'
            ).scalar() or 0
            
            # Monthly revenue
            monthly_revenue = db.session.query(func.sum(BusinessTransaction.amount)).filter(
                and_(
                    BusinessTransaction.transaction_type == 'Income',
                    extract('year', BusinessTransaction.date) == current_year,
                    extract('month', BusinessTransaction.date) == current_month
                )
            ).scalar() or 0
            
            # Monthly expenses
            monthly_expenses = db.session.query(func.sum(BusinessTransaction.amount)).filter(
                and_(
                    BusinessTransaction.transaction_type == 'Expense',
                    extract('year', BusinessTransaction.date) == current_year,
                    extract('month', BusinessTransaction.date) == current_month
                )
            ).scalar() or 0
            
            # Active listings
            active_listings = BusinessInventory.query.filter(
                BusinessInventory.listing_status.in_(['inventory', 'listed'])
            ).count()
            
            # Items sold this month
            items_sold_month = BusinessInventory.query.filter(
                and_(
                    BusinessInventory.listing_status == 'sold',
                    extract('year', BusinessInventory.sold_date) == current_year,
                    extract('month', BusinessInventory.sold_date) == current_month
                )
            ).count()
            
            return {
                'inventory_value': round(float(inventory_value), 2),
                'monthly_revenue': round(float(monthly_revenue), 2),
                'monthly_expenses': round(float(monthly_expenses), 2),
                'monthly_profit': round(float(monthly_revenue) - float(monthly_expenses), 2),
                'active_listings': active_listings,
                'items_sold_month': items_sold_month,
                'inventory_turnover': round((items_sold_month / active_listings * 100), 1) if active_listings > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating key metrics: {e}")
            return {}
    
    @staticmethod
    def _generate_quick_insights():
        """Generate quick actionable insights"""
        try:
            insights = []
            
            # Check inventory levels
            total_items = BusinessInventory.query.filter(BusinessInventory.listing_status != 'sold').count()
            if total_items > 100:
                insights.append({
                    'type': 'warning',
                    'title': 'High Inventory Levels',
                    'message': f'You have {total_items} items in inventory. Consider increasing marketing efforts.',
                    'action': 'review_inventory'
                })
            
            # Check recent sales velocity
            thirty_days_ago = date.today() - timedelta(days=30)
            recent_sales = BusinessInventory.query.filter(
                and_(
                    BusinessInventory.listing_status == 'sold',
                    BusinessInventory.sold_date >= thirty_days_ago
                )
            ).count()
            
            if recent_sales < 5:
                insights.append({
                    'type': 'alert',
                    'title': 'Low Sales Velocity',
                    'message': f'Only {recent_sales} items sold in the last 30 days. Review pricing strategy.',
                    'action': 'optimize_pricing'
                })
            elif recent_sales > 20:
                insights.append({
                    'type': 'success',
                    'title': 'Strong Sales Performance',
                    'message': f'{recent_sales} items sold in the last 30 days. Great momentum!',
                    'action': 'maintain_strategy'
                })
            
            # Check profit margins
            recent_sold = db.session.query(BusinessInventory).filter(
                and_(
                    BusinessInventory.listing_status == 'sold',
                    BusinessInventory.sold_date >= thirty_days_ago,
                    BusinessInventory.cost_of_item.isnot(None),
                    BusinessInventory.sold_price.isnot(None)
                )
            ).all()
            
            if recent_sold:
                avg_margin = sum([
                    ((item.sold_price - item.cost_of_item) / item.cost_of_item * 100)
                    for item in recent_sold if item.cost_of_item > 0
                ]) / len(recent_sold)
                
                if avg_margin < 25:
                    insights.append({
                        'type': 'warning',
                        'title': 'Low Profit Margins',
                        'message': f'Average margin is {avg_margin:.1f}%. Consider adjusting pricing strategy.',
                        'action': 'increase_margins'
                    })
            
            return insights[:5]  # Return top 5 insights
            
        except Exception as e:
            logger.error(f"Error generating quick insights: {e}")
            return []
    
    @staticmethod
    def _analyze_inventory_distribution():
        """Analyze current inventory distribution"""
        try:
            # By category
            category_dist = db.session.query(
                BusinessInventory.category,
                func.count(BusinessInventory.id).label('count'),
                func.sum(BusinessInventory.cost_of_item).label('value')
            ).filter(
                BusinessInventory.listing_status != 'sold'
            ).group_by(BusinessInventory.category).all()
            
            # By condition
            condition_dist = db.session.query(
                BusinessInventory.condition,
                func.count(BusinessInventory.id).label('count')
            ).filter(
                BusinessInventory.listing_status != 'sold'
            ).group_by(BusinessInventory.condition).all()
            
            return {
                'by_category': [
                    {
                        'category': cat.category,
                        'count': cat.count,
                        'value': round(float(cat.value or 0), 2)
                    } for cat in category_dist
                ],
                'by_condition': [
                    {
                        'condition': cond.condition,
                        'count': cond.count
                    } for cond in condition_dist
                ]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing inventory distribution: {e}")
            return {'by_category': [], 'by_condition': []}
    
    @staticmethod
    def _analyze_stock_performance():
        """Analyze stock performance metrics"""
        try:
            total_inventory = BusinessInventory.query.filter(BusinessInventory.listing_status != 'sold').count()
            listed_items = BusinessInventory.query.filter(BusinessInventory.listing_status == 'listed').count()
            inventory_items = BusinessInventory.query.filter(BusinessInventory.listing_status == 'inventory').count()
            
            return {
                'total_items': total_inventory,
                'listed_items': listed_items,
                'inventory_items': inventory_items,
                'listing_rate': round((listed_items / total_inventory * 100), 1) if total_inventory > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing stock performance: {e}")
            return {}
    
    @staticmethod
    def _generate_inventory_recommendations(slow_movers, distribution):
        """Generate inventory optimization recommendations"""
        recommendations = []
        
        if len(slow_movers) > 10:
            recommendations.append({
                'priority': 'high',
                'title': 'Address Slow-Moving Inventory',
                'description': f'{len(slow_movers)} items need attention. Consider price reductions or promotions.',
                'action': 'optimize_slow_movers'
            })
        
        # Check category concentration
        if distribution.get('by_category'):
            sorted_categories = sorted(distribution['by_category'], key=lambda x: x['count'], reverse=True)
            if len(sorted_categories) > 0 and sorted_categories[0]['count'] > 30:
                recommendations.append({
                    'priority': 'medium',
                    'title': 'Diversify Inventory',
                    'description': f'High concentration in {sorted_categories[0]["category"]} category. Consider diversifying.',
                    'action': 'diversify_categories'
                })
        
        return recommendations
    
    @staticmethod
    def _create_inventory_summary(distribution, performance):
        """Create inventory summary"""
        return {
            'total_categories': len(distribution.get('by_category', [])),
            'listing_efficiency': performance.get('listing_rate', 0),
            'optimization_potential': 'High' if len(distribution.get('by_category', [])) < 5 else 'Medium'
        }
    
    @staticmethod
    def _analyze_sales_trends():
        """Analyze sales trend patterns"""
        try:
            # Last 6 months sales
            six_months_ago = date.today() - timedelta(days=180)
            monthly_sales = db.session.query(
                extract('month', BusinessInventory.sold_date).label('month'),
                extract('year', BusinessInventory.sold_date).label('year'),
                func.count(BusinessInventory.id).label('count'),
                func.sum(BusinessInventory.sold_price).label('revenue')
            ).filter(
                and_(
                    BusinessInventory.listing_status == 'sold',
                    BusinessInventory.sold_date >= six_months_ago
                )
            ).group_by(
                extract('year', BusinessInventory.sold_date),
                extract('month', BusinessInventory.sold_date)
            ).all()
            
            trends = []
            for sale in monthly_sales:
                trends.append({
                    'month': int(sale.month),
                    'year': int(sale.year),
                    'items_sold': sale.count,
                    'revenue': round(float(sale.revenue or 0), 2)
                })
            
            return {
                'monthly_data': trends,
                'trend_direction': InsightsService._calculate_trend_direction(trends)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sales trends: {e}")
            return {'monthly_data': [], 'trend_direction': 'stable'}
    
    @staticmethod
    def _calculate_trend_direction(trends):
        """Calculate overall trend direction"""
        if len(trends) < 2:
            return 'insufficient_data'
        
        recent_avg = sum([t['items_sold'] for t in trends[-2:]]) / 2
        earlier_avg = sum([t['items_sold'] for t in trends[:2]]) / 2
        
        if recent_avg > earlier_avg * 1.1:
            return 'increasing'
        elif recent_avg < earlier_avg * 0.9:
            return 'decreasing'
        else:
            return 'stable'
    
    @staticmethod
    def _identify_top_performers():
        """Identify top performing items and categories"""
        try:
            # Top brands by revenue
            top_brands = db.session.query(
                BusinessInventory.brand,
                func.sum(BusinessInventory.sold_price).label('revenue'),
                func.count(BusinessInventory.id).label('items_sold')
            ).filter(
                BusinessInventory.listing_status == 'sold'
            ).group_by(BusinessInventory.brand).order_by(
                func.sum(BusinessInventory.sold_price).desc()
            ).limit(5).all()
            
            return {
                'top_brands': [
                    {
                        'brand': brand.brand,
                        'revenue': round(float(brand.revenue or 0), 2),
                        'items_sold': brand.items_sold
                    } for brand in top_brands if brand.brand
                ]
            }
            
        except Exception as e:
            logger.error(f"Error identifying top performers: {e}")
            return {'top_brands': []}
    
    @staticmethod
    def _generate_sales_insights(category_performance, price_analysis):
        """Generate actionable sales insights"""
        insights = []
        
        # Best performing category
        if category_performance:
            best_category = max(category_performance, key=lambda x: x['total_revenue'])
            insights.append(f"{best_category['category']} is your top revenue generator with ${best_category['total_revenue']}")
        
        # Best price range
        if price_analysis:
            best_price_range = max(price_analysis, key=lambda x: x['items_sold'])
            insights.append(f"{best_price_range['price_range']} price range has the highest sales volume")
        
        return insights[:3]
    
    @staticmethod
    def _analyze_profit_margins():
        """Analyze profit margins across different segments"""
        try:
            # By category
            category_margins = db.session.query(
                BusinessInventory.category,
                func.avg((BusinessInventory.sold_price - BusinessInventory.cost_of_item) / BusinessInventory.cost_of_item * 100).label('avg_margin')
            ).filter(
                and_(
                    BusinessInventory.listing_status == 'sold',
                    BusinessInventory.cost_of_item > 0
                )
            ).group_by(BusinessInventory.category).all()
            
            return {
                'by_category': [
                    {
                        'category': cat.category,
                        'avg_margin': round(float(cat.avg_margin or 0), 1)
                    } for cat in category_margins
                ]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing profit margins: {e}")
            return {'by_category': []}
    
    @staticmethod
    def _analyze_cost_optimization():
        """Analyze cost optimization opportunities"""
        return [
            {
                'area': 'Inventory Investment',
                'recommendation': 'Focus on categories with highest margins',
                'impact': 'Medium'
            },
            {
                'area': 'Pricing Strategy',
                'recommendation': 'Optimize underpriced items in high-demand categories',
                'impact': 'High'
            }
        ]
    
    @staticmethod
    def _generate_profit_insights(margin_analysis):
        """Generate profit optimization insights"""
        insights = []
        
        if margin_analysis.get('by_category'):
            best_margin_category = max(margin_analysis['by_category'], key=lambda x: x['avg_margin'])
            insights.append(f"{best_margin_category['category']} has the highest profit margins at {best_margin_category['avg_margin']}%")
        
        return insights
    
    @staticmethod
    def _generate_market_predictions():
        """Generate market predictions based on trends"""
        return [
            {
                'prediction': 'Seasonal uptick expected in Q4',
                'confidence': 75,
                'timeframe': 'Next 3 months'
            },
            {
                'prediction': 'Designer categories showing growth potential',
                'confidence': 60,
                'timeframe': 'Next 6 months'
            }
        ]
    
    @staticmethod
    def _generate_trend_insights(seasonal_trends, brand_trends):
        """Generate trend-based insights"""
        insights = []
        
        if seasonal_trends:
            peak_month = max(seasonal_trends, key=lambda x: x['sales_count'])
            insights.append(f"{peak_month['month']} is typically your strongest sales month")
        
        if brand_trends:
            top_brand = brand_trends[0] if brand_trends else None
            if top_brand:
                insights.append(f"{top_brand['brand']} is your top performing brand")
        
        return insights[:3]