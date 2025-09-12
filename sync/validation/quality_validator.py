#!/usr/bin/env python3
"""
WILLOW Quality Validator - Comprehensive quality assurance and validation system
Handles output validation, quality metrics, security scanning, and compliance checks
"""

import os
import json
import logging
import asyncio
import subprocess
import hashlib
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

class ValidationSeverity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class ValidationStatus(Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    WARNING = "WARNING"
    SKIPPED = "SKIPPED"

@dataclass
class ValidationResult:
    check_name: str
    status: ValidationStatus
    severity: ValidationSeverity
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class QualityReport:
    validation_id: str
    target_path: str
    overall_status: ValidationStatus
    quality_score: float
    total_checks: int
    passed_checks: int
    failed_checks: int
    warning_checks: int
    results: List[ValidationResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.now)

class QualityValidator:
    """Comprehensive quality validation system for WILLOW outputs"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.setup_logging()
        self.validation_rules = self.load_validation_rules()

    def setup_logging(self):
        """Initialize logging system"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - WILLOW-QV - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/var/log/willow_quality.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules configuration"""
        default_rules = {
            "file_validation": {
                "check_syntax": True,
                "check_encoding": True,
                "check_size_limits": True,
                "max_file_size": 50 * 1024 * 1024,  # 50MB
                "allowed_extensions": [".py", ".md", ".json", ".yaml", ".txt", ".sh"]
            },
            "content_validation": {
                "check_security": True,
                "check_quality": True,
                "check_compliance": True,
                "forbidden_patterns": [
                    r"password\s*=\s*['"][^'"]+['"]",
                    r"api_key\s*=\s*['"][^'"]+['"]",
                    r"secret\s*=\s*['"][^'"]+['"]"
                ]
            },
            "code_validation": {
                "check_python_syntax": True,
                "check_imports": True,
                "check_complexity": True,
                "max_complexity": 10
            },
            "deployment_validation": {
                "check_structure": True,
                "check_dependencies": True,
                "check_permissions": True,
                "required_files": ["README.md", "requirements.txt"]
            }
        }

        # Load custom rules if config file exists
        config_path = Path(self.config.get("rules_file", "/etc/willow/validation_rules.json"))
        if config_path.exists():
            try:
                with open(config_path) as f:
                    custom_rules = json.load(f)
                    default_rules.update(custom_rules)
            except Exception as e:
                self.logger.warning(f"Failed to load custom validation rules: {e}")

        return default_rules

    async def validate_file_structure(self, target_path: Path) -> List[ValidationResult]:
        """Validate file and directory structure"""
        results = []

        try:
            if not target_path.exists():
                results.append(ValidationResult(
                    check_name="file_existence",
                    status=ValidationStatus.FAILED,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Target path does not exist: {target_path}"
                ))
                return results

            # Check file permissions
            if target_path.is_file():
                stat_info = target_path.stat()
                permissions = oct(stat_info.st_mode)[-3:]

                if permissions in ['777', '666']:
                    results.append(ValidationResult(
                        check_name="file_permissions",
                        status=ValidationStatus.WARNING,
                        severity=ValidationSeverity.MEDIUM,
                        message=f"Overly permissive file permissions: {permissions}",
                        details={"permissions": permissions, "path": str(target_path)}
                    ))
                else:
                    results.append(ValidationResult(
                        check_name="file_permissions",
                        status=ValidationStatus.PASSED,
                        severity=ValidationSeverity.LOW,
                        message="File permissions are appropriate"
                    ))

            # Check file size limits
            if target_path.is_file():
                file_size = target_path.stat().st_size
                max_size = self.validation_rules["file_validation"]["max_file_size"]

                if file_size > max_size:
                    results.append(ValidationResult(
                        check_name="file_size",
                        status=ValidationStatus.FAILED,
                        severity=ValidationSeverity.HIGH,
                        message=f"File exceeds size limit: {file_size} > {max_size}",
                        details={"file_size": file_size, "max_size": max_size}
                    ))
                else:
                    results.append(ValidationResult(
                        check_name="file_size",
                        status=ValidationStatus.PASSED,
                        severity=ValidationSeverity.LOW,
                        message="File size is within limits"
                    ))

            # Check file extensions
            if target_path.is_file():
                extension = target_path.suffix.lower()
                allowed_extensions = self.validation_rules["file_validation"]["allowed_extensions"]

                if extension and extension not in allowed_extensions:
                    results.append(ValidationResult(
                        check_name="file_extension",
                        status=ValidationStatus.WARNING,
                        severity=ValidationSeverity.MEDIUM,
                        message=f"Unexpected file extension: {extension}",
                        details={"extension": extension, "allowed": allowed_extensions}
                    ))
                else:
                    results.append(ValidationResult(
                        check_name="file_extension",
                        status=ValidationStatus.PASSED,
                        severity=ValidationSeverity.LOW,
                        message="File extension is acceptable"
                    ))

        except Exception as e:
            results.append(ValidationResult(
                check_name="structure_validation",
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.HIGH,
                message=f"Error during structure validation: {str(e)}"
            ))

        return results

    async def validate_content_security(self, target_path: Path) -> List[ValidationResult]:
        """Validate content for security issues"""
        results = []

        if not target_path.is_file():
            return results

        try:
            # Read file content
            try:
                with open(target_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                results.append(ValidationResult(
                    check_name="content_encoding",
                    status=ValidationStatus.WARNING,
                    severity=ValidationSeverity.MEDIUM,
                    message="File contains non-UTF-8 content",
                    details={"file": str(target_path)}
                ))
                return results

            # Check for forbidden patterns
            forbidden_patterns = self.validation_rules["content_validation"]["forbidden_patterns"]

            for pattern in forbidden_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    results.append(ValidationResult(
                        check_name="security_scan",
                        status=ValidationStatus.FAILED,
                        severity=ValidationSeverity.CRITICAL,
                        message=f"Potential security issue found: {pattern}",
                        details={"pattern": pattern, "matches": len(matches)}
                    ))

            # Check for hardcoded secrets
            secret_indicators = ['password', 'key', 'token', 'secret', 'credential']
            lines_with_secrets = []

            for i, line in enumerate(content.split('\n'), 1):
                line_lower = line.lower()
                if any(indicator in line_lower for indicator in secret_indicators):
                    if '=' in line and ('"' in line or "'" in line):
                        lines_with_secrets.append(i)

            if lines_with_secrets:
                results.append(ValidationResult(
                    check_name="hardcoded_secrets",
                    status=ValidationStatus.WARNING,
                    severity=ValidationSeverity.HIGH,
                    message=f"Potential hardcoded secrets found on lines: {lines_with_secrets}",
                    details={"lines": lines_with_secrets}
                ))
            else:
                results.append(ValidationResult(
                    check_name="hardcoded_secrets",
                    status=ValidationStatus.PASSED,
                    severity=ValidationSeverity.LOW,
                    message="No hardcoded secrets detected"
                ))

        except Exception as e:
            results.append(ValidationResult(
                check_name="security_validation",
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.HIGH,
                message=f"Error during security validation: {str(e)}"
            ))

        return results

    async def validate_python_code(self, target_path: Path) -> List[ValidationResult]:
        """Validate Python code quality and syntax"""
        results = []

        if target_path.suffix.lower() != '.py':
            return results

        try:
            # Check Python syntax
            try:
                subprocess.run([
                    'python3', '-m', 'py_compile', str(target_path)
                ], check=True, capture_output=True, text=True)

                results.append(ValidationResult(
                    check_name="python_syntax",
                    status=ValidationStatus.PASSED,
                    severity=ValidationSeverity.HIGH,
                    message="Python syntax is valid"
                ))
            except subprocess.CalledProcessError as e:
                results.append(ValidationResult(
                    check_name="python_syntax",
                    status=ValidationStatus.FAILED,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Python syntax error: {e.stderr}",
                    details={"error": e.stderr}
                ))

            # Check imports
            try:
                with open(target_path, 'r') as f:
                    content = f.read()

                import_pattern = r'^(?:from\s+[\w.]+\s+)?import\s+[\w.,\s*]+$'
                imports = re.findall(import_pattern, content, re.MULTILINE)

                results.append(ValidationResult(
                    check_name="python_imports",
                    status=ValidationStatus.PASSED,
                    severity=ValidationSeverity.LOW,
                    message=f"Found {len(imports)} import statements",
                    details={"import_count": len(imports)}
                ))

            except Exception as e:
                results.append(ValidationResult(
                    check_name="python_imports",
                    status=ValidationStatus.WARNING,
                    severity=ValidationSeverity.MEDIUM,
                    message=f"Error checking imports: {str(e)}"
                ))

        except Exception as e:
            results.append(ValidationResult(
                check_name="python_validation",
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.HIGH,
                message=f"Error during Python validation: {str(e)}"
            ))

        return results

    async def validate_deployment_readiness(self, target_path: Path) -> List[ValidationResult]:
        """Validate deployment readiness"""
        results = []

        if not target_path.is_dir():
            return results

        try:
            # Check for required files
            required_files = self.validation_rules["deployment_validation"]["required_files"]

            for required_file in required_files:
                file_path = target_path / required_file
                if file_path.exists():
                    results.append(ValidationResult(
                        check_name=f"required_file_{required_file}",
                        status=ValidationStatus.PASSED,
                        severity=ValidationSeverity.MEDIUM,
                        message=f"Required file present: {required_file}"
                    ))
                else:
                    results.append(ValidationResult(
                        check_name=f"required_file_{required_file}",
                        status=ValidationStatus.WARNING,
                        severity=ValidationSeverity.MEDIUM,
                        message=f"Missing recommended file: {required_file}",
                        details={"missing_file": required_file}
                    ))

            # Check directory structure
            expected_dirs = ["core", "automation", "coordination", "validation", "docs"]
            present_dirs = [d.name for d in target_path.iterdir() if d.is_dir()]

            for expected_dir in expected_dirs:
                if expected_dir in present_dirs:
                    results.append(ValidationResult(
                        check_name=f"directory_{expected_dir}",
                        status=ValidationStatus.PASSED,
                        severity=ValidationSeverity.LOW,
                        message=f"Expected directory present: {expected_dir}"
                    ))
                else:
                    results.append(ValidationResult(
                        check_name=f"directory_{expected_dir}",
                        status=ValidationStatus.WARNING,
                        severity=ValidationSeverity.LOW,
                        message=f"Expected directory missing: {expected_dir}"
                    ))

        except Exception as e:
            results.append(ValidationResult(
                check_name="deployment_validation",
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.HIGH,
                message=f"Error during deployment validation: {str(e)}"
            ))

        return results

    async def calculate_quality_score(self, results: List[ValidationResult]) -> float:
        """Calculate overall quality score based on validation results"""
        if not results:
            return 0.0

        severity_weights = {
            ValidationSeverity.CRITICAL: -10,
            ValidationSeverity.HIGH: -5,
            ValidationSeverity.MEDIUM: -2,
            ValidationSeverity.LOW: -1,
            ValidationSeverity.INFO: 0
        }

        status_multipliers = {
            ValidationStatus.PASSED: 1,
            ValidationStatus.WARNING: 0.5,
            ValidationStatus.FAILED: 1,
            ValidationStatus.SKIPPED: 0
        }

        total_score = 100.0
        total_checks = len(results)

        for result in results:
            weight = severity_weights.get(result.severity, 0)
            multiplier = status_multipliers.get(result.status, 0)

            if result.status == ValidationStatus.FAILED:
                total_score += weight * multiplier
            elif result.status == ValidationStatus.WARNING:
                total_score += weight * multiplier * 0.5

        # Normalize to 0-100 range
        quality_score = max(0.0, min(100.0, total_score))

        return quality_score

    async def validate_target(self, target_path: Union[str, Path]) -> QualityReport:
        """Perform comprehensive validation of target path"""
        target_path = Path(target_path)
        validation_id = f"QUAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(str(target_path).encode()).hexdigest()[:8]}"

        self.logger.info(f"Starting quality validation: {validation_id}")

        all_results = []

        # Run all validation checks
        structure_results = await self.validate_file_structure(target_path)
        all_results.extend(structure_results)

        security_results = await self.validate_content_security(target_path)
        all_results.extend(security_results)

        if target_path.is_file():
            python_results = await self.validate_python_code(target_path)
            all_results.extend(python_results)
        elif target_path.is_dir():
            deployment_results = await self.validate_deployment_readiness(target_path)
            all_results.extend(deployment_results)

            # Validate all Python files in directory
            for py_file in target_path.rglob("*.py"):
                python_results = await self.validate_python_code(py_file)
                all_results.extend(python_results)

        # Calculate statistics
        total_checks = len(all_results)
        passed_checks = len([r for r in all_results if r.status == ValidationStatus.PASSED])
        failed_checks = len([r for r in all_results if r.status == ValidationStatus.FAILED])
        warning_checks = len([r for r in all_results if r.status == ValidationStatus.WARNING])

        # Determine overall status
        if failed_checks > 0:
            overall_status = ValidationStatus.FAILED
        elif warning_checks > 0:
            overall_status = ValidationStatus.WARNING
        else:
            overall_status = ValidationStatus.PASSED

        # Calculate quality score
        quality_score = await self.calculate_quality_score(all_results)

        # Create quality report
        report = QualityReport(
            validation_id=validation_id,
            target_path=str(target_path),
            overall_status=overall_status,
            quality_score=quality_score,
            total_checks=total_checks,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            warning_checks=warning_checks,
            results=all_results,
            metadata={
                "validator_version": "1.0",
                "validation_rules": self.validation_rules,
                "target_type": "directory" if target_path.is_dir() else "file"
            }
        )

        self.logger.info(f"Quality validation completed: {validation_id} - Score: {quality_score:.1f}")

        return report

    async def generate_report_json(self, report: QualityReport, output_path: Path) -> bool:
        """Generate JSON quality report"""
        try:
            report_data = {
                "validation_id": report.validation_id,
                "target_path": report.target_path,
                "overall_status": report.overall_status.value,
                "quality_score": report.quality_score,
                "statistics": {
                    "total_checks": report.total_checks,
                    "passed_checks": report.passed_checks,
                    "failed_checks": report.failed_checks,
                    "warning_checks": report.warning_checks
                },
                "results": [
                    {
                        "check_name": r.check_name,
                        "status": r.status.value,
                        "severity": r.severity.value,
                        "message": r.message,
                        "details": r.details,
                        "timestamp": r.timestamp.isoformat()
                    }
                    for r in report.results
                ],
                "metadata": report.metadata,
                "generated_at": report.generated_at.isoformat()
            }

            with open(output_path, 'w') as f:
                json.dump(report_data, f, indent=2)

            self.logger.info(f"Quality report saved: {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to generate JSON report: {e}")
            return False

# CLI Interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="WILLOW Quality Validator")
    parser.add_argument("target", help="Target file or directory to validate")
    parser.add_argument("--output", "-o", help="Output report file (JSON)")
    parser.add_argument("--config", "-c", help="Configuration file path")

    args = parser.parse_args()

    config = {}
    if args.config:
        config["rules_file"] = args.config

    validator = QualityValidator(config)

    # Run validation
    report = asyncio.run(validator.validate_target(args.target))

    # Output report
    if args.output:
        asyncio.run(validator.generate_report_json(report, Path(args.output)))
    else:
        print(f"Quality Validation Report: {report.validation_id}")
        print(f"Target: {report.target_path}")
        print(f"Overall Status: {report.overall_status.value}")
        print(f"Quality Score: {report.quality_score:.1f}/100")
        print(f"Checks: {report.passed_checks} passed, {report.failed_checks} failed, {report.warning_checks} warnings")
