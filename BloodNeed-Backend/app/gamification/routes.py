# app/gamification/routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Donor, Gamification, DonationHistory
from app.utils.helpers import create_response, get_authenticated_user

gamification_bp = Blueprint('gamification', __name__)


# Badge definitions
BADGES = {
    'first_donation': {'name': 'First Donation', 'icon': '🩸', 'points': 50, 'description': 'Made your first blood donation'},
    'regular_donor': {'name': 'Regular Donor', 'icon': '⭐', 'points': 100, 'description': 'Donated 5 times'},
    'super_donor': {'name': 'Super Donor', 'icon': '🏆', 'points': 250, 'description': 'Donated 10 times'},
    'legend_donor': {'name': 'Legend Donor', 'icon': '👑', 'points': 500, 'description': 'Donated 25 times'},
    'emergency_hero': {'name': 'Emergency Hero', 'icon': '🚑', 'points': 150, 'description': 'Responded to 5 emergency requests'},
    'quick_responder': {'name': 'Quick Responder', 'icon': '⚡', 'points': 75, 'description': 'Responded within 5 minutes'},
    'month_streak': {'name': 'Monthly Streak', 'icon': '🔥', 'points': 100, 'description': 'Donated for 3 consecutive months'},
    'rare_blood': {'name': 'Rare Blood Hero', 'icon': '💎', 'points': 200, 'description': 'Donated rare blood type (AB-, O-)'},
    'community_leader': {'name': 'Community Leader', 'icon': '🎖️', 'points': 300, 'description': 'Top 10 donor in your area'}
}

# Tier thresholds
TIERS = {
    'Bronze': {'min_points': 0, 'max_points': 499, 'color': '#CD7F32'},
    'Silver': {'min_points': 500, 'max_points': 1499, 'color': '#C0C0C0'},
    'Gold': {'min_points': 1500, 'max_points': 2999, 'color': '#FFD700'},
    'Platinum': {'min_points': 3000, 'max_points': float('inf'), 'color': '#E5E4E2'}
}


def calculate_tier(points):
    """Calculate donor tier based on points"""
    for tier_name, tier_info in TIERS.items():
        if tier_info['min_points'] <= points <= tier_info['max_points']:
            return tier_name
    return 'Bronze'


def check_and_award_badges(donor, gamification):
    """Check if donor qualifies for new badges"""
    current_badges = eval(gamification.badges) if gamification.badges else []
    new_badges = []
    
    # Check first donation badge
    if donor.total_donations >= 1 and 'first_donation' not in current_badges:
        new_badges.append('first_donation')
        gamification.points += BADGES['first_donation']['points']
    
    # Check regular donor badge
    if donor.total_donations >= 5 and 'regular_donor' not in current_badges:
        new_badges.append('regular_donor')
        gamification.points += BADGES['regular_donor']['points']
    
    # Check super donor badge
    if donor.total_donations >= 10 and 'super_donor' not in current_badges:
        new_badges.append('super_donor')
        gamification.points += BADGES['super_donor']['points']
    
    # Check legend donor badge
    if donor.total_donations >= 25 and 'legend_donor' not in current_badges:
        new_badges.append('legend_donor')
        gamification.points += BADGES['legend_donor']['points']
    
    # Check rare blood badge
    if donor.blood_group in ['AB-', 'O-'] and 'rare_blood' not in current_badges:
        new_badges.append('rare_blood')
        gamification.points += BADGES['rare_blood']['points']
    
    # Update badges list
    if new_badges:
        current_badges.extend(new_badges)
        gamification.badges = str(current_badges)
        gamification.tier = calculate_tier(gamification.points)
    
    return new_badges


@gamification_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_gamification():
    """Get current user's gamification data"""
    try:
        donor, _, error = get_authenticated_user(expected_type='donor')
        if error:
            return jsonify(create_response(success=False, message=error)), 403
        
        gamification = Gamification.query.filter_by(donor_id=donor.donor_id).first()
        
        if not gamification:
            # Create gamification record if it doesn't exist
            gamification = Gamification(
                donor_id=donor.donor_id,
                points=0,
                badges='[]',
                tier='Bronze'
            )
            db.session.add(gamification)
            db.session.commit()
        
        badges = eval(gamification.badges) if gamification.badges else []
        badge_details = [BADGES.get(badge, {}) for badge in badges]
        
        tier_info = TIERS.get(gamification.tier, TIERS['Bronze'])
        next_tier = None
        for tier_name, tier_data in TIERS.items():
            if tier_data['min_points'] > gamification.points:
                next_tier = {'name': tier_name, 'points_needed': tier_data['min_points'] - gamification.points}
                break
        
        return jsonify(create_response(
            success=True,
            data={
                'points': gamification.points,
                'tier': gamification.tier,
                'tier_color': tier_info['color'],
                'badges': badge_details,
                'total_badges': len(badges),
                'next_tier': next_tier,
                'total_donations': donor.total_donations,
                'response_rate': float(donor.response_rate) if donor.response_rate else 0
            },
            message="Gamification data retrieved"
        )), 200

    except Exception as e:
        return jsonify(create_response(
            success=False,
            message=f"Error: {str(e)}"
        )), 500


