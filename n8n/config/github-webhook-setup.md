# GitHub Webhook Configuration

## Setting Up GitHub Webhook for N8N

### 1. Generate N8N Webhook URL
In your N8N workflow:
1. Click on the "GitHub CMA Trigger" node
2. Copy the webhook URL provided
3. Note: URL format will be `https://your-n8n-instance.com/webhook/...`

### 2. Configure GitHub Repository Webhook
1. Go to GitHub repository: `https://github.com/HVSCMA/hvscma-cmas`
2. Navigate to Settings → Webhooks
3. Click "Add webhook"

### 3. Webhook Settings
- **Payload URL**: Your N8N webhook URL
- **Content type**: `application/json`
- **Secret**: (optional, leave empty for now)
- **SSL verification**: Enable SSL verification

### 4. Event Selection
Select "Let me select individual events":
- ☑️ **Pushes** (required)
- ☐ Pull requests (optional)
- ☐ Issues (not needed)

### 5. Activation
- ☑️ **Active** (ensure webhook is active)
- Click "Add webhook"

## Testing Webhook

### Manual Test
1. Deploy any `.html` file to the repository
2. Check N8N workflow executions
3. Verify webhook payload is received
4. Monitor workflow execution logs

### Validation Steps
1. Webhook shows green checkmark in GitHub
2. Recent deliveries show 200 status codes
3. N8N execution history shows triggered workflows
4. FUB system receives tasks and activities

## Troubleshooting
- **Red X on webhook**: Check N8N URL accessibility
- **No workflow triggers**: Verify webhook is active and N8N workflow is enabled
- **Payload issues**: Check GitHub webhook delivery details for error messages
