from flask import Blueprint, render_template, request, jsonify
from datetime import datetime
from models import BusinessTransaction, BusinessAsset, BusinessInventory, BusinessCategory
from models import get_financial_summary, get_inventory_summary, get_assets_summary

# Create dashboard blueprint
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def dashboard():
    """Main business dashboard with overview"""
    
    print("💼 Loading business dashboard...")
    
    try:
        # Get current date for filtering
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        
        # Calculate business metrics using helper functions
        metrics = calculate_dashboard_metrics(current_year, current_month)
        
        # Get recent transactions (last 10)
        recent_transactions = BusinessTransaction.query.order_by(
            BusinessTransaction.date.desc(), 
            BusinessTransaction.id.desc()
        ).limit(10).all()
        
        # Get assets and inventory summary
        assets_summary = get_assets_summary()
        inventory_summary = get_inventory_summary()
        
        return render_template('dashboard.html',
                             metrics=metrics,
                             recent_transactions=recent_transactions,
                             assets_summary=assets_summary,
                             inventory_summary=inventory_summary,
                             current_year=current_year,
                             current_month=current_month)
                             
    except Exception as e:
        print(f"❌ Error loading business dashboard: {e}")
        import traceback
        traceback.print_exc()
        
        return render_template('dashboard.html',
                             metrics=None,
                             recent_transactions=[],
                             assets_summary={},
                             inventory_summary={},
                             current_year=current_year,
                             current_month=current_month,
                             error=str(e))

def calculate_dashboard_metrics(year, month):
    """Calculate key business metrics for dashboard"""
    try:
        from sqlalchemy import func, extract
        from models import db
        
        # Current month filter
        monthly_transactions = BusinessTransaction.query.filter(
            extract('year', BusinessTransaction.date) == year,
            extract('month', BusinessTransaction.date) == month
        )
        
        # Calculate monthly totals
        monthly_income = monthly_transactions.filter(
            BusinessTransaction.transaction_type == 'Income'
        ).with_entities(func.sum(BusinessTransaction.amount)).scalar() or 0
        
        monthly_expenses = monthly_transactions.filter(
            BusinessTransaction.transaction_type == 'Expense'
        ).with_entities(func.sum(BusinessTransaction.amount)).scalar() or 0
        
        # Year-to-date metrics
        ytd_transactions = BusinessTransaction.query.filter(
            extract('year', BusinessTransaction.date) == year
        )
        
        ytd_income = ytd_transactions.filter(
            BusinessTransaction.transaction_type == 'Income'
        ).with_entities(func.sum(BusinessTransaction.amount)).scalar() or 0
        
        ytd_expenses = ytd_transactions.filter(
            BusinessTransaction.transaction_type == 'Expense'
        ).with_entities(func.sum(BusinessTransaction.amount)).scalar() or 0
        
        # NEW: All-time metrics
        all_time_income = BusinessTransaction.query.filter(
            BusinessTransaction.transaction_type == 'Income'
        ).with_entities(func.sum(BusinessTransaction.amount)).scalar() or 0
        
        all_time_expenses = BusinessTransaction.query.filter(
            BusinessTransaction.transaction_type == 'Expense'
        ).with_entities(func.sum(BusinessTransaction.amount)).scalar() or 0
        
        return {
            'monthly_revenue': float(monthly_income),
            'monthly_expenses': float(monthly_expenses),
            'monthly_profit': float(monthly_income) - float(monthly_expenses),
            'ytd_revenue': float(ytd_income),
            'ytd_expenses': float(ytd_expenses),
            'ytd_profit': float(ytd_income) - float(ytd_expenses),
            # NEW: All-time metrics
            'all_time_profit': float(all_time_income) - float(all_time_expenses),
            'current_year_profit': float(ytd_income) - float(ytd_expenses),
            'current_month_profit': float(monthly_income) - float(monthly_expenses)
        }
        
    except Exception as e:
        print(f"❌ Error calculating dashboard metrics: {e}")
        return {
            'monthly_revenue': 0,
            'monthly_expenses': 0,
            'monthly_profit': 0,
            'ytd_revenue': 0,
            'ytd_expenses': 0,
            'ytd_profit': 0,
            'all_time_profit': 0,
            'current_year_profit': 0,
            'current_month_profit': 0
        }

@dashboard_bp.route('/api/dashboard/metrics')
def dashboard_metrics_api():
    """API endpoint for dashboard metrics"""
    try:
        # Get current date for filtering
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        
        # Calculate business metrics
        metrics = calculate_dashboard_metrics(current_year, current_month)
        
        return jsonify({
            'success': True,
            'metrics': metrics
        })
        
    except Exception as e:
        print(f"❌ Error getting dashboard metrics: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'metrics': {
                'monthly_revenue': 0,
                'monthly_expenses': 0,
                'monthly_profit': 0,
                'ytd_revenue': 0,
                'ytd_expenses': 0,
                'ytd_profit': 0
            }
        }), 500