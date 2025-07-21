# 🧠 WILLOW v32.0 - N8N CMA-FUB Automation Pipeline

## Overview
Complete N8N workflow automation for Hudson Valley SOLD real estate operations. Automatically synchronizes CMA deployments with Follow Up Boss CRM system.

## 🚀 Quick Start

### 1. Import Workflow
1. Copy the JSON from `workflows/willow-v32-production-pipeline.json`
2. In N8N, go to Workflows → Import from JSON
3. Paste the workflow JSON and save

### 2. Configure Credentials
Create N8N credential named `fub-basic-auth`:
- Type: HTTP Basic Auth
- Username: `fka_0oHt62ZolMwCPYGPvnAISdbsYxDhH4NWbH`
- Password: (leave empty)

### 3. Activate Workflow
- Enable the workflow in N8N
- Configure GitHub webhook to trigger on push events
- Test with a CMA deployment

## 📋 Workflow Components

### Nodes
1. **GitHub CMA Trigger** - Listens for repository push events
2. **Extract CMA Data** - Parses CMA deployment information
3. **Filter Valid CMAs** - Validates CMA files
4. **Prepare FUB Data** - Formats data for FUB integration
5. **Create FUB Task** - Creates follow-up task in FUB
6. **Create FUB Activity** - Adds activity note to client record
7. **Success Logger** - Logs completion and results

### Features
- ✅ Automatic CMA detection from GitHub deployments
- ✅ Smart client name extraction from filenames
- ✅ Property address parsing and formatting
- ✅ Agent assignment based on property location
- ✅ Automatic due date calculation (48 hours)
- ✅ Comprehensive error handling and logging
- ✅ FUB task and activity note creation

## 🔧 Configuration

### Agent Assignment Rules
- **Beacon/Fishkill**: Justin Phillips (ID: 6)
- **Cold Spring/Garrison**: Heather Martin (ID: 2)  
- **Poughkeepsie/Hyde Park**: Lloyd Gray (ID: 3)
- **Default**: Glenn Fitzgerald (ID: 1)

### File Naming Convention
CMAs should be named: `lastname-123-street-name.html`
- Example: `smith-456-main-street.html`
- Extracts: Client "Smith", Address "456 Main Street"

## 🎯 Testing

### Manual Test
1. Deploy a test CMA file to the repository
2. Check N8N execution log for workflow trigger
3. Verify task creation in Follow Up Boss
4. Confirm activity note is added to client record

### Validation
- GitHub webhook receives push events
- CMA files are detected and parsed correctly
- FUB API credentials are valid
- Tasks and activities are created successfully

## 🛠️ Troubleshooting

### Common Issues
1. **Webhook not triggering**: Check GitHub webhook configuration
2. **FUB API errors**: Verify credentials and API key validity
3. **Missing data**: Ensure CMA filenames follow naming convention
4. **Task creation fails**: Check person ID exists in FUB system

### Support
- Workflow Version: v32.0
- Created: {datetime.now().strftime('%Y-%m-%d')}
- Author: Glenn Fitzgerald / WILLOW v32.0
- Repository: HVSCMA/hvscma-cmas

## 📊 Monitoring
Monitor workflow executions in N8N dashboard. All successful executions will show:
- CMA property address
- Client name extracted
- FUB task ID created
- Activity note ID added
- Completion timestamp

---
*🧠 Powered by WILLOW v32.0 - 24/7 FUB Butler System*
