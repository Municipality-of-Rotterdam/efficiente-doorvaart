import requests, os, json, response
from configuratie import confDetails
from jsonschema import validate, ValidationError, RefResolver
from scipy.signal import get_window, lfilter, resample, resample_poly, tukey, welch

conf = confDetails()

def getObject(requestUrl):
    
    data = requests.get(conf['base_url_objects'] + requestUrl, headers={'Authorization': 'Token ' + conf['token_objects']} )
    dataJson = data.json()

    for i in dataJson['results']:
        print(str(i["record"]["data"]))
        
def getBrugObjecttype(requestUrl):
    data = requests.get(conf['base_url_object_types'] + requestUrl, headers={'Authorization': 'Token ' + conf['uuid_bruggen']})
    dataJson = data.json()
    
    if response.status_code == 200:
        try:
            dataJson = response.json()
        except json.JSONDecodeError:
            print("Error parsing JSON")
    else:
        print(f"Request failed with status code {response.status_code}")

    for i in dataJson['results']:
        print(str(i["record"]["data"]))
        
getBrugObjecttype('/objects?type=http://localhost:8001/api/v1/objecttypes/5dedd5fb-6731-4225-8527-f75d30c74034')

def alleObjecttypes(headers = {"Authorization": "Token " + conf['token_object_types'], "Content-Type": "application/json"}):
    response = requests.get(f"{conf['base_url_object_types']}/objecttypes", headers=headers)
   
    if response.status_code == 200:
        objecttypes = response.json()
       
        for objecttype in objecttypes:
            objecttype_details = [f"{key}: {value}" for key, value in objecttype.items()]
            print('\n'.join(objecttype_details))
            print('\n---\n') 
    else:
        print("Fout bij het ophalen van objecttypes:", response.text)
        
def deleteObject(requestUrl):
    data = requests.delete(requestUrl, headers={'Authorization': 'Token ' + conf['token_objects']} )

def putObject(requestUrl, data):
    response = requests.put(requestUrl, json=data, headers={'Authorization': 'Token ' + conf['token_objects']})
    
    if response.status_code == 200:
        print("Object updated successfully")
    else:
        print("Fout:", response.text)
        

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Load the schema from the local file
schema_path = os.path.join(script_dir, 'jsonschema.txt')
with open(schema_path, 'r') as f:
    schema = json.load(f)

# Create a RefResolver with the base URI pointing to the local directory
base_uri = 'file://' + os.path.abspath(os.path.dirname(schema_path)) + '/'
resolver = RefResolver(base_uri=base_uri, referrer=schema)

def send_data(request_url, data):
    """
    Sends data to the specified request URL, with authorization and JSON schema validation.
    
    Args:
        request_url (str): The URL to send the data to.
        data (dict): The data to be sent, in the form of a dictionary.
    
    Returns:
        None
    """
    # Validate the data against the JSON schema
    try:
        validate(instance=data, schema=schema, resolver=resolver)
    except ValidationError as e:
        print(f"Error validating data: {e}")
        return

    # Add the required headers
    headers = {
        'Authorization': f'Token {conf["token_objects"]}',
        'Content-Crs': 'EPSG:4326'
    }

    # Send the data using a POST request
    response = requests.post(request_url, json=data, headers=headers)

    # Check the response status code
    if response.status_code == 200 or response.status_code == 201:
        print("Object created successfully")
    else:
        print(f"Error creating object: {response.text}")


data = {"boomhoogteactueel": 123, "leeftijd": 1234, "typeVersion": 1, "startAt": "2021-01-01", "type": "http://localhost:8001/api/v1/objecttypes/5dedd5fb-6731-4225-8527-f75d30c74034"}
send_data(f"{conf['base_url_objects']}/objects", data)

# getObject('/objects?type=http://localhost:8001/api/v1/objecttypes/feeaa795-d212-4fa2-bb38-2c34996e5702')



