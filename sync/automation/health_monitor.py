#!/usr/bin/env python3
"""
WILLOW Sync Health Monitor
Automated system health monitoring and alerting
"""

import json
import asyncio
import psutil
import logging
from datetime import datetime, timezone
from pathlib import Path
import requests

class HealthMonitor:
    def __init__(self, config_path="config/health_config.json"):
        self.config = self.load_config(config_path)
        self.setup_logging()

    def load_config(self, config_path):
        """Load monitoring configuration."""
        default_config = {
            "thresholds": {
                "cpu_usage": 80.0,
                "memory_usage": 85.0,
                "disk_usage": 90.0,
                "response_time": 5000
            },
            "check_interval": 60,
            "alert_cooldown": 300,
            "notifications": {
                "webhook_url": "",
                "email_enabled": True
            }
        }

        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except FileNotFoundError:
            return default_config

    def setup_logging(self):
        """Setup logging for health monitor."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/health_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('HealthMonitor')

    async def monitor_loop(self):
        """Main monitoring loop."""
        self.logger.info("Starting health monitoring system")

        while True:
            try:
                health_data = await self.collect_metrics()
                alerts = self.check_thresholds(health_data)

                if alerts:
                    await self.send_alerts(alerts, health_data)

                # Log health status
                self.logger.info(f"Health check: CPU={health_data['cpu']:.1f}% "
                               f"MEM={health_data['memory']:.1f}% "
                               f"DISK={health_data['disk']:.1f}%")

                await asyncio.sleep(self.config["check_interval"])

            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(10)

    async def collect_metrics(self):
        """Collect system health metrics."""
        metrics = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cpu": psutil.cpu_percent(interval=1),
            "memory": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage('/').percent,
            "load": psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0,
            "processes": len(psutil.pids()),
            "network": {
                "bytes_sent": psutil.net_io_counters().bytes_sent,
                "bytes_recv": psutil.net_io_counters().bytes_recv
            }
        }

        return metrics

    def check_thresholds(self, metrics):
        """Check if any metrics exceed thresholds."""
        alerts = []
        thresholds = self.config["thresholds"]

        if metrics["cpu"] > thresholds["cpu_usage"]:
            alerts.append({
                "type": "cpu_high",
                "message": f"High CPU usage: {metrics['cpu']:.1f}%",
                "severity": "warning",
                "value": metrics["cpu"],
                "threshold": thresholds["cpu_usage"]
            })

        if metrics["memory"] > thresholds["memory_usage"]:
            alerts.append({
                "type": "memory_high", 
                "message": f"High memory usage: {metrics['memory']:.1f}%",
                "severity": "warning",
                "value": metrics["memory"],
                "threshold": thresholds["memory_usage"]
            })

        if metrics["disk"] > thresholds["disk_usage"]:
            alerts.append({
                "type": "disk_high",
                "message": f"High disk usage: {metrics['disk']:.1f}%",
                "severity": "critical",
                "value": metrics["disk"],
                "threshold": thresholds["disk_usage"]
            })

        return alerts

    async def send_alerts(self, alerts, metrics):
        """Send alerts via configured channels."""
        for alert in alerts:
            self.logger.warning(f"ALERT: {alert['message']}")

            # Send webhook notification
            if self.config["notifications"]["webhook_url"]:
                await self.send_webhook_alert(alert, metrics)

    async def send_webhook_alert(self, alert, metrics):
        """Send alert via webhook."""
        try:
            payload = {
                "alert": alert,
                "metrics": metrics,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "WILLOW Health Monitor"
            }

            response = requests.post(
                self.config["notifications"]["webhook_url"],
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                self.logger.info("Webhook alert sent successfully")
            else:
                self.logger.error(f"Webhook alert failed: {response.status_code}")

        except Exception as e:
            self.logger.error(f"Webhook alert error: {e}")

def main():
    """Main entry point."""
    monitor = HealthMonitor()

    try:
        asyncio.run(monitor.monitor_loop())
    except KeyboardInterrupt:
        monitor.logger.info("Health monitor shutdown requested")

if __name__ == "__main__":
    main()
