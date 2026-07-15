# app/matching/routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import BloodRequest, Donor, DonorMatch
from app.utils.helpers import (
    calculate_distance, calculate_response_probability,
    calculate_ranking_score, create_response
)

matching_bp = Blueprint('matching', __name__)

@matching_bp.route('/find/<int:request_id>', methods=['GET'])
@jwt_required()
def find_donors(request_id):
    """Find matching donors for a request"""
    try:
        # Get request
        blood_request = BloodRequest.query.get(request_id)
        if not blood_request:
            return jsonify(create_response(
                success=False,
                message="Request not found"
            )), 404
        
        # Get hospital location
        hospital_lat = blood_request.hospital_latitude
        hospital_lng = blood_request.hospital_longitude
        
        # Find matching donors
        donors = Donor.query.filter_by(
            blood_group=blood_request.blood_group,
            is_available=True
        ).all()
        
        if not donors:
            return jsonify(create_response(
                success=False,
                message="No matching donors found"
            )), 404
        
        matched_donors = []
        
        for donor in donors:
            existing = DonorMatch.query.filter_by(
                request_id=request_id, donor_id=donor.donor_id
            ).first()
            if existing:
                matched_donors.append({
                    'donor_id': donor.donor_id,
                    'name': donor.name,
                    'blood_group': donor.blood_group,
                    'distance_km': float(existing.distance_km) if existing.distance_km else None,
                    'response_probability': float(existing.response_probability) if existing.response_probability else None,
                    'ranking_score': float(existing.ranking_score) if existing.ranking_score else None,
                    'available': donor.is_available
                })
                continue
            
            distance = calculate_distance(
                hospital_lat, hospital_lng,
                donor.latitude, donor.longitude
            ) if hospital_lat and donor.latitude else None
            
            # Calculate response probability
            response_prob = calculate_response_probability(
                donor, distance, blood_request.emergency_level
            )
            
            # Calculate ranking score
            ranking_score = calculate_ranking_score(
                donor, distance, response_prob, blood_request.emergency_level
            )
            
            # Create match record
            match = DonorMatch(
                request_id=request_id,
                donor_id=donor.donor_id,
                distance_km=distance,
                response_probability=response_prob,
                ranking_score=ranking_score,
                donor_response='Pending'
            )
            db.session.add(match)
            
            matched_donors.append({
                'donor_id': donor.donor_id,
                'name': donor.name,
                'blood_group': donor.blood_group,
                'distance_km': distance,
                'response_probability': response_prob,
                'ranking_score': ranking_score,
                'available': donor.is_available
            })
        
        db.session.commit()
        
        # Sort by ranking score (descending)
        matched_donors.sort(key=lambda x: x['ranking_score'], reverse=True)
        
        return jsonify(create_response(
            success=True,
            data={
                'request_id': request_id,
                'total_donors': len(matched_donors),
                'matched_donors': matched_donors
            }
        )), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify(create_response(
            success=False,
            message=f"Error: {str(e)}"
        )), 500


@matching_bp.route('/ranking/<int:request_id>', methods=['GET'])
@jwt_required()
def get_ranking(request_id):
    """Get ranked donors for a request"""
    try:
        matches = DonorMatch.query.filter_by(
            request_id=request_id
        ).order_by(DonorMatch.ranking_score.desc()).all()
        
        if not matches:
            return jsonify(create_response(
                success=False,
                message="No matches found for this request"
            )), 404
        
        result = []
        for match in matches:
            donor = Donor.query.get(match.donor_id)
            if donor:
                result.append({
                    'match_id': match.match_id,
                    'donor_id': donor.donor_id,
                    'name': donor.name,
                    'blood_group': donor.blood_group,
                    'distance_km': float(match.distance_km) if match.distance_km else None,
                    'response_probability': float(match.response_probability) if match.response_probability else None,
                    'ranking_score': float(match.ranking_score) if match.ranking_score else None,
                    'status': match.donor_response
                })
        
        return jsonify(create_response(
            success=True,
            data=result
        )), 200
        
    except Exception as e:
        return jsonify(create_response(
            success=False,
            message=f"Error: {str(e)}"
        )), 500