import os
from flask import Flask, render_template, redirect, url_for
from blueprints.api.category_condition_api import category_condition_api
from models import BusinessCondition

def register_error_handlers(app):
    """Register error handlers"""
    from flask import render_template
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        from models import db
        db.session.rollback()
        return render_template('errors/500.html'), 500

def create_app():
    """Application factory for Girasoul Business Dashboard"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('config.Config')
    
    # Import and initialize database with app
    from models import db
    db.init_app(app)
    
    # Ensure data directory exists
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"✅ Created data directory: {data_dir}")
    
    # Register blueprints AFTER db initialization
    register_blueprints(app)
    
    # Create database tables within app context
    with app.app_context():
        create_database_tables()
        # migrate_database_schema()  # Temporarily disabled
    
    # Register error handlers
    register_error_handlers(app)
    
    print("🚀 Girasoul Business Dashboard initialized successfully!")
    return app

def register_blueprints(app):
    """Register all business blueprints"""
    
    # Views Blueprints (register first)
    try:
        from blueprints.views.dashboard import dashboard_bp
        from blueprints.views.assets import assets_bp
        from blueprints.views.financial import financial_bp
        from blueprints.views.inventory import inventory_bp
        from blueprints.views.insights import insights_bp
        
        # Register views with proper URL prefixes
        app.register_blueprint(dashboard_bp)  # Root level (/)
        app.register_blueprint(assets_bp, url_prefix='/assets')
        app.register_blueprint(financial_bp, url_prefix='/financial')
        app.register_blueprint(inventory_bp, url_prefix='/inventory')
        app.register_blueprint(insights_bp)  # Root level for /insights
        app.register_blueprint(category_condition_api, url_prefix='/api')
        print("✅ Views blueprints registered")
        
    except ImportError as e:
        print(f"⚠️ Views blueprints import error: {e}")
        import traceback
        traceback.print_exc()
    
    # API Blueprints (register with correct prefix)
    try:
        from blueprints.api.assets import assets_api_bp
        from blueprints.api.inventory import inventory_api_bp
        from blueprints.api.transactions import transactions_api_bp
        from blueprints.api.insights import insights_api_bp
        
        # Register API blueprints with /api prefix only
        app.register_blueprint(assets_api_bp, url_prefix='/api/assets')
        app.register_blueprint(inventory_api_bp, url_prefix='/api/inventory')
        app.register_blueprint(transactions_api_bp, url_prefix='/api/transactions')
        app.register_blueprint(insights_api_bp)  # Already has /api/insights prefix
        print("✅ API blueprints registered correctly")
        
    except ImportError as e:
        print(f"⚠️ API blueprints import error: {e}")
        import traceback
        traceback.print_exc()
    
    # Root route - redirect to dashboard
    @app.route('/')
    def index():
        """Redirect to dashboard"""
        try:
            return redirect(url_for('dashboard.dashboard'))
        except Exception as e:
            print(f"⚠️ Dashboard redirect error: {e}")
            # Fallback to a simple dashboard page
            return render_template('dashboard.html', 
                                 metrics={}, 
                                 recent_transactions=[], 
                                 assets_summary={}, 
                                 inventory_summary={})

def create_database_tables():
    """Create all database tables if they don't exist"""
    try:
        # Import models to register them with SQLAlchemy
        from models import (
            db, BusinessTransaction, BusinessAsset, 
            BusinessInventory, BusinessSold, BusinessCategory  # Added BusinessSold, removed BusinessReport
        )
        
        # Create all tables
        db.create_all()
        
        # Initialize default data
        initialize_default_data()
        
        print("✅ Database tables created/verified")
        
    except Exception as e:
        print(f"⚠️ Database initialization error: {e}")
        import traceback
        traceback.print_exc()

