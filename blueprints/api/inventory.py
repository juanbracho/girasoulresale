"""
Inventory API Blueprint - REST API Endpoints
Handles all AJAX requests for inventory management
"""

from flask import Blueprint, request, jsonify
from blueprints.services.inventory_service import InventoryService

# Create the inventory API blueprint
inventory_api_bp = Blueprint('inventory_api', __name__, url_prefix='/api/inventory')


# =============================================================================
# INVENTORY DATA RETRIEVAL ENDPOINTS
# =============================================================================

@inventory_api_bp.route('', methods=['GET'])
def get_all_inventory():
    """Get all inventory items - corrected for actual schema"""
    try:
        print("📦 API: Getting all inventory from database...")
        
        from models import BusinessInventory
        
        # Get all inventory items (no is_active filter)
        try:
            items = BusinessInventory.query.order_by(BusinessInventory.date_added.desc()).all()
        except AttributeError:
            # Fallback if date_added doesn't exist
            items = BusinessInventory.query.order_by(BusinessInventory.id.desc()).all()
        
        # Convert to dict format
        items_data = []
        for item in items:
            try:
                items_data.append(item.to_dict())
            except AttributeError:
                # Fallback if to_dict doesn't exist
                items_data.append({
                    'id': item.id,
                    'sku': item.sku,
                    'name': item.name,
                    'description': item.description,
                    'category': item.category,
                    'brand': getattr(item, 'brand', ''),
                    'condition': getattr(item, 'condition', ''),
                    'cost_of_item': float(item.cost_of_item or 0),
                    'selling_price': float(item.selling_price or 0),
                    'listing_status': item.listing_status,
                    'date_added': getattr(item, 'date_added', None)
                })
        
        print(f"📦 API: Retrieved {len(items_data)} inventory items")
        
        return jsonify({
            'success': True,
            'items': items_data,
            'count': len(items_data)
        })
        
    except Exception as e:
        print(f"❌ API Error getting all inventory: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve inventory items'
        }), 500
    
@inventory_api_bp.route('/<sku>', methods=['GET'])
def get_inventory_item(sku):
    """Get single inventory item by SKU"""
    try:
        print(f"📦 API: Getting inventory item with SKU: {sku}")
        
        item_data = InventoryService.get_inventory_by_sku(sku)
        
        if item_data:
            print(f"✅ API: Successfully retrieved item: {sku}")
            return jsonify({
                'success': True,
                'item': item_data
            })
        else:
            print(f"❌ API: Item not found: {sku}")
            return jsonify({
                'success': False,
                'error': 'Item not found'
            }), 404
            
    except Exception as e:
        print(f"❌ API Error getting inventory item {sku}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get inventory item'
        }), 500

@inventory_api_bp.route('/search', methods=['POST'])
def search_inventory():
    """Search inventory with filters - corrected for actual schema"""
    try:
        data = request.get_json() or {}
        print(f"📦 API: Searching inventory with filters: {data}")
        
        from models import BusinessInventory, db
        
        # Build base query (no is_active filter)
        query = BusinessInventory.query
        
        # Apply filters
        if data.get('status'):
            query = query.filter(BusinessInventory.listing_status == data['status'])
            
        if data.get('category'):
            query = query.filter(BusinessInventory.category == data['category'])
            
        if data.get('condition'):
            query = query.filter(BusinessInventory.condition == data['condition'])
            
        if data.get('brand'):
            query = query.filter(BusinessInventory.brand == data['brand'])
            
        if data.get('search'):
            search_pattern = f"%{data['search']}%"
            query = query.filter(
                (BusinessInventory.name.ilike(search_pattern)) |
                (BusinessInventory.description.ilike(search_pattern)) |
                (BusinessInventory.sku.ilike(search_pattern)) |
                (BusinessInventory.brand.ilike(search_pattern))
            )
        
        # Execute query and convert to dict
        try:
            items = query.order_by(BusinessInventory.date_added.desc()).all()
        except AttributeError:
            # Fallback if date_added doesn't exist
            items = query.order_by(BusinessInventory.id.desc()).all()
        
        # Convert to dict format
        items_data = []
        for item in items:
            try:
                items_data.append(item.to_dict())
            except AttributeError:
                # Fallback if to_dict doesn't exist
                items_data.append({
                    'id': item.id,
                    'sku': item.sku,
                    'name': item.name,
                    'description': item.description,
                    'category': item.category,
                    'brand': getattr(item, 'brand', ''),
                    'condition': getattr(item, 'condition', ''),
                    'cost_of_item': float(item.cost_of_item or 0),
                    'selling_price': float(item.selling_price or 0),
                    'listing_status': item.listing_status,
                    'date_added': getattr(item, 'date_added', None)
                })
        
        return jsonify({
            'success': True,
            'items': items_data,
            'count': len(items_data)
        })
        
    except Exception as e:
        print(f"❌ API Error searching inventory: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to search inventory'
        }), 500

