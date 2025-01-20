import requests
import json
from datetime import datetime
import hashlib
# For demonstration, using a simple in-memory set
processed_incident_hashes = set()


def get_incident_hash(incident):
    """Generates a unique hash for an incident."""
    incident_string = json.dumps(incident, sort_keys=True).encode('utf-8')
    return hashlib.sha256(incident_string).hexdigest()


def fetch_incidents(username, password):
    """Fetches incident data from the API."""
    api_url = "https://exercisedev.dsec.it/api/incidents"
    try:
        response = requests.get(api_url, auth=(username, password)) # Basic Auth with username and password
        response.raise_for_status()  # Raise an exception for bad status codes (404, 500, etc.)
        return response.json()  # Parse the JSON response
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def process_incident(incident):
    """Performs some processing on an incident and returns relevant data."""

    processed_data = {
        "description": incident.get('description', 'N/A'),
        "type": incident.get('type', 'N/A'),
        "priority": incident.get('priority', 'N/A'),
        "status": incident.get('status', 'N/A'),
    }

    creation_time = incident.get('creation_time', None)
    if creation_time:
        try:
          creation_time_datetime = datetime.fromisoformat(creation_time.replace('Z', '+00:00')) # Handle ISO formats
          processed_data["creation_time"] = creation_time_datetime.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError as e:
            processed_data["creation_time"] = f"Error parsing datetime: {creation_time}, error {e}"
    else:
      processed_data["creation_time"] = "N/A"

    return processed_data

def create_case(incident_data):
    """Creates a 'case' in the simple orchestrator (in-memory set here)."""

    incident_hash = get_incident_hash(incident_data)

    if incident_hash in processed_incident_hashes:
        print(f"Skipping duplicate case for incident: {incident_hash}")
        return

    # For now just print the case data here
    print(f"Creating new case: {incident_hash}")
    for key, value in incident_data.items():
        print(f"    {key}: {value}")

    processed_incident_hashes.add(incident_hash)


def main():
    username = "its"
    password = "xzgfXgwroJBGGt6Q" # Using the password provided
    incidents = fetch_incidents(username, password) # We now pass the password in

    if incidents:
        if isinstance(incidents, list):
            for incident in incidents:
               processed_incident = process_incident(incident)
               create_case(processed_incident)

        else:
           print("The API response was not in the expected JSON list format.")

    else:
        print("No incidents were received from the API")

    print("Done processing incidents")


if __name__ == "__main__":
    main()