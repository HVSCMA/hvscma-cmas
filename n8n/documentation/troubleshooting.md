# WILLOW v32.0 - Troubleshooting Guide

## 🚨 Common Issues & Solutions

### 1. FUB API Authentication Errors

#### Error: "401 Unauthorized"
**Cause**: Wrong authentication method
**Solution**: 
- Ensure using HTTP Basic Auth, not Bearer token
- Username: `fka_0oHt62ZolMwCPYGPvnAISdbsYxDhH4NWbH`
- Password: Leave empty

#### Error: "Invalid fields in request body"
**Cause**: Using incorrect field names
**Solution**:
- Use `name` not `description` for tasks
- Use `personId` not `person_id` 
- Use `dueDate` in `YYYY-MM-DD` format

### 2. Webhook Issues

#### Error: "Webhook not triggering"
**Solutions**:
1. Check webhook URL is correct
2. Verify GitHub webhook is active
3. Check N8N workflow is activated
4. Test with manual POST request

#### Error: "Webhook timeout"
**Solutions**:
1. Check N8N server status
2. Verify network connectivity
3. Increase timeout settings
4. Check for resource limitations

### 3. Task Creation Failures

#### Error: "Person not found"
**Solutions**:
1. Use default person ID: 1903
2. Create person first before task
3. Verify person exists in FUB

#### Error: "Date format invalid"
**Solutions**:
1. Use `YYYY-MM-DD` format only
2. Don't include time stamps
3. Ensure date is in the future

### 4. Agent Assignment Issues

#### Wrong agent assigned
**Solutions**:
1. Check property address formatting
2. Verify agent IDs are correct
3. Update assignment logic if needed

### 5. Workflow Execution Errors

#### Error: "Node execution failed"
**Debug Steps**:
1. Check N8N execution logs
2. Verify all credentials are configured
3. Test each node individually
4. Check input data format

## 📊 Monitoring & Logging

### N8N Execution Logs
- Go to **Executions** tab in N8N
- Filter by workflow name
- Check error details and stack traces

### FUB API Response Codes
- **200**: Success
- **400**: Bad Request (field validation)
- **401**: Unauthorized (authentication)
- **404**: Not Found (resource missing)
- **500**: Server Error (FUB issue)

## 🛠️ Advanced Debugging

### Test FUB API Directly
```bash
# Test authentication
curl -X GET "https://api.followupboss.com/v1/users"   -H "Authorization: Basic $(echo -n 'fka_0oHt62ZolMwCPYGPvnAISdbsYxDhH4NWbH:' | base64)"

# Test task creation
curl -X POST "https://api.followupboss.com/v1/tasks"   -H "Authorization: Basic $(echo -n 'fka_0oHt62ZolMwCPYGPvnAISdbsYxDhH4NWbH:' | base64)"   -H "Content-Type: application/json"   -d '{
    "name": "Test Task",
    "personId": 1903,
    "dueDate": "2025-07-23"
  }'
```

### N8N Workflow Debug Mode
1. Open workflow in N8N
2. Click **Execute Workflow** 
3. Provide test data
4. Check each node output
5. Identify failure points

## 📞 Support Contacts
- **Technical Issues**: Check N8N community forum
- **FUB API Issues**: Follow Up Boss support
- **WILLOW System**: Glenn Fitzgerald - Hudson Valley SOLD
