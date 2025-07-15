"""
AI-Powered Business Analytics and Calculations
Provides intelligent insights for fashion resale business optimization
"""

import logging
from datetime import datetime, date, timedelta
from sqlalchemy import func, extract, case, and_, or_
from models import db, BusinessInventory, BusinessTransaction
from collections import defaultdict, Counter
import statistics

logger = logging.getLogger(__name__)

class BusinessIntelligence:
    """AI-powered business intelligence engine for fashion resale optimization"""
    
    @staticmethod
    def calculate_business_health_score():
        """Calculate overall business health score (0-100)"""
        try:
            # Get current month data
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            # Revenue trend (30%)
            revenue_score = BusinessIntelligence._calculate_revenue_trend_score(current_year, current_month)
            
            # Inventory efficiency (25%)
            inventory_score = BusinessIntelligence._calculate_inventory_efficiency_score()
            
            # Profit margin health (25%)
            profit_score = BusinessIntelligence._calculate_profit_margin_score()
            
            # Sales velocity (20%)
            velocity_score = BusinessIntelligence._calculate_sales_velocity_score()
            
            # Weighted overall score
            overall_score = (
                revenue_score * 0.30 +
                inventory_score * 0.25 +
                profit_score * 0.25 +
                velocity_score * 0.20
            )
            
            return {
                'overall_score': round(overall_score, 1),
                'revenue_score': round(revenue_score, 1),
                'inventory_score': round(inventory_score, 1),
                'profit_score': round(profit_score, 1),
                'velocity_score': round(velocity_score, 1),
                'status': BusinessIntelligence._get_health_status(overall_score),
                'recommendations': BusinessIntelligence._get_health_recommendations(overall_score)
            }
            
        except Exception as e:
            logger.error(f"Error calculating business health score: {e}")
            return {
                'overall_score': 0,
                'revenue_score': 0,
                'inventory_score': 0,
                'profit_score': 0,
                'velocity_score': 0,
                'status': 'Error',
                'recommendations': ['Unable to calculate health score']
            }
    
    @staticmethod
    def _calculate_revenue_trend_score(year, month):
        """Calculate revenue trend score based on growth"""
        try:
            # Current month revenue
            current_revenue = db.session.query(func.sum(BusinessTransaction.amount)).filter(
                and_(
                    BusinessTransaction.transaction_type == 'Income',
                    extract('year', BusinessTransaction.date) == year,
                    extract('month', BusinessTransaction.date) == month
                )
            ).scalar() or 0
            
            # Previous month revenue
            prev_month = month - 1 if month > 1 else 12
            prev_year = year if month > 1 else year - 1
            
            prev_revenue = db.session.query(func.sum(BusinessTransaction.amount)).filter(
                and_(
                    BusinessTransaction.transaction_type == 'Income',
                    extract('year', BusinessTransaction.date) == prev_year,
                    extract('month', BusinessTransaction.date) == prev_month
                )
            ).scalar() or 0
            
            if prev_revenue == 0:
                return 80 if current_revenue > 0 else 50
            
            growth_rate = ((current_revenue - prev_revenue) / prev_revenue) * 100
            
            # Score based on growth rate
            if growth_rate >= 20:
                return 100
            elif growth_rate >= 10:
                return 85
            elif growth_rate >= 0:
                return 70
            elif growth_rate >= -10:
                return 50
            else:
                return 25
                
        except Exception as e:
            logger.error(f"Error calculating revenue trend score: {e}")
            return 50
    
    @staticmethod
    def _calculate_inventory_efficiency_score():
        """Calculate inventory efficiency based on turnover and age"""
        try:
            # Total inventory value
            total_inventory_value = db.session.query(func.sum(BusinessInventory.cost_of_item)).filter(
                BusinessInventory.listing_status != 'sold'
            ).scalar() or 0
            
            # Items older than 90 days (estimated)
            total_items = BusinessInventory.query.filter(BusinessInventory.listing_status != 'sold').count()
            
            if total_items == 0:
                return 100
            
            # Sales rate (items sold in last 30 days)
            thirty_days_ago = date.today() - timedelta(days=30)
            recent_sales = BusinessInventory.query.filter(
                and_(
                    BusinessInventory.listing_status == 'sold',
                    BusinessInventory.sold_date >= thirty_days_ago
                )
            ).count()
            
            # Calculate efficiency score
            if total_items > 0:
                turnover_rate = (recent_sales / total_items) * 100
                if turnover_rate >= 30:
                    return 100
                elif turnover_rate >= 20:
                    return 85
                elif turnover_rate >= 10:
                    return 70
                elif turnover_rate >= 5:
                    return 55
                else:
                    return 30
            
            return 50
            
        except Exception as e:
            logger.error(f"Error calculating inventory efficiency score: {e}")
            return 50
    
    @staticmethod
    def _calculate_profit_margin_score():
        """Calculate profit margin health score"""
        try:
            # Get sold items with profit data
            sold_items = db.session.query(
                BusinessInventory.cost_of_item,
                BusinessInventory.sold_price
            ).filter(
                and_(
                    BusinessInventory.listing_status == 'sold',
                    BusinessInventory.sold_price.isnot(None),
                    BusinessInventory.cost_of_item.isnot(None)
                )
            ).all()
            
            if not sold_items:
                return 50
            
            margins = []
            for item in sold_items:
                if item.cost_of_item > 0:
                    margin = ((item.sold_price - item.cost_of_item) / item.cost_of_item) * 100
                    margins.append(margin)
            
            if not margins:
                return 50
            
            avg_margin = statistics.mean(margins)
            
            # Score based on average margin
            if avg_margin >= 100:  # 100%+ margin
                return 100
            elif avg_margin >= 75:   # 75%+ margin
                return 90
            elif avg_margin >= 50:   # 50%+ margin
                return 80
            elif avg_margin >= 25:   # 25%+ margin
                return 65
            elif avg_margin >= 0:    # Positive margin
                return 40
            else:                    # Negative margin
                return 20
                
        except Exception as e:
            logger.error(f"Error calculating profit margin score: {e}")
            return 50
    
    @staticmethod
    def _calculate_sales_velocity_score():
        """Calculate sales velocity score"""
        try:
            # Sales in last 30 days
            thirty_days_ago = date.today() - timedelta(days=30)
            recent_sales_count = BusinessInventory.query.filter(
                and_(
                    BusinessInventory.listing_status == 'sold',
                    BusinessInventory.sold_date >= thirty_days_ago
                )
            ).count()
            
            # Score based on sales velocity
            if recent_sales_count >= 20:
                return 100
            elif recent_sales_count >= 15:
                return 85
            elif recent_sales_count >= 10:
                return 70
            elif recent_sales_count >= 5:
                return 55
            elif recent_sales_count >= 1:
                return 40
            else:
                return 20
                
        except Exception as e:
            logger.error(f"Error calculating sales velocity score: {e}")
            return 50
    
    @staticmethod
    def _get_health_status(score):
        """Get health status based on score"""
        if score >= 85:
            return 'Excellent'
        elif score >= 70:
            return 'Good'
        elif score >= 55:
            return 'Fair'
        elif score >= 40:
            return 'Poor'
        else:
            return 'Critical'
    
    @staticmethod
    def _get_health_recommendations(score):
        """Get recommendations based on health score"""
        if score >= 85:
            return [
                'Business is performing excellently',
                'Continue current strategies',
                'Consider expanding successful categories'
            ]
        elif score >= 70:
            return [
                'Business is performing well',
                'Focus on optimizing underperforming areas',
                'Increase marketing for slow-moving inventory'
            ]
        elif score >= 55:
            return [
                'Business needs attention',
                'Review pricing strategy',
                'Identify and liquidate slow-moving inventory',
                'Focus on high-margin categories'
            ]
        else:
            return [
                'Business requires immediate action',
                'Review all pricing strategies',
                'Liquidate old inventory',
                'Focus on proven high-performing categories',
                'Consider reducing inventory investment'
            ]

