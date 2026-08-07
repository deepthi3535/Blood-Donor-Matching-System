# app/auth/routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models import Donor, Patient, Hospital
from app.utils.helpers import (
    hash_password, verify_password, validate_email,
    validate_phone, validate_blood_group,
    create_response, create_jwt_identity, parse_jwt_identity,
    email_exists, phone_exists
)
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register/donor', methods=['POST'])
def register_donor():
    """Register a new donor"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'password', 'blood_group']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify(create_response(
                    success=False,
                    message=f"Missing required field: {field}"
                )), 400
        
        # Validate email
        if not validate_email(data['email']):
            return jsonify(create_response(
                success=False,
                message="Invalid email format"
            )), 400
        
        # Validate phone
        if not validate_phone(data['phone']):
            return jsonify(create_response(
                success=False,
                message="Invalid phone number (must be 10 digits starting with 6-9)"
            )), 400
        
        # Validate blood group
        if not validate_blood_group(data['blood_group']):
            return jsonify(create_response(
                success=False,
                message="Invalid blood group"
            )), 400
        
        # Check if email/phone already exists (donor or patient)
        if email_exists(data['email']):
            return jsonify(create_response(
                success=False,
                message="Email already registered"
            )), 409

        if phone_exists(data['phone']):
            return jsonify(create_response(
                success=False,
                message="Phone number already registered"
            )), 409

        date_of_birth = None
        if data.get('date_of_birth'):
            date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()

        weight = float(data['weight']) if data.get('weight') else None

        # Create new donor
        donor = Donor(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            password_hash=hash_password(data['password']),
            blood_group=data['blood_group'],
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            date_of_birth=date_of_birth,
            weight=weight,
            is_available=True
        )
        
        db.session.add(donor)
        db.session.commit()
        
        access_token = create_access_token(
            identity=create_jwt_identity('donor', donor.donor_id),
            additional_claims={'user_type': 'donor'}
        )
        
        return jsonify(create_response(
            success=True,
            data={
                'token': access_token,
                'user': donor.to_dict()
            },
            message="Donor registered successfully"
        )), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify(create_response(
            success=False,
            message=f"Registration failed: {str(e)}"
        )), 500


@auth_bp.route('/register/patient', methods=['POST'])
def register_patient():
    """Register a new patient"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify(create_response(
                    success=False,
                    message=f"Missing required field: {field}"
                )), 400
        
        # Validate email
        if not validate_email(data['email']):
            return jsonify(create_response(
                success=False,
                message="Invalid email format"
            )), 400
        
        # Validate phone
        if not validate_phone(data['phone']):
            return jsonify(create_response(
                success=False,
                message="Invalid phone number (must be 10 digits starting with 6-9)"
            )), 400
        
        # Check if email/phone already exists (donor or patient)
        if email_exists(data['email']):
            return jsonify(create_response(
                success=False,
                message="Email already registered"
            )), 409

        if phone_exists(data['phone']):
            return jsonify(create_response(
                success=False,
                message="Phone number already registered"
            )), 409
        
        # Create new patient
        patient = Patient(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            password_hash=hash_password(data['password']),
            blood_group=data.get('blood_group'),
            hospital_name=data.get('hospital_name')
        )
        
        db.session.add(patient)
        db.session.commit()
        
        access_token = create_access_token(
            identity=create_jwt_identity('patient', patient.patient_id),
            additional_claims={'user_type': 'patient'}
        )
        
        return jsonify(create_response(
            success=True,
            data={
                'token': access_token,
                'user': patient.to_dict()
            },
            message="Patient registered successfully"
        )), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify(create_response(
            success=False,
            message=f"Registration failed: {str(e)}"
        )), 500


@auth_bp.route('/register/hospital', methods=['POST'])
def register_hospital():
    """Register a new hospital"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify(create_response(
                    success=False,
                    message=f"Missing required field: {field}"
                )), 400
        
        # Validate email
        if not validate_email(data['email']):
            return jsonify(create_response(
                success=False,
                message="Invalid email format"
            )), 400
        
        # Validate phone
        if not validate_phone(data['phone']):
            return jsonify(create_response(
                success=False,
                message="Invalid phone number (must be 10 digits starting with 6-9)"
            )), 400
        
        # Check if email/phone already exists
        if email_exists(data['email']):
            return jsonify(create_response(
                success=False,
                message="Email already registered"
            )), 409

        if phone_exists(data['phone']):
            return jsonify(create_response(
                success=False,
                message="Phone number already registered"
            )), 409
        
        # Create new hospital
        hospital = Hospital(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            password_hash=hash_password(data['password']),
            address=data.get('address'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude')
        )
        
        db.session.add(hospital)
        db.session.commit()
        
        access_token = create_access_token(
            identity=create_jwt_identity('hospital', hospital.hospital_id),
            additional_claims={'user_type': 'hospital'}
        )
        
        return jsonify(create_response(
            success=True,
            data={
                'token': access_token,
                'user': hospital.to_dict()
            },
            message="Hospital registered successfully"
        )), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify(create_response(
            success=False,
            message=f"Registration failed: {str(e)}"
        )), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user (donor or patient)"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify(create_response(
                success=False,
                message="Email and password required"
            )), 400
        
        email = data['email']
        password = data['password']
        
        # Try to find donor
        user = Donor.query.filter_by(email=email).first()
        user_type = 'donor'
        user_id_field = 'donor_id'
        
        # If not donor, try patient
        if not user:
            user = Patient.query.filter_by(email=email).first()
            user_type = 'patient'
            user_id_field = 'patient_id'
            
        # If not patient, try hospital
        if not user:
            user = Hospital.query.filter_by(email=email).first()
            user_type = 'hospital'
            user_id_field = 'hospital_id'
        
        if not user:
            return jsonify(create_response(
                success=False,
                message="Invalid credentials"
            )), 401
        
        # Verify password
        if not verify_password(password, user.password_hash):
            return jsonify(create_response(
                success=False,
                message="Invalid credentials"
            )), 401
        
        user_id = getattr(user, user_id_field)

        access_token = create_access_token(
            identity=create_jwt_identity(user_type, user_id),
            additional_claims={'user_type': user_type}
        )
        
        return jsonify(create_response(
            success=True,
            data={
                'token': access_token,
                'user': user.to_dict(),
                'user_type': user_type
            },
            message="Login successful"
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            message=f"Login failed: {str(e)}"
        )), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Return the currently authenticated donor or patient."""
    try:
        user_type, user_id = parse_jwt_identity(get_jwt_identity())
        claims = get_jwt()
        user_type = user_type or claims.get('user_type')

        if user_type == 'donor':
            user = Donor.query.get(user_id)
        elif user_type == 'patient':
            user = Patient.query.get(user_id)
        elif user_type == 'hospital':
            user = Hospital.query.get(user_id)
        else:
            return jsonify(create_response(
                success=False,
                message="Invalid user type"
            )), 400

        if not user:
            return jsonify(create_response(
                success=False,
                message="User not found"
            )), 404

        return jsonify(create_response(
            success=True,
            data={
                'user': user.to_dict(),
                'user_type': user_type
            }
        )), 200

    except Exception as e:
        return jsonify(create_response(
            success=False,
            message=f"Error: {str(e)}"
        )), 500