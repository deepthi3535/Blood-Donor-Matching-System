# app/donor/routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import DonationHistory, Gamification, DonorMatch, BloodRequest
from app.utils.helpers import create_response, get_authenticated_user

donor_bp = Blueprint('donor', __name__)


def _get_donor_or_error():
    donor, _, error = get_authenticated_user(expected_type='donor')
    if error:
        return None, jsonify(create_response(success=False, message=error)), 403
    if not donor:
        return None, jsonify(create_response(success=False, message="Donor not found")), 404
    return donor, None, None


@donor_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get donor profile"""
    try:
        donor, error_response, status = _get_donor_or_error()
        if error_response:
            return error_response, status

        return jsonify(create_response(
            success=True,
            data=donor.to_dict()
        )), 200

    except Exception as e:
        return jsonify(create_response(
            success=False,
            message=f"Error: {str(e)}"
        )), 500


@donor_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update donor profile"""
    try:
        donor, error_response, status = _get_donor_or_error()
        if error_response:
            return error_response, status

        data = request.get_json()

        if 'name' in data:
            donor.name = data['name']
        if 'phone' in data:
            donor.phone = data['phone']
        if 'blood_group' in data:
            donor.blood_group = data['blood_group']
        if 'latitude' in data:
            donor.latitude = data['latitude']
        if 'longitude' in data:
            donor.longitude = data['longitude']
        if 'date_of_birth' in data:
            donor.date_of_birth = data['date_of_birth']
        if 'weight' in data:
            donor.weight = data['weight']

        db.session.commit()

        return jsonify(create_response(
            success=True,
            data=donor.to_dict(),
            message="Profile updated successfully"
        )), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(create_response(
            success=False,
            message=f"Error: {str(e)}"
        )), 500


@donor_bp.route('/availability', methods=['POST'])
@jwt_required()
def update_availability():
    """Update donor availability"""
    try:
        donor, error_response, status = _get_donor_or_error()
        if error_response:
            return error_response, status

        data = request.get_json()
        is_available = data.get('available', True)

        donor.is_available = is_available
        db.session.commit()

        return jsonify(create_response(
            success=True,
            data={'available': is_available},
            message=f"Availability updated: {'Available' if is_available else 'Not Available'}"
        )), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(create_response(
            success=False,
            message=f"Error: {str(e)}"
        )), 500


@donor_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    """Get donor donation history"""
    try:
        donor, error_response, status = _get_donor_or_error()
        if error_response:
            return error_response, status

        history = DonationHistory.query.filter_by(donor_id=donor.donor_id).order_by(
            DonationHistory.donation_date.desc()
        ).all()

        return jsonify(create_response(
            success=True,
            data=[h.to_dict() for h in history]
        )), 200

    except Exception as e:
        return jsonify(create_response(
            success=False,
            message=f"Error: {str(e)}"
        )), 500


@donor_bp.route('/gamification', methods=['GET'])
@jwt_required()
def get_gamification():
    """Get donor gamification stats"""
    try:
        donor, error_response, status = _get_donor_or_error()
        if error_response:
            return error_response, status

        gamification = Gamification.query.filter_by(donor_id=donor.donor_id).first()

        if not gamification:
            gamification = Gamification(
                donor_id=donor.donor_id,
                points=0,
                badges='[]',
                tier='Bronze'
            )
            db.session.add(gamification)
            db.session.commit()

        return jsonify(create_response(
            success=True,
            data=gamification.to_dict()
        )), 200

    except Exception as e:
        return jsonify(create_response(
            success=False,
            message=f"Error: {str(e)}"
        )), 500


@donor_bp.route('/respond', methods=['POST'])
@jwt_required()
def respond_to_request():
    """Respond to a matching blood request (Accept/Reject)"""
    try:
        donor, error_response, status = _get_donor_or_error()
        if error_response:
            return error_response, status
            
        data = request.get_json()
        match_id = data.get('matchId')
        response = data.get('response') # 'Accepted' or 'Rejected'
        
        if not match_id or response not in ['Accepted', 'Rejected']:
            return jsonify(create_response(
                success=False,
                message="Invalid parameters. matchId and response ('Accepted'/'Rejected') required."
            )), 400
            
        match = DonorMatch.query.filter_by(match_id=match_id, donor_id=donor.donor_id).first()
        if not match:
            return jsonify(create_response(
                success=False,
                message="Match record not found"
            )), 404
            
        match.donor_response = response
        
        # Calculate response speed in seconds
        from datetime import datetime
        if match.matched_at:
            elapsed = (datetime.utcnow() - match.matched_at).total_seconds()
            match.response_time_seconds = int(max(0, elapsed))
        
        # If accepted, generate a 6-digit OTP
        if response == 'Accepted':
            import random
            match.otp = str(random.randint(100000, 999999))
            
            # Set request status to 'Processing'
            blood_request = BloodRequest.query.get(match.request_id)
            if blood_request and blood_request.status == 'Pending':
                blood_request.status = 'Processing'
                
        db.session.commit()
        
        return jsonify(create_response(
            success=True,
            data=match.to_dict(),
            message=f"Request response registered as {response}."
        )), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify(create_response(
            success=False,
            message=f"Error: {str(e)}"
        )), 500
