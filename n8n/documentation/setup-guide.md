# WILLOW v32.0 - N8N CMA-FUB Setup Guide

## 🚀 Quick Start Setup

### Prerequisites
- N8N instance running (v1.0 or later)
- Follow Up Boss account with API access
- GitHub account with webhook permissions
- Hudson Valley SOLD broker access

### 1. Import Workflow
1. Open your N8N instance
2. Go to **Workflows** → **Import from file**
3. Upload `workflows/cma-fub-sync-pipeline.json`
4. Click **Import workflow**

### 2. Configure FUB API Credentials
1. Go to **Settings** → **Credentials**
2. Click **Add credential** → **HTTP Basic Auth**
3. Set credential name: `FUB API Credentials`
4. Configure:
   - **Username**: `fka_0oHt62ZolMwCPYGPvnAISdbsYxDhH4NWbH`
   - **Password**: (leave empty)
5. Click **Save**

### 3. Activate Workflow
1. Open the imported workflow
2. Click **Activate** toggle (top right)
3. Copy the webhook URL from the first node
4. The webhook URL will be: `https://your-n8n.com/webhook/cma-deployed`

### 4. GitHub Integration
1. Go to `HVSCMA/hvscma-cmas` repository settings
2. Navigate to **Settings** → **Webhooks**
3. Click **Add webhook**
4. Configure:
   - **Payload URL**: Your webhook URL from step 3
   - **Content type**: `application/json`
   - **Events**: Select "Pushes" only
5. Click **Add webhook**

## 🎯 Testing the Workflow

### Manual Test
Send a POST request to your webhook URL:
```json
{
  "property_address": "123 Test Street, Beacon NY 12508",
  "client_name": "Test Client",
  "cma_url": "https://hvscma.com/test-cma",
  "person_id": 1903
}
```

### Expected Results
- ✅ FUB Task created with 48-hour due date
- ✅ FUB Activity Note with deployment details
- ✅ Agent assignment based on property location
- ✅ Comprehensive logging and error handling

## 🏡 Hudson Valley Agent Assignment Logic
- **Beacon/Fishkill**: Justin Phillips (Agent ID: 6)
- **Cold Spring/Garrison**: Heather Martin (Agent ID: 2)  
- **Poughkeepsie/Hyde Park**: Justin Phillips (Agent ID: 6)
- **Default**: Glenn Fitzgerald (Agent ID: 1)

## ⚠️ Troubleshooting
See `troubleshooting.md` for common issues and solutions.
