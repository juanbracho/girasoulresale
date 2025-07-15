from flask import Blueprint, render_template, request
from datetime import datetime
from sqlalchemy import func, extract, case
from models import db, BusinessTransaction

# Create financial blueprint
financial_bp = Blueprint('financial', __name__)

@financial_bp.route('/financial')
def financial():
    """Enhanced business financial overview with comprehensive data"""
    
    print("💰 Loading enhanced business financial page...")
    
    try:
        # Get filter parameters - FIXED: Handle "all" string for year
        year_param = request.args.get('year', datetime.now().year)
        if year_param == 'all':
            year = 'all'
        else:
            year = int(year_param)
        month = request.args.get('month', datetime.now().month)
        if month != 'all':
            month = int(month)
        category = request.args.get('category', 'all')
        page = request.args.get('page', 1, type=int)

        # Get available years for filter
        available_years = get_available_years()

        # Default to current year if no data
        if not available_years:
            if isinstance(year, int):
                available_years = [year - 1, year, year + 1]
            else:
                available_years = [datetime.now().year - 1, datetime.now().year, datetime.now().year + 1]

        # Get available months (all 12 months)
        available_months = get_available_months()

        # Get available categories
        available_categories = get_available_categories()

        # Get financial summary
        financial_summary = calculate_financial_summary(year, month, category)

        # Get recent business transactions with pagination (50 per page)
        per_page = 50
        business_transactions, pagination_info = get_filtered_transactions_paginated(year, month, category, page, per_page)

        # Get category breakdown
        category_breakdown = get_category_breakdown(year, month, category)

        # Get current month name
        if year == 'all':
            if month != 'all':
                current_month_name = datetime(datetime.now().year, int(month), 1).strftime('%B')
            else:
                current_month_name = datetime.now().strftime('%B')
            current_year = 'All Years'
        else:
            if month != 'all':
                current_month_name = datetime(year, int(month), 1).strftime('%B')
            else:
                current_month_name = datetime(year, datetime.now().month, 1).strftime('%B')
            current_year = year
        
        return render_template('financial.html',
                             financial_summary=financial_summary,
                             business_transactions=business_transactions,
                             category_breakdown=category_breakdown,
                             available_years=available_years,
                             available_months=available_months,
                             available_categories=available_categories,
                             selected_year=year,  # This will be 'all' or integer
                             selected_month=month,
                             selected_category=category,
                             current_year=current_year,
                             current_month_name=current_month_name,
                             pagination=pagination_info)
    except Exception as e:
        print(f"❌ Error loading financial page: {e}")
        import traceback
        traceback.print_exc()
        
        return render_template('financial.html',
                             financial_summary={},
                             business_transactions=[],
                             category_breakdown=[],
                             available_years=['all', datetime.now().year],
                             available_months=get_available_months(),
                             available_categories=[],
                             selected_year=year if 'year' in locals() else datetime.now().year,
                             selected_month=month if 'month' in locals() else 'all',
                             selected_category=category if 'category' in locals() else 'all',
                             current_year=datetime.now().year,
                             current_month_name=datetime.now().strftime('%B'),
                             pagination=None,
                             error=str(e))

def get_available_years():
    """Get years that have transaction data, plus 'All Years' option"""
    try:
        results = db.session.query(
            extract('year', BusinessTransaction.date).label('year')
        ).distinct().order_by('year').all()
        
        years = [int(result.year) for result in results if result.year]
        
        # Always include current year
        current_year = datetime.now().year
        if current_year not in years:
            years.append(current_year)
        
        # Add "All Years" option at the beginning
        years_with_all = ['all'] + sorted(years)
        
        return years_with_all
        
    except Exception as e:
        print(f"❌ Error getting available years: {e}")
        return ['all', datetime.now().year]

def get_available_months():
    """Get all 12 months for filter dropdown"""
    months = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]
    return months

def calculate_financial_summary(year, month, category='all'):
    """Calculate financial summary for given period"""
    try:
        # Monthly totals
        if year == 'all':
            monthly_query = db.session.query(
                BusinessTransaction.transaction_type,
                func.sum(BusinessTransaction.amount).label('total')
            )
        else:
            monthly_query = db.session.query(
                BusinessTransaction.transaction_type,
                func.sum(BusinessTransaction.amount).label('total')
            ).filter(
                extract('year', BusinessTransaction.date) == year
            )
        
        if month != 'all':
            monthly_query = monthly_query.filter(
                extract('month', BusinessTransaction.date) == int(month)
            )
        
        # NEW: Category filter
        if category != 'all':
            monthly_query = monthly_query.filter(BusinessTransaction.category == category)
        
        monthly_results = monthly_query.group_by(
            BusinessTransaction.transaction_type
        ).all()
        
        monthly_revenue = 0
        monthly_expenses = 0
        
        for transaction_type, total in monthly_results:
            if transaction_type == 'Income':
                monthly_revenue = float(total)
            elif transaction_type == 'Expense':
                monthly_expenses = float(total)
        
        # YTD totals (same logic for consistency)
        if year == 'all':
            ytd_query = db.session.query(
                BusinessTransaction.transaction_type,
                func.sum(BusinessTransaction.amount).label('total')
            )
        else:
            ytd_query = db.session.query(
                BusinessTransaction.transaction_type,
                func.sum(BusinessTransaction.amount).label('total')
            ).filter(
                extract('year', BusinessTransaction.date) == year
            )
        
        if month != 'all':
            ytd_query = ytd_query.filter(
                extract('month', BusinessTransaction.date) <= int(month)
            )
        
        # NEW: Category filter
        if category != 'all':
            ytd_query = ytd_query.filter(BusinessTransaction.category == category)
        
        ytd_results = ytd_query.group_by(
            BusinessTransaction.transaction_type
        ).all()
        
        ytd_revenue = 0
        ytd_expenses = 0
        
        for transaction_type, total in ytd_results:
            if transaction_type == 'Income':
                ytd_revenue = float(total)
            elif transaction_type == 'Expense':
                ytd_expenses = float(total)
        
        return {
            'monthly_revenue': monthly_revenue,
            'monthly_expenses': monthly_expenses,
            'monthly_profit': monthly_revenue - monthly_expenses,
            'ytd_revenue': ytd_revenue,
            'ytd_expenses': ytd_expenses,
            'ytd_profit': ytd_revenue - ytd_expenses
        }
        
    except Exception as e:
        print(f"❌ Error calculating financial summary: {e}")
        return {
            'monthly_revenue': 0,
            'monthly_expenses': 0,
            'monthly_profit': 0,
            'ytd_revenue': 0,
            'ytd_expenses': 0,
            'ytd_profit': 0
        }

