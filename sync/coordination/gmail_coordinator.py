#!/usr/bin/env python3
"""
WILLOW Gmail Coordinator - Email-based task coordination and communication system
Handles automated email processing, task initiation, and status reporting
"""

import os
import json
import logging
import asyncio
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re

@dataclass
class EmailConfig:
    smtp_server: str
    smtp_port: int
    imap_server: str
    imap_port: int
    username: str
    password: str
    use_tls: bool = True

@dataclass
class EmailTask:
    task_id: str
    sender: str
    subject: str
    content: str
    willow_command: Optional[str]
    priority: str = "medium"
    timestamp: datetime = None

class GmailCoordinator:
    """Gmail-based coordination system for WILLOW"""

    def __init__(self, email_config: EmailConfig):
        self.config = email_config
        self.processed_emails = set()
        self.active_tasks = {}
        self.setup_logging()

    def setup_logging(self):
        """Initialize logging system"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - WILLOW-GMAIL - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/var/log/willow_gmail.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def parse_willow_command_from_email(self, content: str) -> Optional[str]:
        """Extract WILLOW sync commands from email content"""
        # Look for WILLOW_SYNC commands in email
        pattern = r'WILLOW_SYNC:[A-Z]+(?::[^\n]*)?'
        matches = re.findall(pattern, content, re.IGNORECASE)

        if matches:
            return matches[0].upper()

        # Check for common task keywords and convert to WILLOW commands
        content_lower = content.lower()

        if any(word in content_lower for word in ['deploy', 'deployment']):
            return "WILLOW_SYNC:DEPLOY:PRODUCTION:AUTO"
        elif any(word in content_lower for word in ['status', 'check', 'report']):
            return "WILLOW_SYNC:STATUS:ALL"
        elif any(word in content_lower for word in ['initialize', 'init', 'start']):
            return "WILLOW_SYNC:INIT:EMAIL_TASK"
        elif any(word in content_lower for word in ['validate', 'test', 'verify']):
            return "WILLOW_SYNC:VALIDATE:LATEST"
        elif any(word in content_lower for word in ['monitor', 'watch', 'track']):
            return "WILLOW_SYNC:MONITOR:ALL"

        return None

    async def connect_imap(self) -> imaplib.IMAP4_SSL:
        """Establish IMAP connection to Gmail"""
        try:
            imap = imaplib.IMAP4_SSL(self.config.imap_server, self.config.imap_port)
            imap.login(self.config.username, self.config.password)
            return imap
        except Exception as e:
            self.logger.error(f"IMAP connection failed: {e}")
            raise

    async def connect_smtp(self) -> smtplib.SMTP:
        """Establish SMTP connection to Gmail"""
        try:
            smtp = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
            smtp.starttls()
            smtp.login(self.config.username, self.config.password)
            return smtp
        except Exception as e:
            self.logger.error(f"SMTP connection failed: {e}")
            raise

    async def check_for_new_emails(self) -> List[EmailTask]:
        """Check for new emails with WILLOW tasks"""
        self.logger.info("Checking for new emails...")

        new_tasks = []
        imap = await self.connect_imap()

        try:
            # Select INBOX
            imap.select('INBOX')

            # Search for unread emails
            status, messages = imap.search(None, 'UNSEEN')

            if status != 'OK':
                self.logger.warning("No new messages found")
                return new_tasks

            message_ids = messages[0].split()
            self.logger.info(f"Found {len(message_ids)} new emails")

            for msg_id in message_ids[-10:]:  # Process last 10 emails
                # Fetch email
                status, msg_data = imap.fetch(msg_id, '(RFC822)')

                if status != 'OK':
                    continue

                # Parse email
                email_msg = email.message_from_bytes(msg_data[0][1])

                sender = email_msg.get('From', '')
                subject = email_msg.get('Subject', '')

                # Get email content
                content = ""
                if email_msg.is_multipart():
                    for part in email_msg.walk():
                        if part.get_content_type() == "text/plain":
                            content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            break
                else:
                    content = email_msg.get_payload(decode=True).decode('utf-8', errors='ignore')

                # Parse WILLOW command
                willow_command = self.parse_willow_command_from_email(content)

                if willow_command or any(keyword in subject.lower() for keyword in ['willow', 'sync', 'deploy']):
                    task = EmailTask(
                        task_id=f"EMAIL_{msg_id.decode()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        sender=sender,
                        subject=subject,
                        content=content,
                        willow_command=willow_command,
                        timestamp=datetime.now()
                    )

                    new_tasks.append(task)
                    self.logger.info(f"New WILLOW task from {sender}: {willow_command}")

                # Mark as read
                imap.store(msg_id, '+FLAGS', '\\Seen')

        finally:
            imap.close()
            imap.logout()

        return new_tasks

    async def send_status_email(self, recipient: str, task_result: Dict[str, Any]) -> bool:
        """Send status update email"""
        try:
            smtp = await self.connect_smtp()

            msg = MIMEMultipart()
            msg['From'] = self.config.username
            msg['To'] = recipient
            msg['Subject'] = f"WILLOW Sync Status Update - {task_result.get('task_id', 'Unknown')}"

            # Create email body
            body = f"""
WILLOW Sync Status Report
=========================