@inventory_api_bp.route('/summary', methods=['GET'])
def get_inventory_summary():
    """Get inventory summary statistics"""
    try:
        print("📦 API: Getting inventory summary...")
        
        summary = InventoryService.get_inventory_summary()
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        print(f"❌ API Error getting inventory summary: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get inventory summary'
        }), 500


@inventory_api_bp.route('/brands', methods=['GET'])
def get_brands_list():
    """Get list of unique brands for filtering"""
    try:
        print("📦 API: Getting brands list...")
        
        brands = InventoryService.get_brands_list()
        
        return jsonify({
            'success': True,
            'brands': brands
        })
        
    except Exception as e:
        print(f"❌ API Error getting brands list: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get brands list'
        }), 500


# =============================================================================
# INVENTORY CREATION AND MODIFICATION ENDPOINTS
# =============================================================================

@inventory_api_bp.route('', methods=['POST'])
def create_inventory_item():
    """Create new inventory item"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        print(f"📦 API: Creating new inventory item: {data.get('name', 'Unknown')}")
        
        result = InventoryService.create_inventory_item(data)
        
        if result['success']:
            print(f"✅ API: Successfully created inventory item with SKU: {result['item']['sku']}")
            return jsonify(result), 201
        else:
            print(f"❌ API: Failed to create inventory item: {result['error']}")
            return jsonify(result), 400
            
    except Exception as e:
        print(f"❌ API Error creating inventory item: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to create inventory item'
        }), 500


@inventory_api_bp.route('/<sku>', methods=['PUT'])
def update_inventory_item(sku):
    """Update existing inventory item"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        print(f"📦 API: Updating inventory item with SKU: {sku}")
        
        result = InventoryService.update_inventory_item(sku, data)
        
        if result['success']:
            print(f"✅ API: Successfully updated inventory item: {sku}")
            return jsonify(result)
        else:
            print(f"❌ API: Failed to update inventory item {sku}: {result['error']}")
            return jsonify(result), 400
            
    except Exception as e:
        print(f"❌ API Error updating inventory item {sku}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update inventory item'
        }), 500


