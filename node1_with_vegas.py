import psycopg2
from contextlib import closing
import requests
import uuid
 
# Database connection details
DB_HOST = "one"
DB_PORT = 5432
DB_NAME = "oneops"
DB_USER = ""
DB_PASSWORD = ""
 
class VegasClient:
    """
    Use an instance of this class to make requests to the Vegas API.
    """
    _API_ENDPOINT = "http"
 
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
 
def get_ith_value(i, column_name, query):
    try:
        with closing(psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
 
                if i < 0 or i >= len(rows):
                    return f"Error: i={i} is out of range. There are {len(rows)} rows."
 
                col_index = next((index for index, desc in enumerate(cursor.description) if desc[0] == column_name), None)
                if col_index is None:
                    return f"Error: Column '{column_name}' not found in query result."
 
                return rows[i][col_index]
    except Exception as e:
        return f"Error: {e}"
 
def fetch_alarms_details(i):
    query1 = "SELECT * FROM analytics.all_alerts LIMIT 10"
  
    # Get the necessary values from the database query
    field = get_ith_value(i, "field", query1)
    policy_name = get_ith_value(i, "policy_name", query1) 
    vsad = get_ith_value(i, "vsad", query1)
    condition_name = get_ith_value(i, "condition_name", query1)
    entity_type = get_ith_value(i, "entity_type", query1)
    entity_name = get_ith_value(i, "entity_name", query1)
    alert_description = get_ith_value(i, "alert_description", query1)
    is_root_incident = get_ith_value(i, "is_root_incident", query1)
    alert_start_time = get_ith_value(i, "alert_start_time", query1)
    priority = get_ith_value(i, "priority", query1)
    alert_end_time = get_ith_value(i, "alert_end_time", query1)
    data_source = get_ith_value(i, "data_source", query1)
    record_last_update_time = get_ith_value(i, "record_last_update_time", query1)
    alert_last_reported_time = get_ith_value(i, "alert_last_reported_time", query1)
    environment = get_ith_value(i, "environment", query1)
 
    # Create a dictionary to store the results
    result_dict = {
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
 
    # Instantiate the client
    newclient = VegasClient("nspr-np-6af9bc82-6346-4292-aae8-1d94adb82304", "10221")
 
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
   
    return f"{i}th alarm details", result_dict, response
def fetch_alarm_details_also_gcp_details(ays_inc_num_fetched):
    query2 = f"""
        SELECT analytics.all_alerts.*,  datacollection.oneops_gcp_outage_data.*
        FROM analytics.all_alerts
        JOIN  datacollection.oneops_gcp_outage_data
        ON analytics.all_alerts.ays_incident_number =  datacollection.oneops_gcp_outage_data.number
        WHERE analytics.all_alerts.ays_incident_number = %s
    """
    try:
        with closing(psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query2, (ays_inc_num_fetched,))
                rows = cursor.fetchall()
 
                if len(rows) == 0:
                    return f"{ays_inc_num_fetched}th alarm details", {"message": "No data found"}
 
                col_names = [desc for desc in cursor.description]
                incident_id_index = col_names.index("device_id")
                resolution_index = col_names.index("resolution")
 
                det_fetch = rows[incident_id_index]
                det_fetch2 = rows[resolution_index]
 
                print("det_fetch:", det_fetch)
                print("det_fetch2:", det_fetch2)
 
                return f"{ays_inc_num_fetched}th alarm details", {"device_id": det_fetch, "resolution": det_fetch2}
    except Exception as e:
        return f"Error: {e}", None
 
def main():
    query1 = "SELECT * FROM analytics.all_alerts LIMIT 10"
 
    with closing(psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM analytics.all_alerts LIMIT 10")
            row_count = cursor.fetchone()
 
            for i in range(10):
                ays_inc_num_fetched = get_ith_value(i, "ays_incident_number", query1)
 
                if not ays_inc_num_fetched or "Error" in str(ays_inc_num_fetched):
                    # Alarm has no incident_id or there's an error
                    details_fetch_title, details_fetch_dict, response = fetch_alarms_details(i)
                    print(details_fetch_title, details_fetch_dict, response)
                else:
                    cursor.execute("SELECT COUNT(*) FROM datacollection.oneops_gcp_outage_data WHERE number = %s", (ays_inc_num_fetched,))
                    ays_count = cursor.fetchone()
 
                    if ays_count == 1:
                        # Incident exists in incident_resolutions
                        det_fetch_title, det_fetch_dict = fetch_alarm_details_also_gcp_details(ays_inc_num_fetched)
                        print(det_fetch_title, det_fetch_dict)
                    else:
                        # Incident not found in incident_resolutions
                        details_fetch_title, details_fetch_dict, response = fetch_alarms_details(i)
                        print(details_fetch_title, details_fetch_dict, response)
 
if __name__ == "__main__":
    main()
