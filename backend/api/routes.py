from flask import Blueprint, jsonify, current_app
from .models import SalesAggregated

# Create Blueprint for API routes
api_bp = Blueprint('api', __name__)

# Health check endpoint
@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'API is running correctly'})

# Get all sales data
@api_bp.route('/sales', methods=['GET'])
def get_all_sales():
    try:
        # Get sales data from database
        session = current_app.db_session
        sales = session.query(SalesAggregated).all()
        
        # Return data as JSON
        return jsonify({
            'success': True,
            'data': [sale.to_dict() for sale in sales],
            'count': len(sales)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Get sales for a specific product
@api_bp.route('/sales/<int:product_id>', methods=['GET'])
def get_product_sales(product_id):
    try:
        # Get product data from database
        session = current_app.db_session
        sale = session.query(SalesAggregated).filter_by(product_id=product_id).first()
        
        # Check if product exists
        if not sale:
            return jsonify({
                'success': False,
                'error': f'Product with ID {product_id} not found'
            }), 404
            
        # Return data as JSON
        return jsonify({
            'success': True,
            'data': sale.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Get top selling products
@api_bp.route('/sales/top/<int:limit>', methods=['GET'])
def get_top_sales(limit):
    try:
        # Get top products from database
        session = current_app.db_session
        sales = session.query(SalesAggregated).order_by(
            SalesAggregated.total_sale_amount.desc()
        ).limit(limit).all()
        
        # Return data as JSON
        return jsonify({
            'success': True,
            'data': [sale.to_dict() for sale in sales],
            'count': len(sales)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500 