class InventoryIntelligence:
    """Advanced inventory analysis and optimization"""
    
    @staticmethod
    def analyze_slow_moving_inventory():
        """Identify slow-moving inventory items"""
        try:
            # Items that have been in inventory for estimated 60+ days
            slow_moving_items = BusinessInventory.query.filter(
                and_(
                    BusinessInventory.listing_status == 'inventory',
                    # Add age estimation logic here when date_added is available
                )
            ).all()
            
            analyzed_items = []
            for item in slow_moving_items:
                analyzed_items.append({
                    'sku': item.sku,
                    'name': item.name,
                    'category': item.category,
                    'brand': item.brand,
                    'cost': float(item.cost_of_item or 0),
                    'current_price': float(item.selling_price or 0),
                    'recommendation': InventoryIntelligence._get_item_recommendation(item),
                    'suggested_action': InventoryIntelligence._get_suggested_action(item)
                })
            
            return analyzed_items[:20]  # Top 20 slow movers
            
        except Exception as e:
            logger.error(f"Error analyzing slow moving inventory: {e}")
            return []
    
    @staticmethod
    def _get_item_recommendation(item):
        """Get recommendation for specific item"""
        cost = float(item.cost_of_item or 0)
        price = float(item.selling_price or 0)
        
        if cost == 0:
            return "Review pricing - no cost data"
        
        margin = ((price - cost) / cost) * 100
        
        if margin > 100:
            return "Consider price reduction to increase velocity"
        elif margin > 50:
            return "Price is reasonable - increase marketing"
        elif margin > 0:
            return "Low margin - consider bundling or promotion"
        else:
            return "Selling at loss - immediate action required"
    
    @staticmethod
    def _get_suggested_action(item):
        """Get suggested action for item"""
        cost = float(item.cost_of_item or 0)
        price = float(item.selling_price or 0)
        
        if cost == 0:
            return "update_pricing"
        
        margin = ((price - cost) / cost) * 100
        
        if margin > 100:
            return "reduce_price"
        elif margin > 50:
            return "increase_marketing"
        elif margin > 0:
            return "create_bundle"
        else:
            return "liquidate"

