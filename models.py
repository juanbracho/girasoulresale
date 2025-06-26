"""
Girasoul Business Dashboard Models - Updated Schema
Database models for business management with all requested schema changes
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from decimal import Decimal

db = SQLAlchemy()

class BusinessTransaction(db.Model):
    """Business transactions for income and expense tracking"""
    __tablename__ = 'business_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    sub_category = db.Column(db.String(50))
    transaction_type = db.Column(db.String(10), nullable=False, index=True)  # 'income' or 'expense'
    account_name = db.Column(db.String(100), nullable=False)
    
    # Additional optional fields
    vendor = db.Column(db.String(100))
    invoice_number = db.Column(db.String(50))
    notes = db.Column(db.Text)
    
    # REMOVED: tax_deductible, source_type, source_id, created_at, updated_at
    
    def __repr__(self):
        return f'<BusinessTransaction {self.id}: {self.description} - ${self.amount}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'description': self.description,
            'amount': float(self.amount) if self.amount else 0.0,
            'category': self.category,
            'sub_category': self.sub_category,
            'transaction_type': self.transaction_type,
            'account_name': self.account_name,
            'vendor': self.vendor,
            'invoice_number': self.invoice_number,
            'notes': self.notes
        }

class BusinessAsset(db.Model):
    """Business assets for tracking"""
    __tablename__ = 'business_assets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    asset_category = db.Column(db.String(50), nullable=False, index=True)
    asset_type = db.Column(db.String(50), nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    purchase_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Status tracking
    is_active = db.Column(db.Boolean, default=True, index=True)
    
    # REMOVED: current_value, depreciation_method, depreciation_years, annual_depreciation,
    # accumulated_depreciation, salvage_value, location, serial_number, vendor, 
    # warranty_expiry, disposal_date, disposal_value, created_at, updated_at
    
    def __repr__(self):
        return f'<BusinessAsset {self.id}: {self.name}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'asset_category': self.asset_category,
            'asset_type': self.asset_type,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'purchase_price': float(self.purchase_price) if self.purchase_price else 0.0,
            'is_active': self.is_active
        }

class BusinessInventory(db.Model):
    """Business inventory items for fashion business"""
    __tablename__ = 'business_inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)  # Will be numerical starting at 1
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False, index=True)
    
    # Pricing
    cost_of_item = db.Column(db.Numeric(10, 2), nullable=False)
    selling_price = db.Column(db.Numeric(10, 2))
    sold_price = db.Column(db.Numeric(10, 2))  # Actual sold price
    w_tax_price = db.Column(db.Numeric(10, 2))  # NEW: Price with tax
    
    # Status tracking
    listing_status = db.Column(db.String(20), default='inventory', index=True)  # inventory, listed, sold, kept
    
    # Dates
    sold_date = db.Column(db.Date)  # TEMPORARY: for migration only
    
    # Additional details
    location = db.Column(db.String(100))
    size = db.Column(db.String(20))  # Changed to text input (no more dropdown)
    condition = db.Column(db.String(20))
    brand = db.Column(db.String(100))
    drop_field = db.Column(db.Text)  # NEW: Collection/drop description
    
    # REMOVED: supplier, quantity_on_hand, quantity_reserved, reorder_point, reorder_quantity,
    # date_added, last_purchase_date, last_sale_date, total_cost, total_value, 
    # is_active, created_at, updated_at
    
    @property
    def margin_percentage(self):
        """Profit margin percentage"""
        if self.selling_price and self.cost_of_item:
            return ((float(self.selling_price) - float(self.cost_of_item)) / float(self.selling_price)) * 100
        return 0
    
    @property
    def profit_amount(self):
        """Profit amount if sold at selling price"""
        if self.selling_price and self.cost_of_item:
            return float(self.selling_price) - float(self.cost_of_item)
        return 0
    
    def __repr__(self):
        return f'<BusinessInventory {self.sku}: {self.name}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'sku': self.sku,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'cost_of_item': float(self.cost_of_item) if self.cost_of_item else 0.0,
            'selling_price': float(self.selling_price) if self.selling_price else 0.0,
            'sold_price': float(self.sold_price) if self.sold_price else None,
            'w_tax_price': float(self.w_tax_price) if self.w_tax_price else None,
            'listing_status': self.listing_status,
            'sold_date': self.sold_date.isoformat() if self.sold_date else None,
            'location': self.location,
            'size': self.size,
            'condition': self.condition,
            'brand': self.brand,
            'drop_field': self.drop_field,
            'margin_percentage': self.margin_percentage,
            'profit_amount': self.profit_amount
        }

class BusinessSold(db.Model):
    """Business sold items - separate table for sold inventory"""
    __tablename__ = 'business_sold'
    
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), nullable=False, index=True)  # Original SKU from inventory
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False, index=True)
    
    # Pricing
    cost_of_item = db.Column(db.Numeric(10, 2), nullable=False)
    selling_price = db.Column(db.Numeric(10, 2))  # Listed price
    sold_price = db.Column(db.Numeric(10, 2), nullable=False)  # Actual sold price
    w_tax_price = db.Column(db.Numeric(10, 2))  # Price with tax
    
    # Sale details
    sold_date = db.Column(db.Date, nullable=False)
    platform = db.Column(db.String(50), nullable=False)  # Facebook, Instagram, Poshmark, F&F, Other
    
    # Item details
    location = db.Column(db.String(100))
    size = db.Column(db.String(20))
    condition = db.Column(db.String(20))
    brand = db.Column(db.String(100))
    drop_field = db.Column(db.Text)  # Collection/drop description
    
    @property
    def profit_amount(self):
        """Actual profit amount from sale"""
        if self.sold_price and self.cost_of_item:
            return float(self.sold_price) - float(self.cost_of_item)
        return 0
    
    @property
    def profit_percentage(self):
        """Actual profit percentage from sale"""
        if self.sold_price and self.cost_of_item and self.sold_price > 0:
            return ((float(self.sold_price) - float(self.cost_of_item)) / float(self.sold_price)) * 100
        return 0
    
    def __repr__(self):
        return f'<BusinessSold {self.sku}: {self.name} - ${self.sold_price}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'sku': self.sku,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'cost_of_item': float(self.cost_of_item) if self.cost_of_item else 0.0,
            'selling_price': float(self.selling_price) if self.selling_price else 0.0,
            'sold_price': float(self.sold_price) if self.sold_price else 0.0,
            'w_tax_price': float(self.w_tax_price) if self.w_tax_price else None,
            'sold_date': self.sold_date.isoformat() if self.sold_date else None,
            'platform': self.platform,
            'location': self.location,
            'size': self.size,
            'condition': self.condition,
            'brand': self.brand,
            'drop_field': self.drop_field,
            'profit_amount': self.profit_amount,
            'profit_percentage': self.profit_percentage
        }

class BusinessCategory(db.Model):
    """Business-specific categories for assets, transactions, and inventory"""
    __tablename__ = 'business_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_type = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.Text)
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True, index=True)
    
    # CHANGED: from DATETIME to DATE
    created_at = db.Column(db.Date, default=date.today)
    
    # REMOVED: color field (why was this here indeed!)
    
    def __repr__(self):
        return f'<BusinessCategory {self.name} ({self.category_type})>'
    
    @staticmethod
    def get_by_type(category_type):
        """Get all active categories of a specific type"""
        return BusinessCategory.query.filter_by(
            category_type=category_type, 
            is_active=True
        ).order_by(BusinessCategory.name).all()
    
    @staticmethod
    def get_asset_categories():
        """Get all asset categories"""
        return BusinessCategory.get_by_type('asset_category')
    
    @staticmethod
    def get_transaction_categories():
        """Get all transaction categories"""
        return BusinessCategory.get_by_type('transaction_category')
    
    @staticmethod
    def get_inventory_categories():
        """Get all inventory categories"""
        return BusinessCategory.get_by_type('inventory_category')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'category_type': self.category_type,
            'description': self.description,
            'is_default': self.is_default,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class BusinessCondition(db.Model):
    """Business inventory conditions"""
    __tablename__ = 'business_conditions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True, index=True)
    description = db.Column(db.Text)
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True, index=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<BusinessCondition {self.name}>'
    
    @staticmethod
    def get_active_conditions():
        """Get all active conditions ordered by name"""
        return BusinessCondition.query.filter_by(is_active=True).order_by(BusinessCondition.name).all()
    
    @staticmethod
    def condition_exists(name):
        """Check if condition exists (case insensitive)"""
        return BusinessCondition.query.filter(
            db.func.lower(BusinessCondition.name) == name.lower(),
            BusinessCondition.is_active == True
        ).first() is not None
    
    @classmethod
    def create_condition(cls, name, description=None):
        """Create a new condition with duplicate checking"""
        if cls.condition_exists(name):
            raise ValueError(f"Condition '{name}' already exists")
        
        condition = cls(
            name=name.strip(),
            description=description.strip() if description else None
        )
        
        try:
            db.session.add(condition)
            db.session.commit()
            return condition
        except Exception as e:
            db.session.rollback()
            raise e
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_default': self.is_default,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
# Helper functions for database operations
def get_financial_summary(year=None, month=None):
    """Get financial summary for a given period"""
    from sqlalchemy import func, extract
    
    query = db.session.query(
        BusinessTransaction.transaction_type,
        func.sum(BusinessTransaction.amount).label('total')
    )
    
    if year:
        query = query.filter(extract('year', BusinessTransaction.date) == year)
    if month:
        query = query.filter(extract('month', BusinessTransaction.date) == month)
    
    results = query.group_by(BusinessTransaction.transaction_type).all()
    
    summary = {'income': 0, 'expense': 0}
    for transaction_type, total in results:
        if transaction_type.lower() == 'income':
            summary['income'] = float(total)
        elif transaction_type.lower() == 'expense':
            summary['expense'] = float(total)
    
    summary['profit'] = summary['income'] - summary['expense']
    summary['profit_margin'] = (summary['profit'] / summary['income'] * 100) if summary['income'] > 0 else 0
    
    return summary

def get_inventory_summary():
    """Get inventory summary statistics - Updated for new schema"""
    from sqlalchemy import func
    
    # Active inventory (no more is_active field)
    active_inventory = db.session.query(
        func.count(BusinessInventory.id).label('total_items'),
        func.sum(BusinessInventory.cost_of_item).label('total_cost'),
        func.sum(BusinessInventory.selling_price).label('total_value')
    ).filter(
        BusinessInventory.listing_status != 'sold'
    ).first()
    
    # Sold items - now from BusinessSold table
    sold_summary = db.session.query(
        func.count(BusinessSold.id).label('sold_items'),
        func.sum(BusinessSold.sold_price).label('total_revenue'),
        func.sum(BusinessSold.sold_price - BusinessSold.cost_of_item).label('total_profit')
    ).first()
    
    return {
        'total_items': active_inventory.total_items or 0,
        'total_cost': float(active_inventory.total_cost or 0),
        'total_value': float(active_inventory.total_value or 0),
        'sold_items': sold_summary.sold_items or 0,
        'total_revenue': float(sold_summary.total_revenue or 0),
        'total_profit': float(sold_summary.total_profit or 0)
    }

def get_assets_summary():
    """Get assets summary statistics - Updated for new schema"""
    from sqlalchemy import func
    
    summary = db.session.query(
        func.count(BusinessAsset.id).label('total_assets'),
        func.sum(BusinessAsset.purchase_price).label('total_purchase_value')
    ).filter(BusinessAsset.is_active == True).first()
    
    disposed_count = db.session.query(func.count(BusinessAsset.id)).filter(
        BusinessAsset.is_active == False
    ).scalar()
    
    return {
        'total_assets': summary.total_assets or 0,
        'total_purchase_value': float(summary.total_purchase_value or 0),
        'disposed_assets': disposed_count or 0
    }