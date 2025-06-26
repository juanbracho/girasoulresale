from flask import Blueprint, request, jsonify
from datetime import datetime
from models import db, BusinessTransaction

# Create transactions API blueprint
transactions_api_bp = Blueprint('transactions_api', __name__)

@transactions_api_bp.route('', methods=['POST'])
def add_transaction():
    """Add new business transaction - Updated for new schema"""
    
    try:
        data = request.get_json()
        print(f"💰 API: Adding business transaction: {data}")
        
        # Validate required fields (updated for new schema)
        required_fields = ['transaction_type', 'date', 'description', 'amount', 'category', 'account_name']
        for field in required_fields:
            if not data.get(field):
                print(f"❌ Missing field: {field}")
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        # Validate amount
        try:
            amount = float(data['amount'])
            if amount <= 0:
                print(f"❌ Invalid amount: {amount}")
                return jsonify({'success': False, 'error': 'Amount must be greater than zero'}), 400
        except (ValueError, TypeError) as e:
            print(f"❌ Amount conversion error: {e}")
            return jsonify({'success': False, 'error': 'Invalid amount format'}), 400
        
        # Validate date
        try:
            transaction_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError as e:
            print(f"❌ Date parsing error: {e}")
            return jsonify({'success': False, 'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Validate transaction type
        if data['transaction_type'] not in ['Income', 'Expense']:
            print(f"❌ Invalid transaction type: {data['transaction_type']}")
            return jsonify({'success': False, 'error': 'Transaction type must be Income or Expense'}), 400
        
        # Create new transaction (UPDATED: Removed vendor, invoice_number, tax_deductible, source_type, source_id)
        transaction = BusinessTransaction(
            date=transaction_date,
            description=data['description'].strip(),
            amount=amount,
            category=data['category'].strip(),
            sub_category=data.get('sub_category', '').strip(),
            transaction_type=data['transaction_type'],
            account_name=data['account_name'].strip(),
            notes=data.get('notes', '').strip()
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        print(f"✅ Successfully added transaction '{data['description']}' (ID: {transaction.id})")
        
        return jsonify({
            'success': True,
            'message': f'Transaction "{data["description"]}" added successfully!',
            'transaction_id': transaction.id,
            'transaction': transaction.to_dict()
        })
        
    except Exception as e:
        print(f"❌ Error adding transaction: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@transactions_api_bp.route('/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """Get specific transaction by ID"""
    
    try:
        transaction = BusinessTransaction.query.get(transaction_id)
        
        if not transaction:
            return jsonify({'success': False, 'error': 'Transaction not found'}), 404
        
        return jsonify({
            'success': True,
            'transaction': transaction.to_dict()
        })
        
    except Exception as e:
        print(f"❌ Error getting transaction: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@transactions_api_bp.route('/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    """Update existing transaction - Updated for new schema"""
    
    try:
        transaction = BusinessTransaction.query.get(transaction_id)
        
        if not transaction:
            return jsonify({'success': False, 'error': 'Transaction not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided (UPDATED: Removed vendor, invoice_number, tax_deductible fields)
        if 'description' in data:
            transaction.description = data['description'].strip()
        if 'amount' in data:
            try:
                amount = float(data['amount'])
                if amount <= 0:
                    return jsonify({'success': False, 'error': 'Amount must be greater than zero'}), 400
                transaction.amount = amount
            except (ValueError, TypeError):
                return jsonify({'success': False, 'error': 'Invalid amount format'}), 400
        if 'category' in data:
            transaction.category = data['category'].strip()
        if 'sub_category' in data:
            transaction.sub_category = data['sub_category'].strip()
        if 'transaction_type' in data:
            if data['transaction_type'] in ['Income', 'Expense']:
                transaction.transaction_type = data['transaction_type']
            else:
                return jsonify({'success': False, 'error': 'Transaction type must be Income or Expense'}), 400
        if 'account_name' in data:
            transaction.account_name = data['account_name'].strip()
        if 'notes' in data:
            transaction.notes = data['notes'].strip()
        if 'date' in data:
            try:
                transaction.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # REMOVED: transaction.updated_at = datetime.utcnow() (field no longer exists)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Transaction updated successfully!',
            'transaction': transaction.to_dict()
        })
        
    except Exception as e:
        print(f"❌ Error updating transaction: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@transactions_api_bp.route('/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    """Delete transaction"""
    
    try:
        transaction = BusinessTransaction.query.get(transaction_id)
        
        if not transaction:
            return jsonify({'success': False, 'error': 'Transaction not found'}), 404
        
        description = transaction.description
        db.session.delete(transaction)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Transaction "{description}" deleted successfully!'
        })
        
    except Exception as e:
        print(f"❌ Error deleting transaction: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@transactions_api_bp.route('', methods=['GET'])
def get_transactions():
    """Get filtered list of transactions"""
    
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        transaction_type = request.args.get('type')
        category = request.args.get('category')
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        
        # Build query
        query = BusinessTransaction.query
        
        if transaction_type:
            query = query.filter(BusinessTransaction.transaction_type == transaction_type)
        
        if category:
            query = query.filter(BusinessTransaction.category == category)
        
        if year:
            from sqlalchemy import extract
            query = query.filter(extract('year', BusinessTransaction.date) == year)
        
        if month:
            from sqlalchemy import extract
            query = query.filter(extract('month', BusinessTransaction.date) == month)
        
        # Order by date (newest first)
        query = query.order_by(BusinessTransaction.date.desc(), BusinessTransaction.id.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=min(per_page, 100),  # Limit to max 100 per page
            error_out=False
        )
        
        transactions = [transaction.to_dict() for transaction in pagination.items]
        
        return jsonify({
            'success': True,
            'transactions': transactions,
            'pagination': {
                'page': pagination.page,
                'pages': pagination.pages,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        print(f"❌ Error getting transactions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@transactions_api_bp.route('/test', methods=['GET'])
def test_api():
    """Test endpoint to verify API is working"""
    return jsonify({
        'success': True,
        'message': 'Transactions API is working!',
        'endpoint': '/api/transactions'
    })