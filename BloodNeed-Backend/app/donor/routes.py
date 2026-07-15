# app/donor/routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import DonationHistory, Gamification
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
