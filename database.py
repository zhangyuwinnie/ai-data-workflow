from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pandas as pd

DATABASE_URL = "sqlite:///./data.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class SalesData(Base):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    product = Column(String, index=True)
    category = Column(String, index=True)
    sales_amount = Column(Float)
    quantity = Column(Integer)
    date = Column(DateTime, default=datetime.utcnow)
    region = Column(String)

def create_sample_data():
    Base.metadata.create_all(bind=engine)
    
    sample_data = [
        {"product": "Laptop", "category": "Electronics", "sales_amount": 1200.00, "quantity": 5, "region": "North"},
        {"product": "Mouse", "category": "Electronics", "sales_amount": 25.00, "quantity": 50, "region": "South"},
        {"product": "Keyboard", "category": "Electronics", "sales_amount": 75.00, "quantity": 20, "region": "East"},
        {"product": "Monitor", "category": "Electronics", "sales_amount": 300.00, "quantity": 8, "region": "West"},
        {"product": "Chair", "category": "Furniture", "sales_amount": 150.00, "quantity": 12, "region": "North"},
        {"product": "Desk", "category": "Furniture", "sales_amount": 400.00, "quantity": 6, "region": "South"},
        {"product": "Tablet", "category": "Electronics", "sales_amount": 500.00, "quantity": 15, "region": "East"},
        {"product": "Phone", "category": "Electronics", "sales_amount": 800.00, "quantity": 25, "region": "West"},
    ]
    
    db = SessionLocal()
    try:
        existing_count = db.query(SalesData).count()
        if existing_count == 0:
            for item in sample_data:
                db_item = SalesData(**item)
                db.add(db_item)
            db.commit()
            print("Sample data created successfully!")
        else:
            print("Sample data already exists.")
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()