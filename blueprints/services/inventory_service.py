"""
Business logic for inventory management - COMPLETE IMPLEMENTATION
"""

from datetime import datetime, date
from sqlalchemy import func
from models import db, BusinessInventory, BusinessTransaction
from blueprints.services.transaction_service import TransactionService
from blueprints.utils.validators import validate_inventory_data
import random
import string

class InventoryService:
    """Service class for inventory business logic"""

    @staticmethod
    def create_inventory_item(data):
        """Create a new inventory item with automatic expense transaction"""
        try:
            # Validate data using the validators
            validation_result = validate_inventory_data(data)
            if not validation_result['valid']:
                return {'success': False, 'error': validation_result['error']}
            
            # Generate SKU if not provided
            sku = data.get('sku') or InventoryService.generate_sku()
            
            # Check if SKU already exists
            existing_item = BusinessInventory.query.filter_by(sku=sku).first()
            if existing_item:
                return {'success': False, 'error': 'SKU already exists'}
            
            # Create inventory item using correct field names from database schema
            inventory_item = BusinessInventory(
                sku=sku,
                name=data['name'],
                description=data.get('description', ''),
                category=data['category'],
                cost_of_item=float(data['cost_of_item']),  # Correct field name
                selling_price=float(data['selling_price']),
                listing_status=data.get('listing_status', 'inventory'),
                location=data.get('location', ''),
                size=data.get('size', ''),
                condition=data.get('condition', ''),
                brand=data.get('brand', ''),
                drop_field=data.get('drop_field', '')  # Collection tracking
            )
            
            # Calculate w_tax_price automatically (8.3% tax)
            if inventory_item.selling_price:
                inventory_item.w_tax_price = float(inventory_item.selling_price) * 1.083
            
            db.session.add(inventory_item)
            db.session.flush()  # Get the ID
            
            # Create automatic expense transaction
            transaction_data = {
                'transaction_type': 'Expense',
                'description': f'Inventory Purchase - {inventory_item.name}',
                'amount': float(inventory_item.cost_of_item),
                'category': 'Inventory Purchase',
                'account_name': 'Business Checking',
                'date': datetime.now().strftime('%Y-%m-%d')
            }
            
            transaction_result = TransactionService.create_transaction(transaction_data)
            if not transaction_result['success']:
                db.session.rollback()
                return {'success': False, 'error': f'Failed to create expense transaction: {transaction_result["error"]}'}
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Inventory item created successfully',
                'item': inventory_item.to_dict(),
                'transaction_id': transaction_result['transaction']['id']
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_all_inventory():
        """Get all active inventory items"""
        try:
            items = BusinessInventory.query.filter_by().order_by(BusinessInventory.id.desc()).all()
            return [item.to_dict() for item in items]
        except Exception as e:
            print(f"❌ Error getting all inventory: {e}")
            return []

    @staticmethod
    def update_inventory_item(sku, data):
        """Update existing inventory item and handle financial transaction updates"""
        try:
            item = BusinessInventory.query.filter_by(sku=sku).first()
            if not item:
                return {'success': False, 'error': 'Item not found'}
            
            # Check if item can be edited (business rule: only recent items)
            if not InventoryService.can_edit_item(item):
                return {'success': False, 'error': 'Item is locked and cannot be edited (older than 1 month)'}
            
            # Validate updated data
            validation_result = validate_inventory_data(data)
            if not validation_result['valid']:
                return {'success': False, 'error': validation_result['error']}
            
            # Store original cost for transaction update
            original_cost = float(item.cost_of_item)
            new_cost = float(data['cost_of_item'])
            
            # Update fields
            item.name = data['name']
            item.description = data.get('description', '')
            item.category = data['category']
            item.cost_of_item = new_cost
            item.selling_price = float(data['selling_price'])
            item.listing_status = data.get('listing_status', 'inventory')
            item.location = data.get('location', '')
            item.size = data.get('size', '')
            item.condition = data.get('condition', '')
            item.brand = data.get('brand', '')
            item.drop_field = data.get('drop_field', '')
            
            # Recalculate w_tax_price
            if item.selling_price:
                item.w_tax_price = float(item.selling_price) * 1.083
            
            # Handle transaction update if cost changed
            if original_cost != new_cost:
                # Find the original expense transaction for this item
                original_transaction = BusinessTransaction.query.filter(
                    BusinessTransaction.description.like(f'%{item.name}%'),
                    BusinessTransaction.transaction_type == 'Expense',
                    BusinessTransaction.category == 'Inventory Purchase'
                ).first()
                
                if original_transaction:
                    # Update existing transaction amount instead of creating new one
                    original_transaction.amount = new_cost
                    original_transaction.description = f'Inventory Purchase - {item.name} (Updated)'
                else:
                    # If no original transaction found, create adjustment transaction
                    cost_difference = new_cost - original_cost
                    if cost_difference != 0:
                        transaction_type = 'Expense' if cost_difference > 0 else 'Income'
                        transaction_data = {
                            'transaction_type': transaction_type,
                            'description': f'Inventory Cost Adjustment - {item.name}',
                            'amount': abs(cost_difference),
                            'category': 'Inventory Adjustment',
                            'account_name': 'Business Checking',
                            'date': datetime.now().strftime('%Y-%m-%d')
                        }
                        
                        transaction_result = TransactionService.create_transaction(transaction_data)
                        if not transaction_result['success']:
                            db.session.rollback()
                            return {'success': False, 'error': f'Failed to create adjustment transaction: {transaction_result["error"]}'}
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Inventory item updated successfully',
                'item': item.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}

    @staticmethod
    def update_inventory_item(sku, data):
        """Update existing inventory item WITHOUT creating new transaction"""
        try:
            item = BusinessInventory.query.filter_by(sku=sku).first()
            if not item:
                return {'success': False, 'error': 'Item not found'}
            
            # Check if item can be edited (business rule: only recent items)
            if not InventoryService.can_edit_item(item):
                return {'success': False, 'error': 'Item is locked and cannot be edited (older than 1 month)'}
            
            # Validate updated data
            validation_result = validate_inventory_data(data)
            if not validation_result['valid']:
                return {'success': False, 'error': validation_result['error']}
            
            # Store old cost for transaction update logic
            old_cost = float(item.cost_of_item)
            new_cost = float(data['cost_of_item'])
            cost_changed = old_cost != new_cost
            
            # Update item fields
            item.name = data['name']
            item.description = data.get('description', '')
            item.category = data['category']
            item.cost_of_item = new_cost
            item.selling_price = float(data['selling_price'])
            item.listing_status = data.get('listing_status', 'inventory')
            item.location = data.get('location', '')
            item.size = data.get('size', '')
            item.condition = data.get('condition', '')
            item.brand = data.get('brand', '')
            item.drop_field = data.get('drop_field', '')
            
            # Recalculate w_tax_price
            if item.selling_price:
                item.w_tax_price = float(item.selling_price) * 1.083
            
            # If cost changed, update the linked expense transaction
            if cost_changed:
                # Find the original expense transaction for this item
                # Look for transaction with description containing the item name and "Inventory Purchase"
                original_transaction = BusinessTransaction.query.filter(
                    BusinessTransaction.description.like(f'%{item.name}%'),
                    BusinessTransaction.description.like('%Inventory Purchase%'),
                    BusinessTransaction.transaction_type == 'Expense',
                    BusinessTransaction.amount == old_cost
                ).first()
                
                if original_transaction:
                    # Update the transaction amount to match new cost
                    original_transaction.amount = new_cost
                    original_transaction.description = f'Inventory Purchase - {item.name}'
                    print(f"📦 Updated linked transaction {original_transaction.id} amount from ${old_cost} to ${new_cost}")
                else:
                    print(f"⚠️ Could not find original expense transaction for item {item.name} (${old_cost})")
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Inventory item updated successfully',
                'item': item.to_dict(),
                'cost_updated': cost_changed
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}

    @staticmethod
    def sell_inventory_item(sku, sold_price, sale_date=None, platform='Other', notes=''):
        """Mark inventory item as sold and create income transaction (if amount > 0)"""
        try:
            item = BusinessInventory.query.filter_by(sku=sku).first()
            if not item:
                return {'success': False, 'error': 'Item not found'}
            
            if item.listing_status == 'sold':
                return {'success': False, 'error': 'Item is already sold'}
            
            # Update item status
            item.listing_status = 'sold'
            item.sold_price = float(sold_price)
            item.sold_date = datetime.strptime(sale_date, '%Y-%m-%d').date() if sale_date else date.today()
            
            # NEW: Only create income transaction if sold_price > 0
            if float(sold_price) > 0:
                # Create income transaction
                transaction_data = {
                    'transaction_type': 'Income',
                    'description': f'Sale - {item.name} (SKU: {item.sku})',
                    'amount': float(sold_price),
                    'category': 'Sales Revenue',
                    'sub_category': item.category if hasattr(item, 'category') else 'Other',
                    'account_name': 'Business Checking',
                    'date': item.sold_date.strftime('%Y-%m-%d'),
                    'notes': notes if notes else f'Platform: {platform}'
                }
                
                transaction_result = TransactionService.create_transaction(transaction_data)
                if not transaction_result['success']:
                    db.session.rollback()
                    return {'success': False, 'error': f'Failed to create income transaction: {transaction_result["error"]}'}
                
                db.session.commit()
                
                return {
                    'success': True,
                    'message': f'Item sold successfully for ${sold_price}',
                    'item': item.to_dict(),
                    'transaction_created': True,
                    'transaction_id': transaction_result['transaction']['id']
                }
            else:
                # For $0 sales, just mark as sold without creating transaction
                db.session.commit()
                
                return {
                    'success': True,
                    'message': 'Item marked as sold (no revenue transaction created for $0 sale)',
                    'item': item.to_dict(),
                    'transaction_created': False,
                    'zero_sale': True
                }
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error selling inventory item {sku}: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def delete_inventory_item(sku):
        """Delete inventory item completely from database"""
        try:
            item = BusinessInventory.query.filter_by(sku=sku).first()
            if not item:
                return {'success': False, 'error': 'Item not found'}
            
            # Remove validation that was preventing deletion
            # Simply delete the item from database
            db.session.delete(item)
            db.session.commit()
            
            return {'success': True, 'message': 'Item deleted successfully'}
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error deleting item {sku}: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def search_inventory(filters):
        """Search inventory with filters"""
        try:
            query = BusinessInventory.query
            
            # Apply filters
            if filters.get('category'):
                query = query.filter(BusinessInventory.category == filters['category'])
            
            if filters.get('brand'):
                query = query.filter(BusinessInventory.brand.ilike(f"%{filters['brand']}%"))
            
            if filters.get('listing_status'):
                query = query.filter(BusinessInventory.listing_status == filters['listing_status'])
            
            if filters.get('condition'):
                query = query.filter(BusinessInventory.condition == filters['condition'])
            
            if filters.get('size'):
                query = query.filter(BusinessInventory.size == filters['size'])
            
            if filters.get('search_term'):
                search_term = f"%{filters['search_term']}%"
                query = query.filter(
                    db.or_(
                        BusinessInventory.name.ilike(search_term),
                        BusinessInventory.description.ilike(search_term),
                        BusinessInventory.sku.ilike(search_term)
                    )
                )
            
            items = query.order_by(BusinessInventory.id.desc()).all()
            return [item.to_dict() for item in items]
            
        except Exception as e:
            print(f"❌ Error searching inventory: {e}")
            return []

    @staticmethod
    def get_inventory_summary():
        """Get inventory summary statistics"""
        try:
            # Count items by status
            total_items = BusinessInventory.query.count()
            available_items = BusinessInventory.query.filter(BusinessInventory.listing_status != 'sold').count()
            sold_items = BusinessInventory.query.filter(BusinessInventory.listing_status == 'sold').count()
            
            # Calculate values for available items
            available_cost = db.session.query(func.sum(BusinessInventory.cost_of_item)).filter(
                BusinessInventory.listing_status != 'sold'
            ).scalar() or 0
            
            available_value = db.session.query(func.sum(BusinessInventory.selling_price)).filter(
                BusinessInventory.listing_status != 'sold'
            ).scalar() or 0
            
            # Calculate sold revenue and profit
            sold_revenue = db.session.query(func.sum(BusinessInventory.sold_price)).filter(
                BusinessInventory.listing_status == 'sold'
            ).scalar() or 0
            
            sold_cost = db.session.query(func.sum(BusinessInventory.cost_of_item)).filter(
                BusinessInventory.listing_status == 'sold'
            ).scalar() or 0
            
            return {
                'total_items': total_items,
                'available_items': available_items,
                'sold_items': sold_items,
                'total_cost': float(available_cost),
                'total_value': float(available_value),
                'potential_profit': float(available_value) - float(available_cost),
                'sold_revenue': float(sold_revenue),
                'sold_profit': float(sold_revenue) - float(sold_cost)
            }
            
        except Exception as e:
            print(f"❌ Error getting inventory summary: {e}")
            return {
                'total_items': 0,
                'available_items': 0,
                'sold_items': 0,
                'total_cost': 0,
                'total_value': 0,
                'potential_profit': 0,
                'sold_revenue': 0,
                'sold_profit': 0
            }

    @staticmethod
    def get_brands_list():
        """Get list of unique brands for filtering"""
        try:
            brands = db.session.query(BusinessInventory.brand).distinct().filter(
                BusinessInventory.brand.isnot(None),
                BusinessInventory.brand != ''
            ).order_by(BusinessInventory.brand).all()
            
            return [brand[0] for brand in brands if brand[0]]
            
        except Exception as e:
            print(f"❌ Error getting brands list: {e}")
            return []

    @staticmethod
    def get_category_breakdown():
        """Get inventory breakdown by category"""
        try:
            results = db.session.query(
                BusinessInventory.category,
                func.count(BusinessInventory.id).label('count'),
                func.sum(BusinessInventory.cost_of_item).label('total_cost'),
                func.sum(BusinessInventory.selling_price).label('total_value')
            ).filter(
                BusinessInventory.listing_status != 'sold'
            ).group_by(BusinessInventory.category).all()
            
            breakdown = []
            for result in results:
                breakdown.append({
                    'category': result.category,
                    'count': result.count,
                    'total_cost': float(result.total_cost or 0),
                    'total_value': float(result.total_value or 0),
                    'potential_profit': float(result.total_value or 0) - float(result.total_cost or 0)
                })
            
            return breakdown
            
        except Exception as e:
            print(f"❌ Error getting category breakdown: {e}")
            return []

    @staticmethod
    def calculate_w_tax_price(selling_price):
        """Calculate price with tax (8.3%)"""
        try:
            return float(selling_price) * 1.083
        except (ValueError, TypeError):
            return 0

    @staticmethod
    def calculate_profit(cost, selling_price):
        """Calculate profit amount"""
        try:
            return float(selling_price) - float(cost)
        except (ValueError, TypeError):
            return 0

    @staticmethod
    def can_edit_item(item):
        """Check if item can be edited (business rule: only recent items)"""
        try:
            if not hasattr(item, 'created_at') or not item.created_at:
                # If no creation date, allow editing for safety
                return True
            
            # Allow editing for items created within the last 30 days
            days_since_creation = (datetime.now() - item.created_at).days
            return days_since_creation <= 30
            
        except Exception as e:
            print(f"❌ Error checking edit permissions: {e}")
            return True  # Allow editing if check fails

    @staticmethod
    def generate_sku():
        """Generate a unique SKU for inventory items"""
        try:
            # Get the highest existing SKU number
            all_items = BusinessInventory.query.all()
            max_sku = 0
            
            for item in all_items:
                if item.sku and item.sku.isdigit():
                    sku_num = int(item.sku)
                    if sku_num > max_sku:
                        max_sku = sku_num
            
            # Return next number in sequence
            new_sku = str(max_sku + 1)
            print(f"📦 Generated new SKU: {new_sku}")
            return new_sku
            
        except Exception as e:
            print(f"❌ Error generating SKU: {e}")
            # Fallback to random SKU if sequence fails
            return str(random.randint(1000, 9999))

    @staticmethod
    def get_inventory_by_sku(sku):
        """Get single inventory item by SKU"""
        try:
            item = BusinessInventory.query.filter_by(sku=sku).first()
            if item:
                return item.to_dict()
            return None
        except Exception as e:
            print(f"❌ Error getting inventory item by SKU {sku}: {e}")
            return None

    # Additional utility methods for compatibility
    
    @staticmethod
    def get_low_stock_items(threshold=1):
        """Get items with low stock (simplified for single-item inventory)"""
        try:
            return BusinessInventory.query.filter(
                BusinessInventory.listing_status == 'inventory'
            ).limit(10).all()
        except Exception as e:
            print(f"❌ Error getting low stock items: {e}")
            return []

    @staticmethod
    def validate_sku(sku):
        """Validate SKU format"""
        if not sku or not isinstance(sku, str):
            return {'valid': False, 'error': 'SKU must be a non-empty string'}
        
        if len(sku) > 50:
            return {'valid': False, 'error': 'SKU must be 50 characters or less'}
        
        # Check if SKU already exists
        existing_item = BusinessInventory.query.filter_by(sku=sku).first()
        if existing_item:
            return {'valid': False, 'error': 'SKU already exists'}
        
        return {'valid': True}