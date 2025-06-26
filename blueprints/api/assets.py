"""
Complete Assets API Blueprint - Full replacement to fix schema issues
Aligned with simplified BusinessAsset model (no current_value field)
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from models import db, BusinessAsset, BusinessTransaction

# Create blueprint
assets_api_bp = Blueprint('assets_api', __name__, url_prefix='/api/assets')

@assets_api_bp.route('', methods=['POST'])
def add_asset():
    """Add new business asset with automatic expense transaction using selected expense category"""
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['name', 'asset_type', 'purchase_date', 'purchase_price', 'expense_category']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False, 
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Parse and validate purchase date
        try:
            purchase_date = datetime.strptime(data['purchase_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False, 
                'error': 'Invalid purchase date format. Use YYYY-MM-DD'
            }), 400
        
        # Parse and validate purchase price
        try:
            purchase_price = float(data['purchase_price'])
            if purchase_price <= 0:
                return jsonify({
                    'success': False, 
                    'error': 'Purchase price must be greater than 0'
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                'success': False, 
                'error': 'Invalid purchase price format'
            }), 400
        
        # Create new asset with simplified schema (no current_value field)
        asset = BusinessAsset(
            name=data['name'].strip(),
            description=data.get('description', '').strip(),
            asset_category=data.get('expense_category', '').strip(),  # Now uses expense category
            asset_type=data['asset_type'].strip(),
            purchase_date=purchase_date,
            purchase_price=purchase_price,
            is_active=data.get('is_active', True)  # Default to active
        )
        
        db.session.add(asset)
        db.session.flush()  # Get the asset ID
        
        # Create automatic expense transaction using selected categories
        expense_transaction = BusinessTransaction(
            date=purchase_date,
            description=f"Asset Purchase: {asset.name}",
            amount=purchase_price,
            category=data['expense_category'],  # Use selected expense category
            sub_category=data.get('expense_sub_category', 'Asset Purchase'),  # Use selected sub-category or default
            transaction_type="Expense",
            account_name=data.get('account_name', 'Business Checking'),  # Use selected account
            notes=f"Automatic transaction for asset purchase (Asset ID: {asset.id})"
        )
        
        db.session.add(expense_transaction)
        db.session.commit()
        
        print(f"✅ Asset added successfully: {asset.name} (ID: {asset.id})")
        print(f"✅ Expense transaction created: ${purchase_price} in category '{data['expense_category']}' (ID: {expense_transaction.id})")
        
        return jsonify({
            'success': True,
            'message': 'Asset added successfully with expense transaction!',
            'asset': asset.to_dict(),
            'transaction': expense_transaction.to_dict(),
            'asset_id': asset.id,
            'transaction_id': expense_transaction.id
        })
        
    except Exception as e:
        print(f"❌ Error adding asset: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@assets_api_bp.route('/<int:asset_id>', methods=['PUT'])
def update_asset(asset_id):
    """Update existing asset"""
    
    try:
        asset = BusinessAsset.query.get(asset_id)
        
        if not asset:
            return jsonify({'success': False, 'error': 'Asset not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Update basic fields if provided
        if 'name' in data:
            asset.name = data['name'].strip()
        if 'description' in data:
            asset.description = data['description'].strip()
        if 'expense_category' in data:
            asset.asset_category = data['expense_category'].strip()  # Store expense category as asset category
        if 'asset_type' in data:
            asset.asset_type = data['asset_type'].strip()
        if 'is_active' in data:
            asset.is_active = bool(data['is_active'])
        
        # Update purchase date if provided
        if 'purchase_date' in data and data['purchase_date']:
            try:
                asset.purchase_date = datetime.strptime(data['purchase_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False, 
                    'error': 'Invalid purchase date format. Use YYYY-MM-DD'
                }), 400
        
        # Update purchase price if provided
        if 'purchase_price' in data:
            try:
                purchase_price = float(data['purchase_price'])
                if purchase_price <= 0:
                    return jsonify({
                        'success': False, 
                        'error': 'Purchase price must be greater than 0'
                    }), 400
                asset.purchase_price = purchase_price
            except (ValueError, TypeError):
                return jsonify({
                    'success': False, 
                    'error': 'Invalid purchase price format'
                }), 400
        
        db.session.commit()
        
        print(f"✅ Asset updated successfully: {asset.name} (ID: {asset.id})")
        
        return jsonify({
            'success': True,
            'message': 'Asset updated successfully!',
            'asset': asset.to_dict()
        })
        
    except Exception as e:
        print(f"❌ Error updating asset: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@assets_api_bp.route('/<int:asset_id>', methods=['DELETE'])
def delete_asset(asset_id):
    """Delete an asset"""
    
    try:
        asset = BusinessAsset.query.get(asset_id)
        
        if not asset:
            return jsonify({'success': False, 'error': 'Asset not found'}), 404
        
        asset_name = asset.name
        db.session.delete(asset)
        db.session.commit()
        
        print(f"✅ Asset deleted successfully: {asset_name} (ID: {asset_id})")
        
        return jsonify({
            'success': True,
            'message': f'Asset "{asset_name}" deleted successfully!'
        })
        
    except Exception as e:
        print(f"❌ Error deleting asset: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@assets_api_bp.route('', methods=['GET'])
def get_assets():
    """Get all assets with optional filtering"""
    
    try:
        # Get query parameters
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        category = request.args.get('category')
        
        # Build query
        query = BusinessAsset.query
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        if category:
            query = query.filter_by(asset_category=category)
        
        # Get assets
        assets = query.order_by(BusinessAsset.purchase_date.desc()).all()
        
        # Convert to dictionaries
        assets_data = [asset.to_dict() for asset in assets]
        
        return jsonify({
            'success': True,
            'assets': assets_data,
            'count': len(assets_data)
        })
        
    except Exception as e:
        print(f"❌ Error getting assets: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@assets_api_bp.route('/<int:asset_id>', methods=['GET'])
def get_asset(asset_id):
    """Get single asset details"""
    
    try:
        asset = BusinessAsset.query.get(asset_id)
        
        if not asset:
            return jsonify({'success': False, 'error': 'Asset not found'}), 404
        
        return jsonify({
            'success': True,
            'asset': asset.to_dict()
        })
        
    except Exception as e:
        print(f"❌ Error getting asset: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500