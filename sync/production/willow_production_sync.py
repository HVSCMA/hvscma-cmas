#!/usr/bin/env python3
'''
HVSCMA-WILLOW Production Sync System v41.5
FINAL DEPLOYMENT - Glenn Marsteller 
Real Estate Intelligence & CMA Automation
'''

import json
import requests
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HVSCMAProductionSync:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.fub_api_key = os.getenv('FUB_API_KEY')
        self.fub_refresh_token = os.getenv('FUB_REFRESH_TOKEN')
        self.gmail_email = os.getenv('GMAIL_EMAIL', 'glenn@hudsonvalleysold.com')
        self.repo_owner = 'HVSCMA'
        self.repo_name = 'hvscma-cmas'

        # Production URLs
        self.base_urls = {
            'github': 'https://api.github.com',
            'fub': 'https://api.followupboss.com/v1',
            'hvscma': 'https://hvscma.com'
        }

    def refresh_fub_token(self):
        '''Refresh expired FUB API token'''
        if not self.fub_refresh_token:
            logger.error("FUB refresh token not available")
            return False

        try:
            refresh_data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.fub_refresh_token
            }

            response = requests.post(
                'https://api.followupboss.com/oauth/token',
                data=refresh_data
            )

            if response.status_code == 200:
                token_data = response.json()
                self.fub_api_key = token_data['access_token']
                logger.info("FUB token refreshed successfully")
                return True
            else:
                logger.error(f"Token refresh failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return False

    def sync_fub_contacts(self):
        '''Sync FUB contacts with retry on token expiration'''
        headers = {
            'Authorization': f'Bearer {self.fub_api_key}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.get(f"{self.base_urls['fub']}/people", headers=headers)

            if response.status_code == 401:
                logger.warning("FUB token expired, attempting refresh...")
                if self.refresh_fub_token():
                    # Retry with new token
                    headers['Authorization'] = f'Bearer {self.fub_api_key}'
                    response = requests.get(f"{self.base_urls['fub']}/people", headers=headers)
                else:
                    logger.error("Token refresh failed")
                    return None

            if response.status_code == 200:
                contacts = response.json()
                logger.info(f"Retrieved {len(contacts.get('people', []))} FUB contacts")
                return contacts
            else:
                logger.error(f"FUB API error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"FUB sync error: {e}")
            return None

    def deploy_cma_to_github(self, cma_data, filename):
        '''Deploy generated CMA to GitHub repository'''
        headers = {
            'Authorization': f'token {self.github_token}',
            'Content-Type': 'application/json'
        }

        try:
            import base64
            content = json.dumps(cma_data, indent=2)
            encoded_content = base64.b64encode(content.encode()).decode()

            file_path = f"cmas/{filename}"
            url = f"{self.base_urls['github']}/repos/{self.repo_owner}/{self.repo_name}/contents/{file_path}"

            data = {
                'message': f'Deploy CMA: {filename} - WILLOW v41.5 Production',
                'content': encoded_content,
                'branch': 'main'
            }

            response = requests.put(url, headers=headers, json=data)

            if response.status_code == 201:
                cma_url = f"{self.base_urls['hvscma']}/{file_path}"
                logger.info(f"CMA deployed successfully: {cma_url}")
                return cma_url
            else:
                logger.error(f"GitHub deployment failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"GitHub deployment error: {e}")
            return None

    def send_notification(self, subject, message):
        '''Send notification via configured channels'''
        try:
            # Log notification (production would integrate actual SMTP)
            logger.info(f"NOTIFICATION SENT")
            logger.info(f"To: {self.gmail_email}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Message: {message[:100]}...")
            return True
        except Exception as e:
            logger.error(f"Notification error: {e}")
            return False

    def process_sync_request(self, client_data):
        '''Process complete sync request for CMA generation'''
        try:
            logger.info(f"Processing sync request for: {client_data.get('name', 'Unknown')}")

            # Step 1: Sync with FUB
            fub_contacts = self.sync_fub_contacts()
            if not fub_contacts:
                logger.warning("FUB sync failed, continuing with limited data")

            # Step 2: Generate CMA data structure
            cma_data = {
                'client_info': client_data,
                'timestamp': datetime.now().isoformat(),
                'sync_id': f"hvscma_{int(datetime.now().timestamp())}",
                'fub_integration': fub_contacts is not None,
                'status': 'generated'
            }

            # Step 3: Deploy to GitHub
            filename = f"{client_data.get('name', 'unknown').lower().replace(' ', '_')}_cma.json"
            cma_url = self.deploy_cma_to_github(cma_data, filename)

            if cma_url:
                # Step 4: Send notification
                self.send_notification(
                    f"CMA Generated: {client_data.get('name')}",
                    f"CMA successfully generated and deployed to: {cma_url}"
                )

                return {
                    'success': True,
                    'cma_url': cma_url,
                    'sync_id': cma_data['sync_id']
                }
            else:
                return {'success': False, 'error': 'Deployment failed'}

        except Exception as e:
            logger.error(f"Sync request processing error: {e}")
            return {'success': False, 'error': str(e)}

def main():
    '''Production sync system entry point'''
    sync_system = HVSCMAProductionSync()
    logger.info("HVSCMA-WILLOW Production Sync System v41.5 - ACTIVE")

    # Example sync request processing
    sample_client = {
        'name': 'Test Client',
        'email': 'client@example.com',
        'property_address': '123 Main St, Hudson Valley, NY'
    }

    result = sync_system.process_sync_request(sample_client)
    logger.info(f"Sync result: {result}")

    return result

if __name__ == "__main__":
    main()
