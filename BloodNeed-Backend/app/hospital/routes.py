# app/hospital/routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import Hospital, BloodRequest, DonorMatch, DonationHistory, Donor, Gamification
from app.utils.helpers import create_response, get_authenticated_user

hospital_bp = Blueprint('hospital', __name__)


def _get_hospital_or_error():
    hospital, _, error = get_authenticated_user(expected_type='hospital')
    if error:
        return None, jsonify(create_response(success=False, message=error)), 403
    if not hospital:
        return None, jsonify(create_response(success=False, message="Hospital not found")), 404
    return hospital, None, None


@hospital_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get hospital profile"""
    try:
        hospital, error_response, status = _get_hospital_or_error()
        if error_response:
            return error_response, status

        return jsonify(create_response(
            success=True,
            data=hospital.to_dict()
        )), 200
    except Exception as e:
        return jsonify(create_response(
            success=False,
            message=f"Error: {str(e)}"
        )), 500


@hospital_bp.route('/requests', methods=['GET'])
@jwt_required()
def get_requests():
    """Get active requests matching this hospital's name"""
    try:
        hospital, error_response, status = _get_hospital_or_error()
        if error_response:
            return error_response, status

        # Get active requests (Pending, Processing) assigned to this hospital
        requests = BloodRequest.query.filter(
            BloodRequest.hospital_name == hospital.name,
            BloodRequest.status.in_(['Pending', 'Processing'])
        ).all()

        return jsonify(create_response(
            success=True,
            data=[r.to_dict() for r in requests]
        )), 200
    except Exception as e:
        return jsonify(create_response(
            success=False,
            message=f"Error: {str(e)}"
        )), 500


@hospital_bp.route('/verify-donation', methods=['POST'])
@jwt_required()
def verify_donation():
    """Verify donor OTP and complete the donation"""
    try:
        hospital, error_response, status = _get_hospital_or_error()
        if error_response:
            return error_response, status

        data = request.get_json()
        request_id = data.get('requestId')
        donor_id = data.get('donorId')
        otp = data.get('otp')

        if not request_id or not donor_id or not otp:
            return jsonify(create_response(
                success=False,
                message="Missing requestId, donorId, or otp"
            )), 400

        # Find match record
        match = DonorMatch.query.filter_by(
            request_id=request_id,
            donor_id=donor_id,
            donor_response='Accepted'
        ).first()

        if not match:
            # Check if there is a match record that isn't accepted
            match = DonorMatch.query.filter_by(
                request_id=request_id,
                donor_id=donor_id
            ).first()
            if match and match.donor_response != 'Accepted':
                return jsonify(create_response(
                    success=False,
                    message="Donor has not accepted this request yet"
                )), 400
            return jsonify(create_response(
                success=False,
                message="No match record found for this donor and request"
            )), 404

        # Check OTP
        if match.otp != str(otp):
            return jsonify(create_response(
                success=False,
                message="Invalid OTP code"
            )), 400

        # Complete request and donation
        blood_request = BloodRequest.query.get(request_id)
        if blood_request:
            blood_request.status = 'Fulfilled'

        # Create donation history
        history = DonationHistory(
            donor_id=donor_id,
            request_id=request_id,
            status='Completed'
        )
        db.session.add(history)

        # Update donor stats
        donor = Donor.query.get(donor_id)
        if donor:
            donor.total_donations += 1
            donor.last_donation_date = db.func.current_date()

        # Award gamification points (100 points)
        gamification = Gamification.query.filter_by(donor_id=donor_id).first()
        if not gamification:
            gamification = Gamification(
                donor_id=donor_id,
                points=0,
                badges='[]',
                tier='Bronze'
            )
            db.session.add(gamification)

        gamification.points += 100

        # Upgrade tier based on points
        if gamification.points >= 500:
            gamification.tier = 'Platinum'
        elif gamification.points >= 300:
            gamification.tier = 'Gold'
        elif gamification.points >= 100:
            gamification.tier = 'Silver'

        db.session.commit()

        return jsonify(create_response(
            success=True,
            message="Donation verified successfully! Donor awarded 100 points."
        )), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(create_response(
            success=False,
            message=f"Verification failed: {str(e)}"
        )), 500


@hospital_bp.route('/analytics/response-stats', methods=['GET'])
@jwt_required()
def get_response_stats():
    """Get hospital analytics on donor response speed and decisions"""
    try:
        # Check if the user is a hospital user
        hospital, error_response, status = _get_hospital_or_error()
        if error_response:
            return error_response, status

        # Fetch all matches that are not pending
        accepted_count = DonorMatch.query.filter_by(donor_response='Accepted').count()
        rejected_count = DonorMatch.query.filter_by(donor_response='Rejected').count()

        # Calculate average response time
        # Get all response times that are not None
        matches_with_time = DonorMatch.query.filter(DonorMatch.response_time_seconds.isnot(None)).all()
        if matches_with_time:
            total_time = sum(m.response_time_seconds for m in matches_with_time)
            avg_response_time = round(total_time / len(matches_with_time), 2)
        else:
            avg_response_time = 0.0

        return jsonify(create_response(
            success=True,
            data={
                'average_response_time_seconds': avg_response_time,
                'total_accepted': accepted_count,
                'total_rejected': rejected_count,
                'sample_size': len(matches_with_time)
            },
            message="Hospital analytics response stats retrieved."
        )), 200

    except Exception as e:
        return jsonify(create_response(
            success=False,
            message=f"Failed to fetch stats: {str(e)}"
        )), 500

