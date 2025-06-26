"""
Assets Route Blueprint - Complete fix for server-side rendering
Handles web routes for asset management pages
"""

from flask import Blueprint, render_template
from models import BusinessAsset
from sqlalchemy import func

# Create assets blueprint
assets_bp = Blueprint('assets', __name__)

@assets_bp.route('/')
def assets():
    """Business assets management page"""
    
    print("🏢 Loading business assets page...")
    
    try:
        # Get all assets ordered by purchase date (newest first)
        business_assets = BusinessAsset.query.order_by(
            BusinessAsset.purchase_date.desc()
        ).all()
        
        print(f"📊 Found {len(business_assets)} assets in database")
        
        # Calculate assets metrics
        assets_metrics = calculate_assets_metrics(business_assets)
        
        # Group assets by category
        assets_by_category = group_assets_by_category(business_assets)
        
        return render_template('assets.html',
                             business_assets=business_assets,
                             assets_metrics=assets_metrics,
                             assets_by_category=assets_by_category,
                             total_assets=len(business_assets),
                             total_value=assets_metrics.get('total_value', 0),
                             active_assets=assets_metrics.get('active_assets', 0))
                             
    except Exception as e:
        print(f"❌ Error loading assets page: {e}")
        import traceback
        traceback.print_exc()
        return render_template('assets.html',
                             business_assets=[],
                             assets_metrics={},
                             assets_by_category={},
                             total_assets=0,
                             total_value=0,
                             active_assets=0,
                             error=str(e))

def calculate_assets_metrics(business_assets):
    """Calculate assets metrics from assets list"""
    try:
        if not business_assets:
            return {
                'total_assets': 0,
                'active_assets': 0,
                'disposed_assets': 0,
                'total_value': 0,
                'active_value': 0
            }
        
        total_assets = len(business_assets)
        active_assets = sum(1 for asset in business_assets if asset.is_active)
        disposed_assets = total_assets - active_assets
        
        total_value = sum(float(asset.purchase_price or 0) for asset in business_assets)
        active_value = sum(float(asset.purchase_price or 0) for asset in business_assets if asset.is_active)
        
        return {
            'total_assets': total_assets,
            'active_assets': active_assets,
            'disposed_assets': disposed_assets,
            'total_value': total_value,
            'active_value': active_value
        }
        
    except Exception as e:
        print(f"❌ Error calculating assets metrics: {e}")
        return {
            'total_assets': 0,
            'active_assets': 0,
            'disposed_assets': 0,
            'total_value': 0,
            'active_value': 0
        }

def group_assets_by_category(business_assets):
    """Group assets by category"""
    try:
        if not business_assets:
            return {}
        
        categories = {}
        for asset in business_assets:
            category = asset.asset_category or 'Other'
            if category not in categories:
                categories[category] = []
            categories[category].append(asset)
        
        return categories
        
    except Exception as e:
        print(f"❌ Error grouping assets by category: {e}")
        return {}