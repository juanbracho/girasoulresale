"""
Data validation functions for Girasoul Business Dashboard
"""

import re
from datetime import datetime, date
from decimal import Decimal, InvalidOperation

# General Validation Functions

def validate_required_fields(data, required_fields):
    """Validate that all required fields are present and not empty"""
    missing_fields = []
    
    for field in required_fields:
        if not data.get(field) or (isinstance(data.get(field), str) and data.get(field).strip() == ''):
            missing_fields.append(field)
    
    if missing_fields:
        return {'valid': False, 'error': f'Missing required fields: {", ".join(missing_fields)}'}
    
    return {'valid': True}

def validate_string_length(value, field_name, min_length=0, max_length=255):
    """Validate string length"""
    if not isinstance(value, str):
        return {'valid': False, 'error': f'{field_name} must be a string'}
    
    length = len(value.strip())
    
    if length < min_length:
        return {'valid': False, 'error': f'{field_name} must be at least {min_length} characters long'}
    
    if length > max_length:
        return {'valid': False, 'error': f'{field_name} must be no more than {max_length} characters long'}
    
    return {'valid': True}

def validate_positive_number(value, field_name, allow_zero=False):
    """Validate that value is a positive number"""
    try:
        num_value = float(value)
        
        if allow_zero and num_value < 0:
            return {'valid': False, 'error': f'{field_name} must be zero or greater'}
        elif not allow_zero and num_value <= 0:
            return {'valid': False, 'error': f'{field_name} must be greater than zero'}
        
        return {'valid': True, 'value': num_value}
        
    except (ValueError, TypeError):
        return {'valid': False, 'error': f'{field_name} must be a valid number'}

def validate_currency_amount(value, field_name, allow_zero=False):
    """Validate currency amount (up to 2 decimal places)"""
    try:
        # Convert to Decimal for precise currency handling
        decimal_value = Decimal(str(value))
        
        # Check if it has more than 2 decimal places
        if decimal_value.as_tuple().exponent < -2:
            return {'valid': False, 'error': f'{field_name} cannot have more than 2 decimal places'}
        
        float_value = float(decimal_value)
        
        if allow_zero and float_value < 0:
            return {'valid': False, 'error': f'{field_name} must be zero or greater'}
        elif not allow_zero and float_value <= 0:
            return {'valid': False, 'error': f'{field_name} must be greater than zero'}
        
        return {'valid': True, 'value': float_value}
        
    except (ValueError, TypeError, InvalidOperation):
        return {'valid': False, 'error': f'{field_name} must be a valid currency amount'}

def validate_date_string(date_string, field_name, date_format='%Y-%m-%d'):
    """Validate date string format"""
    try:
        parsed_date = datetime.strptime(date_string, date_format).date()
        return {'valid': True, 'value': parsed_date}
    except (ValueError, TypeError):
        return {'valid': False, 'error': f'{field_name} must be in format YYYY-MM-DD'}

def validate_date_range(start_date, end_date, field_prefix='Date'):
    """Validate that start date is before or equal to end date"""
    try:
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if start_date > end_date:
            return {'valid': False, 'error': f'{field_prefix} start must be before or equal to end date'}
        
        return {'valid': True}
        
    except (ValueError, TypeError):
        return {'valid': False, 'error': f'{field_prefix} format must be YYYY-MM-DD'}

def validate_percentage(value, field_name, min_percent=0, max_percent=100):
    """Validate percentage value"""
    try:
        percent_value = float(value)
        
        if percent_value < min_percent or percent_value > max_percent:
            return {'valid': False, 'error': f'{field_name} must be between {min_percent}% and {max_percent}%'}
        
        return {'valid': True, 'value': percent_value}
        
    except (ValueError, TypeError):
        return {'valid': False, 'error': f'{field_name} must be a valid percentage'}

def validate_integer(value, field_name, min_value=None, max_value=None):
    """Validate integer value"""
    try:
        int_value = int(value)
        
        if min_value is not None and int_value < min_value:
            return {'valid': False, 'error': f'{field_name} must be at least {min_value}'}
        
        if max_value is not None and int_value > max_value:
            return {'valid': False, 'error': f'{field_name} must be no more than {max_value}'}
        
        return {'valid': True, 'value': int_value}
        
    except (ValueError, TypeError):
        return {'valid': False, 'error': f'{field_name} must be a valid integer'}

# Business-Specific Validation Functions

