#!/usr/bin/env python3
"""
WILLOW Gmail Integration Module
Production-ready Gmail API integration for sync coordination
"""

import json
import base64
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any

class GmailIntegration:
    """Gmail API integration for WILLOW sync system."""

    SCOPES = [
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify'
    ]

    def __init__(self, credentials_path: str = "config/gmail_credentials.json"):
        self.credentials_path = credentials_path
        self.token_path = "config/gmail_token.json"
        self.service = None
        self.logger = self._setup_logging()
        self._authenticate()

    def _setup_logging(self):
        """Setup logging for Gmail integration."""
        logger = logging.getLogger('GmailIntegration')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _authenticate(self):
        """Authenticate with Gmail API."""
        creds = None

        # Load existing token
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    self.logger.error(f"Token refresh failed: {e}")
                    creds = None

            if not creds:
                if os.path.exists(self.credentials_path):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                else:
                    raise FileNotFoundError(f"Gmail credentials file not found: {self.credentials_path}")

            # Save credentials
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        self.service = build('gmail', 'v1', credentials=creds)
        self.logger.info("Gmail authentication successful")

    def send_sync_notification(self, 
                             recipient: str, 
                             subject: str, 
                             body: str,
                             attachment_data: Optional[Dict] = None) -> bool:
        """Send sync notification email."""
        try:
            message = MIMEMultipart()
            message['to'] = recipient
            message['subject'] = subject

            # Add body
            msg_body = MIMEText(body, 'plain')
            message.attach(msg_body)

            # Add attachments if provided
            if attachment_data:
                for filename, content in attachment_data.items():
                    attachment = MIMEApplication(content)
                    attachment.add_header(
                        'Content-Disposition',
                        'attachment',
                        filename=filename
                    )
                    message.attach(attachment)

            # Send message
            raw_message = base64.urlsafe_b64encode(
                message.as_bytes()
            ).decode('utf-8')

            send_message = {'raw': raw_message}
            result = self.service.users().messages().send(
                userId='me', 
                body=send_message
            ).execute()

            self.logger.info(f"Email sent successfully: {result['id']}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False

    def send_agent_status_report(self, 
                               recipients: List[str], 
                               agent_data: Dict) -> bool:
        """Send agent status report to administrators."""
        try:
            subject = f"WILLOW Agent Status Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

            body = f"""
WILLOW Sync System - Agent Status Report

Generated: {datetime.now(timezone.utc).isoformat()}

Active Agents: {agent_data.get('active_agents', 0)}
Total Messages: {agent_data.get('total_messages', 0)}
Success Rate: {agent_data.get('success_rate', 'N/A')}%
System Health: {agent_data.get('health_status', 'Unknown')}

Detailed Metrics:
{json.dumps(agent_data.get('detailed_metrics', {}), indent=2)}

Last Updated: {agent_data.get('last_updated', 'N/A')}

This is an automated report from the WILLOW sync coordination system.
            """

            success_count = 0
            for recipient in recipients:
                if self.send_sync_notification(recipient, subject, body):
                    success_count += 1

            self.logger.info(f"Status report sent to {success_count}/{len(recipients)} recipients")
            return success_count == len(recipients)

        except Exception as e:
            self.logger.error(f"Failed to send status report: {e}")
            return False

    def send_alert_notification(self, 
                              recipients: List[str], 
                              alert_type: str, 
                              alert_data: Dict) -> bool:
        """Send critical alert notification."""
        try:
            subject = f"CRITICAL ALERT: {alert_type} - WILLOW Sync System"

            body = f"""
🚨 CRITICAL ALERT 🚨

Alert Type: {alert_type}
Severity: {alert_data.get('severity', 'HIGH')}
Timestamp: {datetime.now(timezone.utc).isoformat()}

Details:
{alert_data.get('message', 'No additional details')}

Affected Components:
{json.dumps(alert_data.get('affected_components', []), indent=2)}

Action Required: {alert_data.get('action_required', 'Immediate investigation needed')}

System Status: {alert_data.get('system_status', 'Unknown')}

Please respond immediately to resolve this issue.

WILLOW Sync Monitoring System
            """

            success_count = 0
            for recipient in recipients:
                if self.send_sync_notification(recipient, subject, body):
                    success_count += 1

            self.logger.warning(f"Alert sent to {success_count}/{len(recipients)} recipients")
            return success_count == len(recipients)

        except Exception as e:
            self.logger.error(f"Failed to send alert: {e}")
            return False

    def check_sync_emails(self, query: str = "label:WILLOW-SYNC") -> List[Dict]:
        """Check for sync-related emails."""
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=50
            ).execute()

            messages = results.get('messages', [])
            processed_messages = []

            for message in messages:
                msg_detail = self.service.users().messages().get(
                    userId='me',
                    id=message['id']
                ).execute()

                processed_messages.append({
                    'id': message['id'],
                    'subject': self._get_header_value(msg_detail, 'Subject'),
                    'sender': self._get_header_value(msg_detail, 'From'),
                    'date': self._get_header_value(msg_detail, 'Date'),
                    'snippet': msg_detail.get('snippet', '')
                })

            self.logger.info(f"Retrieved {len(processed_messages)} sync emails")
            return processed_messages

        except Exception as e:
            self.logger.error(f"Failed to check emails: {e}")
            return []

    def _get_header_value(self, message: Dict, header_name: str) -> str:
        """Extract header value from email message."""
        headers = message.get('payload', {}).get('headers', [])
        for header in headers:
            if header.get('name') == header_name:
                return header.get('value', '')
        return ''

    def create_sync_label(self, label_name: str = "WILLOW-SYNC") -> bool:
        """Create label for sync emails."""
        try:
            label_object = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }

            result = self.service.users().labels().create(
                userId='me',
                body=label_object
            ).execute()

            self.logger.info(f"Created label: {label_name}")
            return True

        except Exception as e:
            if "already exists" in str(e).lower():
                self.logger.info(f"Label already exists: {label_name}")
                return True
            else:
                self.logger.error(f"Failed to create label: {e}")
                return False

def main():
    """Test Gmail integration."""
    try:
        gmail = GmailIntegration()

        # Create sync label
        gmail.create_sync_label()

        # Test notification
        test_data = {
            'active_agents': 3,
            'success_rate': 98.5,
            'health_status': 'Healthy',
            'last_updated': datetime.now().isoformat()
        }

        # Note: Add actual recipient email for testing
        # gmail.send_agent_status_report(['admin@example.com'], test_data)

        print("Gmail integration test completed successfully")

    except Exception as e:
        print(f"Gmail integration test failed: {e}")

if __name__ == "__main__":
    main()
