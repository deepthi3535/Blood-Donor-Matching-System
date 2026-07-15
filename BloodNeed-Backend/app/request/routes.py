# app/request/routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import BloodRequest
from app.utils.helpers import create_response, get_emergency_level, get_authenticated_user

request_bp = Blueprint('request', __name__)


def _get_patient_or_error():
    patient, _, error = get_authenticated_user(expected_type='patient')
    if error:
        return None, jsonify(create_response(success=False, message=error)), 403
    if not patient:
        return None, jsonify(create_response(success=False, message="Patient not found")), 404
    return patient, None, None


@request_bp.route('/blood', methods=['POST'])
@jwt_required()
def create_request():
    """Create a new blood request"""
    try:
        patient, error_response, status = _get_patient_or_error()
        if error_response:
            return error_response, status

        data = request.get_json()

        required_fields = ['blood_group', 'hospital_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify(create_response(
                    success=False,
                    message=f"Missing required field: {field}"
                )), 400

        blood_request = BloodRequest(
            patient_id=patient.patient_id,
            blood_group=data['blood_group'],
            units_needed=data.get('units_needed', 1),
            emergency_level=get_emergency_level(data.get('emergency_level')),
            hospital_name=data['hospital_name'],
            hospital_latitude=data.get('hospital_latitude'),
            hospital_longitude=data.get('hospital_longitude'),
            notes=data.get('notes'),
            status='Pending'
        )

        db.session.add(blood_request)
        db.session.commit()

        return jsonify(create_response(
            success=True,
            data=blood_request.to_dict(),
            message="Blood request created successfully"
        )), 201

    except Exception as e:
        db.session.rollback()
        return jsonify(create_response(
            success=False,
            message=f"Error: {str(e)}"
        )), 500


@request_bp.route('/patient/requests', methods=['GET'])
@jwt_required()
def get_patient_requests():
    """Get all requests for current patient"""
    try:
        patient, error_response, status = _get_patient_or_error()
        if error_response:
            return error_response, status

        requests = BloodRequest.query.filter_by(patient_id=patient.patient_id).order_by(
            BloodRequest.request_time.desc()
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


@request_bp.route('/patient/request/<int:request_id>', methods=['GET'])
@jwt_required()
def get_request_status(request_id):
    """Get status of a specific request"""
    try:
        patient, error_response, status = _get_patient_or_error()
        if error_response:
            return error_response, status

        blood_request = BloodRequest.query.filter_by(
            request_id=request_id,
            patient_id=patient.patient_id
        ).first()

        if not blood_request:
            return jsonify(create_response(
                success=False,
                message="Request not found"
            )), 404

        return jsonify(create_response(
            success=True,
            data=blood_request.to_dict()
        )), 200

    except Exception as e:
        return jsonify(create_response(
            success=False,
            message=f"Error: {str(e)}"
        )), 500


@request_bp.route('/patient/request/<int:request_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_request(request_id):
    """Cancel a blood request"""
    try:
        patient, error_response, status = _get_patient_or_error()
        if error_response:
            return error_response, status

        blood_request = BloodRequest.query.filter_by(
            request_id=request_id,
            patient_id=patient.patient_id
        ).first()

        if not blood_request:
            return jsonify(create_response(
                success=False,
                message="Request not found"
            )), 404

        if blood_request.status in ['Fulfilled', 'Cancelled']:
            return jsonify(create_response(
                success=False,
                message=f"Request already {blood_request.status}"
            )), 400

        blood_request.status = 'Cancelled'
        db.session.commit()

        return jsonify(create_response(
            success=True,
            message="Request cancelled successfully"
        )), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(create_response(
            success=False,
            message=f"Error: {str(e)}"
        )), 500
