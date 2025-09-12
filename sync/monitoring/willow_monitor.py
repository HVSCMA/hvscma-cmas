#!/usr/bin/env python3
"""
WILLOW System Monitor v41.5
Automated monitoring and alerting for HVSCMA sync operations
"""

import json
import time
import logging
import psutil
import requests
from datetime import datetime, timedelta
from pathlib import Path

class WillowMonitor:
    def __init__(self, config_path="/opt/willow-sync/sync/coordination/willow_config.json"):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        self.metrics = {}

    def _load_config(self, config_path):
        """Load monitoring configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._default_config()

    def _default_config(self):
        """Default monitoring configuration"""
        return {
            "monitoring": {
                "check_interval": 300,  # 5 minutes
                "alert_thresholds": {
                    "cpu_usage": 80,
                    "memory_usage": 85,
                    "disk_usage": 90,
                    "sync_failures": 3
                }
            }
        }

    def _setup_logging(self):
        """Set up monitoring logger"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - WILLOW-MONITOR - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/var/log/willow/monitor.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)

    def collect_system_metrics(self):
        """Collect system performance metrics"""
        self.metrics.update({
            "timestamp": datetime.now().isoformat(),
            "cpu_usage": psutil.cpu_percent(interval=1),
            "memory": psutil.virtual_memory()._asdict(),
            "disk": psutil.disk_usage('/')._asdict(),
            "network": psutil.net_io_counters()._asdict(),
            "processes": len(psutil.pids())
        })

        self.logger.info(f"System metrics collected - CPU: {self.metrics['cpu_usage']}%, "
                        f"Memory: {self.metrics['memory']['percent']}%, "
                        f"Disk: {self.metrics['disk']['percent']}%")

    def check_sync_status(self):
        """Monitor WILLOW sync operations"""
        sync_log_path = Path("/var/log/willow/willow_sync.log")

        if sync_log_path.exists():
            # Check recent sync activities
            recent_entries = self._get_recent_log_entries(sync_log_path, hours=1)

            error_count = sum(1 for entry in recent_entries if "ERROR" in entry)
            success_count = sum(1 for entry in recent_entries if "Sync completed successfully" in entry)

            self.metrics.update({
                "sync_errors_1h": error_count,
                "sync_success_1h": success_count,
                "sync_health": "healthy" if error_count == 0 else "degraded" if error_count < 3 else "critical"
            })

            self.logger.info(f"Sync health: {self.metrics['sync_health']} "
                           f"(Errors: {error_count}, Success: {success_count})")
        else:
            self.metrics["sync_health"] = "unknown"
            self.logger.warning("Sync log file not found")

    def _get_recent_log_entries(self, log_path, hours=1):
        """Get log entries from the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_entries = []

        try:
            with open(log_path, 'r') as f:
                for line in f:
                    if cutoff_time.strftime("%Y-%m-%d") in line:
                        recent_entries.append(line.strip())
        except Exception as e:
            self.logger.error(f"Error reading log file: {e}")

        return recent_entries

    def check_alerts(self):
        """Check for alert conditions"""
        alerts = []
        thresholds = self.config.get("monitoring", {}).get("alert_thresholds", {})

        # CPU usage alert
        if self.metrics.get("cpu_usage", 0) > thresholds.get("cpu_usage", 80):
            alerts.append(f"High CPU usage: {self.metrics['cpu_usage']}%")

        # Memory usage alert
        memory_percent = self.metrics.get("memory", {}).get("percent", 0)
        if memory_percent > thresholds.get("memory_usage", 85):
            alerts.append(f"High memory usage: {memory_percent}%")

        # Disk usage alert
        disk_percent = self.metrics.get("disk", {}).get("percent", 0)
        if disk_percent > thresholds.get("disk_usage", 90):
            alerts.append(f"High disk usage: {disk_percent}%")

        # Sync failure alert
        sync_errors = self.metrics.get("sync_errors_1h", 0)
        if sync_errors >= thresholds.get("sync_failures", 3):
            alerts.append(f"Multiple sync failures: {sync_errors} in last hour")

        if alerts:
            for alert in alerts:
                self.logger.warning(f"ALERT: {alert}")
            self._send_alerts(alerts)

    def _send_alerts(self, alerts):
        """Send alert notifications"""
        alert_payload = {
            "timestamp": datetime.now().isoformat(),
            "system": "WILLOW_SYNC",
            "alerts": alerts,
            "metrics": self.metrics
        }

        # Log alert locally
        with open("/var/log/willow/alerts.log", "a") as f:
            f.write(json.dumps(alert_payload) + "\n")

        # Here you could add external alerting (email, webhook, etc.)

    def generate_health_report(self):
        """Generate system health report"""
        report = {
            "report_type": "health_check",
            "timestamp": datetime.now().isoformat(),
            "system_status": self._determine_system_status(),
            "metrics": self.metrics,
            "recommendations": self._generate_recommendations()
        }

        # Save report
        report_path = f"/var/log/willow/health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"Health report generated: {report_path}")
        return report

    def _determine_system_status(self):
        """Determine overall system status"""
        if self.metrics.get("sync_health") == "critical":
            return "critical"
        elif (self.metrics.get("cpu_usage", 0) > 90 or 
              self.metrics.get("memory", {}).get("percent", 0) > 95):
            return "warning"
        else:
            return "healthy"

    def _generate_recommendations(self):
        """Generate performance recommendations"""
        recommendations = []

        if self.metrics.get("cpu_usage", 0) > 80:
            recommendations.append("Consider scaling CPU resources or optimizing processes")

        if self.metrics.get("memory", {}).get("percent", 0) > 85:
            recommendations.append("Monitor memory usage and consider increasing available RAM")

        if self.metrics.get("sync_errors_1h", 0) > 0:
            recommendations.append("Review sync logs for error patterns and resolution")

        return recommendations

    def run_monitoring_cycle(self):
        """Execute one complete monitoring cycle"""
        self.logger.info("Starting monitoring cycle")

        self.collect_system_metrics()
        self.check_sync_status()
        self.check_alerts()

        if datetime.now().hour % 6 == 0:  # Generate health report every 6 hours
            self.generate_health_report()

        self.logger.info("Monitoring cycle completed")

# Main execution
if __name__ == "__main__":
    monitor = WillowMonitor()

    while True:
        try:
            monitor.run_monitoring_cycle()
            time.sleep(300)  # Wait 5 minutes between cycles
        except KeyboardInterrupt:
            monitor.logger.info("Monitoring stopped by user")
            break
        except Exception as e:
            monitor.logger.error(f"Monitoring error: {e}")
            time.sleep(60)  # Wait 1 minute on error