def initialize_default_data():
    """Initialize default business categories and sample data"""
    try:
        from models import BusinessCategory, BusinessCondition
        
        # Check if we already have data
        if BusinessCategory.query.count() > 0:
            print("📊 Default data already exists")
            return
        
        # Default business categories (existing code - keep as is)
        default_categories = [
            # Asset categories
            ('Marketing', 'asset_category', 'Marketing and promotional materials'),
            ('Technology', 'asset_category', 'Technology equipment and devices'),
            ('Furniture', 'asset_category', 'Furniture and fixtures'),
            ('Other Assets', 'asset_category', 'Other business assets'),
            
            # Transaction categories
            ('Sales Revenue', 'transaction_category', 'Revenue from sales'),
            ('Service Revenue', 'transaction_category', 'Revenue from services'),
            ('Other Income', 'transaction_category', 'Other business income'),
            ('Cost of Goods Sold', 'transaction_category', 'Direct costs of goods sold'),
            ('Marketing & Advertising', 'transaction_category', 'Marketing and advertising expenses'),
            ('Operations', 'transaction_category', 'Operational expenses'),
            ('Equipment & Supplies', 'transaction_category', 'Equipment and supplies'),
            ('Professional Services', 'transaction_category', 'Legal, accounting, consulting'),
            ('Travel & Transport', 'transaction_category', 'Business travel expenses'),
            ('Other Expenses', 'transaction_category', 'Other business expenses'),
            
            # Inventory categories
            ('Tops', 'inventory_category', 'Shirts, blouses, tank tops'),
            ('Bottoms', 'inventory_category', 'Pants, jeans, skirts'),
            ('Dresses', 'inventory_category', 'All types of dresses'),
            ('Shoes', 'inventory_category', 'Footwear'),
            ('Accessories', 'inventory_category', 'Jewelry, bags, belts'),
            ('Outerwear', 'inventory_category', 'Jackets, coats'),
            ('Activewear', 'inventory_category', 'Workout and sports clothing'),
            ('Intimates', 'inventory_category', 'Undergarments and sleepwear'),
            ('Mens', 'inventory_category', 'Mens clothing items'),
            ('Other', 'inventory_category', 'Other clothing items'),
        ]
        
        for name, category_type, description in default_categories:
            category = BusinessCategory(
                name=name,
                category_type=category_type,
                description=description,
                is_default=True,
                is_active=True
            )
            db.session.add(category)
        
        db.session.commit()
        print(f"✅ Created {len(default_categories)} default business categories")
        
        # ADD THIS NEW SECTION - Default inventory conditions
        default_conditions = [
            ('good', 'Good condition - shows normal wear'),
            ('NWT', 'New with Tags - brand new item with original tags'),
            ('NWOT', 'New without Tags - brand new item without original tags')
        ]
        
        for name, description in default_conditions:
            condition = BusinessCondition(
                name=name,
                description=description,
                is_default=True,
                is_active=True
            )
            db.session.add(condition)
        
        db.session.commit()
        print(f"✅ Created {len(default_conditions)} default business conditions")
        
    except Exception as e:
        print(f"❌ Error initializing default data: {e}")
        db.session.rollback()

def migrate_database_schema():
    """Handle database schema migrations gracefully"""
    try:
        from models import db, BusinessInventory
        from sqlalchemy import text
        
        # Check if we need to add date_added column
        try:
            # Try to query using date_added - if it fails, the column doesn't exist
            with db.engine.connect() as conn:
                conn.execute(text("SELECT date_added FROM business_inventory LIMIT 1"))
            print("✅ Database schema is up to date")
        except Exception as e:
            print(f"⚠️ Database schema migration needed: {e}")
            try:
                # Try to add the column manually (this is SQLite specific)
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE business_inventory ADD COLUMN date_added DATE'))
                    conn.commit()
                print("✅ Successfully added date_added column")
            except Exception as migration_error:
                print(f"⚠️ Could not add date_added column: {migration_error}")
                print("📝 Database will work without this column")
        
    except Exception as e:
        print(f"❌ Error during database migration: {e}")

def get_database_stats():
    """Get basic statistics about the database content"""
    try:
        from models import BusinessTransaction, BusinessAsset, BusinessInventory, BusinessSold, BusinessCategory
        
        # Get stats with error handling for missing columns
        try:
            inventory_count = BusinessInventory.query.filter(BusinessInventory.listing_status != 'sold').count()
        except Exception:
            # Fallback if there are schema issues
            inventory_count = BusinessInventory.query.count()
        
        try:
            sold_count = BusinessInventory.query.filter_by(listing_status='sold').count()
        except Exception:
            sold_count = 0
        
        stats = {
            'transactions': BusinessTransaction.query.count(),
            'assets': BusinessAsset.query.filter_by(is_active=True).count(),
            'inventory_items': inventory_count,
            'sold_items': sold_count,
            'categories': BusinessCategory.query.filter_by(is_active=True).count()
        }
        
        return stats
        
    except Exception as e:
        print(f"❌ Error getting database stats: {e}")
        return {
            'transactions': 0,
            'assets': 0,
            'inventory_items': 0,
            'sold_items': 0,
            'categories': 0
        }


if __name__ == '__main__':
    print("🚀 Starting Girasoul Business Dashboard...")
    print("📊 Dashboard will be available at: http://127.0.0.1:5000")
    print("💾 Using database: data/business.db")
    print("=" * 60)
    
    # Create and run the app
    app = create_app()
    
    # Show database stats
    with app.app_context():
        stats = get_database_stats()
        print("\n📊 Database Statistics:")
        print(f"   - Transactions: {stats['transactions']:,}")
        print(f"   - Assets: {stats['assets']}")
        print(f"   - Inventory items: {stats['inventory_items']}")
        print(f"   - Sold items: {stats['sold_items']}")
        print(f"   - Categories: {stats['categories']}")
    
    print("\n🌟 Ready to start! Database is initialized and connected...")
    print("=" * 60)
    
    app.run(debug=True, host='127.0.0.1', port=5000)