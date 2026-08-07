# app/matching/services.py

from app import db
from app.models import BloodRequest, Donor, DonorMatch
from app.utils.helpers import calculate_distance

# Blood Matrix: recipient group -> list of compatible donor groups
RECIPIENT_COMPATIBLE_DONORS = {
    'O-': ['O-'],
    'O+': ['O-', 'O+'],
    'A-': ['O-', 'A-'],
    'A+': ['O-', 'O+', 'A-', 'A+'],
    'B-': ['O-', 'B-'],
    'B+': ['O-', 'O+', 'B-', 'B+'],
    'AB-': ['O-', 'A-', 'B-', 'AB-'],
    'AB+': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+']
}


def match_and_rank_donors(request_id):
    """
    Find matching donors for a blood request, calculate geo-proximity,
    filter by 15km range, score, and rank them.
    """
    # 1. Fetch Blood Request
    blood_request = BloodRequest.query.get(request_id)
    if not blood_request:
        raise ValueError(f"Blood request with ID {request_id} not found.")

    h_lat = blood_request.hospital_latitude
    h_lng = blood_request.hospital_longitude

    if h_lat is None or h_lng is None:
        raise ValueError("Hospital coordinates (latitude and longitude) are required for proximity matching.")

    # Convert coordinates to floats for calculations
    h_lat = float(h_lat)
    h_lng = float(h_lng)

    # 2. Get Compatible Blood Groups
    recipient_group = blood_request.blood_group
    compatible_donor_groups = RECIPIENT_COMPATIBLE_DONORS.get(recipient_group, [])

    if not compatible_donor_groups:
        return []

    # 3. Query all compatible donors
    donors = Donor.query.filter(Donor.blood_group.in_(compatible_donor_groups)).all()

    ranked_donors = []

    # 4. Proximity Filtering & Scoring
    for donor in donors:
        if donor.latitude is None or donor.longitude is None:
            continue  # Skip donors without location

        d_lat = float(donor.latitude)
        d_lng = float(donor.longitude)

        # Haversine distance
        distance = calculate_distance(h_lat, h_lng, d_lat, d_lng)
        if distance is None or distance > 15.0:
            continue  # Exclude if further than 15km

        # Proximity Points (1.0 at 0km to 0.0 at 15km)
        proximity_points = (15.0 - distance) / 15.0

        # Response Rate (convert 0-100 percentage to 0.0-1.0)
        response_rate = float(donor.response_rate or 0.0) / 100.0

        # Availability Status (1.0 if available, else 0.0)
        availability_status = 1.0 if donor.is_available else 0.0

        # Score calculation
        score = (40.0 * proximity_points) + (30.0 * response_rate) + (30.0 * availability_status)

        # Save/Update DonorMatch record in the database
        match_record = DonorMatch.query.filter_by(
            request_id=request_id,
            donor_id=donor.donor_id
        ).first()

        if not match_record:
            match_record = DonorMatch(
                request_id=request_id,
                donor_id=donor.donor_id,
                distance_km=distance,
                response_probability=response_rate,
                ranking_score=score,
                donor_response='Pending'
            )
            db.session.add(match_record)
        else:
            match_record.distance_km = distance
            match_record.response_probability = response_rate
            match_record.ranking_score = score

        ranked_donors.append({
            'donor_id': donor.donor_id,
            'name': donor.name,
            'blood_group': donor.blood_group,
            'phone': donor.phone,
            'distance_km': round(distance, 2),
            'proximity_points': round(proximity_points, 4),
            'response_rate': float(donor.response_rate or 0.0),
            'availability_status': donor.is_available,
            'score': round(score, 2)
        })

    # 5. Save updates to database
    db.session.commit()

    # 6. Sort by score descending
    ranked_donors.sort(key=lambda x: x['score'], reverse=True)

    return ranked_donors
