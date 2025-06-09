import requests
import uuid
 
class VegasClient:
    """
    Use an instance of this class to make requests to the Vegas API.
    """
    _API_ENDPOINT = "http:/"
 
    def __init__(self, api_key, client_id):
        """
        :param str api_key: Vegas API key.
        :param str client_id: Vegas Client ID.
        """
        self.api_key = api_key
        self.client_id = client_id
 
    def generate_uuid(self):
        """
        Generate a UUID.
        :return: str
        """
        return str(uuid.uuid4())
 
    def make_request(self, use_case, context_id, preSeedInjectionMap, parameters=None):
        """
        Make a request to the Vegas API.
 
        :param str use_case: Registered use case name with VEGAS.
        :param str context_id: Registered context name with VEGAS.
        :param dict preSeedInjectionMap: JSON object with key-value pairs for dynamic runtime variables.
        :param dict parameters: Optional model parameters to tune the response.
        :return: dict
        """
        transaction_metadata = {
            "clientId": self.client_id,
            "clientTransactionId": self.generate_uuid()
        }
 
        payload = {
            "inference_type": "generate",
            "user_id": "varan96",
            "agent_id": use_case,
            "task_id": context_id,
            "model": "VEGAS",
            "variables": preSeedInjectionMap
        }
 
        if parameters:
            payload["parameters"] = parameters
 
        headers = {
            "Content-Type": "application/json",
            "X-api-key": self.api_key
        }
 
        response = requests.post(self._API_ENDPOINT, json=payload, headers=headers)
        return response.json()
 
# Instantiate the client
newclient = VegasClient("nspr-np-6af9bc82-6346-4292-aae8-1d94adb82304", "10221")
 
# Define variables
field = "Heap Memory Usage"
vsad = "IBW"
policy_name = "OSQAR EKS API CRU/Mem Monitoring"
condition_name = "Heap Memory Usage (High)"
entity_type = "APPLICATION"
entity_name = "osgar-user-management-prod-east"
alert_description = (
    "Heap memory usage > 80% for at least 5 minutes on osgar-user-management-prod-east. "
    "Incident Link: https://aiops.service.newrelic.com/accounts/2327062/incidents/5dc38c83-c467-4386-9ee0-b48816"
)
is_root_incident = "True"
alert_start_time = "2025-03-23 13:33:00 +0530"
priority = "Critical"
alert_end_time = "2025-03-23 13:33:00 +0530"
data_source = "New Relic"
record_last_update_time = "2025-03-23 16:44:54 +0530"
alert_last_reported_time = "2025-03-23 16:44:54 +0530"
environment = "Production"
 
# Build the preSeedInjectionMap
preSeedInjectionMap = {
    "field": field,
    "vsad": vsad,
    "policy_name": policy_name,
    "condition_name": condition_name,
    "entity_type": entity_type,
    "entity_name": entity_name,
    "alert_description": alert_description,
    "is_root_incident": is_root_incident,
    "alert_start_time": alert_start_time,
    "priority": priority,
    "alert_end_time": alert_end_time,
    "data_source": data_source,
    "record_last_update_time": record_last_update_time,
    "alert_last_reported_time": alert_last_reported_time,
    "environment": environment
}
 
# Make the API request
response = newclient.make_request('dcpaautomation', 'dcpanba', preSeedInjectionMap, {})
print(response)