def validate_transaction_data(data):
    """Validate business transaction data"""
    # Required fields validation
    required_fields = ['transaction_type', 'date', 'description', 'amount', 'category', 'account_name']
    validation = validate_required_fields(data, required_fields)
    if not validation['valid']:
        return validation
    
    # Validate transaction type
    if data['transaction_type'] not in ['Income', 'Expense']:
        return {'valid': False, 'error': 'Transaction type must be Income or Expense'}
    
    # Validate amount
    validation = validate_currency_amount(data['amount'], 'Amount')
    if not validation['valid']:
        return validation
    
    # Validate date
    validation = validate_date_string(data['date'], 'Date')
    if not validation['valid']:
        return validation
    
    # Validate description length
    validation = validate_string_length(data['description'], 'Description', min_length=3, max_length=255)
    if not validation['valid']:
        return validation
    
    # Validate category length
    validation = validate_string_length(data['category'], 'Category', min_length=2, max_length=100)
    if not validation['valid']:
        return validation
    
    # Validate account name length
    validation = validate_string_length(data['account_name'], 'Account Name', min_length=2, max_length=100)
    if not validation['valid']:
        return validation
    
    # Optional fields validation
    if data.get('vendor'):
        validation = validate_string_length(data['vendor'], 'Vendor', max_length=100)
        if not validation['valid']:
            return validation
    
    if data.get('invoice_number'):
        validation = validate_string_length(data['invoice_number'], 'Invoice Number', max_length=50)
        if not validation['valid']:
            return validation
    
    return {'valid': True}

def validate_inventory_data(data):
    """Validate inventory item data - CORRECTED for actual database schema"""
    # Required fields validation - using CORRECT field names that match database
    required_fields = ['name', 'category', 'cost_of_item', 'selling_price', 'brand', 'size', 'condition', 'location', 'description']
    validation = validate_required_fields(data, required_fields)
    if not validation['valid']:
        return validation
    
    # Validate SKU if provided
    if data.get('sku'):
        validation = validate_sku(data['sku'])
        if not validation['valid']:
            return validation
    
    # Validate name length
    validation = validate_string_length(data['name'], 'Name', min_length=2, max_length=100)
    if not validation['valid']:
        return validation
    
    # Validate cost_of_item (CORRECT FIELD NAME)
    validation = validate_currency_amount(data['cost_of_item'], 'Cost per unit')
    if not validation['valid']:
        return validation
    
    # Validate selling price
    validation = validate_currency_amount(data['selling_price'], 'Selling price')
    if not validation['valid']:
        return validation
    
    # Validate that selling price is higher than cost
    try:
        cost = float(data['cost_of_item'])  # CORRECT FIELD NAME
        price = float(data['selling_price'])
        if price <= cost:
            return {'valid': False, 'error': 'Selling price must be higher than cost per unit'}
    except (ValueError, TypeError):
        return {'valid': False, 'error': 'Invalid cost or price format'}
    
    # Validate category
    validation = validate_string_length(data['category'], 'Category', min_length=2, max_length=50)
    if not validation['valid']:
        return validation
    
    # Validate brand (required now)
    validation = validate_string_length(data['brand'], 'Brand', min_length=1, max_length=100)
    if not validation['valid']:
        return validation
    
    # Validate size (required now)
    validation = validate_string_length(data['size'], 'Size', min_length=1, max_length=20)
    if not validation['valid']:
        return validation
    
    # Validate condition (required now)
    validation = validate_string_length(data['condition'], 'Condition', min_length=1, max_length=20)
    if not validation['valid']:
        return validation
    
    # Validate location (required now)
    validation = validate_string_length(data['location'], 'Location', min_length=1, max_length=100)
    if not validation['valid']:
        return validation
    
    # Validate description (required now)
    validation = validate_string_length(data['description'], 'Description', min_length=3, max_length=500)
    if not validation['valid']:
        return validation
    
    return {'valid': True}

# SKU validation function if it doesn't exist:
def validate_sku(sku):
    """Validate SKU format"""
    if not sku or not isinstance(sku, str):
        return {'valid': False, 'error': 'SKU must be a non-empty string'}
    
    if len(sku) > 50:
        return {'valid': False, 'error': 'SKU must be 50 characters or less'}
    
    return {'valid': True}

