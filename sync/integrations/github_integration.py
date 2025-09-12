#!/usr/bin/env python3
"""
WILLOW GitHub Integration Module
Production-ready GitHub API integration for sync coordination
"""

import json
import base64
import logging
import requests
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path

class GitHubIntegration:
    """GitHub API integration for WILLOW sync system."""

    def __init__(self, token: str, repo_owner: str, repo_name: str):
        self.token = token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        self.logger = self._setup_logging()

    def _setup_logging(self):
        """Setup logging for GitHub integration."""
        logger = logging.getLogger('GitHubIntegration')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def create_sync_report_issue(self, 
                               title: str, 
                               body: str, 
                               labels: List[str] = None) -> Optional[Dict]:
        """Create GitHub issue for sync reports."""
        try:
            url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/issues"

            data = {
                "title": title,
                "body": body,
                "labels": labels or ["sync-report", "automated"]
            }

            response = requests.post(url, headers=self.headers, json=data)

            if response.status_code == 201:
                issue_data = response.json()
                self.logger.info(f"Created issue #{issue_data['number']}: {title}")
                return issue_data
            else:
                self.logger.error(f"Failed to create issue: {response.status_code}")
                self.logger.error(response.text)
                return None

        except Exception as e:
            self.logger.error(f"GitHub issue creation error: {e}")
            return None

    def update_sync_status_file(self, 
                              status_data: Dict, 
                              file_path: str = "sync/status/current_status.json") -> bool:
        """Update sync status file in repository."""
        try:
            # Get current file (if exists)
            url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/contents/{file_path}"
            response = requests.get(url, headers=self.headers)

            # Prepare update data
            content = json.dumps(status_data, indent=2, default=str)
            encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')

            data = {
                "message": f"Update sync status - {datetime.now().isoformat()}",
                "content": encoded_content,
                "branch": "main"
            }

            # Add SHA if file exists
            if response.status_code == 200:
                existing_file = response.json()
                data["sha"] = existing_file["sha"]
                self.logger.info(f"Updating existing file: {file_path}")
            else:
                self.logger.info(f"Creating new file: {file_path}")

            # Update/create file
            response = requests.put(url, headers=self.headers, json=data)

            if response.status_code in [200, 201]:
                self.logger.info(f"Successfully updated status file: {file_path}")
                return True
            else:
                self.logger.error(f"Failed to update status file: {response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"Status file update error: {e}")
            return False

    def create_sync_log_entry(self, 
                            log_data: Dict, 
                            log_dir: str = "sync/logs") -> bool:
        """Create timestamped log entry in repository."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"{log_dir}/sync_log_{timestamp}.json"

            url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/contents/{file_path}"

            content = json.dumps(log_data, indent=2, default=str)
            encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')

            data = {
                "message": f"Add sync log entry - {timestamp}",
                "content": encoded_content,
                "branch": "main"
            }

            response = requests.put(url, headers=self.headers, json=data)

            if response.status_code == 201:
                self.logger.info(f"Created log entry: {file_path}")
                return True
            else:
                self.logger.error(f"Failed to create log entry: {response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"Log entry creation error: {e}")
            return False

    def get_latest_sync_config(self, 
                             config_path: str = "sync/config/sync_config.json") -> Optional[Dict]:
        """Get latest sync configuration from repository."""
        try:
            url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/contents/{config_path}"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                file_data = response.json()
                content = base64.b64decode(file_data['content']).decode('utf-8')
                config = json.loads(content)

                self.logger.info(f"Retrieved config from: {config_path}")
                return config
            else:
                self.logger.error(f"Failed to get config: {response.status_code}")
                return None

        except Exception as e:
            self.logger.error(f"Config retrieval error: {e}")
            return None

    def create_deployment_tag(self, 
                            tag_name: str, 
                            message: str, 
                            commit_sha: str = None) -> bool:
        """Create deployment tag for sync system releases."""
        try:
            # Get latest commit if no SHA provided
            if not commit_sha:
                url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/commits/main"
                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    commit_sha = response.json()['sha']
                else:
                    self.logger.error("Failed to get latest commit SHA")
                    return False

            # Create tag
            url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/git/tags"

            tag_data = {
                "tag": tag_name,
                "message": message,
                "object": commit_sha,
                "type": "commit"
            }

            response = requests.post(url, headers=self.headers, json=tag_data)

            if response.status_code == 201:
                # Create reference
                ref_url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/git/refs"
                ref_data = {
                    "ref": f"refs/tags/{tag_name}",
                    "sha": response.json()['sha']
                }

                ref_response = requests.post(ref_url, headers=self.headers, json=ref_data)

                if ref_response.status_code == 201:
                    self.logger.info(f"Created deployment tag: {tag_name}")
                    return True

            self.logger.error(f"Failed to create tag: {response.status_code}")
            return False

        except Exception as e:
            self.logger.error(f"Tag creation error: {e}")
            return False

    def backup_sync_data(self, 
                        backup_data: Dict, 
                        backup_dir: str = "sync/backups") -> bool:
        """Create backup of sync system data."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"{backup_dir}/sync_backup_{timestamp}.json"

            url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/contents/{file_path}"

            content = json.dumps(backup_data, indent=2, default=str)
            encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')

            data = {
                "message": f"Backup sync data - {timestamp}",
                "content": encoded_content,
                "branch": "main"
            }

            response = requests.put(url, headers=self.headers, json=data)

            if response.status_code == 201:
                self.logger.info(f"Created backup: {file_path}")
                return True
            else:
                self.logger.error(f"Failed to create backup: {response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"Backup creation error: {e}")
            return False

def main():
    """Test GitHub integration."""
    # Note: Replace with actual credentials for testing
    token = "your_github_token"
    repo_owner = "HVSCMA" 
    repo_name = "hvscma-cmas"

    try:
        github = GitHubIntegration(token, repo_owner, repo_name)

        # Test status update
        test_status = {
            "timestamp": datetime.now().isoformat(),
            "system_status": "healthy",
            "active_agents": 3,
            "test_mode": True
        }

        # github.update_sync_status_file(test_status)

        print("GitHub integration test completed successfully")

    except Exception as e:
        print(f"GitHub integration test failed: {e}")

if __name__ == "__main__":
    main()
