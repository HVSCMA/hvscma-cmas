# FUB API Credentials Setup

## Creating FUB Basic Auth Credential in N8N

1. **Navigate to Credentials**
   - In N8N, go to Settings → Credentials
   - Click "Create New Credential"

2. **Select Credential Type**
   - Choose "HTTP Basic Auth"
   - Name: `fub-basic-auth`

3. **Configure Authentication**
   - **Username**: `fka_0oHt62ZolMwCPYGPvnAISdbsYxDhH4NWbH`
   - **Password**: (leave completely empty)

4. **Save and Test**
   - Click "Save" 
   - Test with FUB API endpoint: `https://api.followupboss.com/v1/identity`

## Important Notes
- The FUB API key acts as both username and password
- Leave password field completely empty
- This credential will be used by all FUB-related nodes

## Verification
Use this Python code to verify the credential works:

```python
import requests, base64
api_key = "fka_0oHt62ZolMwCPYGPvnAISdbsYxDhH4NWbH"
credentials = base64.b64encode(f"{api_key}:".encode()).decode()
headers = {"Authorization": f"Basic {credentials}"}
response = requests.get("https://api.followupboss.com/v1/identity", headers=headers)
print(f"Status: {response.status_code}")
```

Expected result: Status 200 with user information.