class SalesIntelligence:
    """Advanced sales pattern analysis"""
    
    @staticmethod
    def analyze_category_performance():
        """Analyze performance by category"""
        try:
            # Get sold items grouped by category
            category_data = db.session.query(
                BusinessInventory.category,
                func.count(BusinessInventory.id).label('items_sold'),
                func.avg(BusinessInventory.sold_price).label('avg_price'),
                func.sum(BusinessInventory.sold_price).label('total_revenue'),
                func.avg(BusinessInventory.cost_of_item).label('avg_cost')
            ).filter(
                BusinessInventory.listing_status == 'sold'
            ).group_by(BusinessInventory.category).all()
            
            categories = []
            for category in category_data:
                avg_cost = float(category.avg_cost or 0)
                avg_price = float(category.avg_price or 0)
                margin = ((avg_price - avg_cost) / avg_cost * 100) if avg_cost > 0 else 0
                
                categories.append({
                    'category': category.category,
                    'items_sold': category.items_sold,
                    'avg_selling_price': round(avg_price, 2),
                    'total_revenue': round(float(category.total_revenue or 0), 2),
                    'avg_margin_percent': round(margin, 1),
                    'performance_rating': SalesIntelligence._rate_category_performance(category.items_sold, margin)
                })
            
            # Sort by total revenue descending
            categories.sort(key=lambda x: x['total_revenue'], reverse=True)
            
            return categories
            
        except Exception as e:
            logger.error(f"Error analyzing category performance: {e}")
            return []
    
    @staticmethod
    def _rate_category_performance(items_sold, margin):
        """Rate category performance"""
        if items_sold >= 10 and margin >= 50:
            return 'Excellent'
        elif items_sold >= 5 and margin >= 25:
            return 'Good'
        elif items_sold >= 3 or margin >= 0:
            return 'Fair'
        else:
            return 'Poor'
    
    @staticmethod
    def analyze_price_range_performance():
        """Analyze performance by price ranges"""
        try:
            sold_items = db.session.query(
                BusinessInventory.sold_price,
                BusinessInventory.cost_of_item
            ).filter(
                and_(
                    BusinessInventory.listing_status == 'sold',
                    BusinessInventory.sold_price.isnot(None)
                )
            ).all()
            
            price_ranges = {
                'Under $25': {'count': 0, 'revenue': 0, 'margin': []},
                '$25-$50': {'count': 0, 'revenue': 0, 'margin': []},
                '$51-$100': {'count': 0, 'revenue': 0, 'margin': []},
                '$101-$200': {'count': 0, 'revenue': 0, 'margin': []},
                'Over $200': {'count': 0, 'revenue': 0, 'margin': []}
            }
            
            for item in sold_items:
                price = float(item.sold_price or 0)
                cost = float(item.cost_of_item or 0)
                margin = ((price - cost) / cost * 100) if cost > 0 else 0
                
                if price < 25:
                    range_key = 'Under $25'
                elif price < 51:
                    range_key = '$25-$50'
                elif price < 101:
                    range_key = '$51-$100'
                elif price < 201:
                    range_key = '$101-$200'
                else:
                    range_key = 'Over $200'
                
                price_ranges[range_key]['count'] += 1
                price_ranges[range_key]['revenue'] += price
                price_ranges[range_key]['margin'].append(margin)
            
            # Format results
            results = []
            for range_name, data in price_ranges.items():
                if data['count'] > 0:
                    avg_margin = statistics.mean(data['margin']) if data['margin'] else 0
                    results.append({
                        'price_range': range_name,
                        'items_sold': data['count'],
                        'total_revenue': round(data['revenue'], 2),
                        'avg_revenue_per_item': round(data['revenue'] / data['count'], 2),
                        'avg_margin_percent': round(avg_margin, 1),
                        'performance': SalesIntelligence._rate_price_range_performance(data['count'], avg_margin)
                    })
            
            return sorted(results, key=lambda x: x['items_sold'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error analyzing price range performance: {e}")
            return []
    
    @staticmethod
    def _rate_price_range_performance(count, margin):
        """Rate price range performance"""
        if count >= 15 and margin >= 50:
            return 'Excellent'
        elif count >= 8 and margin >= 25:
            return 'Good'
        elif count >= 3 or margin >= 0:
            return 'Fair'
        else:
            return 'Poor'

class ProfitOptimization:
    """Profit optimization and pricing recommendations"""
    
    @staticmethod
    def get_pricing_recommendations():
        """Get AI-powered pricing recommendations"""
        try:
            # Analyze current inventory pricing vs market performance
            inventory_items = BusinessInventory.query.filter(
                BusinessInventory.listing_status == 'inventory'
            ).all()
            
            recommendations = []
            for item in inventory_items:
                recommendation = ProfitOptimization._analyze_item_pricing(item)
                if recommendation:
                    recommendations.append(recommendation)
            
            # Sort by potential impact
            recommendations.sort(key=lambda x: x['potential_impact'], reverse=True)
            
            return recommendations[:15]  # Top 15 recommendations
            
        except Exception as e:
            logger.error(f"Error getting pricing recommendations: {e}")
            return []
    
    @staticmethod
    def _analyze_item_pricing(item):
        """Analyze individual item pricing"""
        try:
            # Get similar sold items for comparison
            similar_sold = db.session.query(BusinessInventory).filter(
                and_(
                    BusinessInventory.listing_status == 'sold',
                    BusinessInventory.category == item.category,
                    BusinessInventory.brand == item.brand,
                    BusinessInventory.condition == item.condition
                )
            ).all()
            
            if not similar_sold:
                return None
            
            sold_prices = [float(sold_item.sold_price or 0) for sold_item in similar_sold if sold_item.sold_price]
            
            if not sold_prices:
                return None
            
            avg_market_price = statistics.mean(sold_prices)
            current_price = float(item.selling_price or 0)
            cost = float(item.cost_of_item or 0)
            
            # Calculate recommendation
            price_difference = current_price - avg_market_price
            potential_impact = abs(price_difference)
            
            if price_difference > 20:  # Overpriced
                action = "reduce_price"
                new_price = avg_market_price * 0.95  # 5% below market average
                reason = f"Currently ${price_difference:.2f} above market average"
            elif price_difference < -20:  # Underpriced
                action = "increase_price"
                new_price = avg_market_price * 0.90  # 10% below market average
                reason = f"Currently ${abs(price_difference):.2f} below market potential"
            else:
                return None  # Price is reasonable
            
            return {
                'sku': item.sku,
                'name': item.name,
                'category': item.category,
                'brand': item.brand,
                'current_price': current_price,
                'suggested_price': round(new_price, 2),
                'market_average': round(avg_market_price, 2),
                'action': action,
                'reason': reason,
                'potential_impact': potential_impact,
                'confidence': min(len(similar_sold) * 10, 100)  # Confidence based on sample size
            }
            
        except Exception as e:
            logger.error(f"Error analyzing item pricing for {item.sku}: {e}")
            return None

class TrendAnalysis:
    """Business trend analysis and forecasting"""
    
    @staticmethod
    def analyze_seasonal_trends():
        """Analyze seasonal sales trends"""
        try:
            # Get sales by month
            monthly_sales = db.session.query(
                extract('month', BusinessInventory.sold_date).label('month'),
                func.count(BusinessInventory.id).label('sales_count'),
                func.sum(BusinessInventory.sold_price).label('revenue')
            ).filter(
                and_(
                    BusinessInventory.listing_status == 'sold',
                    BusinessInventory.sold_date.isnot(None)
                )
            ).group_by(extract('month', BusinessInventory.sold_date)).all()
            
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            seasonal_data = []
            for i in range(1, 13):
                month_data = next((sale for sale in monthly_sales if sale.month == i), None)
                seasonal_data.append({
                    'month': months[i-1],
                    'sales_count': month_data.sales_count if month_data else 0,
                    'revenue': float(month_data.revenue or 0) if month_data else 0
                })
            
            return seasonal_data
            
        except Exception as e:
            logger.error(f"Error analyzing seasonal trends: {e}")
            return []
    
    @staticmethod
    def analyze_brand_trends():
        """Analyze brand performance trends"""
        try:
            brand_performance = db.session.query(
                BusinessInventory.brand,
                func.count(BusinessInventory.id).label('items_sold'),
                func.avg(BusinessInventory.sold_price).label('avg_price'),
                func.sum(BusinessInventory.sold_price).label('total_revenue')
            ).filter(
                BusinessInventory.listing_status == 'sold'
            ).group_by(BusinessInventory.brand).all()
            
            brands = []
            for brand in brand_performance:
                if brand.brand:  # Only include brands with names
                    brands.append({
                        'brand': brand.brand,
                        'items_sold': brand.items_sold,
                        'avg_price': round(float(brand.avg_price or 0), 2),
                        'total_revenue': round(float(brand.total_revenue or 0), 2),
                        'performance_tier': TrendAnalysis._categorize_brand_performance(brand.items_sold, float(brand.total_revenue or 0))
                    })
            
            # Sort by total revenue
            brands.sort(key=lambda x: x['total_revenue'], reverse=True)
            
            return brands[:15]  # Top 15 brands
            
        except Exception as e:
            logger.error(f"Error analyzing brand trends: {e}")
            return []
    
    @staticmethod
    def _categorize_brand_performance(items_sold, revenue):
        """Categorize brand performance"""
        if items_sold >= 10 and revenue >= 500:
            return 'Top Performer'
        elif items_sold >= 5 and revenue >= 200:
            return 'Strong Performer'
        elif items_sold >= 3 or revenue >= 100:
            return 'Moderate Performer'
        else:
            return 'Emerging Brand'