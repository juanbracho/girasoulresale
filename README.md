# Girasoul Business Dashboard

A comprehensive Flask-based inventory and business management system designed specifically for Instagram thrift clothing resale businesses. Track unique inventory items, manage financial transactions, and gain business insights through an intuitive web dashboard.

## 🎯 **Project Overview**

Girasoul Business Dashboard is a local web application built to streamline operations for small thrift clothing resale businesses. The system handles the unique challenges of thrift retail where each item is one-of-a-kind, automatically creates financial transactions for purchases and sales, and provides comprehensive business analytics.

### **Key Features**

- **📦 Inventory Management**: Track unique clothing items with detailed attributes (brand, size, condition, cost, pricing)
- **💰 Financial Tracking**: Automatic transaction creation for purchases and sales with profit calculations
- **📊 Business Dashboard**: Real-time metrics, charts, and insights for business performance
- **🏢 Asset Management**: Track business assets, equipment, and depreciation
- **🔄 Lifecycle Tracking**: Monitor items from acquisition through sale with status updates
- **💳 Multi-Platform Sales**: Support for Facebook, Instagram, Poshmark, and Friends & Family sales

## 🛠️ **Technology Stack**

### **Backend**
- **Flask 3.0+**: Python web framework
- **SQLAlchemy 2.0+**: Database ORM
- **SQLite**: Local database storage
- **Blueprint Architecture**: Modular application structure

### **Frontend**
- **Bootstrap 5**: Responsive UI framework
- **Vanilla JavaScript**: Client-side functionality
- **Chart.js/Plotly**: Data visualization
- **HTML5/CSS3**: Modern web standards

### **Architecture**
- **Modular Blueprints**: Organized into API, services, views, and utilities
- **Service Layer**: Business logic separation
- **RESTful API**: JSON endpoints for dynamic functionality

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8+ (Python 3.13+ recommended)
- Git (optional, for cloning)

### **Installation**

1. **Clone or download the repository**
   ```bash
   git clone <repository-url>
   cd girasoul
   ```

2. **Install Python dependencies**
   ```bash
   # On Windows (recommended)
   py -m pip install --upgrade Flask Flask-SQLAlchemy SQLAlchemy

   # On macOS/Linux
   pip install --upgrade Flask Flask-SQLAlchemy SQLAlchemy
   ```

3. **Run the application**
   ```bash
   # On Windows
   py app.py

   # On macOS/Linux
   python app.py
   ```

4. **Access the dashboard**
   - Open your web browser
   - Navigate to: `http://127.0.0.1:5000`

### **First-Time Setup**
The application will automatically:
- Create the `data/` directory for database storage
- Initialize the SQLite database (`data/business.db`)
- Set up default categories for inventory and transactions
- Display startup statistics in the console

## 📁 **Project Structure**

```
girasoul/
├── app.py                          # Main Flask application entry point
├── config.py                       # Application configuration
├── models.py                       # Database models and schema
├── requirements.txt                # Python dependencies
├── data/                           # Database and uploads directory
│   └── business.db                 # SQLite database (auto-generated)
│
├── blueprints/                     # Application modules
│   ├── api/                        # REST API endpoints
│   │   ├── assets.py              # Asset management API
│   │   ├── inventory.py           # Inventory management API
│   │   └── transactions.py        # Financial transactions API
│   │
│   ├── services/                   # Business logic layer
│   │   ├── asset_service.py       # Asset calculations and logic
│   │   ├── inventory_service.py   # Inventory operations
│   │   └── transaction_service.py # Financial calculations
│   │
│   ├── utils/                      # Shared utilities
│   │   ├── calculations.py        # Mathematical operations
│   │   ├── database.py            # Database utilities
│   │   └── validators.py          # Data validation
│   │
│   └── views/                      # Web interface routes
│       ├── dashboard.py           # Main dashboard views
│       ├── assets.py              # Asset management pages
│       ├── financial.py           # Financial management pages
│       └── inventory.py           # Inventory management pages
│
├── static/                         # CSS, JavaScript, and images
│   ├── css/                       # Stylesheets by feature
│   │   ├── main.css              # Global styles
│   │   ├── dashboard.css         # Dashboard-specific styles
│   │   ├── inventory.css         # Inventory page styles
│   │   └── financial.css         # Financial page styles
│   │
│   └── js/                        # JavaScript by feature
│       ├── main.js               # Global functionality
│       ├── dashboard.js          # Dashboard interactions
│       ├── inventory.js          # Inventory management
│       └── financial.js          # Financial operations
│
└── templates/                      # HTML templates
    ├── base.html                  # Base template with navigation
    ├── dashboard.html             # Main dashboard page
    │
    ├── components/                # Reusable components
    │   ├── modals/               # Form dialogs
    │   │   ├── inventory_modal.html
    │   │   ├── transactions_modal.html
    │   │   └── asset_modal.html
    │   │
    │   └── charts/               # Chart components
    │       ├── revenue_chart.html
    │       ├── expense_chart.html
    │       └── inventory_chart.html
    │
    └── errors/                    # Error pages
        ├── 404.html
        └── 500.html
```

