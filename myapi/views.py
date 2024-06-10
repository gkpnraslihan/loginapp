from rest_framework import status
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import requests 
import json
import os
from .UserSerializer import UserSerializer

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

def get_city_list():
    file_path = os.path.join(settings.BASE_DIR, 'static', 'jsons', 'cities.json')
    with open(file_path, 'r', encoding='utf-8') as file:
        cities = json.load(file) 
    return [city['il_adi'] for city in cities]



@api_view(['GET'])
def weather(request):
    api_key = '05c13ccf608154dea88a4e589bf16011'
    cities = get_city_list()
    city = request.GET.get('city') 

    if not city:
        return JsonResponse({'error': 'Şehir belirtilmedi.', 'cities': cities})

    if city not in cities:
        return JsonResponse({'error': 'Geçersiz şehir seçimi.', 'cities': cities})

    base_url = f'https://api.openweathermap.org/data/2.5/weather?appid={api_key}&q={city}'
    response = requests.get(base_url)
    weather_data = response.json()

    if response.status_code == 200:
        if 'main' in weather_data:
            temperature_kelvin = weather_data['main']['temp']
            temperature_celsius = round(temperature_kelvin - 273.15, 2)
            data = {
                'city': city,
                'temperature': temperature_celsius,
                'condition': weather_data['weather'][0]['description'],               
            }
            return JsonResponse({'data': data})
        else:
           return JsonResponse({'error': "Geçersiz API yanıtı formatı."})
    else:
        return JsonResponse({'error': "Hava durumu verileri alınamadı."})
    

@api_view(['GET'])
def users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def user_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user)
    return Response(serializer.data)


def edit_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        serializer = UserSerializer(user, data=request.POST)
        if serializer.is_valid():
            serializer.save()
            return redirect('users-list')
        return render(request, 'blog/edit_user.html', {'serializer': serializer})
    else:
        serializer = UserSerializer(user)
        return render(request, 'blog/edit_user.html', {'serializer': serializer})

def users_list(request):
    users = User.objects.all()
    return render(request, 'blog/users.html', {'users': users})

@api_view(['DELETE'])
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    serializer = UserSerializer(user)
    user.delete()
    return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
    
