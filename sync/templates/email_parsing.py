"""
WILLOW Sync System - Email Parsing and Processing
Handles incoming email coordination requests and responses
"""

import json
import re
import email
import imaplib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging

class EmailCoordinationParser:
    """Parse and process coordination emails for WILLOW sync system"""

    def __init__(self, config_path: str = "gmail_notifications.json"):
        """Initialize email parser with configuration"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.logger = logging.getLogger("email_coordination")
        self.command_patterns = self._compile_command_patterns()

    def _compile_command_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for command recognition"""
        patterns = {
            "sync_request": re.compile(r"SYNC_REQUEST\s*:\s*([A-Za-z_]+)\s*->\s*([A-Za-z_]+)", re.IGNORECASE),
            "status_request": re.compile(r"STATUS_REQUEST\s*:\s*([A-Za-z_]+)", re.IGNORECASE),
            "health_check": re.compile(r"HEALTH_CHECK(?:\s*:\s*([A-Za-z_]+))?", re.IGNORECASE),
            "emergency_halt": re.compile(r"EMERGENCY_HALT(?:\s*:\s*(.+))?", re.IGNORECASE),
            "deployment_trigger": re.compile(r"DEPLOYMENT_TRIGGER\s*:\s*([A-Za-z0-9_.]+)", re.IGNORECASE),
            "operation_id": re.compile(r"Operation ID:\s*([a-f0-9-]{36})", re.IGNORECASE),
            "priority": re.compile(r"Priority:\s*(low|medium|high|critical)", re.IGNORECASE),
            "environment": re.compile(r"Environment:\s*(sandbox|production)", re.IGNORECASE)
        }
        return patterns

    def parse_email_content(self, email_content: str, subject: str) -> Dict[str, Any]:
        """Parse email content and extract coordination commands"""
        parsed_result = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "subject": subject,
            "commands": [],
            "parameters": {},
            "validation_status": "pending",
            "processing_required": False
        }

        try:
            # Extract basic parameters
            for param_name, pattern in self.command_patterns.items():
                if param_name in ["operation_id", "priority", "environment"]:
                    match = pattern.search(email_content)
                    if match:
                        parsed_result["parameters"][param_name] = match.group(1)

            # Extract commands
            commands = []

            # Check for sync request
            sync_match = self.command_patterns["sync_request"].search(email_content)
            if sync_match:
                commands.append({
                    "type": "sync_request",
                    "source_system": sync_match.group(1),
                    "target_system": sync_match.group(2),
                    "operation": "data_sync"
                })

            # Check for status request
            status_match = self.command_patterns["status_request"].search(email_content)
            if status_match:
                commands.append({
                    "type": "status_request",
                    "target_system": status_match.group(1)
                })

            # Check for health check
            health_match = self.command_patterns["health_check"].search(email_content)
            if health_match:
                target_system = health_match.group(1) if health_match.group(1) else "all_systems"
                commands.append({
                    "type": "health_check",
                    "target_system": target_system
                })

            # Check for emergency halt
            halt_match = self.command_patterns["emergency_halt"].search(email_content)
            if halt_match:
                reason = halt_match.group(1) if halt_match.group(1) else "emergency_stop"
                commands.append({
                    "type": "emergency_halt",
                    "reason": reason,
                    "priority": "critical"
                })

            # Check for deployment trigger
            deploy_match = self.command_patterns["deployment_trigger"].search(email_content)
            if deploy_match:
                commands.append({
                    "type": "deployment_trigger",
                    "deployment_version": deploy_match.group(1)
                })

            parsed_result["commands"] = commands
            parsed_result["processing_required"] = len(commands) > 0
            parsed_result["validation_status"] = "valid" if commands else "no_commands_found"

            self.logger.info(f"Parsed {len(commands)} commands from email: {subject[:50]}")

        except Exception as e:
            parsed_result["validation_status"] = "error"
            parsed_result["error"] = str(e)
            self.logger.error(f"Email parsing error: {e}")

        return parsed_result

    def validate_command_authorization(self, sender_email: str, commands: List[Dict]) -> Dict[str, Any]:
        """Validate if sender is authorized to execute commands"""
        # In production, this would check against user database
        authorized_admins = [
            "admin@hvscma.org", 
            "sync-admin@hvscma.org",
            "deploy@hvscma.org"
        ]

        authorized_monitors = authorized_admins + [
            "monitoring@hvscma.org",
            "sync-team@hvscma.org"
        ]

        validation_result = {
            "authorized": False,
            "authorization_level": "none",
            "authorized_commands": [],
            "denied_commands": [],
            "reason": ""
        }

        try:
            # Determine authorization level
            if sender_email in authorized_admins:
                auth_level = "admin"
                authorized = True
            elif sender_email in authorized_monitors:
                auth_level = "monitor" 
                authorized = True
            else:
                auth_level = "none"
                authorized = False

            if not authorized:
                validation_result["denied_commands"] = commands
                validation_result["reason"] = f"Email {sender_email} not in authorized user list"
                return validation_result

            # Check command-level permissions
            for command in commands:
                command_type = command.get("type")

                # Admin-only commands
                if command_type in ["emergency_halt", "deployment_trigger"]:
                    if auth_level == "admin":
                        validation_result["authorized_commands"].append(command)
                    else:
                        validation_result["denied_commands"].append(command)

                # Monitor-level commands  
                elif command_type in ["status_request", "health_check", "sync_request"]:
                    validation_result["authorized_commands"].append(command)

                else:
                    validation_result["denied_commands"].append(command)

            validation_result["authorized"] = len(validation_result["authorized_commands"]) > 0
            validation_result["authorization_level"] = auth_level

            if validation_result["denied_commands"]:
                validation_result["reason"] = f"Some commands require higher authorization level"

        except Exception as e:
            validation_result["reason"] = f"Authorization validation error: {str(e)}"
            self.logger.error(f"Authorization error: {e}")

        return validation_result

    def generate_response_email(self, original_subject: str, processing_result: Dict[str, Any], 
                              recipient_email: str) -> Dict[str, Any]:
        """Generate appropriate response email"""

        response_templates = {
            "success": {
                "subject": "Re: {original_subject} - Commands Executed Successfully",
                "body": """
Your coordination request has been processed successfully.

Execution Summary:
- Commands Processed: {commands_processed}
- Execution Time: {execution_time}
- Status: SUCCESS ✅

Results:
{results_summary}

---
WILLOW Sync System v41.5
Automated Response - Repository: HVSCMA/hvscma-cmas/sync/
                """
            },
            "partial_success": {
                "subject": "Re: {original_subject} - Partial Execution Completed",  
                "body": """
Your coordination request has been partially processed.

Execution Summary:
- Commands Processed: {commands_processed}
- Commands Failed: {commands_failed}
- Status: PARTIAL SUCCESS ⚠️

Successful Operations:
{success_summary}

Failed Operations:
{failure_summary}

---
WILLOW Sync System v41.5
Automated Response - Repository: HVSCMA/hvscma-cmas/sync/
                """
            },
            "authorization_denied": {
                "subject": "Re: {original_subject} - Authorization Required",
                "body": """
Your coordination request could not be processed due to insufficient authorization.

Authorization Details:
- Your Email: {sender_email}
- Authorization Level: {auth_level}
- Required Level: {required_level}

Denied Commands:
{denied_commands}

To execute these commands, please:
1. Contact the system administrator
2. Request appropriate authorization level
3. Verify your email is in the authorized user list

---
WILLOW Sync System v41.5
Automated Response - Repository: HVSCMA/hvscma-cmas/sync/
                """
            },
            "error": {
                "subject": "Re: {original_subject} - Processing Error",
                "body": """
Your coordination request encountered an error during processing.

Error Details:
- Error Type: {error_type}
- Error Message: {error_message}
- Timestamp: {timestamp}

Recommended Actions:
1. Review the command syntax in your request
2. Verify system availability
3. Contact system administrator if error persists

---
WILLOW Sync System v41.5
Automated Response - Repository: HVSCMA/hvscma-cmas/sync/
                """
            }
        }

        # Determine response type
        if processing_result.get("authorization_denied"):
            response_type = "authorization_denied"
        elif processing_result.get("error"):
            response_type = "error"
        elif processing_result.get("partial_success"):
            response_type = "partial_success"
        else:
            response_type = "success"

        template = response_templates[response_type]

        # Format response
        response = {
            "recipient": recipient_email,
            "subject": template["subject"].format(original_subject=original_subject),
            "body": template["body"].format(**processing_result),
            "priority": "normal",
            "template_used": response_type
        }

        return response

