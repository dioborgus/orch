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
        response = requests.get(api_url, auth=(username, password))  # Basic Auth
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def process_incident(incident):
    """Performs processing on an incident, extracting case-related data."""
    description = incident.get('description', 'N/A')
    
    # Extract a title from the description. The incident ids are unique
    if description != "N/A":
        title = f"Incident: {description[17:40]}" #Extract the first 20 characters for the title for simplicity
    else:
         title = "No description available"

    processed_data = {
        "title": title,
        "description": description,
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


def create_case(incident_data, flask_api_url):
    """Creates a case using the Flask API."""
    incident_hash = get_incident_hash(incident_data)
    
    if incident_hash in processed_incident_hashes:
        print(f"Skipping duplicate case for incident: {incident_hash}")
        return
    
    # Prepare the case data for Flask
    case_data = {
        "title": incident_data.get('title'),
        "description": incident_data.get('description'),
        # you can add other parameters here, if you have severity or similar
    }
    
    try:
        response = requests.post(flask_api_url, json=case_data)
        response.raise_for_status()
        print(f"Successfully created case, id: {response.json()['id']}")
        processed_incident_hashes.add(incident_hash)
    except requests.exceptions.RequestException as e:
        print(f"Failed to create case: {e}")


def main():
    username = "its"
    password = "xzgfXgwroJBGGt6Q" # Correct password
    flask_api_url = "http://127.0.0.1:5000/api/cases" # Endpoint where we create the cases
    incidents = fetch_incidents(username, password) # Use correct credentials

    if incidents:
        if isinstance(incidents, list):
          for incident in incidents:
             processed_incident = process_incident(incident)
             create_case(processed_incident, flask_api_url)
        else:
           print("The API response was not in the expected JSON list format.")

    else:
      print("No incidents were received from the API")

    print("Done processing incidents")


if __name__ == "__main__":
    main()
