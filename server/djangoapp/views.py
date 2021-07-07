from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request, RestException
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
from uuid import uuid4

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.

# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact_us.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect('djangoapp:index')
        else:
            # If not, return to login page again
            return render(request, 'djangoapp/registration.html', context)
    else:
        return render(request, 'djangoapp/registration.html', context)


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://c12e13d7.eu-gb.apigw.appdomain.cloud/api/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context['dealership_list'] = dealerships
        # Concat all dealer's short name
        # dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        # return HttpResponse(dealer_names)
        return render(request, 'djangoapp/index.html', context)

# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = "https://c12e13d7.eu-gb.apigw.appdomain.cloud/api/review"
        # Get reviews from the URL
        reviews = get_dealer_reviews_from_cf(url, dealer_id)
        context['reviews'] = reviews

        url = 'https://c12e13d7.eu-gb.apigw.appdomain.cloud/api/dealership'
        try:
            dealer = get_dealers_from_cf(url, id=dealer_id)
        except RestException as e1:
            return HttpResponse('Rest Exception \n' + str(e1))
        if len(dealer) == 0:
            context['dealer'] = {'id': dealer_id, 'full_name': "No name found"}
        else:
            context['dealer'] = dealer[0]      
          
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    if request.method == "GET":
        url = 'https://c12e13d7.eu-gb.apigw.appdomain.cloud/api/dealership'
        try:
            dealer = get_dealers_from_cf(url, id=dealer_id)
        except RestException as e1:
            return HttpResponse('Rest Exception \n' + str(e1))
        if len(dealer):
            dealer_name = dealer[0].full_name
        cars = CarModel.objects.filter(dealer_id=dealer_id)
        context = {"cars": cars, "dealer_id": dealer_id,
                   "dealer_name": dealer_name}
        return render(request, 'djangoapp/add_review.html', context)
    elif request.method == "POST":
        url = "https://c12e13d7.eu-gb.apigw.appdomain.cloud/api/review"
        if not request.user.is_authenticated:
            return {'error': 'Add Review method: Not registered user'}
        review = {}
        review["id"] = uuid4()
        review["time"] = datetime.utcnow().isoformat()
        review['dealership'] = int(dealer_id)
        review["review"] = request.POST['content']
        review["name"] = request.user.first_name + ' ' + request.user.last_name        
        review['purchase'] = True if request.POST['purchasecheck'] == 'on' else False
        try:
            purch_date = datetime.strptime(request.POST['purchasedate'][:10], '%Y-%m-%d')
            review['purchase_date'] = purch_date.strftime('%m/%d/%Y')
        except ValueError as v1:
            print('Error converting datetime: ' + str(v1))
        car_model = CarModel.objects.get(id=request.POST['car'])
        review['car_make'] = car_model.carmake.name
        review['car_model'] = car_model.name
        review['car_year'] = car_model.year.strftime("%Y")

        json_payload = {}
        json_payload["review"] = review
        
        return post_request(url, json_payload, dealerId=dealer_id)
        