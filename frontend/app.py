from flask import Flask, render_template
import requests
import os
import json

# Create Flask application
app = Flask(__name__)

# Backend API URL configuration
app.config['API_URL'] = os.environ.get('API_URL', 'http://backend:5000/api')

# Main dashboard route
@app.route('/')
def index():
    try:
        # Get sales data from backend API
        response = requests.get(f"{app.config['API_URL']}/sales")
        
        if response.status_code == 200:
            response_data = response.json()
            
            if response_data['success']:
                # Process data for dashboard
                data = response_data['data']
                total_quantity = sum(item['total_quantity'] for item in data)
                total_amount = round(sum(item['total_sale_amount'] for item in data), 2)
                
                # Render dashboard template
                return render_template('index.html', 
                                      data=data, 
                                      total_quantity=total_quantity, 
                                      total_amount=total_amount)
        
        # Handle errors
        return render_template('index.html', 
                              data=[], 
                              total_quantity=0, 
                              total_amount=0, 
                              error="Error fetching data")
    
    except Exception as e:
        return render_template('index.html', 
                              data=[], 
                              total_quantity=0, 
                              total_amount=0, 
                              error=str(e))

# Top products route
@app.route('/top-products')
def top_products():
    try:
        # Get top 5 products from backend API
        response = requests.get(f"{app.config['API_URL']}/sales/top/5")
        
        if response.status_code == 200:
            response_data = response.json()
            
            if response_data['success']:
                # Render top products template
                return render_template('top_products.html', data=response_data['data'])
        
        # Handle errors
        return render_template('top_products.html', data=[], error="Error fetching data")
    
    except Exception as e:
        return render_template('top_products.html', data=[], error=str(e))

# Add Jinja2 custom functions
app.jinja_env.globals.update(enumerate=enumerate)

# App factory function for gunicorn
def create_app():
    return app

# Run the app when directly executed
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    app.run(host='0.0.0.0', port=port, debug=False) 