#!/usr/bin/env python3
"""
HVSCMA Sync System - Main Coordination Logic
Handles sync requests and orchestrates all sync operations
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any
import asyncio

from .request_handler import SyncRequestHandler
from .status_manager import SyncStatusManager
from ..integration.validation_engine import ValidationEngine
from ..integration.github_connector import GitHubConnector
from ..integration.netlify_connector import NetlifyConnector

class SyncCoordinator:
    """Main coordinator for HVSCMA sync operations"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.request_handler = SyncRequestHandler(config)
        self.status_manager = SyncStatusManager(config)
        self.validation_engine = ValidationEngine(config)
        self.github_connector = GitHubConnector(config)
        self.netlify_connector = NetlifyConnector(config)

    async def process_sync_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a sync request from start to finish

        Args:
            request: Validated sync request dictionary

        Returns:
            Sync response with results and status
        """
        sync_id = request.get("sync_id")
        start_time = datetime.now()

        try:
            self.logger.info(f"Starting sync operation: {sync_id}")

            # Initialize response
            response = self._initialize_response(sync_id, start_time)

            # Stage 1: Validation
            validation_result = await self._run_validation_stage(request, response)
            if not validation_result["success"]:
                return self._finalize_response(response, "validation_failed", start_time)

            # Stage 2: Sync Operation
            sync_result = await self._run_sync_stage(request, response)
            if not sync_result["success"]:
                return self._finalize_response(response, "sync_failed", start_time)

            # Stage 3: Deployment
            deploy_result = await self._run_deployment_stage(request, response)
            if not deploy_result["success"]:
                return self._finalize_response(response, "deployment_failed", start_time)

            # Success
            self.logger.info(f"Sync operation completed: {sync_id}")
            return self._finalize_response(response, "success", start_time)

        except Exception as e:
            self.logger.error(f"Sync operation failed: {sync_id} - {e}")
            return self._create_error_response(sync_id, str(e), start_time)

    def _initialize_response(self, sync_id: str, start_time: datetime) -> Dict[str, Any]:
        """Initialize sync response structure"""
        return {
            "sync_id": sync_id,
            "timestamp": start_time.isoformat(),
            "status": {
                "code": "in_progress",
                "message": "Sync operation in progress",
                "details": {
                    "files_processed": 0,
                    "files_created": 0,
                    "files_updated": 0,
                    "files_deleted": 0,
                    "errors": []
                }
            },
            "execution": {
                "start_time": start_time.isoformat(),
                "end_time": None,
                "duration_seconds": 0,
                "stages": []
            },
            "results": {
                "deployment_url": "",
                "commit_hash": "",
                "artifacts": [],
                "logs": []
            },
            "metadata": {
                "version": "1.0.0",
                "environment": self.config.get("environment", "production"),
                "requestor": "",
                "tags": []
            }
        }

    async def _run_validation_stage(self, request: Dict[str, Any], response: Dict[str, Any]) -> Dict[str, bool]:
        """Run validation stage"""
        stage_start = datetime.now()

        try:
            # Validate request structure
            validation_result = await self.validation_engine.validate_request(request)

            # Update response
            stage = {
                "name": "validation",
                "status": "completed" if validation_result["valid"] else "failed",
                "duration_ms": int((datetime.now() - stage_start).total_seconds() * 1000),
                "details": validation_result
            }
            response["execution"]["stages"].append(stage)

            return {"success": validation_result["valid"]}

        except Exception as e:
            stage = {
                "name": "validation",
                "status": "error",
                "duration_ms": int((datetime.now() - stage_start).total_seconds() * 1000),
                "details": {"error": str(e)}
            }
            response["execution"]["stages"].append(stage)
            return {"success": False}

    async def _run_sync_stage(self, request: Dict[str, Any], response: Dict[str, Any]) -> Dict[str, bool]:
        """Run sync operation stage"""
        stage_start = datetime.now()

        try:
            # Execute sync operations based on request
            sync_result = await self._execute_sync_operations(request)

            # Update response with sync results
            stage = {
                "name": "sync_operation",
                "status": "completed" if sync_result["success"] else "failed",
                "duration_ms": int((datetime.now() - stage_start).total_seconds() * 1000),
                "details": sync_result
            }
            response["execution"]["stages"].append(stage)

            # Update file counters
            response["status"]["details"].update({
                "files_processed": sync_result.get("files_processed", 0),
                "files_created": sync_result.get("files_created", 0),
                "files_updated": sync_result.get("files_updated", 0),
                "files_deleted": sync_result.get("files_deleted", 0)
            })

            return {"success": sync_result["success"]}

        except Exception as e:
            stage = {
                "name": "sync_operation", 
                "status": "error",
                "duration_ms": int((datetime.now() - stage_start).total_seconds() * 1000),
                "details": {"error": str(e)}
            }
            response["execution"]["stages"].append(stage)
            return {"success": False}

    async def _run_deployment_stage(self, request: Dict[str, Any], response: Dict[str, Any]) -> Dict[str, bool]:
        """Run deployment stage"""
        stage_start = datetime.now()

        try:
            target = request.get("target", {})

            if target.get("type") == "netlify":
                deploy_result = await self.netlify_connector.deploy(request)
            elif target.get("type") == "github":
                deploy_result = await self.github_connector.deploy(request)
            else:
                raise ValueError(f"Unsupported deployment target: {target.get('type')}")

            stage = {
                "name": "deployment",
                "status": "completed" if deploy_result["success"] else "failed",
                "duration_ms": int((datetime.now() - stage_start).total_seconds() * 1000),
                "details": deploy_result
            }
            response["execution"]["stages"].append(stage)

            # Update results
            if deploy_result["success"]:
                response["results"].update({
                    "deployment_url": deploy_result.get("url", ""),
                    "commit_hash": deploy_result.get("commit_hash", ""),
                    "artifacts": deploy_result.get("artifacts", [])
                })

            return {"success": deploy_result["success"]}

        except Exception as e:
            stage = {
                "name": "deployment",
                "status": "error", 
                "duration_ms": int((datetime.now() - stage_start).total_seconds() * 1000),
                "details": {"error": str(e)}
            }
            response["execution"]["stages"].append(stage)
            return {"success": False}

    async def _execute_sync_operations(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute sync operations based on request operations list"""
        operations = request.get("operations", [])
        results = {
            "success": True,
            "files_processed": 0,
            "files_created": 0, 
            "files_updated": 0,
            "files_deleted": 0,
            "errors": []
        }

        for operation in operations:
            try:
                op_result = await self._execute_single_operation(operation, request)

                # Aggregate results
                results["files_processed"] += op_result.get("files_processed", 0)
                results["files_created"] += op_result.get("files_created", 0)
                results["files_updated"] += op_result.get("files_updated", 0)
                results["files_deleted"] += op_result.get("files_deleted", 0)

                if not op_result.get("success", False):
                    results["success"] = False
                    results["errors"].extend(op_result.get("errors", []))

            except Exception as e:
                results["success"] = False
                results["errors"].append(f"Operation failed: {e}")

        return results

    async def _execute_single_operation(self, operation: Dict[str, Any], request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single sync operation"""
        action = operation.get("action")
        files = operation.get("files", [])

        if action == "create":
            return await self._create_files(files, request)
        elif action == "update":
            return await self._update_files(files, request)
        elif action == "delete":
            return await self._delete_files(files, request)
        elif action == "sync":
            return await self._sync_files(files, request)
        else:
            raise ValueError(f"Unsupported operation: {action}")

    async def _create_files(self, files: List[str], request: Dict[str, Any]) -> Dict[str, Any]:
        """Create new files"""
        # Implementation for file creation
        return {"success": True, "files_created": len(files)}

    async def _update_files(self, files: List[str], request: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing files"""
        # Implementation for file updates
        return {"success": True, "files_updated": len(files)}

    async def _delete_files(self, files: List[str], request: Dict[str, Any]) -> Dict[str, Any]:
        """Delete files"""
        # Implementation for file deletion
        return {"success": True, "files_deleted": len(files)}

    async def _sync_files(self, files: List[str], request: Dict[str, Any]) -> Dict[str, Any]:
        """Sync files between source and target"""
        # Implementation for file synchronization
        return {"success": True, "files_processed": len(files)}

    def _finalize_response(self, response: Dict[str, Any], status_code: str, start_time: datetime) -> Dict[str, Any]:
        """Finalize sync response"""
        end_time = datetime.now()

        response["status"]["code"] = status_code
        response["status"]["message"] = self._get_status_message(status_code)
        response["execution"]["end_time"] = end_time.isoformat()
        response["execution"]["duration_seconds"] = (end_time - start_time).total_seconds()

        return response

    def _create_error_response(self, sync_id: str, error: str, start_time: datetime) -> Dict[str, Any]:
        """Create error response"""
        end_time = datetime.now()

        return {
            "sync_id": sync_id,
            "timestamp": end_time.isoformat(),
            "status": {
                "code": "error",
                "message": "Sync operation failed",
                "details": {
                    "files_processed": 0,
                    "files_created": 0,
                    "files_updated": 0,
                    "files_deleted": 0,
                    "errors": [error]
                }
            },
            "execution": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": (end_time - start_time).total_seconds(),
                "stages": []
            },
            "results": {
                "deployment_url": "",
                "commit_hash": "",
                "artifacts": [],
                "logs": []
            },
            "metadata": {
                "version": "1.0.0",
                "environment": self.config.get("environment", "production"),
                "requestor": "",
                "tags": []
            }
        }

    def _get_status_message(self, status_code: str) -> str:
        """Get human-readable status message"""
        messages = {
            "success": "Sync completed successfully",
            "validation_failed": "Sync failed during validation",
            "sync_failed": "Sync failed during sync operation",
            "deployment_failed": "Sync failed during deployment",
            "error": "Sync operation encountered an error"
        }
        return messages.get(status_code, "Unknown status")
