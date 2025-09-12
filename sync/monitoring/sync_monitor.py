"""
WILLOW Sync System - Real-time Monitoring
Provides comprehensive monitoring and alerting for sync operations
"""

import json
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import requests

@dataclass
class SystemMetrics:
    """System performance and health metrics"""
    cpu_usage: float
    memory_usage: float
    active_connections: int
    requests_per_minute: float
    error_count: int
    last_sync_time: Optional[datetime]
    sync_queue_size: int

class WillowSyncMonitor:
    """Real-time monitoring system for WILLOW sync operations"""

    def __init__(self, config_path: str = "sync_protocol.json"):
        """Initialize monitoring system"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.logger = logging.getLogger("willow_sync_monitor")
        self.is_monitoring = False
        self.metrics_history = []
        self.alert_thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "error_rate": 5.0,
            "sync_latency_ms": 1000,
            "queue_size": 100
        }
        self.alert_callbacks = []

    def start_monitoring(self, interval_seconds: int = 30):
        """Start continuous monitoring"""
        self.is_monitoring = True
        self.logger.info("Starting WILLOW sync monitoring")

        def monitor_loop():
            while self.is_monitoring:
                try:
                    metrics = self.collect_metrics()
                    self.analyze_metrics(metrics)
                    self.metrics_history.append({
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "metrics": metrics.__dict__
                    })

                    # Keep only last 24 hours of metrics
                    cutoff_time = datetime.utcnow() - timedelta(hours=24)
                    self.metrics_history = [
                        m for m in self.metrics_history 
                        if datetime.fromisoformat(m["timestamp"].replace("Z", "")) > cutoff_time
                    ]

                    time.sleep(interval_seconds)

                except Exception as e:
                    self.logger.error(f"Monitoring error: {e}")
                    time.sleep(interval_seconds)

        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        self.logger.info("Stopped WILLOW sync monitoring")

    def collect_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        # In production, this would collect real metrics
        # For now, simulate realistic metrics
        import random

        base_time = datetime.utcnow()

        return SystemMetrics(
            cpu_usage=random.uniform(20.0, 75.0),
            memory_usage=random.uniform(30.0, 70.0),
            active_connections=random.randint(5, 50),
            requests_per_minute=random.uniform(10.0, 200.0),
            error_count=random.randint(0, 3),
            last_sync_time=base_time - timedelta(seconds=random.randint(1, 120)),
            sync_queue_size=random.randint(0, 25)
        )

    def analyze_metrics(self, metrics: SystemMetrics):
        """Analyze metrics and trigger alerts if needed"""
        alerts = []

        if metrics.cpu_usage > self.alert_thresholds["cpu_usage"]:
            alerts.append({
                "severity": "warning",
                "type": "high_cpu",
                "message": f"CPU usage {metrics.cpu_usage:.1f}% exceeds threshold {self.alert_thresholds['cpu_usage']:.1f}%",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })

        if metrics.memory_usage > self.alert_thresholds["memory_usage"]:
            alerts.append({
                "severity": "warning", 
                "type": "high_memory",
                "message": f"Memory usage {metrics.memory_usage:.1f}% exceeds threshold {self.alert_thresholds['memory_usage']:.1f}%",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })

        if metrics.sync_queue_size > self.alert_thresholds["queue_size"]:
            alerts.append({
                "severity": "critical",
                "type": "queue_backlog",
                "message": f"Sync queue size {metrics.sync_queue_size} exceeds threshold {self.alert_thresholds['queue_size']}",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })

        # Check sync freshness
        if metrics.last_sync_time:
            sync_age = (datetime.utcnow() - metrics.last_sync_time).total_seconds()
            if sync_age > 300:  # 5 minutes
                alerts.append({
                    "severity": "critical",
                    "type": "sync_stale",
                    "message": f"Last sync was {sync_age:.0f} seconds ago - potential sync failure",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                })

        # Trigger alert callbacks
        for alert in alerts:
            self._trigger_alert(alert)

    def _trigger_alert(self, alert: Dict[str, Any]):
        """Trigger alert through configured channels"""
        self.logger.warning(f"ALERT: {alert['message']}")

        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Alert callback failed: {e}")

    def add_alert_callback(self, callback):
        """Add alert callback function"""
        self.alert_callbacks.append(callback)

    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status summary"""
        if not self.metrics_history:
            return {"status": "no_data", "message": "No metrics available"}

        latest_metrics = self.metrics_history[-1]["metrics"]

        # Determine overall health
        health_score = 100.0
        health_issues = []

        if latest_metrics["cpu_usage"] > self.alert_thresholds["cpu_usage"]:
            health_score -= 20
            health_issues.append("high_cpu")

        if latest_metrics["memory_usage"] > self.alert_thresholds["memory_usage"]:
            health_score -= 20
            health_issues.append("high_memory")

        if latest_metrics["sync_queue_size"] > self.alert_thresholds["queue_size"]:
            health_score -= 30
            health_issues.append("queue_backlog")

        if latest_metrics["error_count"] > 0:
            health_score -= latest_metrics["error_count"] * 5
            health_issues.append("sync_errors")

        # Determine status
        if health_score >= 90:
            status = "healthy"
        elif health_score >= 70:
            status = "degraded"
        elif health_score >= 50:
            status = "warning"
        else:
            status = "critical"

        return {
            "status": status,
            "health_score": max(0, health_score),
            "issues": health_issues,
            "metrics": latest_metrics,
            "last_updated": self.metrics_history[-1]["timestamp"],
            "monitoring_active": self.is_monitoring
        }

    def get_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate performance report for specified time period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        relevant_metrics = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m["timestamp"].replace("Z", "")) > cutoff_time
        ]

        if not relevant_metrics:
            return {"error": "No metrics available for specified time period"}

        # Calculate averages and trends
        cpu_values = [m["metrics"]["cpu_usage"] for m in relevant_metrics]
        memory_values = [m["metrics"]["memory_usage"] for m in relevant_metrics]
        request_values = [m["metrics"]["requests_per_minute"] for m in relevant_metrics]
        error_values = [m["metrics"]["error_count"] for m in relevant_metrics]

        return {
            "time_period_hours": hours,
            "data_points": len(relevant_metrics),
            "averages": {
                "cpu_usage": sum(cpu_values) / len(cpu_values),
                "memory_usage": sum(memory_values) / len(memory_values),
                "requests_per_minute": sum(request_values) / len(request_values),
                "total_errors": sum(error_values)
            },
            "peaks": {
                "max_cpu": max(cpu_values),
                "max_memory": max(memory_values),
                "max_requests": max(request_values)
            },
            "health_trend": self._calculate_health_trend(relevant_metrics),
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }

    def _calculate_health_trend(self, metrics: List[Dict]) -> str:
        """Calculate overall health trend"""
        if len(metrics) < 2:
            return "insufficient_data"

        # Simple trend calculation based on error counts and resource usage
        recent_half = metrics[len(metrics)//2:]
        older_half = metrics[:len(metrics)//2]

        recent_avg_cpu = sum(m["metrics"]["cpu_usage"] for m in recent_half) / len(recent_half)
        older_avg_cpu = sum(m["metrics"]["cpu_usage"] for m in older_half) / len(older_half)

        recent_errors = sum(m["metrics"]["error_count"] for m in recent_half)
        older_errors = sum(m["metrics"]["error_count"] for m in older_half)

        if recent_avg_cpu < older_avg_cpu and recent_errors <= older_errors:
            return "improving"
        elif recent_avg_cpu > older_avg_cpu or recent_errors > older_errors:
            return "degrading"
        else:
            return "stable"

# Global monitor instance
monitor = WillowSyncMonitor()

# Convenience functions
def start_monitoring():
    """Start system monitoring"""
    monitor.start_monitoring()

def stop_monitoring():
    """Stop system monitoring"""
    monitor.stop_monitoring()

def get_status():
    """Get current system status"""
    return monitor.get_system_status()

def get_performance_report(hours=24):
    """Get performance report"""
    return monitor.get_performance_report(hours)

if __name__ == "__main__":
    # Start monitoring when run directly
    import signal
    import sys

    def signal_handler(sig, frame):
        print("\nStopping monitoring...")
        monitor.stop_monitoring()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    print("Starting WILLOW sync monitoring...")
    monitor.start_monitoring(interval_seconds=10)  # More frequent for testing

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop_monitoring()