@inventory_api_bp.route('/<sku>/sell', methods=['POST'])
def sell_inventory_item(sku):
    """Mark inventory item as sold"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No sale data provided'
            }), 400
        
        print(f"📦 API: Selling inventory item with SKU: {sku}")
        
        # Extract sale information
        sold_price = data.get('final_price', 0)
        sale_date = data.get('sale_date')
        platform = data.get('platform', 'Other')
        notes = data.get('notes', '')
        
        result = InventoryService.sell_inventory_item(
            sku=sku,
            sold_price=sold_price,
            sale_date=sale_date,
            platform=platform,
            notes=notes
        )
        
        if result['success']:
            print(f"✅ API: Successfully sold inventory item {sku} for ${sold_price}")
            return jsonify(result)
        else:
            print(f"❌ API: Failed to sell inventory item {sku}: {result['error']}")
            return jsonify(result), 400
            
    except Exception as e:
        print(f"❌ API Error selling inventory item {sku}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to sell inventory item'
        }), 500


@inventory_api_bp.route('/<sku>', methods=['DELETE'])
def delete_inventory_item(sku):
    """Delete inventory item"""
    try:
        print(f"📦 API: Deleting inventory item with SKU: {sku}")
        
        result = InventoryService.delete_inventory_item(sku)
        
        if result['success']:
            print(f"✅ API: Successfully deleted inventory item: {sku}")
            return jsonify(result)
        else:
            print(f"❌ API: Failed to delete inventory item {sku}: {result['error']}")
            return jsonify(result), 400
            
    except Exception as e:
        print(f"❌ API Error deleting inventory item {sku}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete inventory item'
        }), 500


# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@inventory_api_bp.route('/validate', methods=['POST'])
def validate_inventory_data():
    """Validate inventory data without saving"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        validation = InventoryService.validate_inventory_data(data)
        
        return jsonify({
            'success': True,
            'valid': validation['valid'],
            'error': validation.get('error')
        })
        
    except Exception as e:
        print(f"❌ API Error validating inventory data: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to validate data'
        }), 500

