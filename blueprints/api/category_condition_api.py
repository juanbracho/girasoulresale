"""
API endpoints for managing categories and conditions
"""

from flask import Blueprint, request, jsonify
from models import db, BusinessCategory, BusinessCondition

category_condition_api = Blueprint('category_condition_api', __name__)

# ========================================
# CATEGORY ENDPOINTS
# ========================================

@category_condition_api.route('/categories/inventory', methods=['GET'])
def get_inventory_categories():
    """Get all active inventory categories"""
    try:
        categories = BusinessCategory.get_inventory_categories()
        return jsonify({
            'success': True,
            'categories': [cat.to_dict() for cat in categories]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@category_condition_api.route('/categories/inventory', methods=['POST'])
def add_inventory_category():
    """Add a new inventory category"""
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'Category name is required'
            }), 400
        
        name = data['name'].strip()
        description = data.get('description', '').strip() if data.get('description') else None
        
        # Check if category already exists (case insensitive)
        existing = BusinessCategory.query.filter(
            db.func.lower(BusinessCategory.name) == name.lower(),
            BusinessCategory.category_type == 'inventory_category',
            BusinessCategory.is_active == True
        ).first()
        
        if existing:
            return jsonify({
                'success': False,
                'error': f'Category "{name}" already exists'
            }), 400
        
        # Create new category
        category = BusinessCategory(
            name=name,
            category_type='inventory_category',
            description=description,
            is_default=False,
            is_active=True
        )
        
        db.session.add(category)
        db.session.commit()
        
        # Return updated list
        categories = BusinessCategory.get_inventory_categories()
        
        return jsonify({
            'success': True,
            'message': f'Category "{name}" added successfully',
            'category': category.to_dict(),
            'categories': [cat.to_dict() for cat in categories]
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ========================================
# CONDITION ENDPOINTS
# ========================================

@category_condition_api.route('/conditions', methods=['GET'])
def get_conditions():
    """Get all active conditions"""
    try:
        conditions = BusinessCondition.get_active_conditions()
        return jsonify({
            'success': True,
            'conditions': [condition.to_dict() for condition in conditions]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@category_condition_api.route('/conditions', methods=['POST'])
def add_condition():
    """Add a new condition"""
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'Condition name is required'
            }), 400
        
        name = data['name'].strip()
        description = data.get('description', '').strip() if data.get('description') else None
        
        # Check if condition already exists (case insensitive)
        if BusinessCondition.condition_exists(name):
            return jsonify({
                'success': False,
                'error': f'Condition "{name}" already exists'
            }), 400
        
        # Create new condition
        condition = BusinessCondition.create_condition(name, description)
        
        # Return updated list
        conditions = BusinessCondition.get_active_conditions()
        
        return jsonify({
            'success': True,
            'message': f'Condition "{name}" added successfully',
            'condition': condition.to_dict(),
            'conditions': [cond.to_dict() for cond in conditions]
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ========================================
# UTILITY ENDPOINTS
# ========================================

@category_condition_api.route('/categories-and-conditions', methods=['GET'])
def get_categories_and_conditions():
    """Get both categories and conditions in one call"""
    try:
        categories = BusinessCategory.get_inventory_categories()
        conditions = BusinessCondition.get_active_conditions()
        
        return jsonify({
            'success': True,
            'categories': [cat.to_dict() for cat in categories],
            'conditions': [cond.to_dict() for cond in conditions]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500