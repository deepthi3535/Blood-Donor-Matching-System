# app/models.py

from app import db
from datetime import datetime

class Donor(db.Model):
    """Donor Model"""
    __tablename__ = 'donors'
    
    donor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    blood_group = db.Column(db.String(3), nullable=False)
    latitude = db.Column(db.DECIMAL(10, 8), nullable=True)
    longitude = db.Column(db.DECIMAL(11, 8), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    weight = db.Column(db.DECIMAL(5, 2), nullable=True)
    total_donations = db.Column(db.Integer, default=0)
    last_donation_date = db.Column(db.Date, nullable=True)
    is_available = db.Column(db.Boolean, default=True)
    response_rate = db.Column(db.DECIMAL(5, 2), default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    matches = db.relationship('DonorMatch', backref='donor', lazy=True)
    donations = db.relationship('DonationHistory', backref='donor', lazy=True)
    gamification = db.relationship('Gamification', backref='donor', uselist=False, lazy=True)
    
    def to_dict(self):
        return {
            'donor_id': self.donor_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'blood_group': self.blood_group,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'total_donations': self.total_donations,
            'is_available': self.is_available,
            'response_rate': float(self.response_rate) if self.response_rate else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Patient(db.Model):
    """Patient Model"""
    __tablename__ = 'patients'
    
    patient_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    blood_group = db.Column(db.String(3), nullable=True)
    hospital_name = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    requests = db.relationship('BloodRequest', backref='patient', lazy=True)
    
    def to_dict(self):
        return {
            'patient_id': self.patient_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'blood_group': self.blood_group,
            'hospital_name': self.hospital_name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class BloodRequest(db.Model):
    """Blood Request Model"""
    __tablename__ = 'blood_requests'
    
    request_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'), nullable=False)
    blood_group = db.Column(db.String(3), nullable=False)
    units_needed = db.Column(db.Integer, default=1)
    emergency_level = db.Column(db.Enum('Normal', 'Urgent', 'Critical'), default='Normal')
    hospital_name = db.Column(db.String(200), nullable=False)
    hospital_latitude = db.Column(db.DECIMAL(10, 8), nullable=True)
    hospital_longitude = db.Column(db.DECIMAL(11, 8), nullable=True)
    status = db.Column(db.Enum('Pending', 'Processing', 'Fulfilled', 'Cancelled'), default='Pending')
    request_time = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    matches = db.relationship('DonorMatch', backref='request', lazy=True)
    
    def to_dict(self):
        return {
            'request_id': self.request_id,
            'patient_id': self.patient_id,
            'blood_group': self.blood_group,
            'units_needed': self.units_needed,
            'emergency_level': self.emergency_level,
            'hospital_name': self.hospital_name,
            'hospital_latitude': float(self.hospital_latitude) if self.hospital_latitude else None,
            'hospital_longitude': float(self.hospital_longitude) if self.hospital_longitude else None,
            'status': self.status,
            'request_time': self.request_time.isoformat() if self.request_time else None,
            'notes': self.notes
        }


class DonorMatch(db.Model):
    """Donor Match Model"""
    __tablename__ = 'donor_matches'
    
    match_id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('blood_requests.request_id'), nullable=False)
    donor_id = db.Column(db.Integer, db.ForeignKey('donors.donor_id'), nullable=False)
    distance_km = db.Column(db.DECIMAL(8, 2), nullable=True)
    response_probability = db.Column(db.DECIMAL(5, 2), nullable=True)
    ranking_score = db.Column(db.DECIMAL(8, 2), nullable=True)
    donor_response = db.Column(db.Enum('Pending', 'Accepted', 'Rejected'), default='Pending')
    matched_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'match_id': self.match_id,
            'request_id': self.request_id,
            'donor_id': self.donor_id,
            'distance_km': float(self.distance_km) if self.distance_km else None,
            'response_probability': float(self.response_probability) if self.response_probability else None,
            'ranking_score': float(self.ranking_score) if self.ranking_score else None,
            'donor_response': self.donor_response,
            'matched_at': self.matched_at.isoformat() if self.matched_at else None
        }


class DonationHistory(db.Model):
    """Donation History Model"""
    __tablename__ = 'donation_history'
    
    history_id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('donors.donor_id'), nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey('blood_requests.request_id'), nullable=False)
    donation_date = db.Column(db.DateTime, default=datetime.utcnow)
    units_donated = db.Column(db.Integer, default=1)
    status = db.Column(db.Enum('Completed', 'Cancelled'), default='Completed')
    
    def to_dict(self):
        return {
            'history_id': self.history_id,
            'donor_id': self.donor_id,
            'request_id': self.request_id,
            'donation_date': self.donation_date.isoformat() if self.donation_date else None,
            'units_donated': self.units_donated,
            'status': self.status
        }


class Gamification(db.Model):
    """Gamification Model"""
    __tablename__ = 'gamification'
    
    gamification_id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('donors.donor_id'), unique=True, nullable=False)
    points = db.Column(db.Integer, default=0)
    badges = db.Column(db.String(255), default='[]')
    tier = db.Column(db.Enum('Bronze', 'Silver', 'Gold', 'Platinum'), default='Bronze')
    
    def to_dict(self):
        return {
            'gamification_id': self.gamification_id,
            'donor_id': self.donor_id,
            'points': self.points,
            'badges': eval(self.badges) if self.badges else [],
            'tier': self.tier
        }