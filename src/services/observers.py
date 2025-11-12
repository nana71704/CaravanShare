# src/services/observers.py

class NotificationService:
    """옵저버 역할 (실제로는 이메일, SMS, 푸시 알림 전송)"""
    def send_notification(self, user_id: str, message: str):
        print(f"알림 (옵저버): [To: {user_id}] {message}")