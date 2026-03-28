from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

import logging
import json

from .populate import initiate
from .models import CarMake, CarModel
from .restapis import get_request, analyze_review_sentiments, post_review


logger = logging.getLogger(__name__)


# ----------------------------------------
# Login
# ----------------------------------------


@csrf_exempt
def login_user(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']

    user = authenticate(username=username, password=password)
    response_data = {"userName": username}

    if user is not None:
        login(request, user)
        response_data = {
            "userName": username,
            "status": "Authenticated"
        }

    return JsonResponse(response_data)


# ----------------------------------------
# Logout
# ----------------------------------------


def logout_user(request):
    if request.method == "GET":
        logout(request)
        return JsonResponse({"userName": ""})


# ----------------------------------------
# Registration
# ----------------------------------------


@csrf_exempt
def registration(request):
    data = json.loads(request.body)

    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']

    username_exist = False

    try:
        User.objects.get(username=username)
        username_exist = True
    except User.DoesNotExist:
        logger.debug("%s is a new user", username)

    if not username_exist:
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            email=email
        )
        login(request, user)

        return JsonResponse({
            "userName": username,
            "status": "Authenticated"
        })

    return JsonResponse({
        "userName": username,
        "error": "Already Registered"
    })


# ----------------------------------------
# Dealerships
# ----------------------------------------


def get_dealerships(request, state="All"):
    endpoint = "/fetchDealers" if state == "All" else f"/fetchDealers/{state}"

    dealerships = get_request(endpoint)

    return JsonResponse({
        "status": 200,
        "dealers": dealerships
    })


# ----------------------------------------
# Dealer Reviews
# ----------------------------------------


def get_dealer_reviews(request, dealer_id):
    if not dealer_id:
        return JsonResponse({
            "status": 400,
            "message": "Bad Request"
        })

    endpoint = f"/fetchReviews/dealer/{dealer_id}"
    reviews = get_request(endpoint)

    if reviews is None:
        return JsonResponse({
            "status": 500,
            "message": "Error fetching reviews"
        })

    for review_detail in reviews:
        response = analyze_review_sentiments(review_detail['review'])

        if response and 'sentiment' in response:
            review_detail['sentiment'] = response['sentiment']
        else:
            review_detail['sentiment'] = "neutral"

    return JsonResponse({
        "status": 200,
        "reviews": reviews
    })


# ----------------------------------------
# Dealer Details
# ----------------------------------------


def get_dealer_details(request, dealer_id):
    if not dealer_id:
        return JsonResponse({
            "status": 400,
            "message": "Bad Request"
        })

    endpoint = f"/fetchDealer/{dealer_id}"
    dealership = get_request(endpoint)

    return JsonResponse({
        "status": 200,
        "dealer": dealership
    })


# ----------------------------------------
# Add Review
# ----------------------------------------


@csrf_exempt
def add_review(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            "status": 403,
            "message": "Unauthorized"
        })

    try:
        data = json.loads(request.body)
        response = post_review(data)

        if response:
            return JsonResponse({"status": 200})

        return JsonResponse({
            "status": 500,
            "message": "Backend error"
        })

    except Exception as e:
        print("Error:", e)
        return JsonResponse({
            "status": 401,
            "message": "Error in posting review"
        })


# ----------------------------------------
# Cars
# ----------------------------------------


def get_cars(request):
    if CarMake.objects.count() == 0:
        initiate()

    car_models = CarModel.objects.select_related('car_make')

    cars = []
    for car_model in car_models:
        cars.append({
            "CarModel": car_model.name,
            "CarMake": car_model.car_make.name
        })

    return JsonResponse({"CarModels": cars})