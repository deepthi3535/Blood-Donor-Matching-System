# app/database.py

from app import db

def init_db():
    """Initialize database tables"""
    from app.models import Donor, Patient, Hospital, BloodRequest, DonorMatch, DonationHistory, Gamification
    db.create_all()
    print("Database tables created successfully!")

def drop_db():
    """Drop all tables (use with caution)"""
    db.drop_all()
    print("Database tables dropped!")