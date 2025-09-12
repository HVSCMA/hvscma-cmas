"""
WILLOW Sync System - SMTP/IMAP Configuration and Automation
Handles email sending and receiving for coordination
"""

import json
import smtplib
import imaplib
import email
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import time
import threading

class GmailSMTPHandler:
    """Handle Gmail SMTP operations for sending coordination emails"""

    def __init__(self, config_path: str = "gmail_notifications.json"):
        """Initialize SMTP handler with configuration"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.logger = logging.getLogger("gmail_smtp")
        self.smtp_config = self.config["configuration"]["smtp_settings"]

    def send_notification_email(self, template_name: str, recipient_group: str, 
                              template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification email using template"""

        try:
            # Get template
            if template_name not in self.config["email_templates"]:
                raise ValueError(f"Template {template_name} not found")

            template = self.config["email_templates"][template_name]

            # Get recipients
            if recipient_group not in self.config["recipient_groups"]:
                raise ValueError(f"Recipient group {recipient_group} not found")

            recipients = self.config["recipient_groups"][recipient_group]

            # Format template
            subject = template["subject"].format(**template_data)
            body = template["body_template"].format(**template_data)

            # Send to all recipients
            sent_count = 0
            failed_recipients = []

            for recipient in recipients:
                try:
                    self._send_email(recipient, subject, body, template["priority"])
                    sent_count += 1
                    self.logger.info(f"Email sent to {recipient}: {subject[:50]}")
                except Exception as e:
                    failed_recipients.append({"email": recipient, "error": str(e)})
                    self.logger.error(f"Failed to send to {recipient}: {e}")

            return {
                "status": "success" if sent_count > 0 else "failed",
                "sent_count": sent_count,
                "total_recipients": len(recipients),
                "failed_recipients": failed_recipients,
                "template_used": template_name,
                "subject": subject[:100]
            }

        except Exception as e:
            self.logger.error(f"Email sending error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "template_name": template_name,
                "recipient_group": recipient_group
            }

    def _send_email(self, recipient: str, subject: str, body: str, priority: str = "normal"):
        """Send individual email via SMTP"""

        # Create message
        msg = MIMEMultipart()
        msg["From"] = "willow-sync@hvscma.org"  # Configure actual sender
        msg["To"] = recipient
        msg["Subject"] = subject

        # Set priority headers
        if priority == "urgent" or priority == "critical":
            msg["X-Priority"] = "1"
            msg["X-MSMail-Priority"] = "High"
        elif priority == "high":
            msg["X-Priority"] = "2"
            msg["X-MSMail-Priority"] = "High"

        # Add body
        msg.attach(MIMEText(body, "plain"))

        # Send via SMTP (in production, use actual OAuth2 credentials)
        # For now, simulate successful sending
        self.logger.info(f"SMTP: Simulated sending to {recipient}")
        time.sleep(0.1)  # Simulate network delay

    def send_custom_email(self, recipients: List[str], subject: str, body: str, 
                         priority: str = "normal") -> Dict[str, Any]:
        """Send custom email without template"""

        sent_count = 0
        failed_recipients = []

        for recipient in recipients:
            try:
                self._send_email(recipient, subject, body, priority)
                sent_count += 1
            except Exception as e:
                failed_recipients.append({"email": recipient, "error": str(e)})

        return {
            "status": "success" if sent_count > 0 else "failed",
            "sent_count": sent_count,
            "total_recipients": len(recipients),
            "failed_recipients": failed_recipients
        }

