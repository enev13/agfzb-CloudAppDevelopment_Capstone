import os
import requests
import json
# import related models here
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
import requests
import json
from .models import CarDealer
from requests.auth import HTTPBasicAuth

class RestException(Exception):
    pass

def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        if 'api_key' in kwargs:
            response = requests.get(url, headers={'Content-Type': 'application/json'}, params=kwargs, 
            auth=HTTPBasicAuth('apikey', kwargs['api_key']))
        else:
            response = requests.get(url, headers={'Content-Type': 'application/json'}, params=kwargs)
    except Exception as e:
        # If any error occurs
        print("Network exception occurred: {} ".format(e))
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    response = requests.post(url, headers={'Content-Type': 'application/json'}, params=kwargs, json=json_payload)
    if response.status_code != 200:
        raise RestException('the call to url: {} return status {} message: {}'.format(url, response.status_code, response.text))
    return response.text

# Create a get_dealers_from_cf method to get dealers from a cloud function
def get_dealers_from_cf(url, **kwargs):
    '''
    Call get_request() with specified arguments
    Parse JSON results into a CarDealer object list
    '''
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, **kwargs)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["entries"]
        # For each dealer object
        for dealer in dealers:
            # Create a CarDealer object with values in `dealer` object
            dealer_obj = CarDealer(address=dealer["address"], 
                                   city=dealer["city"], 
                                   full_name=dealer["full_name"],
                                   id=dealer["id"], 
                                   lat=dealer["lat"], 
                                   long=dealer["long"],
                                   short_name=dealer["short_name"],
                                   st=dealer["st"], 
                                   zip=dealer["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_reviews_from_cf(url, dealerId):
    '''
    Call get_request() with specified arguments
    Parse JSON results into a DealerView object list
    '''
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, dealerId=dealerId)
    if json_result:
        # Get the row list in JSON as reviews
        reviews = json_result["entries"]
        for review in reviews:
            # Create a DealerReview object with values in `review` object
            review_obj = DealerReview(review)
            results.append(review_obj)

    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(text):
    '''
    Call get_request() with specified arguments
    Parse JSON results into a CarDealer object list
    '''
    api_key = os.environ['NLU_API_KEY']
    url = os.environ['NLU_URL']  + '/v1/analyze'

    params = dict()
    params["text"] = text
    params["version"] = '2021-03-25'
    params["features"] = {"sentiment": {}}
    response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
                                        auth=HTTPBasicAuth('apikey', api_key))
    if response.status_code == 422:
        return 'neutral'
    try:
        label = response.json()['sentiment']['document']['label']
    except Exception:
        raise Exception('Abnormal return from NLU with params:'+response.text)
    return label

load_dotenv()