def get_filtered_transactions_paginated(year, month, category='all', page=1, per_page=50):
    """Get filtered business transactions with pagination"""
    try:
        # NEW: Handle "All Years" option
        if year == 'all':
            query = BusinessTransaction.query
        else:
            query = BusinessTransaction.query.filter(
                extract('year', BusinessTransaction.date) == year
            )
        
        if month != 'all':
            query = query.filter(
                extract('month', BusinessTransaction.date) == int(month)
            )
        
        # NEW: Category filter
        if category != 'all':
            query = query.filter(BusinessTransaction.category == category)
        
        # Order by date (newest first)
        query = query.order_by(
            BusinessTransaction.date.desc(), 
            BusinessTransaction.id.desc()
        )
        
        # Paginate
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # Create pagination info
        pagination_info = {
            'page': pagination.page,
            'pages': pagination.pages,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
            'prev_num': pagination.prev_num,
            'next_num': pagination.next_num,
            'iter_pages': list(pagination.iter_pages())
        }
        
        return pagination.items, pagination_info
        
    except Exception as e:
        print(f"❌ Error getting filtered transactions: {e}")
        return [], None

def get_filtered_transactions(year, month, limit=20):
    """Get filtered business transactions (legacy function, kept for compatibility)"""
    try:
        query = BusinessTransaction.query.filter(
            extract('year', BusinessTransaction.date) == year
        )
        
        if month != 'all':
            query = query.filter(
                extract('month', BusinessTransaction.date) == int(month)
            )
        
        return query.order_by(
            BusinessTransaction.date.desc(), 
            BusinessTransaction.id.desc()
        ).limit(limit).all()
        
    except Exception as e:
        print(f"❌ Error getting filtered transactions: {e}")
        return []

def get_category_breakdown(year, month, category='all'):
    """Get financial breakdown by category - FIXED SQLAlchemy syntax and added category filter"""
    try:
        # Build base query
        if year == 'all':
            base_query = BusinessTransaction.query
        else:
            base_query = BusinessTransaction.query.filter(
                extract('year', BusinessTransaction.date) == year
            )
        
        if month != 'all':
            base_query = base_query.filter(
                extract('month', BusinessTransaction.date) == int(month)
            )
        
        # NEW: Category filter
        if category != 'all':
            base_query = base_query.filter(BusinessTransaction.category == category)
        
        # Get category breakdown - FIXED: Added missing closing parenthesis
        if year == 'all':
            category_results = db.session.query(
                BusinessTransaction.category,
                func.sum(
                    case(
                        (BusinessTransaction.transaction_type == 'Income', BusinessTransaction.amount),
                        else_=0
                    )
                ).label('income'),
                func.sum(
                    case(
                        (BusinessTransaction.transaction_type == 'Expense', BusinessTransaction.amount),
                        else_=0
                    )
                ).label('expenses'),
                func.count(BusinessTransaction.id).label('transaction_count')
            )
        else:
            category_results = db.session.query(
                BusinessTransaction.category,
                func.sum(
                    case(
                        (BusinessTransaction.transaction_type == 'Income', BusinessTransaction.amount),
                        else_=0
                    )
                ).label('income'),
                func.sum(
                    case(
                        (BusinessTransaction.transaction_type == 'Expense', BusinessTransaction.amount),
                        else_=0
                    )
                ).label('expenses'),
                func.count(BusinessTransaction.id).label('transaction_count')
            ).filter(
                extract('year', BusinessTransaction.date) == year
            )
        
        if month != 'all':
            category_results = category_results.filter(
                extract('month', BusinessTransaction.date) == int(month)
            )
        
        # NEW: Category filter
        if category != 'all':
            category_results = category_results.filter(BusinessTransaction.category == category)
        
        category_results = category_results.group_by(
            BusinessTransaction.category
        ).order_by(
            (func.sum(BusinessTransaction.amount)).desc()
        ).all()
        
        category_breakdown = []
        for result in category_results:
            category_breakdown.append({
                'name': result.category,
                'income': float(result.income or 0),
                'expenses': float(result.expenses or 0),
                'net': float(result.income or 0) - float(result.expenses or 0),
                'transaction_count': int(result.transaction_count)
            })
        
        return category_breakdown
        
    except Exception as e:
        print(f"❌ Error getting category breakdown: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_available_categories():
    """Get categories that have transaction data"""
    try:
        results = db.session.query(
            BusinessTransaction.category
        ).distinct().order_by(BusinessTransaction.category).all()
        
        categories = [result.category for result in results if result.category]
        
        return sorted(categories)
        
    except Exception as e:
        print(f"❌ Error getting available categories: {e}")
        return []