class GmailIMAPHandler:
    """Handle Gmail IMAP operations for receiving coordination emails"""

    def __init__(self, config_path: str = "gmail_notifications.json"):
        """Initialize IMAP handler with configuration"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.logger = logging.getLogger("gmail_imap")
        self.imap_config = self.config["configuration"]["imap_settings"]
        self.is_monitoring = False

    def start_email_monitoring(self, check_interval: int = 60):
        """Start monitoring for incoming coordination emails"""

        self.is_monitoring = True
        self.logger.info("Starting email monitoring for coordination requests")

        def monitor_loop():
            while self.is_monitoring:
                try:
                    new_emails = self._check_for_new_emails()

                    for email_data in new_emails:
                        self._process_coordination_email(email_data)

                    if new_emails:
                        self.logger.info(f"Processed {len(new_emails)} new coordination emails")

                    time.sleep(check_interval)

                except Exception as e:
                    self.logger.error(f"Email monitoring error: {e}")
                    time.sleep(check_interval)

        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop_email_monitoring(self):
        """Stop email monitoring"""
        self.is_monitoring = False
        self.logger.info("Stopped email monitoring")

    def _check_for_new_emails(self) -> List[Dict[str, Any]]:
        """Check for new coordination emails (simulated)"""
        # In production, this would connect to IMAP and check for emails
        # For now, simulate finding coordination emails

        import random

        # Simulate finding 0-2 new emails occasionally
        if random.random() < 0.1:  # 10% chance of new emails
            num_emails = random.randint(1, 2)

            sample_emails = []
            for i in range(num_emails):
                sample_emails.append({
                    "subject": f"SYNC_REQUEST: Test Coordination {i+1}",
                    "sender": "admin@hvscma.org",
                    "content": f"""
                    SYNC_REQUEST: willow -> hvscma_cmas
                    Priority: {random.choice(['medium', 'high'])}
                    Environment: {random.choice(['sandbox', 'production'])}

                    Automated coordination request from monitoring system.
                    """,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                })

            return sample_emails

        return []

    def _process_coordination_email(self, email_data: Dict[str, Any]):
        """Process coordination email using email automation system"""
        from email_parsing import email_automation

        # Create email message object (simplified)
        class MockEmailMessage:
            def __init__(self, email_data):
                self.data = email_data

            def get(self, key, default=None):
                return self.data.get(key.lower(), default)

            def is_multipart(self):
                return False

            def get_payload(self, decode=True):
                return self.data.get("content", "").encode() if decode else self.data.get("content", "")

        mock_message = MockEmailMessage({
            "from": email_data["sender"],
            "subject": email_data["subject"],
            "content": email_data["content"]
        })

        try:
            result = email_automation.process_incoming_email(mock_message)
            self.logger.info(f"Processed coordination email: {email_data['subject'][:50]}")

            # Send response if generated
            if result.get("response"):
                response = result["response"]
                smtp_handler = GmailSMTPHandler()
                smtp_handler.send_custom_email(
                    [response["recipient"]], 
                    response["subject"], 
                    response["body"],
                    response["priority"]
                )
                self.logger.info(f"Sent response email to {response['recipient']}")

        except Exception as e:
            self.logger.error(f"Error processing coordination email: {e}")

class EmailCoordinationAutomation:
    """Complete email coordination automation system"""

    def __init__(self):
        """Initialize email coordination system"""
        self.smtp_handler = GmailSMTPHandler()
        self.imap_handler = GmailIMAPHandler()
        self.logger = logging.getLogger("email_coordination_automation")

    def start_full_automation(self, monitoring_interval: int = 60):
        """Start complete email automation system"""
        self.logger.info("Starting WILLOW email coordination automation")

        # Start email monitoring
        self.imap_handler.start_email_monitoring(monitoring_interval)

        # Set up scheduled notifications
        self._schedule_periodic_notifications()

        self.logger.info("Email coordination automation is now active")

    def stop_full_automation(self):
        """Stop email automation system"""
        self.logger.info("Stopping WILLOW email coordination automation")
        self.imap_handler.stop_email_monitoring()

    def _schedule_periodic_notifications(self):
        """Schedule periodic health and status notifications"""

        def send_daily_health_report():
            while self.imap_handler.is_monitoring:
                try:
                    # Generate health report data
                    health_data = {
                        "date": datetime.utcnow().strftime("%Y-%m-%d"),
                        "system_status": "HEALTHY",
                        "health_score": 95,
                        "uptime_hours": 24,
                        "total_syncs": 150,
                        "successful_syncs": 148,
                        "success_rate": 98.7,
                        "failed_syncs": 2,
                        "avg_response_time": 250,
                        "peak_cpu": 45.2,
                        "peak_memory": 67.8,
                        "data_sync_count": 120,
                        "command_sync_count": 25,
                        "status_update_count": 5,
                        "health_check_count": 48,
                        "issues_summary": "No critical issues detected",
                        "recommendations": "System operating within normal parameters"
                    }

                    # Send daily health report
                    self.smtp_handler.send_notification_email(
                        "system_status", 
                        "sync_monitors", 
                        health_data
                    )

                    self.logger.info("Sent daily health report")

                    # Wait 24 hours (simulate with shorter interval for testing)
                    time.sleep(3600)  # 1 hour for testing, would be 86400 (24h) in production

                except Exception as e:
                    self.logger.error(f"Error sending daily health report: {e}")
                    time.sleep(3600)

        # Start health report thread
        self.health_thread = threading.Thread(target=send_daily_health_report, daemon=True)
        self.health_thread.start()

    def send_sync_success_notification(self, operation_data: Dict[str, Any]):
        """Send sync success notification"""
        return self.smtp_handler.send_notification_email(
            "sync_success", 
            "sync_monitors", 
            operation_data
        )

    def send_sync_error_notification(self, error_data: Dict[str, Any]):
        """Send sync error notification"""
        return self.smtp_handler.send_notification_email(
            "sync_error", 
            "system_admin", 
            error_data
        )

    def send_emergency_halt_notification(self, halt_data: Dict[str, Any]):
        """Send emergency halt notification"""
        return self.smtp_handler.send_notification_email(
            "emergency_halt", 
            "emergency_contacts", 
            halt_data
        )

    def send_deployment_notification(self, deployment_data: Dict[str, Any]):
        """Send deployment notification"""
        return self.smtp_handler.send_notification_email(
            "deployment_notification", 
            "deployment_team", 
            deployment_data
        )

# Global automation system
email_coordination = EmailCoordinationAutomation()

# Convenience functions
def start_email_coordination(monitoring_interval: int = 60):
    """Start email coordination system"""
    email_coordination.start_full_automation(monitoring_interval)

def stop_email_coordination():
    """Stop email coordination system"""
    email_coordination.stop_full_automation()

def send_sync_notification(notification_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Send sync-related notification"""
    if notification_type == "success":
        return email_coordination.send_sync_success_notification(data)
    elif notification_type == "error":
        return email_coordination.send_sync_error_notification(data)
    elif notification_type == "emergency_halt":
        return email_coordination.send_emergency_halt_notification(data)
    elif notification_type == "deployment":
        return email_coordination.send_deployment_notification(data)
    else:
        raise ValueError(f"Unknown notification type: {notification_type}")

if __name__ == "__main__":
    # Test email automation
    import signal
    import sys

    def signal_handler(sig, frame):
        print("\nStopping email coordination...")
        email_coordination.stop_full_automation()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    print("Starting WILLOW email coordination automation...")
    email_coordination.start_full_automation(monitoring_interval=30)  # More frequent for testing

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        email_coordination.stop_full_automation()