## 💼 **Business Workflow**

### **Adding New Inventory**
1. Navigate to Inventory Management
2. Click "Add New Item"
3. Fill in item details (brand, type, size, condition, cost, price)
4. **Automatic**: System creates expense transaction for item cost
5. Item appears in active inventory

### **Selling Items**
1. Find item in inventory list
2. Click "Mark as Sold"
3. Enter sale details (actual selling price, platform)
4. **Automatic**: System creates income transaction and calculates profit
5. Item moves to sold items history

### **Financial Tracking**
- **Dashboard**: View monthly revenue, expenses, and profit
- **Transactions**: Manual income/expense entry for non-inventory items
- **Reports**: Generate financial summaries and charts

## 🔧 **Configuration**

### **Environment Variables**
Create a `.env` file for customization:

```bash
# Database
DATABASE_URL=sqlite:///data/business.db

# Security
SECRET_KEY=your-secret-key-here

# Business Settings
DEFAULT_CURRENCY=USD
TAX_RATE=0.08

# Development
FLASK_DEBUG=True
SQLALCHEMY_ECHO=False
```

### **Business Categories**
The system includes default categories that can be customized:

**Inventory Categories**: Tops, Bottoms, Dresses, Shoes, Accessories, Outerwear, Activewear, Intimates, Mens, Other

**Transaction Categories**: Sales Revenue, Cost of Goods Sold, Marketing & Advertising, Operations, Equipment & Supplies, Professional Services

## 📊 **Dashboard Features**

### **Key Metrics**
- Monthly revenue and expenses
- Profit margins and trends
- Inventory count and value
- Top-selling categories

### **Visual Analytics**
- Revenue vs expense charts
- Monthly performance trends
- Inventory distribution
- Profit analysis

### **Quick Actions**
- Add new inventory items
- Record transactions
- Mark items as sold
- View recent activity

## 🛡️ **Data Security**

- **Local Storage**: All data stored locally in SQLite database
- **No Cloud Dependencies**: Complete offline operation
- **Backup Friendly**: Simple database file for easy backups
- **Privacy Focused**: No external data transmission

## 🔄 **Database Management**

### **Backup**
```bash
# Copy the database file
cp data/business.db data/business_backup_$(date +%Y%m%d).db
```

### **Reset Database**
```bash
# Delete database (will be recreated on next startup)
rm data/business.db
```

## 🐛 **Troubleshooting**

### **Common Issues**

**Problem**: `pip not found` on Windows  
**Solution**: Use `py -m pip install` instead of `pip install`

**Problem**: SQLAlchemy compatibility errors  
**Solution**: Update to latest versions: `py -m pip install --upgrade Flask Flask-SQLAlchemy SQLAlchemy`

**Problem**: Application won't start  
**Solution**: Ensure Python 3.8+ is installed and all dependencies are met

**Problem**: Database errors  
**Solution**: Delete `data/business.db` to recreate with fresh schema

### **Development Mode**
For development with detailed error messages:
```bash
export FLASK_DEBUG=True  # Linux/macOS
set FLASK_DEBUG=True     # Windows
py app.py
```

## 🗂️ **Data Import**

The system supports importing existing business data from Excel files. See the project documentation for detailed import procedures for:
- Existing inventory items
- Historical transactions
- Asset records

## 🚀 **Performance**

- **Local Operation**: No network dependencies for core functionality
- **Lightweight**: Minimal resource requirements
- **Fast Startup**: Typically loads in under 5 seconds
- **Efficient Queries**: Optimized for small to medium business scale

## 📈 **Scalability**

Designed for personal to small business use:
- **Inventory Items**: Efficiently handles 1,000+ unique items
- **Transactions**: Supports years of financial history
- **Performance**: Optimized for local SQLite operations

## 🤝 **Support**

This is a personal business management tool. For issues:
1. Check the troubleshooting section above
2. Review console output for error messages
3. Ensure all dependencies are properly installed
4. Verify Python version compatibility

## 📝 **License**

This project is created for personal business use. Please respect intellectual property and use responsibly.

---

**Built with ❤️ for small business owners who value simplicity and control over their data.**