import psycopg2
from contextlib import closing
 
# Database connection details
DB_HOST = "oneopsdb-np.ebiz.verizon.com"
DB_PORT = 5432
DB_NAME = "oneops"
DB_USER = "cts_user"
DB_PASSWORD = "cts123"
 
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
    query1 = "SELECT * FROM analytics.all_alerts"
    details_fetch = get_ith_value(i, "alert_last_reported_time", query1)
    print(details_fetch)
    detail_fetch2 = get_ith_value(i, "parent_incident_id", query1)
    print("details_fetch2:", detail_fetch2)
    return details_fetch, detail_fetch2
 
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
                    return "No data found", "No data found"
 
                col_names = [desc[0] for desc in cursor.description]
                incident_id_index = col_names.index("device_id")
                resolution_index = col_names.index("resolution")
 
                det_fetch = rows[0][incident_id_index]
                det_fetch2 = rows[0][resolution_index]
 
                print("det_fetch:", det_fetch)
                print("det_fetch2:", det_fetch2)
 
                return det_fetch, det_fetch2
    except Exception as e:
        return f"Error: {e}", None
 
def main():
    query1 = "SELECT * FROM analytics.all_alerts"
 
    with closing(psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM analytics.all_alerts")
            row_count = cursor.fetchone()[0]
 
            for i in range(row_count):
                ays_inc_num_fetched = get_ith_value(i, "ays_incident_number", query1)
 
                if not ays_inc_num_fetched or "Error" in str(ays_inc_num_fetched):
                    # Alarm has no incident_id or there's an error
                    details_fetch, detail_fetch2 = fetch_alarms_details(i)
                else:
                    cursor.execute("SELECT COUNT(*) FROM datacollection.oneops_gcp_outage_data WHERE number = %s", (ays_inc_num_fetched,))
                    ays_count = cursor.fetchone()[0]
 
                    if ays_count == 1:
                        # Incident exists in incident_resolutions
                        det_fetch, det_fetch2 = fetch_alarm_details_also_gcp_details(ays_inc_num_fetched)
                    else:
                        # Incident not found in incident_resolutions
                        details_fetch, detail_fetch2 = fetch_alarms_details(i)
 
if __name__ == "__main__":
    main()