class EmailAutomationSystem:
    """Complete email automation system for WILLOW sync coordination"""

    def __init__(self):
        """Initialize email automation system"""
        self.parser = EmailCoordinationParser()
        self.logger = logging.getLogger("email_automation")

    def process_incoming_email(self, email_message: email.message.Message) -> Dict[str, Any]:
        """Process incoming coordination email"""

        sender = email_message.get("From", "unknown@unknown.com")
        subject = email_message.get("Subject", "No Subject")

        # Extract email content
        content = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    content += part.get_payload(decode=True).decode()
        else:
            content = email_message.get_payload(decode=True).decode()

        # Parse content
        parsed_result = self.parser.parse_email_content(content, subject)

        # Validate authorization
        if parsed_result.get("processing_required"):
            auth_result = self.parser.validate_command_authorization(sender, parsed_result["commands"])
            parsed_result["authorization"] = auth_result

        # Process commands if authorized
        if parsed_result.get("authorization", {}).get("authorized"):
            processing_result = self._execute_authorized_commands(
                parsed_result["authorization"]["authorized_commands"]
            )
            parsed_result["processing_result"] = processing_result

        # Generate response
        if parsed_result.get("processing_required"):
            response = self.parser.generate_response_email(
                subject, 
                parsed_result.get("processing_result", {"error": "No processing performed"}),
                sender
            )
            parsed_result["response"] = response

        return parsed_result

    def _execute_authorized_commands(self, commands: List[Dict]) -> Dict[str, Any]:
        """Execute authorized commands and return results"""
        results = {
            "commands_processed": len(commands),
            "commands_failed": 0,
            "execution_time": datetime.utcnow().isoformat() + "Z",
            "results_summary": [],
            "success_summary": [],
            "failure_summary": []
        }

        for command in commands:
            try:
                # Simulate command execution
                command_result = self._simulate_command_execution(command)

                if command_result["status"] == "success":
                    results["success_summary"].append(f"✅ {command['type']}: {command_result['message']}")
                else:
                    results["failure_summary"].append(f"❌ {command['type']}: {command_result['message']}")
                    results["commands_failed"] += 1

                results["results_summary"].append({
                    "command": command["type"],
                    "status": command_result["status"],
                    "message": command_result["message"]
                })

            except Exception as e:
                results["commands_failed"] += 1
                results["failure_summary"].append(f"❌ {command['type']}: Execution error - {str(e)}")

        return results

    def _simulate_command_execution(self, command: Dict) -> Dict[str, Any]:
        """Simulate command execution (replace with actual implementation)"""
        command_type = command.get("type")

        # Simulate different execution outcomes
        if command_type == "health_check":
            return {
                "status": "success",
                "message": f"Health check completed for {command.get('target_system', 'all systems')} - Status: HEALTHY"
            }
        elif command_type == "status_request":
            return {
                "status": "success", 
                "message": f"Status retrieved for {command.get('target_system')} - Status: ONLINE"
            }
        elif command_type == "sync_request":
            return {
                "status": "success",
                "message": f"Sync initiated: {command.get('source_system')} -> {command.get('target_system')}"
            }
        elif command_type == "emergency_halt":
            return {
                "status": "success",
                "message": f"Emergency halt activated - Reason: {command.get('reason', 'emergency')}"
            }
        elif command_type == "deployment_trigger":
            return {
                "status": "success",
                "message": f"Deployment triggered for version {command.get('deployment_version')}"
            }
        else:
            return {
                "status": "error",
                "message": f"Unknown command type: {command_type}"
            }

# Global instances
email_parser = EmailCoordinationParser()
email_automation = EmailAutomationSystem()

# Convenience functions
def parse_coordination_email(content: str, subject: str) -> Dict[str, Any]:
    """Parse coordination email content"""
    return email_parser.parse_email_content(content, subject)

def process_email_message(email_msg: email.message.Message) -> Dict[str, Any]:
    """Process complete email message"""
    return email_automation.process_incoming_email(email_msg)

if __name__ == "__main__":
    # Test with sample email content
    test_content = """
    SYNC_REQUEST: willow -> hvscma_cmas
    Priority: high
    Environment: production
    Operation ID: 12345678-1234-1234-1234-123456789abc

    Please execute synchronization between systems.
    """

    result = parse_coordination_email(test_content, "Test Sync Request")
    print(json.dumps(result, indent=2))
