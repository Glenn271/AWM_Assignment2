from django.shortcuts import render, redirect
from .forms import PropertySearchForm
import requests
from bs4 import BeautifulSoup
import urllib.parse
from django.views import generic
import json
from django.http import JsonResponse

locations = [
    {
        'author': 'CoreyMS',
        'title': 'location 1',
        'content': 'First post content',
        'date_posted': 'August 27, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'location 2',
        'content': 'Second post content',
        'date_posted': 'August 28, 2018'
    }
]


def home(request):
    context = {
        'locations': locations
    }
    return render(request, 'world/home.html', context)


def about(request):
    return render(request, 'world/about.html', {'title': 'About'})

#property search form
def search(request):
    context = {}
    prop_list = []
    if request.method == 'POST':
        form = PropertySearchForm(request.POST)

        if form.is_valid():
            city = form.cleaned_data['city']

            #get housing data from myHome
            page = requests.get("https://www.myhome.ie/rentals/dublin/house-to-rent-in-{0}".format(city))
            soup = BeautifulSoup(page.content, 'html.parser')
            propertyCard = soup.find_all(class_="PropertyListingCard")

            #parsing content and assigning to variables
            for prop in propertyCard:
                propList = prop
                propAddress = propList.find(class_="PropertyListingCard__Address").get_text()
                rentPrice = propList.find(class_="PropertyListingCard__Price").get_text()

                #using Nominatim for lat/lon info of property
                url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(propAddress) + '?format=json'
                response = requests.get(url).json()

                lat = response[0]["lat"]
                lon = response[0]["lon"]

                print(propAddress)
                print(lat + " " + lon)

                #making JSON object for property data
                property = {
                    'address' : propAddress,
                    'city' : city,
                    'lat' : lat,
                    'lon' : lon,
                    'rent' : rentPrice
                }

                #add to list of properties
                prop_list.append(property)

            #context
            context['prop_list'] = prop_list
            context['form'] = form

            #search results if form is valid
            return render(request, 'world/results.html', context)

    else:
        form = PropertySearchForm()
    return render(request, 'world/search.html', {'form' : form})