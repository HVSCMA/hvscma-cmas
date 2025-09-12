#!/usr/bin/env python3
"""
HVSCMA Sync System - Status Manager
Manages sync operation status and progress tracking
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import threading
import time

class SyncStatus(Enum):
    """Sync operation status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VALIDATING = "validating"
    SYNCING = "syncing"
    DEPLOYING = "deploying"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ERROR = "error"

class SyncStatusManager:
    """Manages status tracking and reporting for sync operations"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # In-memory status storage (in production, use database)
        self.status_store = {}
        self.status_history = {}

        # Thread safety
        self._lock = threading.Lock()

        # Auto-cleanup configuration
        self.max_history_days = config.get("status", {}).get("max_history_days", 30)
        self.cleanup_interval = config.get("status", {}).get("cleanup_interval_hours", 24)

        # Start background cleanup task
        self._start_cleanup_task()

    def create_status_entry(self, sync_id: str, initial_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create initial status entry for sync operation

        Args:
            sync_id: Unique sync operation ID
            initial_request: Initial sync request

        Returns:
            Created status entry
        """
        with self._lock:
            now = datetime.now()

            status_entry = {
                "sync_id": sync_id,
                "status": SyncStatus.PENDING.value,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "progress": {
                    "stage": "initialization",
                    "percentage": 0,
                    "current_step": "Request received",
                    "total_steps": 0,
                    "completed_steps": 0
                },
                "timing": {
                    "start_time": None,
                    "end_time": None,
                    "stage_times": {},
                    "total_duration": 0
                },
                "results": {
                    "files_processed": 0,
                    "files_created": 0,
                    "files_updated": 0,
                    "files_deleted": 0,
                    "errors": [],
                    "warnings": []
                },
                "metadata": {
                    "priority": initial_request.get("priority", "medium"),
                    "requestor": initial_request.get("metadata", {}).get("requestor", "unknown"),
                    "source_type": initial_request.get("source", {}).get("type"),
                    "target_type": initial_request.get("target", {}).get("type"),
                    "operations_count": len(initial_request.get("operations", []))
                }
            }

            self.status_store[sync_id] = status_entry

            # Initialize history
            self.status_history[sync_id] = [{
                "timestamp": now.isoformat(),
                "status": SyncStatus.PENDING.value,
                "message": "Sync request received"
            }]

            self.logger.info(f"Created status entry for sync: {sync_id}")
            return status_entry.copy()

    def update_status(self, sync_id: str, new_status: str, 
                     message: Optional[str] = None, 
                     progress_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update sync operation status

        Args:
            sync_id: Sync operation ID
            new_status: New status value
            message: Optional status message
            progress_data: Optional progress information

        Returns:
            True if update was successful
        """
        with self._lock:
            if sync_id not in self.status_store:
                self.logger.error(f"Status entry not found for sync: {sync_id}")
                return False

            now = datetime.now()
            entry = self.status_store[sync_id]

            # Validate status transition
            if not self._is_valid_status_transition(entry["status"], new_status):
                self.logger.warning(f"Invalid status transition for {sync_id}: {entry['status']} -> {new_status}")
                return False

            # Update status
            old_status = entry["status"]
            entry["status"] = new_status
            entry["updated_at"] = now.isoformat()

            # Update timing information
            if new_status == SyncStatus.IN_PROGRESS.value and not entry["timing"]["start_time"]:
                entry["timing"]["start_time"] = now.isoformat()

            if new_status in [SyncStatus.SUCCESS.value, SyncStatus.FAILED.value, 
                             SyncStatus.ERROR.value, SyncStatus.CANCELLED.value]:
                entry["timing"]["end_time"] = now.isoformat()
                if entry["timing"]["start_time"]:
                    start_time = datetime.fromisoformat(entry["timing"]["start_time"])
                    entry["timing"]["total_duration"] = (now - start_time).total_seconds()

            # Update progress data
            if progress_data:
                entry["progress"].update(progress_data)

                # Auto-calculate percentage if steps provided
                if "completed_steps" in progress_data and "total_steps" in progress_data:
                    total = progress_data["total_steps"]
                    completed = progress_data["completed_steps"]
                    if total > 0:
                        entry["progress"]["percentage"] = min(100, (completed / total) * 100)

            # Add to history
            if sync_id not in self.status_history:
                self.status_history[sync_id] = []

            self.status_history[sync_id].append({
                "timestamp": now.isoformat(),
                "status": new_status,
                "message": message or f"Status changed to {new_status}",
                "progress_snapshot": entry["progress"].copy()
            })

            self.logger.info(f"Updated status for {sync_id}: {old_status} -> {new_status}")
            return True

    def update_progress(self, sync_id: str, stage: str, percentage: Optional[int] = None,
                       current_step: Optional[str] = None, 
                       completed_steps: Optional[int] = None,
                       total_steps: Optional[int] = None) -> bool:
        """
        Update progress information for sync operation

        Args:
            sync_id: Sync operation ID
            stage: Current stage name
            percentage: Progress percentage (0-100)
            current_step: Current step description
            completed_steps: Number of completed steps
            total_steps: Total number of steps

        Returns:
            True if update was successful
        """
        progress_data = {"stage": stage}

        if percentage is not None:
            progress_data["percentage"] = max(0, min(100, percentage))

        if current_step is not None:
            progress_data["current_step"] = current_step

        if completed_steps is not None:
            progress_data["completed_steps"] = completed_steps

        if total_steps is not None:
            progress_data["total_steps"] = total_steps

        return self.update_status(sync_id, None, 
                                f"Progress update: {stage}", progress_data)

    def update_results(self, sync_id: str, results_data: Dict[str, Any]) -> bool:
        """
        Update results information for sync operation

        Args:
            sync_id: Sync operation ID
            results_data: Results data to update

        Returns:
            True if update was successful
        """
        with self._lock:
            if sync_id not in self.status_store:
                return False

            entry = self.status_store[sync_id]
            entry["results"].update(results_data)
            entry["updated_at"] = datetime.now().isoformat()

            return True

    def add_error(self, sync_id: str, error_message: str, error_details: Optional[Dict] = None) -> bool:
        """
        Add error to sync operation

        Args:
            sync_id: Sync operation ID
            error_message: Error message
            error_details: Optional error details

        Returns:
            True if error was added
        """
        with self._lock:
            if sync_id not in self.status_store:
                return False

            error_entry = {
                "timestamp": datetime.now().isoformat(),
                "message": error_message,
                "details": error_details or {}
            }

            self.status_store[sync_id]["results"]["errors"].append(error_entry)
            self.status_store[sync_id]["updated_at"] = datetime.now().isoformat()

            return True

    def add_warning(self, sync_id: str, warning_message: str, warning_details: Optional[Dict] = None) -> bool:
        """
        Add warning to sync operation

        Args:
            sync_id: Sync operation ID
            warning_message: Warning message
            warning_details: Optional warning details

        Returns:
            True if warning was added
        """
        with self._lock:
            if sync_id not in self.status_store:
                return False

            warning_entry = {
                "timestamp": datetime.now().isoformat(),
                "message": warning_message,
                "details": warning_details or {}
            }

            self.status_store[sync_id]["results"]["warnings"].append(warning_entry)
            self.status_store[sync_id]["updated_at"] = datetime.now().isoformat()

            return True

    def get_status(self, sync_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current status for sync operation

        Args:
            sync_id: Sync operation ID

        Returns:
            Status entry or None if not found
        """
        with self._lock:
            return self.status_store.get(sync_id, {}).copy() if sync_id in self.status_store else None

    def get_status_history(self, sync_id: str) -> List[Dict[str, Any]]:
        """
        Get status history for sync operation

        Args:
            sync_id: Sync operation ID

        Returns:
            List of status history entries
        """
        with self._lock:
            return self.status_history.get(sync_id, []).copy()

    def list_active_syncs(self) -> List[Dict[str, Any]]:
        """
        Get list of currently active sync operations

        Returns:
            List of active sync status entries
        """
        active_statuses = [SyncStatus.PENDING.value, SyncStatus.IN_PROGRESS.value, 
                          SyncStatus.VALIDATING.value, SyncStatus.SYNCING.value, 
                          SyncStatus.DEPLOYING.value]

        with self._lock:
            return [entry.copy() for entry in self.status_store.values() 
                   if entry["status"] in active_statuses]

    def list_recent_syncs(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get list of sync operations from recent hours

        Args:
            hours: Number of hours to look back

        Returns:
            List of recent sync status entries
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        with self._lock:
            return [entry.copy() for entry in self.status_store.values()
                   if datetime.fromisoformat(entry["created_at"]) >= cutoff_time]

    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Get summary statistics for sync operations

        Returns:
            Summary statistics dictionary
        """
        with self._lock:
            total_syncs = len(self.status_store)

            if total_syncs == 0:
                return {"total_syncs": 0}

            status_counts = {}
            for entry in self.status_store.values():
                status = entry["status"]
                status_counts[status] = status_counts.get(status, 0) + 1

            # Calculate success rate
            success_count = status_counts.get(SyncStatus.SUCCESS.value, 0)
            completed_count = success_count + status_counts.get(SyncStatus.FAILED.value, 0) + \
                            status_counts.get(SyncStatus.ERROR.value, 0)

            success_rate = (success_count / completed_count * 100) if completed_count > 0 else 0

            # Recent activity (last 24 hours)
            recent_syncs = self.list_recent_syncs(24)

            return {
                "total_syncs": total_syncs,
                "status_breakdown": status_counts,
                "success_rate_percent": round(success_rate, 2),
                "recent_activity_24h": len(recent_syncs),
                "active_syncs": len(self.list_active_syncs())
            }

    def _is_valid_status_transition(self, current_status: str, new_status: str) -> bool:
        """Validate if status transition is allowed"""
        if current_status == new_status:
            return True

        # Define valid transitions
        valid_transitions = {
            SyncStatus.PENDING.value: [SyncStatus.IN_PROGRESS.value, SyncStatus.CANCELLED.value],
            SyncStatus.IN_PROGRESS.value: [SyncStatus.VALIDATING.value, SyncStatus.FAILED.value, 
                                         SyncStatus.ERROR.value, SyncStatus.CANCELLED.value],
            SyncStatus.VALIDATING.value: [SyncStatus.SYNCING.value, SyncStatus.FAILED.value, 
                                        SyncStatus.ERROR.value],
            SyncStatus.SYNCING.value: [SyncStatus.DEPLOYING.value, SyncStatus.FAILED.value, 
                                     SyncStatus.ERROR.value],
            SyncStatus.DEPLOYING.value: [SyncStatus.SUCCESS.value, SyncStatus.FAILED.value, 
                                       SyncStatus.ERROR.value],
            # Terminal states generally don't transition
            SyncStatus.SUCCESS.value: [],
            SyncStatus.FAILED.value: [SyncStatus.PENDING.value],  # Allow retry
            SyncStatus.ERROR.value: [SyncStatus.PENDING.value],   # Allow retry
            SyncStatus.CANCELLED.value: [SyncStatus.PENDING.value]  # Allow restart
        }

        return new_status in valid_transitions.get(current_status, [])

    def _start_cleanup_task(self):
        """Start background task for cleaning up old status entries"""
        def cleanup_worker():
            while True:
                try:
                    self._cleanup_old_entries()
                    time.sleep(self.cleanup_interval * 3600)  # Convert hours to seconds
                except Exception as e:
                    self.logger.error(f"Status cleanup error: {e}")
                    time.sleep(3600)  # Wait 1 hour before retrying

        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()

    def _cleanup_old_entries(self):
        """Clean up old status entries based on configuration"""
        cutoff_date = datetime.now() - timedelta(days=self.max_history_days)

        with self._lock:
            sync_ids_to_remove = []

            for sync_id, entry in self.status_store.items():
                # Only remove completed syncs older than cutoff
                if entry["status"] in [SyncStatus.SUCCESS.value, SyncStatus.FAILED.value, 
                                     SyncStatus.ERROR.value, SyncStatus.CANCELLED.value]:
                    if datetime.fromisoformat(entry["created_at"]) < cutoff_date:
                        sync_ids_to_remove.append(sync_id)

            # Remove old entries
            for sync_id in sync_ids_to_remove:
                del self.status_store[sync_id]
                if sync_id in self.status_history:
                    del self.status_history[sync_id]

            if sync_ids_to_remove:
                self.logger.info(f"Cleaned up {len(sync_ids_to_remove)} old status entries")
