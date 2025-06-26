"""
Database utilities for Girasoul Business Dashboard
"""

import os
from datetime import datetime, date
from pathlib import Path
from models import db, BusinessTransaction, BusinessAsset, BusinessInventory, BusinessCategory

def ensure_data_directory():
    """Ensure the data directory exists"""
    data_dir = Path(__file__).parent.parent.parent / 'data'
    data_dir.mkdir(exist_ok=True)
    return data_dir

def create_database_tables():
    """Create all database tables if they don't exist"""
    try:
        # Create all tables
        db.create_all()
        print("✅ Database tables created/verified")
        return True
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return False

def initialize_sample_data():
    """Initialize sample business data for testing/demo"""
    try:
        # Check if we already have transactions
        if BusinessTransaction.query.count() > 0:
            print("📊 Sample data already exists")
            return True
        
        print("📊 Initializing sample business data...")
        
        # Sample business transactions
        sample_transactions = [
            {
                'date': date(2024, 12, 1),
                'description': 'Online sales - Multiple items',
                'amount': 245.00,
                'category': 'Sales Revenue',
                'sub_category': 'Online Store',
                'transaction_type': 'Income',
                'account_name': 'Business Checking',
                'notes': 'Website sales'
            },
            {
                'date': date(2024, 12, 5),
                'description': 'Instagram advertising campaign',
                'amount': 85.00,
                'category': 'Marketing & Advertising',
                'sub_category': 'Social Media',
                'transaction_type': 'Expense',
                'account_name': 'Business Credit Card',
                'vendor': 'Meta Platforms',
                'invoice_number': 'INV-2024-001',
                'notes': 'Social media ads'
            },
            {
                'date': date(2024, 12, 10),
                'description': 'Inventory restocking',
                'amount': 375.00,
                'category': 'Cost of Goods Sold',
                'sub_category': 'Inventory Purchase',
                'transaction_type': 'Expense',
                'account_name': 'Business Checking',
                'vendor': 'Fashion Wholesale Co',
                'invoice_number': 'INV-2024-002',
                'notes': 'Restocked inventory'
            },
            {
                'date': date(2024, 12, 15),
                'description': 'Market booth rental',
                'amount': 125.00,
                'category': 'Operations',
                'sub_category': 'Venue Rental',
                'transaction_type': 'Expense',
                'account_name': 'Business Checking',
                'vendor': 'Local Market Association',
                'notes': 'Weekend market booth'
            }
        ]
        
        for transaction_data in sample_transactions:
            transaction = BusinessTransaction(**transaction_data)
            db.session.add(transaction)
        
        # Sample business assets
        sample_assets = [
            {
                'name': 'iPad POS System',
                'description': 'Point of sale system with card reader',
                'asset_category': 'Technology',
                'asset_type': 'POS Equipment',
                'purchase_date': date(2024, 1, 15),
                'purchase_price': 850.00,
                'current_value': 850.00,
                'location': 'Main Store',
                'vendor': 'Square Inc'
            },
            {
                'name': 'Clothing Rack Set',
                'description': 'Professional metal clothing racks for displays',
                'asset_category': 'Furniture',
                'asset_type': 'Display Equipment',
                'purchase_date': date(2024, 3, 20),
                'purchase_price': 450.00,
                'current_value': 450.00,
                'location': 'Display Area',
                'vendor': 'Display Solutions Inc'
            },
            {
                'name': 'Business Cards',
                'description': 'Professional business cards with logo design',
                'asset_category': 'Marketing',
                'asset_type': 'Marketing Materials',
                'purchase_date': date(2024, 2, 10),
                'purchase_price': 150.00,
                'current_value': 150.00,
                'location': 'Office Storage',
                'vendor': 'PrintShop Pro'
            }
        ]
        
        for asset_data in sample_assets:
            asset = BusinessAsset(**asset_data)
            db.session.add(asset)
        
        # Sample inventory items
        sample_inventory = [
            {
                'sku': 'ITEM-001',
                'name': 'Summer Tank Top',
                'description': 'Cotton blend tank top in various colors',
                'category': 'Tops',
                'supplier': 'Fashion Wholesale Co',
                'cost_per_unit': 12.50,
                'selling_price': 25.00,
                'quantity_on_hand': 5,
                'listing_status': 'inventory',
                'location': 'Main Inventory',
                'size': 'M',
                'condition': 'NWT',
                'brand': 'Summer Style'
            },
            {
                'sku': 'ITEM-002',
                'name': 'Casual Summer Dress',
                'description': 'Lightweight summer dress in multiple sizes',
                'category': 'Dresses',
                'supplier': 'Summer Styles Inc',
                'cost_per_unit': 18.75,
                'selling_price': 42.00,
                'quantity_on_hand': 3,
                'listing_status': 'listed',
                'location': 'Main Inventory',
                'size': 'L',
                'condition': 'EUC',
                'brand': 'Coastal Chic'
            },
            {
                'sku': 'ITEM-003',
                'name': 'Statement Necklace',
                'description': 'Handcrafted statement necklace',
                'category': 'Accessories',
                'supplier': 'Local Artisan',
                'cost_per_unit': 8.00,
                'selling_price': 22.00,
                'quantity_on_hand': 1,
                'listing_status': 'inventory',
                'location': 'Accessories Display',
                'size': 'OS',
                'condition': 'NWT',
                'brand': 'Artisan Made'
            }
        ]
        
        for inventory_data in sample_inventory:
            inventory_item = BusinessInventory(**inventory_data)
            inventory_item.update_total_values()
            db.session.add(inventory_item)
        
        db.session.commit()
        print(f"✅ Created sample data: {len(sample_transactions)} transactions, {len(sample_assets)} assets, {len(sample_inventory)} inventory items")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing sample data: {e}")
        db.session.rollback()
        return False

