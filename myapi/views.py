from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
import requests 

@api_view(['POST'])
def login_request(request):
    if request.user.is_authenticated:
        return Response({"detail": "User already authenticated."}, status=status.HTTP_400_BAD_REQUEST)

    data = request.data
    username = data.get("username")
    password = data.get("password")

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        return Response({"detail": ("Login successful."+username)}, status=status.HTTP_200_OK)
    else:
        return Response({"error": ("Invalid username or password. Username is:"+username)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def register_request(request):
    if request.user.is_authenticated:
        return Response({"detail": "User already authenticated."}, status=status.HTTP_400_BAD_REQUEST)

    data = request.data
    username = data.get("username")
    email = data.get("email")
    firstname = data.get("firstname")
    lastname = data.get("lastname")
    password = data.get("password")
    repassword = data.get("repassword")

    if password == repassword:
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)
        elif User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user = User.objects.create_user(username=username, email=email, first_name=firstname, last_name=lastname, password=password)
            user.save()
            return Response({"detail": "Registration successful."}, status=status.HTTP_201_CREATED)
    else:
        return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def logout_request(request):
    if not request.user.is_authenticated:
        return Response({"detail": "User not authenticated."}, status=status.HTTP_400_BAD_REQUEST)
    
    logout(request)
    return Response({"detail": "Logout successful."}, status=status.HTTP_200_OK)


@api_view(['GET'])
def weather_view(request):
    api_key = '05c13ccf608154dea88a4e589bf16011'
    city = request.GET.get('city', 'Istanbul') 
    base_url = f'https://api.openweathermap.org/data/2.5/weather?appid={api_key}&q={city}'

    response = requests.get(base_url)
    weather_data = response.json()

    print(weather_data)

    if response.status_code == 200:
        if 'main' in weather_data:
            temperature_kelvin = weather_data['main']['temp']
            temperature_celsius = round(temperature_kelvin - 273.15, 2)
            data = {
                'city': city,
                'temperature': temperature_celsius,
                'condition': weather_data['weather'][0]['description'],               
            }
            return render(request, 'blog/weather_view.html', {'data': data})
        else:
           return render(request, 'blog/weather_view.html', {'error': "Invalid API response format."})
    else:
        return render(request, 'blog/weather_view.html', {'error': "Failed to retrieve weather data."})


