from sqlalchemy import Column, Integer, Numeric, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create base class for models
Base = declarative_base()

# Model for aggregated sales data
class SalesAggregated(Base):
    __tablename__ = 'sales_aggregated'
    
    # Columns
    product_id = Column(Integer, primary_key=True)
    total_quantity = Column(Integer)
    total_sale_amount = Column(Numeric(10, 2))
    
    # Convert to dictionary for JSON response
    def to_dict(self):
        return {
            'product_id': self.product_id,
            'total_quantity': self.total_quantity,
            'total_sale_amount': float(self.total_sale_amount) if self.total_sale_amount else 0
        }

# Create database session
def get_db_session(db_uri):
    engine = create_engine(db_uri)
    Session = sessionmaker(bind=engine)
    return Session() 