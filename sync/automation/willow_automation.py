#!/usr/bin/env python3
"""
WILLOW Sync Automation - Production-ready automation scripts
Handles automated deployment, monitoring, and maintenance tasks
"""

import os
import sys
import json
import subprocess
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class DeploymentConfig:
    target_environment: str
    github_repo: str
    branch: str = "main"
    sync_directory: str = "/sync/"
    validation_enabled: bool = True
    rollback_enabled: bool = True

class WillowAutomation:
    """Production automation system for WILLOW sync deployment"""

    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.setup_logging()

    def setup_logging(self):
        """Initialize production logging"""
        log_dir = Path("/var/log/willow")
        log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - WILLOW-AUTO - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "automation.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    async def deploy_to_github(self, github_token: str) -> Dict[str, Any]:
        """Deploy WILLOW sync system to GitHub repository"""
        self.logger.info(f"Starting GitHub deployment to {self.config.github_repo}")

        deployment_results = {
            "status": "SUCCESS",
            "deployment_time": datetime.now().isoformat(),
            "files_deployed": [],
            "errors": []
        }

        # Simplified GitHub deployment using git commands
        repo_path = Path("/tmp/willow_deployment")
        if repo_path.exists():
            subprocess.run(["rm", "-rf", str(repo_path)])

        try:
            # Clone repository
            clone_cmd = f"git clone https://{github_token}@github.com/{self.config.github_repo}.git {repo_path}"
            subprocess.run(clone_cmd, shell=True, check=True)

            self.logger.info("Repository cloned successfully")

            # Deploy sync files
            sync_source = Path("/home/user/output/sync")
            sync_target = repo_path / "sync"

            # Create sync directory and copy files
            sync_target.mkdir(exist_ok=True)
            subprocess.run([
                "cp", "-r", f"{sync_source}/.", str(sync_target)
            ], check=True)

            # Stage and commit changes
            os.chdir(repo_path)
            subprocess.run(["git", "add", "sync/"], check=True)
            subprocess.run([
                "git", "commit", "-m", 
                f"WILLOW Sync Deployment - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            ], check=True)

            # Push to repository
            subprocess.run(["git", "push", "origin", self.config.branch], check=True)

            deployment_results["files_deployed"] = [
                str(f.relative_to(sync_source)) 
                for f in sync_source.rglob("*") 
                if f.is_file()
            ]

            self.logger.info(f"Deployed {len(deployment_results['files_deployed'])} files")

        except Exception as e:
            deployment_results["status"] = "ERROR"
            deployment_results["errors"].append(f"Deployment failed: {str(e)}")

        return deployment_results

    async def validate_deployment(self) -> Dict[str, Any]:
        """Validate deployed WILLOW sync system"""
        self.logger.info("Starting deployment validation")

        validation_results = {
            "status": "SUCCESS",
            "validation_time": datetime.now().isoformat(),
            "checks": {},
            "errors": []
        }

        # Check core files exist
        required_files = [
            "core/willow_master_prompt.md",
            "core/willow_coordinator.py",
            "automation/willow_automation.py"
        ]

        for file_path in required_files:
            full_path = Path("/home/user/output/sync") / file_path
            validation_results["checks"][file_path] = {
                "exists": full_path.exists(),
                "size": full_path.stat().st_size if full_path.exists() else 0
            }

            if not full_path.exists():
                validation_results["errors"].append(f"Missing required file: {file_path}")

        # Validate Python syntax
        python_files = list(Path("/home/user/output/sync").rglob("*.py"))
        for py_file in python_files:
            try:
                subprocess.run([
                    "python3", "-m", "py_compile", str(py_file)
                ], check=True, capture_output=True)
                validation_results["checks"][f"syntax_{py_file.name}"] = True
            except subprocess.CalledProcessError:
                validation_results["errors"].append(f"Syntax error in {py_file.name}")
                validation_results["checks"][f"syntax_{py_file.name}"] = False

        if validation_results["errors"]:
            validation_results["status"] = "FAILED"

        return validation_results

    async def run_full_deployment(self, github_token: str) -> Dict[str, Any]:
        """Execute complete WILLOW sync deployment"""
        self.logger.info("Starting full WILLOW sync deployment")

        deployment_summary = {
            "deployment_id": f"WILLOW_DEPLOY_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "start_time": datetime.now().isoformat(),
            "status": "IN_PROGRESS",
            "phases": {},
            "errors": []
        }

        try:
            # Phase 1: GitHub Deployment
            github_result = await self.deploy_to_github(github_token)
            deployment_summary["phases"]["github_deployment"] = github_result

            # Phase 2: Validation
            validation_result = await self.validate_deployment()
            deployment_summary["phases"]["validation"] = validation_result

            if github_result["status"] == "SUCCESS" and validation_result["status"] == "SUCCESS":
                deployment_summary["status"] = "SUCCESS"
            else:
                deployment_summary["status"] = "FAILED"
                deployment_summary["errors"].extend(github_result.get("errors", []))
                deployment_summary["errors"].extend(validation_result.get("errors", []))

            deployment_summary["end_time"] = datetime.now().isoformat()

            self.logger.info("Full WILLOW sync deployment completed")

        except Exception as e:
            deployment_summary["status"] = "ERROR"
            deployment_summary["errors"].append(f"Deployment failed: {str(e)}")
            deployment_summary["end_time"] = datetime.now().isoformat()

        return deployment_summary

# CLI Interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="WILLOW Sync Automation System")
    parser.add_argument("--github-token", required=True, help="GitHub access token")
    parser.add_argument("--repo", required=True, help="GitHub repository (owner/repo)")
    parser.add_argument("--environment", default="production", help="Target environment")
    parser.add_argument("--branch", default="main", help="Git branch")

    args = parser.parse_args()

    config = DeploymentConfig(
        target_environment=args.environment,
        github_repo=args.repo,
        branch=args.branch
    )

    automation = WillowAutomation(config)

    # Run deployment
    result = asyncio.run(automation.run_full_deployment(args.github_token))
    print(json.dumps(result, indent=2, default=str))
