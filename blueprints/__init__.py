from flask import Blueprint

# Create business blueprint
business_bp = Blueprint('business', __name__, 
                       template_folder='templates',
                       static_folder='static')