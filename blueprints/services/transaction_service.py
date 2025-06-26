"""
Business logic for transaction management - UPDATED for new schema
"""

from datetime import datetime, date
from sqlalchemy import func, extract
from models import db, BusinessTransaction

class TransactionService:
    """Service class for transaction business logic"""
        
    @staticmethod
    def create_transaction(data):
        """Create a new business transaction - FIXED to return dictionary"""
        try:
            # Validate data
            validation_result = TransactionService.validate_transaction_data(data)
            if not validation_result['valid']:
                return {'success': False, 'error': validation_result['error']}
            
            # Create transaction
            transaction = BusinessTransaction(
                date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
                description=data['description'],
                amount=float(data['amount']),
                category=data['category'],
                sub_category=data.get('sub_category', ''),
                transaction_type=data['transaction_type'],
                account_name=data['account_name'],
                notes=data.get('notes', '')
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            # FIXED: Return transaction as dictionary instead of object
            return {
                'success': True,
                'transaction': transaction.to_dict(),  # ← This fixes the "not subscriptable" error
                'message': f'Transaction "{transaction.description}" created successfully!'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
        
    @staticmethod
    def validate_transaction_data(data):
            """Validate transaction data"""
            required_fields = ['transaction_type', 'date', 'description', 'amount', 'category', 'account_name']
            
            for field in required_fields:
                if not data.get(field):
                    return {'valid': False, 'error': f'{field} is required'}
            
            # Validate amount
            try:
                amount = float(data['amount'])
                if amount <= 0:
                    return {'valid': False, 'error': 'Amount must be greater than zero'}
            except (ValueError, TypeError):
                return {'valid': False, 'error': 'Invalid amount format'}
            
            # Validate date
            try:
                datetime.strptime(data['date'], '%Y-%m-%d')
            except ValueError:
                return {'valid': False, 'error': 'Invalid date format. Use YYYY-MM-DD'}
            
            # Validate transaction type
            if data['transaction_type'] not in ['Income', 'Expense']:
                return {'valid': False, 'error': 'Transaction type must be Income or Expense'}
            
            return {'valid': True}
        
    @staticmethod
    def get_monthly_summary(year, month):
            """Get monthly financial summary"""
            try:
                results = db.session.query(
                    BusinessTransaction.transaction_type,
                    func.sum(BusinessTransaction.amount).label('total')
                ).filter(
                    extract('year', BusinessTransaction.date) == year,
                    extract('month', BusinessTransaction.date) == month
                ).group_by(BusinessTransaction.transaction_type).all()
                
                summary = {'income': 0, 'expenses': 0}
                for transaction_type, total in results:
                    if transaction_type.lower() == 'income':
                        summary['income'] = float(total)
                    elif transaction_type.lower() == 'expense':
                        summary['expenses'] = float(total)
                
                summary['profit'] = summary['income'] - summary['expenses']
                summary['profit_margin'] = (summary['profit'] / summary['income'] * 100) if summary['income'] > 0 else 0
                
                return summary
                
            except Exception as e:
                return {'income': 0, 'expenses': 0, 'profit': 0, 'profit_margin': 0}
        
    @staticmethod
    def get_yearly_summary(year):
            """Get yearly financial summary"""
            try:
                results = db.session.query(
                    BusinessTransaction.transaction_type,
                    func.sum(BusinessTransaction.amount).label('total')
                ).filter(
                    extract('year', BusinessTransaction.date) == year
                ).group_by(BusinessTransaction.transaction_type).all()
                
                summary = {'income': 0, 'expenses': 0}
                for transaction_type, total in results:
                    if transaction_type.lower() == 'income':
                        summary['income'] = float(total)
                    elif transaction_type.lower() == 'expense':
                        summary['expenses'] = float(total)
                
                summary['profit'] = summary['income'] - summary['expenses']
                summary['profit_margin'] = (summary['profit'] / summary['income'] * 100) if summary['income'] > 0 else 0
                
                return summary
                
            except Exception as e:
                return {'income': 0, 'expenses': 0, 'profit': 0, 'profit_margin': 0}
        
    @staticmethod
    def get_category_breakdown(year, month=None):
            """Get expense breakdown by category"""
            try:
                from sqlalchemy import case
                
                query = db.session.query(
                    BusinessTransaction.category,
                    func.sum(case(
                        (BusinessTransaction.transaction_type == 'Income', BusinessTransaction.amount),
                        else_=0
                    )).label('income'),
                    func.sum(case(
                        (BusinessTransaction.transaction_type == 'Expense', BusinessTransaction.amount),
                        else_=0
                    )).label('expenses'),
                    func.count(BusinessTransaction.id).label('count')
                ).filter(
                    extract('year', BusinessTransaction.date) == year
                )
                
                if month:
                    query = query.filter(extract('month', BusinessTransaction.date) == month)
                
                results = query.group_by(BusinessTransaction.category).all()
            
                breakdown = []
                for result in results:
                    breakdown.append({
                        'category': result.category,
                        'income': float(result.income or 0),
                        'expenses': float(result.expenses or 0),
                        'net': float(result.income or 0) - float(result.expenses or 0),
                        'transaction_count': int(result.count)
                    })
                
                return breakdown
                
            except Exception as e:
                return []
        
    @staticmethod
    def get_cash_flow_data(year, months=12):
            """Get cash flow data for charts"""
            try:
                cash_flow = []
                
                for month in range(1, months + 1):
                    summary = TransactionService.get_monthly_summary(year, month)
                    cash_flow.append({
                        'month': month,
                        'month_name': date(year, month, 1).strftime('%B'),
                        'income': summary['income'],
                        'expenses': summary['expenses'],
                        'profit': summary['profit']
                    })
                
                return cash_flow
                
            except Exception as e:
                return []
        
    @staticmethod
    def create_automatic_transaction(source_type, source_id, transaction_data):
            """Create automatic transaction from other business operations
            
            NOTE: source_type and source_id are no longer stored in database
            but kept as parameters for backward compatibility
            """
            try:
                # Simply create the transaction without source tracking
                return TransactionService.create_transaction(transaction_data)
                
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
    @staticmethod
    def get_profit_loss_statement(year, month=None):
        """Generate profit & loss statement"""
        try:
            # Get all transactions for the period
            query = BusinessTransaction.query.filter(
                extract('year', BusinessTransaction.date) == year
            )
            
            if month:
                query = query.filter(extract('month', BusinessTransaction.date) == month)
            
            transactions = query.all()
            
            # Calculate totals
            total_income = sum(float(t.amount) for t in transactions if t.transaction_type == 'Income')
            total_expenses = sum(float(t.amount) for t in transactions if t.transaction_type == 'Expense')
            net_profit = total_income - total_expenses
            
            # Group by category
            income_categories = {}
            expense_categories = {}
            
            for t in transactions:
                if t.transaction_type == 'Income':
                    income_categories[t.category] = income_categories.get(t.category, 0) + float(t.amount)
                else:
                    expense_categories[t.category] = expense_categories.get(t.category, 0) + float(t.amount)
            
            return {
                'period': f"{date(year, month, 1).strftime('%B %Y')}" if month else f"{year}",
                'total_income': total_income,
                'total_expenses': total_expenses,
                'net_profit': net_profit,
                'profit_margin': (net_profit / total_income * 100) if total_income > 0 else 0,
                'income_categories': income_categories,
                'expense_categories': expense_categories
            }
            
        except Exception as e:
            return {
                'period': f"{year}",
                'total_income': 0,
                'total_expenses': 0,
                'net_profit': 0,
                'profit_margin': 0,
                'income_categories': {},
                'expense_categories': {}
            }