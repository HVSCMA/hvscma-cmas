#!/usr/bin/env python3
"""
WILLOW Data Processing Automation
Automated data processing and sync coordination
"""

import json
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import sqlite3
from dataclasses import dataclass
import hashlib

@dataclass
class ProcessingTask:
    """Data processing task definition."""
    task_id: str
    task_type: str
    source_data: Any
    target_format: str
    priority: int = 5
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

class DataProcessor:
    """Automated data processing engine for WILLOW sync system."""

    def __init__(self, db_path: str = "sync/data/processing.db"):
        self.db_path = db_path
        self.logger = self._setup_logging()
        self.processing_queue = []
        self.active_tasks = {}
        self._init_database()

    def _setup_logging(self):
        """Setup logging for data processor."""
        logger = logging.getLogger('DataProcessor')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _init_database(self):
        """Initialize processing database."""
        try:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS processing_tasks (
                        task_id TEXT PRIMARY KEY,
                        task_type TEXT NOT NULL,
                        status TEXT DEFAULT 'pending',
                        created_at TIMESTAMP,
                        started_at TIMESTAMP,
                        completed_at TIMESTAMP,
                        data_hash TEXT,
                        result_path TEXT,
                        error_message TEXT
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS sync_metrics (
                        timestamp TIMESTAMP PRIMARY KEY,
                        processed_tasks INTEGER,
                        failed_tasks INTEGER,
                        avg_processing_time REAL,
                        data_volume_mb REAL
                    )
                """)

            self.logger.info("Processing database initialized")

        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")

    async def start_processing_loop(self):
        """Start the main processing loop."""
        self.logger.info("Starting automated data processing loop")

        while True:
            try:
                await self.process_pending_tasks()
                await self.update_metrics()
                await self.cleanup_old_tasks()

                await asyncio.sleep(30)

            except Exception as e:
                self.logger.error(f"Processing loop error: {e}")
                await asyncio.sleep(5)

    async def process_pending_tasks(self):
        """Process all pending tasks in queue."""
        if not self.processing_queue:
            return

        self.processing_queue.sort(key=lambda x: x.priority)

        tasks_to_process = []
        while self.processing_queue and len(tasks_to_process) < 5:
            task = self.processing_queue.pop(0)
            tasks_to_process.append(task)

        if tasks_to_process:
            await asyncio.gather(
                *[self.process_task(task) for task in tasks_to_process],
                return_exceptions=True
            )

    async def process_task(self, task: ProcessingTask):
        """Process individual data processing task."""
        try:
            self.active_tasks[task.task_id] = task
            start_time = datetime.now(timezone.utc)

            self._update_task_status(task.task_id, 'processing', started_at=start_time)

            self.logger.info(f"Processing task {task.task_id} ({task.task_type})")

            result = await self._route_task(task)

            if result:
                end_time = datetime.now(timezone.utc)
                processing_time = (end_time - start_time).total_seconds()

                self._update_task_status(
                    task.task_id, 
                    'completed', 
                    completed_at=end_time,
                    result_path=result.get('output_path')
                )

                self.logger.info(f"Task {task.task_id} completed in {processing_time:.2f}s")
            else:
                self._update_task_status(task.task_id, 'failed', error_message="Processing returned no result")

        except Exception as e:
            self.logger.error(f"Task {task.task_id} failed: {e}")
            self._update_task_status(task.task_id, 'failed', error_message=str(e))

        finally:
            self.active_tasks.pop(task.task_id, None)

    async def _route_task(self, task: ProcessingTask) -> Optional[Dict]:
        """Route task to appropriate processing method."""
        if task.task_type == 'json_processing':
            return await self._process_json_data(task)
        elif task.task_type == 'sync_coordination':
            return await self._process_sync_data(task)
        else:
            self.logger.warning(f"Unknown task type: {task.task_type}")
            return None

    async def _process_json_data(self, task: ProcessingTask) -> Dict:
        """Process JSON data with schema validation."""
        try:
            if isinstance(task.source_data, str):
                with open(task.source_data, 'r') as f:
                    data = json.load(f)
            else:
                data = task.source_data

            if not isinstance(data, (dict, list)):
                raise ValueError("Invalid JSON structure")

            processed_data = self._flatten_json(data)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"sync/processed/json_{task.task_id}_{timestamp}.json"

            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w') as f:
                json.dump(processed_data, f, indent=2, default=str)

            return {
                'output_path': output_path,
                'records_processed': len(processed_data) if isinstance(processed_data, list) else 1,
                'data_hash': self._calculate_data_hash(json.dumps(processed_data, sort_keys=True))
            }

        except Exception as e:
            raise Exception(f"JSON processing failed: {e}")

    async def _process_sync_data(self, task: ProcessingTask) -> Dict:
        """Process sync coordination data."""
        try:
            data = task.source_data

            required_fields = ['message_id', 'from_agent', 'message_type', 'timestamp']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")

            processed_sync = {
                'message_id': data['message_id'],
                'from_agent': data['from_agent'],
                'to_agents': data.get('to_agents', []),
                'message_type': data['message_type'],
                'payload': data.get('payload', {}),
                'timestamp': data['timestamp'],
                'processed_at': datetime.now(timezone.utc).isoformat(),
                'priority': data.get('priority', 'normal')
            }

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"sync/processed/sync_{task.task_id}_{timestamp}.json"

            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w') as f:
                json.dump(processed_sync, f, indent=2)

            return {
                'output_path': output_path,
                'message_id': processed_sync['message_id'],
                'from_agent': processed_sync['from_agent'],
                'message_type': processed_sync['message_type']
            }

        except Exception as e:
            raise Exception(f"Sync processing failed: {e}")

    def _flatten_json(self, data: Any, parent_key: str = '', sep: str = '.') -> Dict:
        """Flatten nested JSON structure."""
        items = []

        if isinstance(data, dict):
            for k, v in data.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                items.extend(self._flatten_json(v, new_key, sep=sep).items())
        elif isinstance(data, list):
            for i, v in enumerate(data):
                new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
                items.extend(self._flatten_json(v, new_key, sep=sep).items())
        else:
            return {parent_key: data}

        return dict(items)

    def _calculate_data_hash(self, data: str) -> str:
        """Calculate hash of data for integrity checking."""
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def _update_task_status(self, task_id: str, status: str, **kwargs):
        """Update task status in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                update_fields = []
                values = []

                update_fields.append("status = ?")
                values.append(status)

                for field, value in kwargs.items():
                    if value is not None:
                        update_fields.append(f"{field} = ?")
                        values.append(value)

                values.append(task_id)

                query = f"UPDATE processing_tasks SET {', '.join(update_fields)} WHERE task_id = ?"
                conn.execute(query, values)

        except Exception as e:
            self.logger.error(f"Status update failed: {e}")

    async def update_metrics(self):
        """Update processing metrics."""
        try:
            current_time = datetime.now(timezone.utc)

            with sqlite3.connect(self.db_path) as conn:
                one_hour_ago = current_time - timedelta(hours=1)

                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_tasks,
                        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_tasks,
                        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_tasks,
                        AVG(CASE WHEN completed_at IS NOT NULL AND started_at IS NOT NULL 
                            THEN (julianday(completed_at) - julianday(started_at)) * 24 * 3600 
                            ELSE NULL END) as avg_processing_time
                    FROM processing_tasks 
                    WHERE created_at >= ?
                """, (one_hour_ago,))

                result = cursor.fetchone()

                if result and result[0] > 0:
                    conn.execute("""
                        INSERT OR REPLACE INTO sync_metrics 
                        (timestamp, processed_tasks, failed_tasks, avg_processing_time, data_volume_mb)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        current_time,
                        result[1],
                        result[2],
                        result[3] or 0,
                        0
                    ))

        except Exception as e:
            self.logger.error(f"Metrics update failed: {e}")

    async def cleanup_old_tasks(self):
        """Cleanup old completed tasks."""
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "DELETE FROM processing_tasks WHERE completed_at < ? AND status = 'completed'",
                    (cutoff_date,)
                )

                if cursor.rowcount > 0:
                    self.logger.info(f"Cleaned up {cursor.rowcount} old tasks")

        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")

    def add_task(self, task: ProcessingTask):
        """Add task to processing queue."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO processing_tasks (task_id, task_type, created_at, data_hash)
                    VALUES (?, ?, ?, ?)
                """, (
                    task.task_id,
                    task.task_type,
                    task.created_at,
                    self._calculate_data_hash(str(task.source_data))
                ))

            self.processing_queue.append(task)
            self.logger.info(f"Added task {task.task_id} to processing queue")

        except Exception as e:
            self.logger.error(f"Failed to add task: {e}")

def main():
    """Main entry point for data processor."""
    processor = DataProcessor()

    try:
        asyncio.run(processor.start_processing_loop())
    except KeyboardInterrupt:
        processor.logger.info("Data processor shutdown requested")

if __name__ == "__main__":
    main()
