# WILLOW Sync - Enhanced Coordination System

## Overview

WILLOW Sync is a comprehensive AI coordination system designed for multi-agent collaboration, task orchestration, and production deployment. This enhanced version includes advanced synchronization capabilities, Gmail integration, quality validation, and automated deployment tools.

## Features

### Core Capabilities
- **Multi-Agent Orchestration**: Coordinate between specialized AI agents
- **Sync Command System**: Structured command interface for coordination
- **Quality Assurance**: Automated validation and quality metrics
- **Production Deployment**: Seamless GitHub integration and deployment
- **Gmail Coordination**: Email-based task initiation and status updates
- **Monitoring & Reporting**: Comprehensive logging and alerting

### Sync Command Structure
All WILLOW sync commands follow the format: `WILLOW_SYNC:[COMMAND]:[PARAMETERS]`

**Available Commands:**
- `WILLOW_SYNC:INIT:[PROJECT_ID]` - Initialize sync coordination
- `WILLOW_SYNC:STATUS:[AGENT_ID]` - Request status update
- `WILLOW_SYNC:COORDINATE:[TASK_ID]:[AGENTS]` - Coordinate multi-agent tasks
- `WILLOW_SYNC:VALIDATE:[OUTPUT_ID]` - Trigger quality validation
- `WILLOW_SYNC:DEPLOY:[TARGET]:[CONFIG]` - Execute deployment
- `WILLOW_SYNC:MONITOR:[METRICS]` - Activate monitoring
- `WILLOW_SYNC:ESCALATE:[PRIORITY]:[ISSUE]` - Escalate issues

## System Architecture

```
WILLOW Sync System
├── core/                    # Core coordination system
│   ├── willow_master_prompt.md      # Enhanced master prompt
│   └── willow_coordinator.py        # Main coordinator
├── automation/             # Production automation
│   └── willow_automation.py         # Deployment automation
├── coordination/           # Communication systems
│   └── gmail_coordinator.py         # Email coordination
├── validation/             # Quality assurance
│   └── quality_validator.py         # Validation system
└── docs/                   # Documentation
    ├── README.md                    # This file
    ├── INSTALLATION.md              # Installation guide
    └── API.md                       # API documentation
```

## Installation

### Prerequisites
- Python 3.8+
- Git
- GitHub account with appropriate permissions
- Gmail account with app passwords enabled (for email coordination)

### Quick Installation

1. **Clone Repository**
   ```bash
   git clone https://github.com/HVSCMA/hvscma-cmas.git
   cd hvscma-cmas/sync
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp config/config.example.json config/config.json
   # Edit config.json with your settings
   ```

4. **Initialize WILLOW**
   ```bash
   python core/willow_coordinator.py WILLOW_SYNC:INIT:PRODUCTION
   ```

### Production Setup

For production deployment, use the automated setup:

```bash
python automation/willow_automation.py \
  --github-token YOUR_TOKEN \
  --repo HVSCMA/hvscma-cmas \
  --environment production
```

## Configuration

### Core Configuration (config/config.json)
```json
{
  "coordination": {
    "max_agents": 10,
    "task_timeout": 3600,
    "retry_attempts": 3
  },
  "github": {
    "repository": "HVSCMA/hvscma-cmas",
    "branch": "main",
    "auto_deploy": true
  },
  "email": {
    "smtp_server": "smtp.gmail.com",
    "imap_server": "imap.gmail.com",
    "check_interval": 300
  },
  "validation": {
    "auto_validate": true,
    "quality_threshold": 80,
    "security_scan": true
  }
}
```

### Gmail Configuration
1. Enable 2-factor authentication on Gmail
2. Generate app password for WILLOW
3. Configure email settings in config file

### GitHub Configuration
1. Create personal access token with repo permissions
2. Configure repository settings
3. Set up webhook for automatic deployments (optional)

## Usage

### Command Line Interface

**Start WILLOW Coordinator:**
```bash
python core/willow_coordinator.py WILLOW_SYNC:INIT:PROJECT_NAME
```

**Deploy to Production:**
```bash
python automation/willow_automation.py \
  --github-token TOKEN \
  --repo OWNER/REPO \
  --environment production
```

**Start Gmail Monitoring:**
```bash
python coordination/gmail_coordinator.py \
  --username your@gmail.com \
  --password app_password \
  --mode monitor
```

**Run Quality Validation:**
```bash
python validation/quality_validator.py /path/to/validate \
  --output quality_report.json
```

### Python API

