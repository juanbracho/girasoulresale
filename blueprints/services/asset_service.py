"""
Business logic for asset management
"""

from datetime import datetime, date
from sqlalchemy import func
from models import db, BusinessAsset
from blueprints.services.transaction_service import TransactionService

class AssetService:
    """Service class for asset business logic"""
    
    @staticmethod
    def create_asset(data):
        """Create a new business asset with automatic expense transaction"""
        try:
            # Validate data
            validation_result = AssetService.validate_asset_data(data)
            if not validation_result['valid']:
                return {'success': False, 'error': validation_result['error']}
            
            # Create asset
            asset = BusinessAsset(
                name=data['name'],
                description=data.get('description', ''),
                asset_category=data['asset_category'],
                asset_type=data['asset_type'],
                purchase_date=datetime.strptime(data['purchase_date'], '%Y-%m-%d').date(),
                purchase_price=float(data['purchase_price']),
                current_value=float(data['purchase_price']),  # Starts as purchase price
                location=data.get('location', ''),
                serial_number=data.get('serial_number', ''),
                vendor=data.get('vendor', ''),
                warranty_expiry=datetime.strptime(data['warranty_expiry'], '%Y-%m-%d').date() if data.get('warranty_expiry') else None,
                depreciation_years=data.get('depreciation_years', 5),
                salvage_value=data.get('salvage_value', 0)
            )
            
            db.session.add(asset)
            db.session.flush()  # Get the ID
            
            # Create automatic expense transaction
            transaction_data = {
                'date': data['purchase_date'],
                'description': f"Asset Purchase: {data['name']}",
                'amount': float(data['purchase_price']),
                'category': 'Equipment & Supplies',
                'transaction_type': 'Expense',
                'account_name': 'Business Account',
                'vendor': data.get('vendor', ''),
                'notes': f"Purchase of business asset: {data['name']}"
            }
            
            transaction_result = TransactionService.create_automatic_transaction(
                'asset_purchase',
                asset.id,
                transaction_data
            )
            
            if not transaction_result['success']:
                db.session.rollback()
                return {'success': False, 'error': f"Failed to create expense transaction: {transaction_result['error']}"}
            
            db.session.commit()
            
            return {
                'success': True,
                'asset': asset,
                'transaction': transaction_result['transaction'],
                'message': f'Asset "{asset.name}" created successfully!'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def dispose_asset(asset_id, disposal_date=None, disposal_value=0):
        """Dispose of an asset and create disposal transaction if value > 0"""
        try:
            asset = BusinessAsset.query.get(asset_id)
            
            if not asset:
                return {'success': False, 'error': 'Asset not found'}
            
            if not asset.is_active:
                return {'success': False, 'error': 'Asset already disposed'}
            
            if not disposal_date:
                disposal_date = date.today()
            
            # Validate disposal value
            try:
                disposal_value = float(disposal_value) if disposal_value else 0
            except (ValueError, TypeError):
                return {'success': False, 'error': 'Invalid disposal value format'}
            
            # Update asset
            asset.is_active = False
            asset.disposal_date = disposal_date
            asset.disposal_value = disposal_value
            asset.updated_at = datetime.utcnow()
            
            transaction_result = None
            
            # Create disposal transaction if there's disposal value
            if disposal_value > 0:
                transaction_data = {
                    'date': disposal_date.isoformat(),
                    'description': f"Asset Disposal: {asset.name}",
                    'amount': disposal_value,
                    'category': 'Other Income',
                    'transaction_type': 'Income',
                    'account_name': 'Business Account',
                    'notes': f"Disposal of {asset.name}"
                }
                
                transaction_result = TransactionService.create_automatic_transaction(
                    'asset_disposal',
                    asset.id,
                    transaction_data
                )
                
                if not transaction_result['success']:
                    db.session.rollback()
                    return {'success': False, 'error': f"Failed to create disposal transaction: {transaction_result['error']}"}
            
            db.session.commit()
            
            return {
                'success': True,
                'asset': asset,
                'transaction': transaction_result['transaction'] if transaction_result else None,
                'message': f'Asset "{asset.name}" disposed successfully!'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def validate_asset_data(data):
        """Validate asset data"""
        required_fields = ['name', 'asset_category', 'asset_type', 'purchase_date', 'purchase_price']
        
        for field in required_fields:
            if not data.get(field):
                return {'valid': False, 'error': f'{field} is required'}
        
        # Validate purchase price
        try:
            price = float(data['purchase_price'])
            if price <= 0:
                return {'valid': False, 'error': 'Purchase price must be greater than zero'}
        except (ValueError, TypeError):
            return {'valid': False, 'error': 'Invalid purchase price format'}
        
        # Validate purchase date
        try:
            datetime.strptime(data['purchase_date'], '%Y-%m-%d')
        except ValueError:
            return {'valid': False, 'error': 'Invalid date format. Use YYYY-MM-DD'}
        
        # Validate warranty expiry date if provided
        if data.get('warranty_expiry'):
            try:
                datetime.strptime(data['warranty_expiry'], '%Y-%m-%d')
            except ValueError:
                return {'valid': False, 'error': 'Invalid warranty expiry date format. Use YYYY-MM-DD'}
        
        return {'valid': True}
    
    @staticmethod
    def calculate_asset_depreciation(asset):
        """Calculate depreciation for a specific asset"""
        try:
            if not asset.is_active or asset.disposal_date:
                return {
                    'annual_depreciation': 0,
                    'accumulated_depreciation': float(asset.accumulated_depreciation or 0),
                    'current_value': float(asset.current_value or 0),
                    'years_owned': 0
                }
            
            if asset.depreciation_method == 'straight_line':
                depreciable_amount = float(asset.purchase_price) - float(asset.salvage_value or 0)
                annual_depreciation = depreciable_amount / (asset.depreciation_years or 5)
                
                # Calculate years since purchase
                years_owned = (date.today() - asset.purchase_date).days / 365.25
                total_depreciation = min(
                    annual_depreciation * years_owned,
                    depreciable_amount
                )
                
                current_value = float(asset.purchase_price) - total_depreciation
                
                return {
                    'annual_depreciation': annual_depreciation,
                    'accumulated_depreciation': total_depreciation,
                    'current_value': current_value,
                    'years_owned': years_owned,
                    'remaining_years': max(0, (asset.depreciation_years or 5) - years_owned)
                }
            
            return {
                'annual_depreciation': 0,
                'accumulated_depreciation': 0,
                'current_value': float(asset.purchase_price),
                'years_owned': 0
            }
            
        except Exception as e:
            return {
                'annual_depreciation': 0,
                'accumulated_depreciation': 0,
                'current_value': float(asset.purchase_price or 0),
                'years_owned': 0,
                'error': str(e)
            }
    
    @staticmethod
    def get_assets_summary():
        """Get comprehensive assets summary"""
        try:
            # Active assets summary
            active_summary = db.session.query(
                func.count(BusinessAsset.id).label('total_assets'),
                func.sum(BusinessAsset.purchase_price).label('total_purchase_value'),
                func.sum(BusinessAsset.current_value).label('total_current_value')
            ).filter(BusinessAsset.is_active == True).first()
            
            # Disposed assets count
            disposed_count = BusinessAsset.query.filter_by(is_active=False).count()
            
            # Assets by category
            category_breakdown = db.session.query(
                BusinessAsset.asset_category,
                func.count(BusinessAsset.id).label('count'),
                func.sum(BusinessAsset.purchase_price).label('purchase_value'),
                func.sum(BusinessAsset.current_value).label('current_value')
            ).filter(
                BusinessAsset.is_active == True
            ).group_by(BusinessAsset.asset_category).all()
            
            categories = {}
            for category in category_breakdown:
                categories[category.asset_category] = {
                    'count': category.count,
                    'purchase_value': float(category.purchase_value or 0),
                    'current_value': float(category.current_value or 0),
                    'depreciation': float(category.purchase_value or 0) - float(category.current_value or 0)
                }
            
            return {
                'total_assets': active_summary.total_assets or 0,
                'total_purchase_value': float(active_summary.total_purchase_value or 0),
                'total_current_value': float(active_summary.total_current_value or 0),
                'total_depreciation': float(active_summary.total_purchase_value or 0) - float(active_summary.total_current_value or 0),
                'disposed_assets': disposed_count,
                'categories': categories
            }
            
        except Exception as e:
            return {
                'total_assets': 0,
                'total_purchase_value': 0.0,
                'total_current_value': 0.0,
                'total_depreciation': 0.0,
                'disposed_assets': 0,
                'categories': {},
                'error': str(e)
            }
    
    @staticmethod
    def get_depreciation_schedule(asset_id):
        """Get depreciation schedule for a specific asset"""
        try:
            asset = BusinessAsset.query.get(asset_id)
            if not asset or not asset.is_active:
                return None
            
            # Calculate depreciation schedule
            if asset.depreciation_method == 'straight_line':
                years = asset.depreciation_years or 5
                annual_depreciation = (float(asset.purchase_price) - float(asset.salvage_value or 0)) / years
                
                schedule = []
                remaining_value = float(asset.purchase_price)
                
                for year in range(1, years + 1):
                    depreciation_amount = min(annual_depreciation, remaining_value - float(asset.salvage_value or 0))
                    remaining_value -= depreciation_amount
                    
                    schedule.append({
                        'year': year,
                        'depreciation_amount': depreciation_amount,
                        'accumulated_depreciation': float(asset.purchase_price) - remaining_value,
                        'book_value': remaining_value
                    })
                    
                    if remaining_value <= float(asset.salvage_value or 0):
                        break
                
                return schedule
            
            return None
            
        except Exception as e:
            return None
    
    @staticmethod
    def get_assets_needing_attention():
        """Get assets that may need attention (warranty expiring, etc.)"""
        try:
            from datetime import timedelta
            
            # Assets with warranty expiring in next 30 days
            warning_date = date.today() + timedelta(days=30)
            
            expiring_warranty = BusinessAsset.query.filter(
                BusinessAsset.is_active == True,
                BusinessAsset.warranty_expiry != None,
                BusinessAsset.warranty_expiry <= warning_date,
                BusinessAsset.warranty_expiry >= date.today()
            ).all()
            
            # Assets that are fully depreciated
            fully_depreciated = []
            active_assets = BusinessAsset.query.filter_by(is_active=True).all()
            
            for asset in active_assets:
                depreciation_info = AssetService.calculate_asset_depreciation(asset)
                if depreciation_info['current_value'] <= float(asset.salvage_value or 0):
                    fully_depreciated.append(asset)
            
            return {
                'expiring_warranty': expiring_warranty,
                'fully_depreciated': fully_depreciated
            }
            
        except Exception as e:
            return {
                'expiring_warranty': [],
                'fully_depreciated': [],
                'error': str(e)
            }
    
    @staticmethod
    def update_all_asset_depreciation():
        """Update depreciation for all active assets"""
        try:
            active_assets = BusinessAsset.query.filter_by(is_active=True).all()
            updated_count = 0
            
            for asset in active_assets:
                depreciation_info = AssetService.calculate_asset_depreciation(asset)
                
                # Update asset with calculated values
                asset.annual_depreciation = depreciation_info['annual_depreciation']
                asset.accumulated_depreciation = depreciation_info['accumulated_depreciation']
                asset.current_value = depreciation_info['current_value']
                asset.updated_at = datetime.utcnow()
                
                updated_count += 1
            
            db.session.commit()
            
            return {
                'success': True,
                'updated_count': updated_count,
                'message': f'Updated depreciation for {updated_count} assets'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e),
                'updated_count': 0
            }