def validate_asset_data(data):
    """Validate business asset data"""
    # Required fields validation
    required_fields = ['name', 'asset_category', 'asset_type', 'purchase_date', 'purchase_price']
    validation = validate_required_fields(data, required_fields)
    if not validation['valid']:
        return validation
    
    # Validate name length
    validation = validate_string_length(data['name'], 'Name', min_length=2, max_length=100)
    if not validation['valid']:
        return validation
    
    # Validate purchase price
    validation = validate_currency_amount(data['purchase_price'], 'Purchase price')
    if not validation['valid']:
        return validation
    
    # Validate purchase date
    validation = validate_date_string(data['purchase_date'], 'Purchase date')
    if not validation['valid']:
        return validation
    
    # Validate asset category
    validation = validate_string_length(data['asset_category'], 'Asset category', min_length=2, max_length=50)
    if not validation['valid']:
        return validation
    
    # Validate asset type
    validation = validate_string_length(data['asset_type'], 'Asset type', min_length=2, max_length=50)
    if not validation['valid']:
        return validation
    
    # Validate warranty expiry date if provided
    if data.get('warranty_expiry'):
        validation = validate_date_string(data['warranty_expiry'], 'Warranty expiry date')
        if not validation['valid']:
            return validation
        
        # Validate date range (warranty should be after purchase)
        validation = validate_date_range(data['purchase_date'], data['warranty_expiry'], 'Warranty')
        if not validation['valid']:
            return validation
    
    # Validate depreciation years if provided
    if data.get('depreciation_years') is not None:
        validation = validate_integer(data['depreciation_years'], 'Depreciation years', min_value=1, max_value=50)
        if not validation['valid']:
            return validation
    
    # Validate salvage value if provided
    if data.get('salvage_value') is not None:
        validation = validate_currency_amount(data['salvage_value'], 'Salvage value', allow_zero=True)
        if not validation['valid']:
            return validation
    
    # Validate optional string fields
    if data.get('vendor'):
        validation = validate_string_length(data['vendor'], 'Vendor', max_length=100)
        if not validation['valid']:
            return validation
    
    if data.get('location'):
        validation = validate_string_length(data['location'], 'Location', max_length=100)
        if not validation['valid']:
            return validation
    
    if data.get('serial_number'):
        validation = validate_string_length(data['serial_number'], 'Serial number', max_length=100)
        if not validation['valid']:
            return validation
    
    return {'valid': True}

def validate_category_data(data):
    """Validate business category data"""
    # Required fields validation
    required_fields = ['name', 'category_type']
    validation = validate_required_fields(data, required_fields)
    if not validation['valid']:
        return validation
    
    # Validate name length
    validation = validate_string_length(data['name'], 'Name', min_length=2, max_length=100)
    if not validation['valid']:
        return validation
    
    # Validate category type
    valid_types = ['asset_category', 'transaction_category', 'inventory_category']
    if data['category_type'] not in valid_types:
        return {'valid': False, 'error': f'Category type must be one of: {", ".join(valid_types)}'}
    
    # Validate optional description
    if data.get('description'):
        validation = validate_string_length(data['description'], 'Description', max_length=500)
        if not validation['valid']:
            return validation
    
    return {'valid': True}


def validate_report_data(data):
    """Validate business report data"""
    # Required fields validation
    required_fields = ['report_name', 'report_type', 'date_from', 'date_to']
    validation = validate_required_fields(data, required_fields)
    if not validation['valid']:
        return validation
    
    # Validate report name
    validation = validate_string_length(data['report_name'], 'Report name', min_length=3, max_length=100)
    if not validation['valid']:
        return validation
    
    # Validate report type
    valid_types = ['financial', 'inventory', 'assets', 'transactions', 'custom']
    if data['report_type'] not in valid_types:
        return {'valid': False, 'error': f'Report type must be one of: {", ".join(valid_types)}'}
    
    # Validate dates
    validation = validate_date_string(data['date_from'], 'Date from')
    if not validation['valid']:
        return validation
    
    validation = validate_date_string(data['date_to'], 'Date to')
    if not validation['valid']:
        return validation
    
    # Validate date range
    validation = validate_date_range(data['date_from'], data['date_to'], 'Report date')
    if not validation['valid']:
        return validation
    
    return {'valid': True}

def sanitize_input(value, max_length=None):
    """Sanitize user input by removing potentially harmful characters"""
    if not isinstance(value, str):
        return value
    
    # Remove potentially harmful characters
    sanitized = re.sub(r'[<>"\';\\]', '', value.strip())
    
    # Truncate if max_length specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized

def is_safe_filename(filename):
    """Check if filename is safe for file operations"""
    if not filename:
        return False
    
    # Check for potentially dangerous patterns
    dangerous_patterns = [
        '..', '/', '\\', ':', '*', '?', '"', '<', '>', '|',
        'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    ]
    
    filename_upper = filename.upper()
    
    for pattern in dangerous_patterns:
        if pattern in filename_upper:
            return False
    
    # Check length
    if len(filename) > 255:
        return False
    
    return True