@gamification_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get donor leaderboard"""
    try:
        period = request.args.get('period', 'monthly')
        limit = int(request.args.get('limit', 50))
        
        # Get top donors by points
        gamifications = Gamification.query.order_by(
            Gamification.points.desc()
        ).limit(limit).all()
        
        leaderboard = []
        for idx, gam in enumerate(gamifications, 1):
            donor = Donor.query.get(gam.donor_id)
            if donor:
                badges = eval(gam.badges) if gam.badges else []
                leaderboard.append({
                    'rank': idx,
                    'donor_id': donor.donor_id,
                    'name': donor.name,
                    'blood_group': donor.blood_group,
                    'points': gam.points,
                    'tier': gam.tier,
                    'total_donations': donor.total_donations,
                    'badges_count': len(badges),
                    'response_rate': float(donor.response_rate) if donor.response_rate else 0
                })
        
        return jsonify(create_response(
            success=True,
            data={
                'period': period,
                'leaderboard': leaderboard
            },
            message="Leaderboard retrieved"
        )), 200

    except Exception as e:
        return jsonify(create_response(
            success=False,
            message=f"Error: {str(e)}"
        )), 500


@gamification_bp.route('/badges', methods=['GET'])
def get_all_badges():
    """Get all available badges"""
    try:
        badges_list = []
        for badge_id, badge_info in BADGES.items():
            badges_list.append({
                'id': badge_id,
                'name': badge_info['name'],
                'icon': badge_info['icon'],
                'points': badge_info['points'],
                'description': badge_info['description']
            })
        
        return jsonify(create_response(
            success=True,
            data=badges_list,
            message="All badges retrieved"
        )), 200

    except Exception as e:
        return jsonify(create_response(
            success=False,
            message=f"Error: {str(e)}"
        )), 500


@gamification_bp.route('/challenges', methods=['GET'])
def get_challenges():
    """Get available challenges for donors"""
    try:
        challenges = [
            {
                'id': 'monthly_donation',
                'name': 'Monthly Donation Challenge',
                'description': 'Donate blood this month',
                'points': 100,
                'progress': 0,
                'target': 1,
                'icon': '🩸'
            },
            {
                'id': 'emergency_response',
                'name': 'Emergency Response',
                'description': 'Respond to an emergency request',
                'points': 150,
                'progress': 0,
                'target': 1,
                'icon': '🚑'
            },
            {
                'id': 'referral_challenge',
                'name': 'Refer a Friend',
                'description': 'Get a friend to register as a donor',
                'points': 75,
                'progress': 0,
                'target': 1,
                'icon': '👥'
            },
            {
                'id': 'profile_complete',
                'name': 'Complete Profile',
                'description': 'Fill in all profile details',
                'points': 50,
                'progress': 0,
                'target': 100,
                'icon': '📝'
            }
        ]
        
        return jsonify(create_response(
            success=True,
            data=challenges,
            message="Challenges retrieved"
        )), 200

    except Exception as e:
        return jsonify(create_response(
            success=False,
            message=f"Error: {str(e)}"
        )), 500


@gamification_bp.route('/award-points', methods=['POST'])
@jwt_required()
def award_points():
    """Award points to a donor (admin function)"""
    try:
        data = request.get_json()
        donor_id = data.get('donor_id')
        points = data.get('points', 0)
        reason = data.get('reason', 'Points awarded')
        
        if not donor_id:
            return jsonify(create_response(
                success=False,
                message="Donor ID required"
            )), 400
        
        gamification = Gamification.query.filter_by(donor_id=donor_id).first()
        if not gamification:
            return jsonify(create_response(
                success=False,
                message="Gamification record not found"
            )), 404
        
        gamification.points += points
        gamification.tier = calculate_tier(gamification.points)
        db.session.commit()
        
        return jsonify(create_response(
            success=True,
            data={
                'points': gamification.points,
                'tier': gamification.tier
            },
            message=f"{reason}: {points} points awarded"
        )), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(create_response(
            success=False,
            message=f"Error: {str(e)}"
        )), 500
