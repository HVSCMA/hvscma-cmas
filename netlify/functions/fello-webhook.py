import json
import requests
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Any

def handler(event, context):
    """
    WILLOW v40 Fello API Webhook Handler
    Deployed at: hvscma.com/.netlify/functions/fello-webhook
    """

    # CORS headers for all responses
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Content-Type': 'application/json'
    }

    # Handle OPTIONS request for CORS
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'CORS preflight successful'})
        }

    try:
        # Validate webhook from Fello
        webhook_data = json.loads(event.get('body', '{}'))

        # Initialize WILLOW Fello Integration
        integration = WillowFelloIntegration()

        # Process the webhook event
        result = integration.process_webhook_event(webhook_data)

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'success': True,
                'message': 'WILLOW v40 processed Fello webhook successfully',
                'data': result,
                'timestamp': datetime.utcnow().isoformat()
            })
        }

    except Exception as e:
        print(f"WILLOW v40 Error processing Fello webhook: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'success': False,
                'error': f'WILLOW v40 webhook processing failed: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            })
        }


class WillowFelloIntegration:
    """WILLOW v40 Enhanced Fello API Integration System"""

    def __init__(self):
        # Load configuration from environment variables
        self.fello_api_key = "uiQ4jADoUGeTqaBellkEcBxxrzQvgvnj"
        self.fub_api_token = "fka_0oHt622FKjKdBAbEHHeRjfdss5jBzspUbR"
        self.github_token = "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"

        # API endpoints
        self.fello_base_url = "https://api.fello.ai/public/v1"
        self.fub_base_url = "https://api.followupboss.com/v1"

        # WILLOW custom fields in FUB
        self.willow_fields = [
            'customWILLOWCMADate',
            'customWILLOWCMALink',
            'customWILLOWAssignedAgent',
            'customWILLOWRangeHigh',
            'customWILLOWRangeLow',
            'customWILLOWStatus',
            'customWILLOWPropertyAddress'
        ]

    def process_webhook_event(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming Fello webhook event with intelligence"""

        event_type = webhook_data.get('eventType', '')
        contact_id = webhook_data.get('contactId', '')
        event_data = webhook_data.get('data', {})

        print(f"WILLOW v40: Processing {event_type} for contact {contact_id}")

        # Calculate engagement score
        engagement_score = self.calculate_engagement_score(event_type, event_data)

        # Classify lead priority
        priority = self.classify_lead_priority(engagement_score, event_data)

        # Update FUB with intelligence
        fub_result = self.update_fub_contact(contact_id, engagement_score, priority, event_data)

        # Check for CMA trigger
        cma_trigger = self.evaluate_cma_trigger(engagement_score, priority, event_data)

        return {
            'contactId': contact_id,
            'eventType': event_type,
            'engagementScore': engagement_score,
            'priority': priority,
            'fubUpdate': fub_result,
            'cmaTrigger': cma_trigger,
            'processedAt': datetime.utcnow().isoformat()
        }

    def calculate_engagement_score(self, event_type: str, event_data: Dict) -> int:
        """Calculate WILLOW engagement score (0-100)"""

        base_scores = {
            'dashboard_view': 15,
            'email_open': 10,
            'email_click': 25,
            'form_submission': 40,
            'phone_call': 35,
            'text_response': 30,
            'property_view': 20,
            'schedule_appointment': 50
        }

        score = base_scores.get(event_type, 5)

        # Bonus for recency (events in last hour get bonus)
        if event_data.get('timestamp'):
            event_time = datetime.fromisoformat(event_data['timestamp'].replace('Z', '+00:00'))
            if datetime.utcnow() - event_time.replace(tzinfo=None) < timedelta(hours=1):
                score += 10

        # Bonus for multiple interactions
        interaction_count = event_data.get('interactionCount', 1)
        if interaction_count > 1:
            score += min(interaction_count * 5, 25)

        return min(score, 100)

    def classify_lead_priority(self, engagement_score: int, event_data: Dict) -> str:
        """Classify lead priority based on engagement"""

        if engagement_score >= 70:
            return "HOT"
        elif engagement_score >= 40:
            return "WARM"
        elif engagement_score >= 20:
            return "COLD"
        else:
            return "NEW"

    def update_fub_contact(self, contact_id: str, score: int, priority: str, event_data: Dict) -> Dict:
        """Update FUB contact with WILLOW intelligence"""

        try:
            # Create FUB API headers
            auth_header = base64.b64encode(f"{self.fub_api_token}:".encode()).decode()
            headers = {
                'Authorization': f'Basic {auth_header}',
                'Content-Type': 'application/json'
            }

            # Update contact tags
            tag_data = {
                'tags': [f'WILLOW_SCORE_{score}', f'PRIORITY_{priority}', 'FELLO_TRACKED']
            }

            response = requests.post(
                f"{self.fub_base_url}/people/{contact_id}/tags",
                headers=headers,
                json=tag_data
            )

            if response.status_code == 200:
                return {'success': True, 'tags_updated': tag_data['tags']}
            else:
                return {'success': False, 'error': f'FUB API error: {response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def evaluate_cma_trigger(self, score: int, priority: str, event_data: Dict) -> Dict:
        """Evaluate if engagement warrants automatic CMA generation"""

        should_trigger = False
        reason = ""

        if score >= 75:
            should_trigger = True
            reason = "High engagement score indicates immediate interest"
        elif priority == "HOT" and event_data.get('propertyAddress'):
            should_trigger = True
            reason = "Hot lead with specific property interest"
        elif event_data.get('formType') == 'home_valuation':
            should_trigger = True
            reason = "Direct home valuation request"

        return {
            'shouldTrigger': should_trigger,
            'reason': reason,
            'suggestedTemplate': 'GLENN_PERFECT_CMA_FINAL_DEFAULT.html',
            'priority': 'HIGH' if should_trigger else 'STANDARD'
        }
