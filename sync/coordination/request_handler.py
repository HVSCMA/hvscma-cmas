#!/usr/bin/env python3
"""
HVSCMA Sync System - Request Handler
Processes and validates incoming sync requests
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
import jsonschema

class SyncRequestHandler:
    """Handles processing and validation of sync requests"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.schema_cache = {}

    def process_request(self, raw_request: str) -> Dict[str, Any]:
        """
        Process raw sync request and return validated request object

        Args:
            raw_request: JSON string containing sync request

        Returns:
            Processed and validated request dictionary

        Raises:
            ValueError: If request is invalid
        """
        try:
            # Parse JSON
            request = json.loads(raw_request)

            # Add sync_id if not present
            if "sync_id" not in request:
                request["sync_id"] = self._generate_sync_id()

            # Add timestamp if not present
            if "timestamp" not in request:
                request["timestamp"] = datetime.now().isoformat()

            # Validate request structure
            self._validate_request_structure(request)

            # Enrich request with defaults
            request = self._enrich_request(request)

            # Log processed request
            self.logger.info(f"Processed sync request: {request['sync_id']}")

            return request

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in request: {e}")
        except Exception as e:
            raise ValueError(f"Request processing failed: {e}")

    def _generate_sync_id(self) -> str:
        """Generate unique sync ID"""
        return f"sync_{uuid.uuid4().hex[:12]}"

    def _validate_request_structure(self, request: Dict[str, Any]) -> None:
        """Validate request against schema"""
        try:
            # Load schema if not cached
            if "sync_request" not in self.schema_cache:
                schema_path = self.config.get("validation", {}).get("schema_path", "sync/templates/sync_request_schema.json")
                with open(schema_path, 'r') as f:
                    self.schema_cache["sync_request"] = json.load(f)

            # Validate against schema
            jsonschema.validate(request, self.schema_cache["sync_request"])

        except FileNotFoundError:
            self.logger.warning("Schema file not found, skipping validation")
        except jsonschema.ValidationError as e:
            raise ValueError(f"Request validation failed: {e.message}")

    def _enrich_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich request with default values and computed fields"""

        # Set default priority if not specified
        if "priority" not in request:
            request["priority"] = "medium"

        # Set default validation settings
        if "validation" not in request:
            request["validation"] = {
                "required": True,
                "schemas": []
            }

        # Initialize metadata if not present
        if "metadata" not in request:
            request["metadata"] = {}

        # Add system metadata
        request["metadata"].update({
            "processed_at": datetime.now().isoformat(),
            "system_version": self.config.get("version", "1.0.0"),
            "environment": self.config.get("environment", "production")
        })

        # Enrich source information
        if "source" in request:
            request["source"] = self._enrich_source_config(request["source"])

        # Enrich target information  
        if "target" in request:
            request["target"] = self._enrich_target_config(request["target"])

        # Process operations
        if "operations" in request:
            request["operations"] = self._process_operations(request["operations"])

        return request

    def _enrich_source_config(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich source configuration with defaults"""

        # Set default branch
        if "branch" not in source:
            source["branch"] = self.config.get("github", {}).get("default_branch", "main")

        # Set default path
        if "path" not in source and source.get("type") != "external":
            source["path"] = "/"

        # Add authentication if needed
        if source.get("type") == "github" and "auth" not in source:
            source["auth"] = {
                "token": self.config.get("github", {}).get("token", "")
            }

        return source

    def _enrich_target_config(self, target: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich target configuration with defaults"""

        # Set default branch
        if "branch" not in target:
            target["branch"] = self.config.get("github", {}).get("default_branch", "main")

        # Set default path
        if "path" not in target:
            target["path"] = "/"

        # Add deployment configuration
        if target.get("type") == "netlify" and "config" not in target:
            target["config"] = {
                "site_id": self.config.get("netlify", {}).get("site_id", ""),
                "auth_token": self.config.get("netlify", {}).get("auth_token", ""),
                "build_command": self.config.get("netlify", {}).get("build_command", ""),
                "publish_directory": self.config.get("netlify", {}).get("publish_directory", "dist")
            }

        # Add GitHub configuration
        if target.get("type") == "github" and "auth" not in target:
            target["auth"] = {
                "token": self.config.get("github", {}).get("token", "")
            }

        return target

    def _process_operations(self, operations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and validate operations list"""

        processed_operations = []

        for i, operation in enumerate(operations):
            try:
                # Validate required fields
                if "action" not in operation:
                    raise ValueError(f"Operation {i}: missing required field 'action'")

                if "files" not in operation:
                    raise ValueError(f"Operation {i}: missing required field 'files'")

                # Validate action type
                valid_actions = ["create", "update", "delete", "sync"]
                if operation["action"] not in valid_actions:
                    raise ValueError(f"Operation {i}: invalid action '{operation['action']}', must be one of {valid_actions}")

                # Process file patterns
                operation["files"] = self._expand_file_patterns(operation["files"])

                # Add default options
                if "options" not in operation:
                    operation["options"] = {}

                # Add operation metadata
                operation["metadata"] = {
                    "operation_id": f"op_{i}_{uuid.uuid4().hex[:8]}",
                    "created_at": datetime.now().isoformat()
                }

                processed_operations.append(operation)

            except Exception as e:
                raise ValueError(f"Operation processing failed: {e}")

        return processed_operations

    def _expand_file_patterns(self, files: List[str]) -> List[str]:
        """Expand file patterns and globs into specific file lists"""

        expanded_files = []

        for file_pattern in files:
            # For now, just return as-is
            # In a full implementation, this would expand globs and patterns
            expanded_files.append(file_pattern)

        return expanded_files

    def create_request_from_template(self, template_name: str, **kwargs) -> Dict[str, Any]:
        """
        Create a sync request from a predefined template

        Args:
            template_name: Name of the template to use
            **kwargs: Template parameters

        Returns:
            Generated sync request dictionary
        """
        templates = {
            "github_to_netlify": {
                "sync_id": self._generate_sync_id(),
                "timestamp": datetime.now().isoformat(),
                "source": {
                    "type": "github",
                    "repository": kwargs.get("source_repo", ""),
                    "branch": kwargs.get("source_branch", "main"),
                    "path": kwargs.get("source_path", "/")
                },
                "target": {
                    "type": "netlify",
                    "repository": kwargs.get("target_repo", ""),
                    "path": kwargs.get("target_path", "/")
                },
                "operations": [
                    {
                        "action": "sync",
                        "files": kwargs.get("files", ["*"]),
                        "options": {}
                    }
                ],
                "priority": kwargs.get("priority", "medium"),
                "metadata": {
                    "template": template_name,
                    "requestor": kwargs.get("requestor", "system")
                }
            },
            "local_to_github": {
                "sync_id": self._generate_sync_id(),
                "timestamp": datetime.now().isoformat(),
                "source": {
                    "type": "local",
                    "repository": "local",
                    "path": kwargs.get("source_path", "/")
                },
                "target": {
                    "type": "github", 
                    "repository": kwargs.get("target_repo", ""),
                    "branch": kwargs.get("target_branch", "main"),
                    "path": kwargs.get("target_path", "/")
                },
                "operations": [
                    {
                        "action": kwargs.get("action", "update"),
                        "files": kwargs.get("files", []),
                        "options": {}
                    }
                ],
                "priority": kwargs.get("priority", "medium"),
                "metadata": {
                    "template": template_name,
                    "requestor": kwargs.get("requestor", "system")
                }
            }
        }

        if template_name not in templates:
            raise ValueError(f"Unknown template: {template_name}")

        return templates[template_name]

    def validate_request_completeness(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that a request has all necessary information for execution

        Args:
            request: Sync request to validate

        Returns:
            Validation result with success status and issues
        """
        issues = []

        # Check source configuration
        source = request.get("source", {})
        if source.get("type") == "github":
            if not source.get("repository"):
                issues.append("GitHub source missing repository")
            if not source.get("auth", {}).get("token"):
                issues.append("GitHub source missing authentication token")

        # Check target configuration  
        target = request.get("target", {})
        if target.get("type") == "github":
            if not target.get("repository"):
                issues.append("GitHub target missing repository")
            if not target.get("auth", {}).get("token"):
                issues.append("GitHub target missing authentication token")
        elif target.get("type") == "netlify":
            if not target.get("config", {}).get("site_id"):
                issues.append("Netlify target missing site_id")
            if not target.get("config", {}).get("auth_token"):
                issues.append("Netlify target missing auth_token")

        # Check operations
        operations = request.get("operations", [])
        if not operations:
            issues.append("No operations specified")

        for i, op in enumerate(operations):
            if not op.get("files"):
                issues.append(f"Operation {i}: no files specified")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "checked_at": datetime.now().isoformat()
        }
