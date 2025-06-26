"""
Business calculations and metrics for Girasoul Business Dashboard
"""

from datetime import datetime, date
from sqlalchemy import func, extract
from models import db, BusinessTransaction, BusinessAsset, BusinessInventory

def calculate_business_metrics(year, month):
    """Calculate key business metrics for dashboard"""
    try:
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
        
        return {
            'monthly_revenue': float(monthly_income),
            'monthly_expenses': float(monthly_expenses),
            'monthly_profit': float(monthly_income) - float(monthly_expenses),
            'ytd_revenue': float(ytd_income),
            'ytd_expenses': float(ytd_expenses),
            'ytd_profit': float(ytd_income) - float(ytd_expenses)
        }
        
    except Exception as e:
        print(f"❌ Error calculating business metrics: {e}")
        return {
            'monthly_revenue': 0,
            'monthly_expenses': 0,
            'monthly_profit': 0,
            'ytd_revenue': 0,
            'ytd_expenses': 0,
            'ytd_profit': 0
        }

def calculate_financial_summary(year, month):
    """Calculate financial summary for the given period"""
    try:
        # Build base query
        base_query = BusinessTransaction.query.filter(
            extract('year', BusinessTransaction.date) == year
        )
        
        # Add month filter if specified
        if month != 'all':
            base_query = base_query.filter(
                extract('month', BusinessTransaction.date) == int(month)
            )
        
        # Monthly revenue
        monthly_revenue = base_query.filter(
            BusinessTransaction.transaction_type == 'Income'
        ).with_entities(func.sum(BusinessTransaction.amount)).scalar() or 0
        
        # Monthly expenses
        monthly_expenses = base_query.filter(
            BusinessTransaction.transaction_type == 'Expense'
        ).with_entities(func.sum(BusinessTransaction.amount)).scalar() or 0
        
        # YTD calculations (if month filter is applied, calculate up to that month)
        ytd_query = BusinessTransaction.query.filter(
            extract('year', BusinessTransaction.date) == year
        )
        
        if month != 'all':
            ytd_query = ytd_query.filter(
                extract('month', BusinessTransaction.date) <= int(month)
            )
        
        ytd_revenue = ytd_query.filter(
            BusinessTransaction.transaction_type == 'Income'
        ).with_entities(func.sum(BusinessTransaction.amount)).scalar() or 0
        
        ytd_expenses = ytd_query.filter(
            BusinessTransaction.transaction_type == 'Expense'
        ).with_entities(func.sum(BusinessTransaction.amount)).scalar() or 0
        
        return {
            'monthly_revenue': float(monthly_revenue),
            'monthly_expenses': float(monthly_expenses),
            'monthly_profit': float(monthly_revenue) - float(monthly_expenses),
            'ytd_revenue': float(ytd_revenue),
            'ytd_expenses': float(ytd_expenses),
            'ytd_profit': float(ytd_revenue) - float(ytd_expenses)
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

def calculate_inventory_metrics(inventory_items=None):
    """Calculate inventory metrics from items list or database"""
    try:
        if inventory_items is None:
            # Get from database
            inventory_items = BusinessInventory.query.filter_by(is_active=True).all()
        
        if not inventory_items:
            return {
                'total_items': 0,
                'available_items': 0,
                'sold_items': 0,
                'total_cost': 0,
                'total_value': 0,
                'low_stock_items': 0
            }
        
        # Filter items by status
        available_items = [item for item in inventory_items if item.listing_status != 'sold']
        sold_items = [item for item in inventory_items if item.listing_status == 'sold']
        
        # Calculate totals for available items
        total_cost = sum([
            float(item.cost_of_item or 0) * (item.quantity_on_hand or 1) 
            for item in available_items
        ])
        
        total_value = sum([
            float(item.selling_price or 0) * (item.quantity_on_hand or 1) 
            for item in available_items
        ])
        
        # Calculate low stock items
        low_stock_items = len([
            item for item in available_items 
            if (item.reorder_point or 0) > 0 and (item.quantity_on_hand or 0) <= (item.reorder_point or 0)
        ])
        
        return {
            'total_items': len(inventory_items),
            'available_items': len(available_items),
            'sold_items': len(sold_items),
            'total_cost': total_cost,
            'total_value': total_value,
            'low_stock_items': low_stock_items
        }
        
    except Exception as e:
        print(f"❌ Error calculating inventory metrics: {e}")
        return {
            'total_items': 0,
            'available_items': 0,
            'sold_items': 0,
            'total_cost': 0,
            'total_value': 0,
            'low_stock_items': 0
        }

def calculate_assets_metrics(business_assets=None):
    """Calculate assets metrics from assets list or database"""
    try:
        if business_assets is None:
            # Get from database
            business_assets = BusinessAsset.query.all()
        
        if not business_assets:
            return {
                'total_assets': 0,
                'active_assets': 0,
                'disposed_assets': 0,
                'total_purchase_value': 0.0,
                'total_current_value': 0.0,
                'total_depreciation': 0.0
            }
        
        # Filter active and disposed assets
        active_assets = [asset for asset in business_assets if asset.is_active]
        disposed_assets = [asset for asset in business_assets if not asset.is_active]
        
        # Calculate totals for active assets
        total_purchase_value = sum([
            float(asset.purchase_price or 0) 
            for asset in active_assets
        ])
        
        total_current_value = sum([
            float(asset.current_value or asset.purchase_price or 0) 
            for asset in active_assets
        ])
        
        total_depreciation = total_purchase_value - total_current_value
        
        return {
            'total_assets': len(business_assets),
            'active_assets': len(active_assets),
            'disposed_assets': len(disposed_assets),
            'total_purchase_value': total_purchase_value,
            'total_current_value': total_current_value,
            'total_depreciation': total_depreciation
        }
        
    except Exception as e:
        print(f"❌ Error calculating assets metrics: {e}")
        return {
            'total_assets': 0,
            'active_assets': 0,
            'disposed_assets': 0,
            'total_purchase_value': 0.0,
            'total_current_value': 0.0,
            'total_depreciation': 0.0
        }

def calculate_profit_margin(selling_price, cost_price):
    """Calculate profit margin percentage"""
    try:
        selling_price = float(selling_price)
        cost_price = float(cost_price)
        
        if selling_price == 0:
            return 0
        
        return ((selling_price - cost_price) / selling_price) * 100
        
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

def calculate_markup_percentage(selling_price, cost_price):
    """Calculate markup percentage"""
    try:
        selling_price = float(selling_price)
        cost_price = float(cost_price)
        
        if cost_price == 0:
            return 0
        
        return ((selling_price - cost_price) / cost_price) * 100
        
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

def calculate_roi(profit, investment):
    """Calculate return on investment percentage"""
    try:
        profit = float(profit)
        investment = float(investment)
        
        if investment == 0:
            return 0
        
        return (profit / investment) * 100
        
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

def calculate_break_even_point(fixed_costs, variable_cost_of_item, selling_price_per_unit):
    """Calculate break-even point in units"""
    try:
        fixed_costs = float(fixed_costs)
        variable_cost_of_item = float(variable_cost_of_item)
        selling_price_per_unit = float(selling_price_per_unit)
        
        contribution_margin = selling_price_per_unit - variable_cost_of_item
        
        if contribution_margin <= 0:
            return 0
        
        return fixed_costs / contribution_margin
        
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

def calculate_inventory_turnover(cost_of_goods_sold, average_inventory_value):
    """Calculate inventory turnover ratio"""
    try:
        cogs = float(cost_of_goods_sold)
        avg_inventory = float(average_inventory_value)
        
        if avg_inventory == 0:
            return 0
        
        return cogs / avg_inventory
        
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

def calculate_days_sales_outstanding(accounts_receivable, daily_sales):
    """Calculate days sales outstanding (DSO)"""
    try:
        ar = float(accounts_receivable)
        daily_sales = float(daily_sales)
        
        if daily_sales == 0:
            return 0
        
        return ar / daily_sales
        
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

def calculate_cash_conversion_cycle(days_inventory_outstanding, days_sales_outstanding, days_payable_outstanding):
    """Calculate cash conversion cycle"""
    try:
        dio = float(days_inventory_outstanding)
        dso = float(days_sales_outstanding)
        dpo = float(days_payable_outstanding)
        
        return dio + dso - dpo
        
    except (ValueError, TypeError):
        return 0

def calculate_working_capital(current_assets, current_liabilities):
    """Calculate working capital"""
    try:
        assets = float(current_assets)
        liabilities = float(current_liabilities)
        
        return assets - liabilities
        
    except (ValueError, TypeError):
        return 0

def calculate_gross_profit(revenue, cost_of_goods_sold):
    """Calculate gross profit"""
    try:
        revenue = float(revenue)
        cogs = float(cost_of_goods_sold)
        
        return revenue - cogs
        
    except (ValueError, TypeError):
        return 0

def calculate_gross_profit_margin(gross_profit, revenue):
    """Calculate gross profit margin percentage"""
    try:
        gross_profit = float(gross_profit)
        revenue = float(revenue)
        
        if revenue == 0:
            return 0
        
        return (gross_profit / revenue) * 100
        
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

def calculate_net_profit_margin(net_profit, revenue):
    """Calculate net profit margin percentage"""
    try:
        net_profit = float(net_profit)
        revenue = float(revenue)
        
        if revenue == 0:
            return 0
        
        return (net_profit / revenue) * 100
        
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

def calculate_compound_growth_rate(beginning_value, ending_value, periods):
    """Calculate compound annual growth rate (CAGR)"""
    try:
        beginning = float(beginning_value)
        ending = float(ending_value)
        periods = float(periods)
        
        if beginning <= 0 or periods <= 0:
            return 0
        
        return ((ending / beginning) ** (1 / periods) - 1) * 100
        
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

def calculate_depreciation_straight_line(cost, salvage_value, useful_life):
    """Calculate straight-line depreciation"""
    try:
        cost = float(cost)
        salvage = float(salvage_value)
        life = float(useful_life)
        
        if life <= 0:
            return 0
        
        return (cost - salvage) / life
        
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

def calculate_tax_amount(taxable_income, tax_rate):
    """Calculate tax amount"""
    try:
        income = float(taxable_income)
        rate = float(tax_rate)
        
        return income * (rate / 100)
        
    except (ValueError, TypeError):
        return 0

def format_currency(amount, currency_symbol='$'):
    """Format amount as currency string"""
    try:
        amount = float(amount)
        return f"{currency_symbol}{amount:,.2f}"
    except (ValueError, TypeError):
        return f"{currency_symbol}0.00"

def format_percentage(value, decimal_places=2):
    """Format value as percentage string"""
    try:
        value = float(value)
        return f"{value:.{decimal_places}f}%"
    except (ValueError, TypeError):
        return "0.00%"