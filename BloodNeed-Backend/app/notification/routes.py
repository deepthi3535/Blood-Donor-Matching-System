# app/notification/routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.utils.helpers import create_response, get_authenticated_user
from datetime import datetime, timedelta
import os

notification_bp = Blueprint('notification', __name__)


# In-memory notification storage (in production, use database)
notifications_db = {}


def create_notification(user_id, message, notification_type='info', data=None):
    """Create a new notification for a user"""
    if user_id not in notifications_db:
        notifications_db[user_id] = []
    
    notification = {
        'id': len(notifications_db[user_id]) + 1,
        'user_id': user_id,
        'message': message,
        'type': notification_type,
        'data': data or {},
        'read': False,
        'created_at': datetime.utcnow().isoformat()
    }
    
    notifications_db[user_id].insert(0, notification)
    return notification


@notification_bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get notifications for current user"""
    try:
        user, user_type, error = get_authenticated_user()
        if error:
            return jsonify(create_response(success=False, message=error)), 403
        
        user_id = user.donor_id if user_type == 'donor' else user.patient_id
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        user_notifications = notifications_db.get(user_id, [])
        
        # Pagination
        start = (page - 1) * limit
        end = start + limit
        paginated = user_notifications[start:end]
        
        return jsonify(create_response(
            success=True,
            data={
                'notifications': paginated,
                'total': len(user_notifications),
                'page': page,
                'limit': limit
            },
            message="Notifications retrieved"
        )), 200

    except Exception as e:
        return jsonify(create_response(
            success=False,
            message=f"Error: {str(e)}"
        )), 500


@notification_bp.route('/<int:notification_id>/read', methods=['POST'])
@jwt_required()
def mark_as_read(notification_id):
    """Mark a notification as read"""
    try:
        user, user_type, error = get_authenticated_user()
        if error:
            return jsonify(create_response(success=False, message=error)), 403
        
        user_id = user.donor_id if user_type == 'donor' else user.patient_id
        
        if user_id in notifications_db:
            for notification in notifications_db[user_id]:
                if notification['id'] == notification_id:
                    notification['read'] = True
                    return jsonify(create_response(
                        success=True,
                        message="Notification marked as read"
                    )), 200
        
        return jsonify(create_response(
            success=False,
            message="Notification not found"
        )), 404

    except Exception as e:
        return jsonify(create_response(
            success=False,
            message=f"Error: {str(e)}"
        )), 500


@notification_bp.route('/read-all', methods=['POST'])
@jwt_required()
def mark_all_as_read():
    """Mark all notifications as read"""
    try:
        user, user_type, error = get_authenticated_user()
        if error:
            return jsonify(create_response(success=False, message=error)), 403
        
        user_id = user.donor_id if user_type == 'donor' else user.patient_id
        
        if user_id in notifications_db:
            for notification in notifications_db[user_id]:
                notification['read'] = True
        
        return jsonify(create_response(
            success=True,
            message="All notifications marked as read"
        )), 200

    except Exception as e:
        return jsonify(create_response(
            success=False,
            message=f"Error: {str(e)}"
        )), 500


@notification_bp.route('/clear', methods=['DELETE'])
@jwt_required()
def clear_all():
    """Clear all notifications"""
    try:
        user, user_type, error = get_authenticated_user()
        if error:
            return jsonify(create_response(success=False, message=error)), 403
        
        user_id = user.donor_id if user_type == 'donor' else user.patient_id
        
        if user_id in notifications_db:
            notifications_db[user_id] = []
        
        return jsonify(create_response(
            success=True,
            message="All notifications cleared"
        )), 200

    except Exception as e:
        return jsonify(create_response(
            success=False,
            message=f"Error: {str(e)}"
        )), 500


@notification_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """Get count of unread notifications"""
    try:
        user, user_type, error = get_authenticated_user()
        if error:
            return jsonify(create_response(success=False, message=error)), 403
        
        user_id = user.donor_id if user_type == 'donor' else user.patient_id
        
        user_notifications = notifications_db.get(user_id, [])
        unread_count = sum(1 for n in user_notifications if not n['read'])
        
        return jsonify(create_response(
            success=True,
            data={'unread_count': unread_count},
            message="Unread count retrieved"
        )), 200

    except Exception as e:
        return jsonify(create_response(
            success=False,
            message=f"Error: {str(e)}"
        )), 500


@notification_bp.route('/subscribe', methods=['POST'])
@jwt_required()
def subscribe_push():
    """Subscribe to push notifications (Firebase FCM)"""
    try:
        data = request.get_json()
        subscription = data.get('subscription')
        
        if not subscription:
            return jsonify(create_response(
                success=False,
                message="Subscription data required"
            )), 400
        
        # In production, save subscription to database
        # For now, just return success
        return jsonify(create_response(
            success=True,
            message="Successfully subscribed to push notifications"
        )), 200

    except Exception as e:
        return jsonify(create_response(
            success=False,
            message=f"Error: {str(e)}"
        )), 500


@notification_bp.route('/unsubscribe', methods=['POST'])
@jwt_required()
def unsubscribe_push():
    """Unsubscribe from push notifications"""
    try:
        data = request.get_json()
        subscription = data.get('subscription')
        
        # In production, remove subscription from database
        return jsonify(create_response(
            success=True,
            message="Successfully unsubscribed from push notifications"
        )), 200

    except Exception as e:
        return jsonify(create_response(
            success=False,
            message=f"Error: {str(e)}"
        )), 500


@notification_bp.route('/send', methods=['POST'])
@jwt_required()
def send_notification():
    """Send a notification to a user (admin function)"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        message = data.get('message')
        notification_type = data.get('type', 'info')
        notification_data = data.get('data', {})
        
        if not user_id or not message:
            return jsonify(create_response(
                success=False,
                message="User ID and message required"
            )), 400
        
        notification = create_notification(user_id, message, notification_type, notification_data)
        
        # In production, also send via Firebase FCM
        # fcm_service.send_notification(user_id, message, notification_data)
        
        return jsonify(create_response(
            success=True,
            data=notification,
            message="Notification sent successfully"
        )), 200

    except Exception as e:
        return jsonify(create_response(
            success=False,
            message=f"Error: {str(e)}"
        )), 500