@inventory_api_bp.route('/calculate-profit', methods=['POST'])
def calculate_profit():
    """Calculate profit for given cost and selling price"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        cost = float(data.get('cost', 0))
        selling_price = float(data.get('selling_price', 0))
        
        w_tax_price = InventoryService.calculate_w_tax_price(selling_price)
        profit = InventoryService.calculate_profit(cost, selling_price)
        
        return jsonify({
            'success': True,
            'cost': cost,
            'selling_price': selling_price,
            'w_tax_price': w_tax_price,
            'profit': profit,
            'profit_margin': (profit / w_tax_price * 100) if w_tax_price > 0 else 0
        })
        
    except Exception as e:
        print(f"❌ API Error calculating profit: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to calculate profit'
        }), 500

@inventory_api_bp.route('/check-edit-permissions/<sku>', methods=['GET'])
def check_edit_permissions(sku):
    """Check if inventory item can be edited"""
    try:
        print(f"📦 API: Checking edit permissions for SKU: {sku}")
        
        item_data = InventoryService.get_inventory_by_sku(sku)
        if not item_data:
            return jsonify({
                'success': False,
                'error': 'Item not found'
            }), 404
        
        # Create a mock item object to check permissions
        from models import BusinessInventory
        from datetime import datetime
        
        item = BusinessInventory()
        if item_data.get('date_added'):
            item.date_added = datetime.fromisoformat(item_data['date_added']).date()
        else:
            item.date_added = None
        
        can_edit = InventoryService.can_edit_item(item)
        
        return jsonify({
            'success': True,
            'can_edit': can_edit,
            'date_added': item_data.get('date_added'),
            'message': 'Item can be edited' if can_edit else 'Item is locked (older than 1 month)'
        })
        
    except Exception as e:
        print(f"❌ API Error checking edit permissions for {sku}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to check edit permissions'
        }), 500

@inventory_api_bp.route('/categories-and-conditions', methods=['GET'])
def get_categories_and_conditions():
    """Get categories and conditions for filter dropdowns"""
    try:
        print("📦 API: Getting categories and conditions for filters...")
        
        from models import BusinessInventory, db
        
        # Get unique categories from all inventory (no is_active filter)
        categories = db.session.query(BusinessInventory.category)\
            .distinct()\
            .order_by(BusinessInventory.category)\
            .all()
        categories_list = [{'name': cat[0]} for cat in categories if cat[0]]
        
        # Get unique conditions from all inventory
        conditions = db.session.query(BusinessInventory.condition)\
            .distinct()\
            .order_by(BusinessInventory.condition)\
            .all()
        conditions_list = [{'name': cond[0]} for cond in conditions if cond[0]]
        
        return jsonify({
            'success': True,
            'categories': categories_list,
            'conditions': conditions_list
        })
        
    except Exception as e:
        print(f"❌ API Error getting categories and conditions: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get filter data'
        }), 500

@inventory_api_bp.route('/filter-options', methods=['GET'])
def get_filter_options():
    """Get all filter options (categories, conditions, brands, statuses)"""
    try:
        print("📦 API: Getting all filter options...")
        
        from models import BusinessInventory, db
        
        # Get unique categories (no is_active filter)
        categories = db.session.query(BusinessInventory.category)\
            .distinct()\
            .order_by(BusinessInventory.category)\
            .all()
        categories_list = [cat[0] for cat in categories if cat[0]]
        
        # Get unique conditions
        conditions = db.session.query(BusinessInventory.condition)\
            .distinct()\
            .order_by(BusinessInventory.condition)\
            .all()
        conditions_list = [cond[0] for cond in conditions if cond[0]]
        
        # Get unique brands
        brands = db.session.query(BusinessInventory.brand)\
            .distinct()\
            .order_by(BusinessInventory.brand)\
            .all()
        brands_list = [brand[0] for brand in brands if brand[0]]
        
        # Static status options
        statuses = ['kept', 'inventory', 'listed', 'sold']
        
        return jsonify({
            'success': True,
            'categories': categories_list,
            'conditions': conditions_list,
            'brands': brands_list,
            'statuses': statuses
        })
        
    except Exception as e:
        print(f"❌ API Error getting filter options: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get filter options'
        }), 500

# =============================================================================
# BATCH OPERATIONS ENDPOINTS
# =============================================================================

@inventory_api_bp.route('/batch/status', methods=['POST'])
def batch_update_status():
    """Update status for multiple items"""
    try:
        data = request.get_json()
        if not data or not data.get('skus') or not data.get('status'):
            return jsonify({
                'success': False,
                'error': 'SKUs and status are required'
            }), 400
        
        skus = data['skus']
        new_status = data['status']
        
        print(f"📦 API: Batch updating status for {len(skus)} items to '{new_status}'")
        
        results = []
        for sku in skus:
            item_data = InventoryService.get_inventory_by_sku(sku)
            if item_data:
                item_data['listing_status'] = new_status
                result = InventoryService.update_inventory_item(sku, item_data)
                results.append({
                    'sku': sku,
                    'success': result['success'],
                    'error': result.get('error')
                })
            else:
                results.append({
                    'sku': sku,
                    'success': False,
                    'error': 'Item not found'
                })
        
        success_count = sum(1 for r in results if r['success'])
        
        return jsonify({
            'success': True,
            'results': results,
            'success_count': success_count,
            'total_count': len(skus),
            'message': f'Updated {success_count} out of {len(skus)} items'
        })
        
    except Exception as e:
        print(f"❌ API Error in batch status update: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update item statuses'
        }), 500


@inventory_api_bp.route('/export', methods=['GET'])
def export_inventory():
    """Export inventory data"""
    try:
        print("📦 API: Exporting inventory data...")
        
        # Get query parameters for filtering
        status = request.args.get('status')
        category = request.args.get('category')
        format_type = request.args.get('format', 'json')
        
        # Build filters
        filters = {}
        if status:
            filters['status'] = status
        if category:
            filters['category'] = category
        
        # Get filtered items
        if filters:
            items = InventoryService.search_inventory(filters)
        else:
            items = InventoryService.get_all_inventory()
        
        if format_type.lower() == 'csv':
            # Return CSV format
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'SKU', 'Name', 'Brand', 'Item Type', 'Category', 'Size', 
                'Condition', 'Cost', 'Selling Price', 'Status', 'Location', 
                'Collection/Drop', 'Date Added', 'Description'
            ])
            
            # Write data
            for item in items:
                writer.writerow([
                    item.get('sku', ''),
                    item.get('name', ''),
                    item.get('brand', ''),
                    item.get('item_type', ''),
                    item.get('category', ''),
                    item.get('size', ''),
                    item.get('condition', ''),
                    item.get('cost_of_item', ''),
                    item.get('selling_price', ''),
                    item.get('listing_status', ''),
                    item.get('location', ''),
                    item.get('collection_drop', ''),
                    item.get('date_added', ''),
                    item.get('description', '')
                ])
            
            csv_content = output.getvalue()
            output.close()
            
            from flask import Response
            return Response(
                csv_content,
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=inventory_export.csv'}
            )
        
        else:
            # Return JSON format
            return jsonify({
                'success': True,
                'items': items,
                'count': len(items),
                'export_date': str(datetime.now()),
                'filters': filters
            })
        
    except Exception as e:
        print(f"❌ API Error exporting inventory: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to export inventory'
        }), 500


# =============================================================================
# ANALYTICS ENDPOINTS
# =============================================================================

@inventory_api_bp.route('/analytics/category-breakdown', methods=['GET'])
def get_category_breakdown():
    """Get inventory breakdown by category"""
    try:
        print("📦 API: Getting category breakdown...")
        
        from models import db, BusinessInventory
        from sqlalchemy import func
        
        results = db.session.query(
            BusinessInventory.category,
            func.count(BusinessInventory.id).label('count'),
            func.sum(BusinessInventory.cost_of_item).label('total_cost'),
            func.sum(BusinessInventory.selling_price).label('total_value')
        ).filter(
            BusinessInventory.is_active == True
        ).group_by(BusinessInventory.category).all()
        
        breakdown = []
        for result in results:
            total_cost = float(result.total_cost or 0)
            total_value = float(result.total_value or 0)
            w_tax_value = total_value * 1.083
            
            breakdown.append({
                'category': result.category,
                'count': result.count,
                'total_cost': total_cost,
                'total_value': total_value,
                'w_tax_value': w_tax_value,
                'potential_profit': w_tax_value - total_cost
            })
        
        return jsonify({
            'success': True,
            'breakdown': breakdown
        })
        
    except Exception as e:
        print(f"❌ API Error getting category breakdown: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get category breakdown'
        }), 500


@inventory_api_bp.route('/analytics/status-breakdown', methods=['GET'])
def get_status_breakdown():
    """Get inventory breakdown by status"""
    try:
        print("📦 API: Getting status breakdown...")
        
        from models import db, BusinessInventory
        from sqlalchemy import func
        
        results = db.session.query(
            BusinessInventory.listing_status,
            func.count(BusinessInventory.id).label('count'),
            func.sum(BusinessInventory.cost_of_item).label('total_cost'),
            func.sum(BusinessInventory.selling_price).label('total_value')
        ).filter(
            BusinessInventory.is_active == True
        ).group_by(BusinessInventory.listing_status).all()
        
        breakdown = []
        for result in results:
            total_cost = float(result.total_cost or 0)
            total_value = float(result.total_value or 0)
            
            breakdown.append({
                'status': result.listing_status,
                'count': result.count,
                'total_cost': total_cost,
                'total_value': total_value
            })
        
        return jsonify({
            'success': True,
            'breakdown': breakdown
        })
        
    except Exception as e:
        print(f"❌ API Error getting status breakdown: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get status breakdown'
        }), 500


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@inventory_api_bp.errorhandler(400)
def bad_request(error):
    """Handle bad request errors"""
    return jsonify({
        'success': False,
        'error': 'Bad request - invalid data provided'
    }), 400


@inventory_api_bp.errorhandler(404)
def not_found(error):
    """Handle not found errors"""
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404


@inventory_api_bp.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


# =============================================================================
# BLUEPRINT REGISTRATION
# =============================================================================

def register_inventory_api(app):
    """Register the inventory API blueprint with the Flask app"""
    app.register_blueprint(inventory_api_bp)
    print("✅ Inventory API blueprint registered")