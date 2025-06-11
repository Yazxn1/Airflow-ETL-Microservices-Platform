from flask import Flask
from flask_cors import CORS
import os
from api.routes import api_bp
from api.models import get_db_session

# Create Flask application
app = Flask(__name__)
CORS(app)  # Enable cross-origin requests

# Database configuration
db_user = os.environ.get('MYSQL_USER', 'root')
db_password = os.environ.get('MYSQL_PASSWORD', 'mysql')
db_host = os.environ.get('MYSQL_HOST', 'mysql')
db_port = os.environ.get('MYSQL_PORT', '3306')
db_name = os.environ.get('MYSQL_DATABASE', 'retail_data_warehouse')

# MySQL connection string
db_uri = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

# Create database session
app.db_session = get_db_session(db_uri)

# Register API blueprint
app.register_blueprint(api_bp, url_prefix='/api')

# App factory function for gunicorn
def create_app():
    return app

# Run the app when directly executed
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 