Task ID: {task_result.get('task_id', 'N/A')}
Status: {task_result.get('status', 'Unknown')}
Completion Time: {task_result.get('completion_time', datetime.now().isoformat())}

Details:
{json.dumps(task_result, indent=2)}

---
This is an automated message from WILLOW Sync Coordination System
"""

            msg.attach(MIMEText(body, 'plain'))

            # Send email
            smtp.send_message(msg)
            smtp.quit()

            self.logger.info(f"Status email sent to {recipient}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send status email: {e}")
            return False

    async def send_error_notification(self, recipient: str, error_info: Dict[str, Any]) -> bool:
        """Send error notification email"""
        try:
            smtp = await self.connect_smtp()

            msg = MIMEMultipart()
            msg['From'] = self.config.username
            msg['To'] = recipient
            msg['Subject'] = f"WILLOW Sync Error Alert - {error_info.get('error_type', 'Unknown Error')}"

            # Create email body
            body = f"""
WILLOW Sync Error Alert
=======================

Error Type: {error_info.get('error_type', 'Unknown')}
Error Time: {error_info.get('error_time', datetime.now().isoformat())}
Task ID: {error_info.get('task_id', 'N/A')}

Error Details:
{error_info.get('error_message', 'No details available')}

System Status:
{json.dumps(error_info.get('system_status', {}), indent=2)}

Please investigate and take appropriate action.

---
This is an automated error notification from WILLOW Sync Coordination System
"""

            msg.attach(MIMEText(body, 'plain'))

            # Send email
            smtp.send_message(msg)
            smtp.quit()

            self.logger.warning(f"Error notification sent to {recipient}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send error notification: {e}")
            return False

    async def process_email_tasks(self) -> List[Dict[str, Any]]:
        """Process all pending email tasks"""
        new_tasks = await self.check_for_new_emails()

        if not new_tasks:
            return []

        results = []

        for task in new_tasks:
            self.logger.info(f"Processing email task: {task.task_id}")

            # Import WILLOW coordinator (would be imported at runtime)
            try:
                # Simulate WILLOW command execution
                if task.willow_command:
                    # This would normally execute the actual WILLOW command
                    result = {
                        "task_id": task.task_id,
                        "command": task.willow_command,
                        "status": "SUCCESS",
                        "completion_time": datetime.now().isoformat(),
                        "initiated_by": task.sender,
                        "email_subject": task.subject
                    }
                else:
                    result = {
                        "task_id": task.task_id,
                        "command": "NO_COMMAND_FOUND",
                        "status": "PENDING_CLARIFICATION",
                        "completion_time": datetime.now().isoformat(),
                        "initiated_by": task.sender,
                        "email_subject": task.subject
                    }

                results.append(result)

                # Send status email back to sender
                sender_email = task.sender.split('<')[-1].split('>')[0] if '<' in task.sender else task.sender
                await self.send_status_email(sender_email, result)

            except Exception as e:
                error_result = {
                    "task_id": task.task_id,
                    "status": "ERROR",
                    "error": str(e),
                    "completion_time": datetime.now().isoformat()
                }

                results.append(error_result)

                # Send error notification
                sender_email = task.sender.split('<')[-1].split('>')[0] if '<' in task.sender else task.sender
                error_info = {
                    "error_type": "TASK_PROCESSING_ERROR",
                    "error_time": datetime.now().isoformat(),
                    "task_id": task.task_id,
                    "error_message": str(e)
                }
                await self.send_error_notification(sender_email, error_info)

        return results

    async def start_email_monitoring(self, check_interval: int = 300) -> None:
        """Start continuous email monitoring"""
        self.logger.info(f"Starting email monitoring (check every {check_interval} seconds)")

        while True:
            try:
                results = await self.process_email_tasks()

                if results:
                    self.logger.info(f"Processed {len(results)} email tasks")

                    # Log results
                    for result in results:
                        self.logger.info(f"Task {result['task_id']}: {result['status']}")

                # Wait before next check
                await asyncio.sleep(check_interval)

            except Exception as e:
                self.logger.error(f"Email monitoring error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

# CLI Interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="WILLOW Gmail Coordination System")
    parser.add_argument("--smtp-server", default="smtp.gmail.com", help="SMTP server")
    parser.add_argument("--smtp-port", type=int, default=587, help="SMTP port")
    parser.add_argument("--imap-server", default="imap.gmail.com", help="IMAP server")
    parser.add_argument("--imap-port", type=int, default=993, help="IMAP port")
    parser.add_argument("--username", required=True, help="Gmail username")
    parser.add_argument("--password", required=True, help="Gmail app password")
    parser.add_argument("--check-interval", type=int, default=300, help="Email check interval in seconds")
    parser.add_argument("--mode", choices=['monitor', 'check-once'], default='monitor', help="Operation mode")

    args = parser.parse_args()

    config = EmailConfig(
        smtp_server=args.smtp_server,
        smtp_port=args.smtp_port,
        imap_server=args.imap_server,
        imap_port=args.imap_port,
        username=args.username,
        password=args.password
    )

    coordinator = GmailCoordinator(config)

    if args.mode == 'monitor':
        asyncio.run(coordinator.start_email_monitoring(args.check_interval))
    else:
        results = asyncio.run(coordinator.process_email_tasks())
        print(json.dumps(results, indent=2, default=str))
