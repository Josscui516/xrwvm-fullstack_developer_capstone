import requests
import os
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv(
    'backend_url', default="http://localhost:3030"
)

sentiment_analyzer_url = os.getenv(
    'sentiment_analyzer_url',
    default="http://localhost:5050/"
)

# ----------------------------------------
# GET request
# ----------------------------------------


def get_request(endpoint, **kwargs):
    request_url = backend_url + endpoint

    print("GET from {}".format(request_url))

    try:
        response = requests.get(request_url, params=kwargs)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Network exception occurred:", e)
        return None


# ----------------------------------------
# Sentiment Analysis
# ----------------------------------------


def analyze_review_sentiments(text):
    request_url = sentiment_analyzer_url + "analyze/" + text

    print("Analyzing sentiment from {}".format(request_url))

    try:
        response = requests.get(request_url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Error analyzing sentiment:", e)
        return None


# ----------------------------------------
# POST review
# ----------------------------------------


def post_review(data_dict):
    request_url = backend_url + "/insert_review"

    print("POST to {}".format(request_url))

    try:
        response = requests.post(request_url, json=data_dict)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Error posting review:", e)
        return None
