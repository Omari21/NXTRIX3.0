"""Live notification system module"""

class LiveNotificationSystem:
    def __init__(self):
        self.enabled = True
    
    def send_notification(self, user_id, message):
        return {"success": True, "notification_id": "demo_notif_123"}

live_notifications = LiveNotificationSystem()