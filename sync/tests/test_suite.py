#!/usr/bin/env python3
"""
WILLOW Sync Test Suite - Comprehensive testing framework
Tests all components of the WILLOW sync system for quality assurance
"""

import os
import sys
import json
import asyncio
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import subprocess
import unittest

class WillowTestSuite:
    """Comprehensive test suite for WILLOW Sync system"""

    def __init__(self):
        self.test_results = []
        self.setup_test_environment()

    def setup_test_environment(self):
        """Set up isolated test environment"""
        self.test_dir = Path(tempfile.mkdtemp(prefix="willow_test_"))
        self.sync_dir = Path("/home/user/output/sync")

        print(f"Test environment: {self.test_dir}")

        # Copy sync files to test environment
        if self.sync_dir.exists():
            shutil.copytree(self.sync_dir, self.test_dir / "sync")

    def log_test_result(self, test_name: str, status: str, message: str, details: Dict = None):
        """Log test result"""
        result = {
            "test_name": test_name,
            "status": status,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)

        status_symbol = {"PASS": "✓", "FAIL": "✗", "SKIP": "⊝"}.get(status, "?")
        print(f"{status_symbol} {test_name}: {message}")

    async def test_willow_coordinator(self) -> bool:
        """Test WILLOW coordinator functionality"""
        test_name = "willow_coordinator"

        try:
            coordinator_path = self.test_dir / "sync" / "core" / "willow_coordinator.py"

            if not coordinator_path.exists():
                self.log_test_result(test_name, "FAIL", "Coordinator file not found")
                return False

            # Test Python syntax
            result = subprocess.run([
                "python3", "-m", "py_compile", str(coordinator_path)
            ], capture_output=True, text=True)

            if result.returncode != 0:
                self.log_test_result(test_name, "FAIL", f"Syntax error: {result.stderr}")
                return False

            # Test import
            sys.path.insert(0, str(coordinator_path.parent))
            try:
                from willow_coordinator import WillowCoordinator, SyncCommand, SyncCommandType

                # Test basic initialization
                coordinator = WillowCoordinator()

                # Test command parsing
                command = coordinator.parse_sync_command("WILLOW_SYNC:INIT:TEST")
                assert command.command_type == SyncCommandType.INIT
                assert command.parameters == ["TEST"]

                # Test command execution
                result = await coordinator.execute_sync_command(command)
                assert result["status"] == "SUCCESS"

                self.log_test_result(test_name, "PASS", "All coordinator tests passed")
                return True

            except Exception as e:
                self.log_test_result(test_name, "FAIL", f"Import/execution error: {str(e)}")
                return False
            finally:
                sys.path.pop(0)

        except Exception as e:
            self.log_test_result(test_name, "FAIL", f"Unexpected error: {str(e)}")
            return False

    async def test_automation_system(self) -> bool:
        """Test automation system functionality"""
        test_name = "automation_system"

        try:
            automation_path = self.test_dir / "sync" / "automation" / "willow_automation.py"

            if not automation_path.exists():
                self.log_test_result(test_name, "FAIL", "Automation file not found")
                return False

            # Test Python syntax
            result = subprocess.run([
                "python3", "-m", "py_compile", str(automation_path)
            ], capture_output=True, text=True)

            if result.returncode != 0:
                self.log_test_result(test_name, "FAIL", f"Syntax error: {result.stderr}")
                return False

            # Test import
            sys.path.insert(0, str(automation_path.parent))
            try:
                from willow_automation import WillowAutomation, DeploymentConfig

                # Test configuration
                config = DeploymentConfig(
                    target_environment="test",
                    github_repo="test/repo"
                )

                # Test initialization
                automation = WillowAutomation(config)

                # Test validation method
                validation_result = await automation.validate_deployment()
                assert "status" in validation_result

                self.log_test_result(test_name, "PASS", "All automation tests passed")
                return True

            except Exception as e:
                self.log_test_result(test_name, "FAIL", f"Import/execution error: {str(e)}")
                return False
            finally:
                sys.path.pop(0)

        except Exception as e:
            self.log_test_result(test_name, "FAIL", f"Unexpected error: {str(e)}")
            return False

    async def test_gmail_coordinator(self) -> bool:
        """Test Gmail coordination functionality"""
        test_name = "gmail_coordinator"

        try:
            gmail_path = self.test_dir / "sync" / "coordination" / "gmail_coordinator.py"

            if not gmail_path.exists():
                self.log_test_result(test_name, "FAIL", "Gmail coordinator file not found")
                return False

            # Test Python syntax
            result = subprocess.run([
                "python3", "-m", "py_compile", str(gmail_path)
            ], capture_output=True, text=True)

            if result.returncode != 0:
                self.log_test_result(test_name, "FAIL", f"Syntax error: {result.stderr}")
                return False

            # Test import
            sys.path.insert(0, str(gmail_path.parent))
            try:
                from gmail_coordinator import GmailCoordinator, EmailConfig, EmailTask

                # Test configuration
                config = EmailConfig(
                    smtp_server="test.smtp.com",
                    smtp_port=587,
                    imap_server="test.imap.com",
                    imap_port=993,
                    username="test@example.com",
                    password="test_password"
                )

                # Test initialization
                coordinator = GmailCoordinator(config)

                # Test command parsing
                command = coordinator.parse_willow_command_from_email("Please deploy WILLOW_SYNC:DEPLOY:TEST:AUTO")
                assert command is not None

                self.log_test_result(test_name, "PASS", "All Gmail coordinator tests passed")
                return True

            except Exception as e:
                self.log_test_result(test_name, "FAIL", f"Import/execution error: {str(e)}")
                return False
            finally:
                sys.path.pop(0)

        except Exception as e:
            self.log_test_result(test_name, "FAIL", f"Unexpected error: {str(e)}")
            return False

    async def test_quality_validator(self) -> bool:
        """Test quality validation functionality"""
        test_name = "quality_validator"

        try:
            validator_path = self.test_dir / "sync" / "validation" / "quality_validator.py"

            if not validator_path.exists():
                self.log_test_result(test_name, "FAIL", "Quality validator file not found")
                return False

            # Test Python syntax
            result = subprocess.run([
                "python3", "-m", "py_compile", str(validator_path)
            ], capture_output=True, text=True)

            if result.returncode != 0:
                self.log_test_result(test_name, "FAIL", f"Syntax error: {result.stderr}")
                return False

            # Test import
            sys.path.insert(0, str(validator_path.parent))
            try:
                from quality_validator import QualityValidator, ValidationResult, ValidationStatus

                # Test initialization
                validator = QualityValidator()

                # Create test file for validation
                test_file = self.test_dir / "test_file.py"
                test_file.write_text("print('Hello, World!')")

                # Test validation
                report = await validator.validate_target(test_file)
                assert report.validation_id is not None
                assert report.quality_score >= 0

                self.log_test_result(test_name, "PASS", "All quality validator tests passed")
                return True

            except Exception as e:
                self.log_test_result(test_name, "FAIL", f"Import/execution error: {str(e)}")
                return False
            finally:
                sys.path.pop(0)

        except Exception as e:
            self.log_test_result(test_name, "FAIL", f"Unexpected error: {str(e)}")
            return False

    async def test_file_structure(self) -> bool:
        """Test file structure integrity"""
        test_name = "file_structure"

        try:
            required_files = [
                "sync/core/willow_master_prompt.md",
                "sync/core/willow_coordinator.py",
                "sync/automation/willow_automation.py",
                "sync/coordination/gmail_coordinator.py",
                "sync/validation/quality_validator.py",
                "sync/docs/README.md",
                "sync/requirements.txt"
            ]

            missing_files = []

            for file_path in required_files:
                full_path = self.test_dir / file_path
                if not full_path.exists():
                    missing_files.append(file_path)

            if missing_files:
                self.log_test_result(test_name, "FAIL", f"Missing files: {missing_files}")
                return False

            # Check file sizes (basic validation)
            for file_path in required_files:
                full_path = self.test_dir / file_path
                if full_path.stat().st_size < 100:  # Minimum reasonable size
                    self.log_test_result(test_name, "FAIL", f"File too small: {file_path}")
                    return False

            self.log_test_result(test_name, "PASS", "All required files present and valid")
            return True

        except Exception as e:
            self.log_test_result(test_name, "FAIL", f"Unexpected error: {str(e)}")
            return False

    async def test_integration(self) -> bool:
        """Test system integration"""
        test_name = "system_integration"

        try:
            # Test that all components can be imported together
            sys.path.insert(0, str(self.test_dir / "sync" / "core"))
            sys.path.insert(0, str(self.test_dir / "sync" / "automation"))
            sys.path.insert(0, str(self.test_dir / "sync" / "coordination"))
            sys.path.insert(0, str(self.test_dir / "sync" / "validation"))

            try:
                from willow_coordinator import WillowCoordinator
                from willow_automation import WillowAutomation, DeploymentConfig
                from gmail_coordinator import GmailCoordinator, EmailConfig
                from quality_validator import QualityValidator

                # Test basic integration workflow
                coordinator = WillowCoordinator()
                validator = QualityValidator()

                # Test command flow
                command = coordinator.parse_sync_command("WILLOW_SYNC:INIT:INTEGRATION_TEST")
                result = await coordinator.execute_sync_command(command)

                assert result["status"] == "SUCCESS"

                self.log_test_result(test_name, "PASS", "Integration test successful")
                return True

            except Exception as e:
                self.log_test_result(test_name, "FAIL", f"Integration error: {str(e)}")
                return False
            finally:
                # Clean up sys.path
                for _ in range(4):
                    sys.path.pop(0)

        except Exception as e:
            self.log_test_result(test_name, "FAIL", f"Unexpected error: {str(e)}")
            return False

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive test suite"""
        print("🧪 Starting WILLOW Sync Test Suite")
        print("=" * 50)

        start_time = datetime.now()

        # Run all tests
        tests = [
            ("File Structure", self.test_file_structure()),
            ("WILLOW Coordinator", self.test_willow_coordinator()),
            ("Automation System", self.test_automation_system()),
            ("Gmail Coordinator", self.test_gmail_coordinator()),
            ("Quality Validator", self.test_quality_validator()),
            ("System Integration", self.test_integration())
        ]

        passed = 0
        failed = 0

        for test_name, test_coro in tests:
            try:
                result = await test_coro
                if result:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log_test_result(f"test_execution_{test_name.lower().replace(' ', '_')}", 
                                   "FAIL", f"Test execution failed: {str(e)}")
                failed += 1

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Generate summary
        summary = {
            "test_suite": "WILLOW Sync Comprehensive Tests",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "total_tests": len(tests),
            "passed": passed,
            "failed": failed,
            "success_rate": (passed / len(tests)) * 100 if tests else 0,
            "overall_status": "PASS" if failed == 0 else "FAIL",
            "test_results": self.test_results
        }

        print("=" * 50)
        print("🏁 Test Suite Complete")
        print(f"✓ Passed: {passed}")
        print(f"✗ Failed: {failed}")
        print(f"📊 Success Rate: {summary['success_rate']:.1f}%")
        print(f"⏱️ Duration: {duration:.2f} seconds")
        print(f"🎯 Overall Status: {summary['overall_status']}")

        return summary

    def cleanup_test_environment(self):
        """Clean up test environment"""
        if hasattr(self, 'test_dir') and self.test_dir.exists():
            shutil.rmtree(self.test_dir)
            print(f"Cleaned up test environment: {self.test_dir}")

# Test runner function
async def run_willow_tests():
    """Main test runner function"""
    test_suite = WillowTestSuite()

    try:
        summary = await test_suite.run_all_tests()

        # Save test report
        report_path = Path("/home/user/output/willow_test_report.json")
        with open(report_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)

        print(f"\n📋 Test report saved: {report_path}")

        return summary

    finally:
        test_suite.cleanup_test_environment()

# CLI Interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="WILLOW Sync Test Suite")
    parser.add_argument("--output", "-o", help="Output report file (JSON)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Run tests
    summary = asyncio.run(run_willow_tests())

    # Save custom output if specified
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        print(f"Test report saved to: {args.output}")

    # Exit with appropriate code
    exit_code = 0 if summary["overall_status"] == "PASS" else 1
    sys.exit(exit_code)