def validate_database():
    """Validate database integrity and structure"""
    try:
        # Check if all required tables exist
        required_tables = [
            'business_transactions',
            'business_assets', 
            'business_inventory',
            'business_categories'
        ]
        
        missing_tables = []
        for table in required_tables:
            try:
                db.session.execute(f"SELECT 1 FROM {table} LIMIT 1")
            except Exception:
                missing_tables.append(table)
        
        if missing_tables:
            print(f"❌ Missing tables: {missing_tables}")
            return False
        
        # Check if business categories exist
        category_count = BusinessCategory.query.filter_by(is_active=True).count()
        if category_count == 0:
            print("⚠️ No active business categories found")
            return False
        
        print("✅ Database validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Database validation failed: {e}")
        return False

def get_database_info():
    """Get database information and statistics"""
    try:
        info = {
            'database_path': db.engine.url.database,
            'total_transactions': BusinessTransaction.query.count(),
            'total_assets': BusinessAsset.query.count(),
            'active_assets': BusinessAsset.query.filter_by(is_active=True).count(),
            'total_inventory': BusinessInventory.query.count(),
            'active_inventory': BusinessInventory.query.filter_by(is_active=True).count(),
            'available_inventory': BusinessInventory.query.filter(
                BusinessInventory.is_active == True,
                BusinessInventory.listing_status.in_(['inventory', 'listed'])
            ).count(),
            'sold_inventory': BusinessInventory.query.filter_by(
                is_active=True, 
                listing_status='sold'
            ).count(),
            'total_categories': BusinessCategory.query.count(),
            'active_categories': BusinessCategory.query.filter_by(is_active=True).count()
        }
        
        # Get date ranges
        if info['total_transactions'] > 0:
            earliest_transaction = db.session.query(
                db.func.min(BusinessTransaction.date)
            ).scalar()
            latest_transaction = db.session.query(
                db.func.max(BusinessTransaction.date)
            ).scalar()
            
            info['transaction_date_range'] = {
                'earliest': earliest_transaction.isoformat() if earliest_transaction else None,
                'latest': latest_transaction.isoformat() if latest_transaction else None
            }
        
        return info
        
    except Exception as e:
        print(f"❌ Error getting database info: {e}")
        return {}

def backup_database(backup_path=None):
    """Create a backup of the database"""
    try:
        import shutil
        from datetime import datetime
        
        # Get current database path
        db_path = Path(db.engine.url.database)
        
        if not backup_path:
            backup_dir = db_path.parent / 'backups'
            backup_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = backup_dir / f'business_backup_{timestamp}.db'
        
        # Copy database file
        shutil.copy2(db_path, backup_path)
        
        print(f"✅ Database backup created: {backup_path}")
        return str(backup_path)
        
    except Exception as e:
        print(f"❌ Error creating database backup: {e}")
        return None

def reset_database():
    """Reset database (drop all tables and recreate)"""
    try:
        print("⚠️ Resetting database - all data will be lost!")
        
        # Drop all tables
        db.drop_all()
        print("🗑️ All tables dropped")
        
        # Recreate tables
        create_database_tables()
        
        # Reinitialize default categories
        from app import initialize_default_data
        initialize_default_data()
        
        print("✅ Database reset complete")
        return True
        
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        return False

def optimize_database():
    """Optimize database performance"""
    try:
        # SQLite specific optimizations
        if 'sqlite' in str(db.engine.url):
            db.session.execute("VACUUM")
            db.session.execute("ANALYZE")
            db.session.commit()
            print("✅ Database optimized (SQLite)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error optimizing database: {e}")
        return False