from flask import Blueprint, render_template, request, jsonify
from models import BusinessInventory, BusinessCategory, db
from sqlalchemy import func

# Create inventory blueprint
inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/inventory')
def inventory():
    """Business inventory management with filtering support"""
    
    print("📦 Loading business inventory page...")
    
    try:
        # Get filter parameters from URL
        status_filter = request.args.get('status', '')
        category_filter = request.args.get('category', '')
        condition_filter = request.args.get('condition', '')
        brand_filter = request.args.get('brand', '')
        search_query = request.args.get('search', '')
        
        print(f"📦 Applied filters - Status: {status_filter}, Category: {category_filter}, Condition: {condition_filter}, Brand: {brand_filter}, Search: {search_query}")
        
        # Build filtered query - NOTE: No is_active field exists, remove filter_by
        query = BusinessInventory.query
        
        # Apply filters
        if status_filter:
            query = query.filter(BusinessInventory.listing_status == status_filter)
            
        if category_filter:
            query = query.filter(BusinessInventory.category == category_filter)
            
        if condition_filter:
            query = query.filter(BusinessInventory.condition == condition_filter)
            
        if brand_filter:
            query = query.filter(BusinessInventory.brand == brand_filter)
            
        if search_query:
            search_pattern = f"%{search_query}%"
            query = query.filter(
                (BusinessInventory.name.ilike(search_pattern)) |
                (BusinessInventory.description.ilike(search_pattern)) |
                (BusinessInventory.sku.ilike(search_pattern)) |
                (BusinessInventory.brand.ilike(search_pattern))
            )
        
        # Get filtered inventory items (order by date_added if it exists, otherwise by id)
        try:
            inventory_items = query.order_by(BusinessInventory.date_added.desc()).all()
        except AttributeError:
            # Fallback if date_added doesn't exist
            inventory_items = query.order_by(BusinessInventory.id.desc()).all()
        
        # Calculate inventory summary (matching template expectations)
        inventory_summary = calculate_inventory_summary(inventory_items)
        
        # Get filter options for dropdowns
        filter_options = get_filter_options()
        
        # Determine if filters are active
        filters_active = any([status_filter, category_filter, condition_filter, brand_filter, search_query])
        
        print(f"📦 Loaded {len(inventory_items)} inventory items")
        
        return render_template('inventory.html',
                             inventory_items=inventory_items,
                             inventory_summary=inventory_summary,
                             filter_options=filter_options,
                             current_filters={
                                 'status': status_filter,
                                 'category': category_filter,
                                 'condition': condition_filter,
                                 'brand': brand_filter,
                                 'search': search_query
                             },
                             filters_active=filters_active)
                             
    except Exception as e:
        print(f"❌ Error loading inventory page: {e}")
        import traceback
        traceback.print_exc()
        
        # Return page with safe defaults on error
        return render_template('inventory.html',
                             inventory_items=[],
                             inventory_summary={
                                 'total_items': 0,
                                 'available_items': 0,
                                 'sold_items': 0,
                                 'total_cost': 0.0,
                                 'total_value': 0.0,
                                 'potential_profit': 0.0
                             },
                             filter_options={
                                 'categories': [],
                                 'conditions': [],
                                 'brands': [],
                                 'statuses': ['kept', 'inventory', 'listed', 'sold']
                             },
                             current_filters={
                                 'status': '',
                                 'category': '',
                                 'condition': '',
                                 'brand': '',
                                 'search': ''
                             },
                             filters_active=False,
                             error=str(e))

def calculate_inventory_summary(inventory_items):
    """Calculate inventory summary matching template expectations"""
    try:
        if not inventory_items:
            return {
                'total_items': 0,
                'available_items': 0,
                'sold_items': 0,
                'total_cost': 0.0,
                'total_value': 0.0,
                'potential_profit': 0.0
            }
        
        # Separate items by status
        available_items = [item for item in inventory_items if item.listing_status != 'sold']
        sold_items = [item for item in inventory_items if item.listing_status == 'sold']
        
        # Calculate totals for available items only
        total_cost = sum([
            float(item.cost_of_item or 0) for item in available_items
        ])
        
        total_value = sum([
            float(item.selling_price or 0) for item in available_items  
        ])
        
        # Calculate potential profit using w/tax pricing (8.3% tax)
        potential_profit = sum([
            (float(item.selling_price or 0) * 1.083) - float(item.cost_of_item or 0) 
            for item in available_items
        ])
        
        return {
            'total_items': len(inventory_items),
            'available_items': len(available_items),
            'sold_items': len(sold_items),
            'total_cost': total_cost,
            'total_value': total_value,
            'potential_profit': potential_profit
        }
        
    except Exception as e:
        print(f"❌ Error calculating inventory summary: {e}")
        return {
            'total_items': 0,
            'available_items': 0,
            'sold_items': 0,
            'total_cost': 0.0,
            'total_value': 0.0,
            'potential_profit': 0.0
        }

def get_filter_options():
    """Get available options for filter dropdowns"""
    try:
        # Get unique categories from all inventory (no is_active filter)
        categories = db.session.query(BusinessInventory.category)\
            .distinct()\
            .order_by(BusinessInventory.category)\
            .all()
        categories = [cat[0] for cat in categories if cat[0]]
        
        # Get unique conditions from all inventory
        conditions = db.session.query(BusinessInventory.condition)\
            .distinct()\
            .order_by(BusinessInventory.condition)\
            .all()
        conditions = [cond[0] for cond in conditions if cond[0]]
        
        # Get unique brands from all inventory
        brands = db.session.query(BusinessInventory.brand)\
            .distinct()\
            .order_by(BusinessInventory.brand)\
            .all()
        brands = [brand[0] for brand in brands if brand[0]]
        
        # Static status options based on your business model
        statuses = ['kept', 'inventory', 'listed', 'sold']
        
        print(f"📦 Filter options: {len(categories)} categories, {len(conditions)} conditions, {len(brands)} brands")
        
        return {
            'categories': categories,
            'conditions': conditions,
            'brands': brands,
            'statuses': statuses
        }
        
    except Exception as e:
        print(f"❌ Error getting filter options: {e}")
        return {
            'categories': [],
            'conditions': [],
            'brands': [],
            'statuses': ['kept', 'inventory', 'listed', 'sold']
        }