**Basic Coordination:**
```python
from core.willow_coordinator import WillowCoordinator
import asyncio

async def main():
    coordinator = WillowCoordinator()

    # Initialize project
    result = await coordinator.execute_sync_command(
        coordinator.parse_sync_command("WILLOW_SYNC:INIT:MY_PROJECT")
    )
    print(result)

asyncio.run(main())
```

**Automated Deployment:**
```python
from automation.willow_automation import WillowAutomation, DeploymentConfig

config = DeploymentConfig(
    target_environment="production",
    github_repo="OWNER/REPO"
)

automation = WillowAutomation(config)
result = await automation.run_full_deployment("github_token")
```

### Email-Based Coordination

Send emails to your configured Gmail address with WILLOW commands:

**Subject**: WILLOW Sync Request
**Body**: 
```
Please deploy the latest changes to production.

WILLOW_SYNC:DEPLOY:PRODUCTION:AUTO
```

WILLOW will automatically process the email and send status updates.

## Monitoring and Logging

### Log Files
- `/var/log/willow_sync.log` - Main coordinator logs
- `/var/log/willow_gmail.log` - Email coordination logs
- `/var/log/willow_quality.log` - Quality validation logs
- `/var/log/willow_automation.log` - Deployment logs

### Monitoring Commands
```bash
# Check system status
python core/willow_coordinator.py WILLOW_SYNC:STATUS:ALL

# Monitor specific metrics
python core/willow_coordinator.py WILLOW_SYNC:MONITOR:PERFORMANCE

# View recent activity
tail -f /var/log/willow_sync.log
```

## Troubleshooting

### Common Issues

**1. GitHub Authentication Failed**
```bash
# Verify token permissions
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
```

**2. Email Connection Issues**
```bash
# Test email configuration
python coordination/gmail_coordinator.py --mode check-once
```

**3. Quality Validation Failures**
```bash
# Run detailed validation
python validation/quality_validator.py /path/to/check --output detailed_report.json
```

**4. Deployment Errors**
```bash
# Check deployment logs
tail -n 50 /var/log/willow_automation.log
```

### Debug Mode
Enable debug logging by setting environment variable:
```bash
export WILLOW_DEBUG=1
```

## API Reference

### WILLOW Coordinator API

**WillowCoordinator Class**
- `parse_sync_command(command_str)` - Parse command string
- `execute_sync_command(command)` - Execute parsed command
- `handle_init(command)` - Initialize coordination
- `handle_deploy(command)` - Execute deployment
- `handle_validate(command)` - Run validation

### Automation API

**WillowAutomation Class**
- `deploy_to_github(token)` - Deploy to GitHub repository  
- `validate_deployment()` - Validate deployed system
- `run_full_deployment(token)` - Complete deployment process

### Email Coordination API

**GmailCoordinator Class**
- `check_for_new_emails()` - Check for WILLOW tasks
- `process_email_tasks()` - Process pending tasks
- `send_status_email(recipient, result)` - Send status update

### Quality Validator API

**QualityValidator Class**
- `validate_target(path)` - Comprehensive validation
- `validate_file_structure(path)` - Structure validation
- `validate_content_security(path)` - Security scanning
- `generate_report_json(report, path)` - Generate reports

## Security Considerations

### Best Practices
1. **Token Management**: Store GitHub tokens securely
2. **Email Security**: Use app passwords, not account passwords
3. **File Permissions**: Ensure appropriate file access controls
4. **Network Security**: Use HTTPS/TLS for all communications
5. **Validation**: Always validate inputs and outputs
6. **Logging**: Monitor logs for suspicious activity

### Security Features
- Automated security scanning of code and content
- Hardcoded secret detection
- File permission validation
- Input sanitization and validation
- Comprehensive audit logging

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/name`
3. Make changes and test thoroughly
4. Run quality validation: `python validation/quality_validator.py .`
5. Submit pull request with detailed description

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run quality checks
python validation/quality_validator.py . --output qa_report.json
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- GitHub Issues: https://github.com/HVSCMA/hvscma-cmas/issues
- Email: support@hvscma.org
- Documentation: https://github.com/HVSCMA/hvscma-cmas/wiki

## Changelog

### Version 2.0.0 (Current)
- Enhanced sync command system
- Gmail coordination integration
- Comprehensive quality validation
- Automated deployment pipeline
- Production monitoring and alerting

### Version 1.0.0
- Basic WILLOW coordination system
- Multi-agent orchestration
- GitHub integration
