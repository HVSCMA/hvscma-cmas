# WILLOW v32.0 - API Credentials Configuration

## 🔐 Follow Up Boss API Setup

### API Key Information
- **API Key**: `fka_0oHt62ZolMwCPYGPvnAISdbsYxDhH4NWbH`
- **Authentication Method**: HTTP Basic Auth
- **Base URL**: `https://api.followupboss.com/v1`

### N8N Credential Configuration

#### 1. HTTP Basic Auth Credential
```
Name: FUB API Credentials
Type: HTTP Basic Auth
Username: fka_0oHt62ZolMwCPYGPvnAISdbsYxDhH4NWbH  
Password: (leave empty)
```

#### 2. Test Connection
Use N8N's test feature to validate:
```bash
curl -X GET "https://api.followupboss.com/v1/users"   -H "Authorization: Basic $(echo -n 'fka_0oHt62ZolMwCPYGPvnAISdbsYxDhH4NWbH:' | base64)"
```

### FUB Team Member IDs
- **Glenn Fitzgerald**: 1 (Primary/Default)
- **Heather Martin**: 2  
- **Justin Phillips**: 6
- **Lloyd Gray**: 4

### API Endpoints Used
- `POST /v1/tasks` - Create follow-up tasks
- `POST /v1/notes` - Create activity notes
- `GET /v1/people` - Search for clients
- `GET /v1/users` - Team member validation

## 🔧 Advanced Configuration

### Custom Person ID Mapping
Default person ID: 1903 (Test person)
Override in webhook payload: `"person_id": YOUR_PERSON_ID`

### Date Format Requirements
- Due dates: `YYYY-MM-DD` format
- Timezone: UTC (converted automatically)

## 🛡️ Security Best Practices
- Keep API keys secure and rotate regularly
- Use environment variables in production
- Monitor API usage and rate limits
- Implement proper error handling
