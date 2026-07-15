# app/utils/helpers.py

import bcrypt
import re
from datetime import datetime, timedelta
from math import radians, sin, cos, sqrt, asin

def hash_password(password):
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, hashed):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate Indian phone number"""
    pattern = r'^[6-9]\d{9}$'
    return re.match(pattern, phone) is not None

def validate_blood_group(blood_group):
    """Validate blood group"""
    valid_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    return blood_group in valid_groups

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two points in kilometers
    Using Haversine formula
    """
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return None
    
    lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    
    return c * r

def calculate_response_probability(donor, distance_km, emergency_level):
    """
    Simple response probability calculation
    Will be replaced by ML model later
    """
    # Base probability from donor's response rate
    base = float(donor.response_rate) if donor.response_rate else 0.5
    
    # Distance factor (closer = higher probability)
    distance_factor = max(0, 1 - (distance_km / 20)) if distance_km else 0.5
    
    # Availability factor
    availability_factor = 1.0 if donor.is_available else 0.0
    
    # Emergency level factor
    emergency_factor = {
        'Normal': 1.0,
        'Urgent': 1.1,
        'Critical': 1.2
    }.get(emergency_level, 1.0)
    
    # Calculate final probability
    probability = (base * 0.4 + distance_factor * 0.3 + availability_factor * 0.3) * emergency_factor
    
    return min(1.0, max(0.0, probability))

def calculate_ranking_score(donor, distance_km, response_probability, emergency_level):
    """
    Calculate ranking score using weighted formula
    """
    # Weights (can be adjusted based on performance)
    weights = {
        'distance': 0.30,
        'response_probability': 0.35,
        'history': 0.15,
        'availability': 0.10,
        'emergency': 0.05,
        'gamification': 0.05
    }
    
    # Distance score (closer = higher score)
    distance_score = max(0, 1 - (distance_km / 20)) if distance_km else 0.5
    
    # History score (based on total donations)
    history_score = min(1.0, donor.total_donations / 20) if donor.total_donations else 0
    
    # Availability score
    availability_score = 1.0 if donor.is_available else 0.0
    
    # Gamification score (based on points/tier)
    gamification_score = 0.5  # Default, will be enhanced later
    
    # Emergency priority multiplier
    emergency_multiplier = {
        'Normal': 1.0,
        'Urgent': 1.2,
        'Critical': 1.5
    }.get(emergency_level, 1.0)
    
    # Calculate weighted score
    score = (
        weights['distance'] * distance_score +
        weights['response_probability'] * response_probability +
        weights['history'] * history_score +
        weights['availability'] * availability_score +
        weights['gamification'] * gamification_score
    )
    
    # Apply emergency multiplier
    score *= emergency_multiplier
    
    return min(1.0, max(0.0, score))

def get_emergency_level(level):
    """Get emergency level with default, handles case-insensitive input"""
    mapping = {'normal': 'Normal', 'urgent': 'Urgent', 'critical': 'Critical'}
    if isinstance(level, str):
        normalized = mapping.get(level.lower())
        if normalized:
            return normalized
    valid_levels = ['Normal', 'Urgent', 'Critical']
    return level if level in valid_levels else 'Normal'

def to_dict_list(objects):
    """Convert list of objects to dict list"""
    return [obj.to_dict() for obj in objects]

def create_response(success=True, data=None, message=None, errors=None):
    """Create standardized API response"""
    response = {
        'success': success,
        'data': data,
        'message': message,
        'errors': errors
    }
    # Remove None values
    return {k: v for k, v in response.items() if v is not None}


def create_jwt_identity(user_type, user_id):
    """Build a unique JWT subject for donor/patient accounts."""
    return f"{user_type}:{user_id}"


def parse_jwt_identity(identity):
    """Parse JWT subject into (user_type, user_id). Supports legacy numeric IDs."""
    if identity is None:
        return None, None

    identity_str = str(identity)
    if ':' in identity_str:
        user_type, user_id = identity_str.split(':', 1)
        return user_type, int(user_id)

    return None, int(identity_str)


def email_exists(email):
    """Check if email is registered as donor or patient."""
    from app.models import Donor, Patient
    return (
        Donor.query.filter_by(email=email).first() is not None
        or Patient.query.filter_by(email=email).first() is not None
    )


def phone_exists(phone):
    """Check if phone is registered as donor or patient."""
    from app.models import Donor, Patient
    return (
        Donor.query.filter_by(phone=phone).first() is not None
        or Patient.query.filter_by(phone=phone).first() is not None
    )


def get_authenticated_user(expected_type=None):
    """Resolve the current JWT user as a Donor or Patient model instance."""
    from flask_jwt_extended import get_jwt_identity, get_jwt
    from app.models import Donor, Patient

    user_type, user_id = parse_jwt_identity(get_jwt_identity())
    claims = get_jwt()
    user_type = user_type or claims.get('user_type')

    if expected_type and user_type != expected_type:
        return None, user_type, f"Only {expected_type} accounts can access this resource"

    if user_type == 'donor':
        return Donor.query.get(user_id), user_type, None
    if user_type == 'patient':
        return Patient.query.get(user_id), user_type, None

    return None, user_type, "Invalid user type"