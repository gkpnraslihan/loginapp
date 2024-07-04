from datetime import timedelta
from django.utils import timezone
from rest_framework import status
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import requests 
import json
import os


from .UserSerializer import UserSerializer
from rest_framework.permissions import IsAdminUser,AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication



def generate_token(user_id):
    token, created = Token.objects.get_or_create(user_id=user_id, is_deleted=False)
    token.valid_to = timezone.now() + timedelta(days=30)
    token.save()
        
    return token.key

@api_view(['POST'])
@permission_classes([])
def login_api(request):
    username = request.data['username']
    password = request.data['password']
    token = ""
    user = authenticate(request, username = username, password = password)
    token = generate_token(user.id)
    return Response({"token": token}, status=status.HTTP_200_OK)

   
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
@permission_classes([AllowAny])
def logout_request(request):
    if not checkTokenIsValid(request):
       return Response({"error": "No valid token provided"},status=status.HTTP_401_UNAUTHORIZED, content_type='application/json')
    
    h=request
    
    
    try:
         a = Token.objects.filter(key=request.headers["Authorization"])
         a.update(is_deleted=True)

    except Token.DoesNotExist:
         pass  
    
    return Response({"detail": "Logout successful."}, status=status.HTTP_200_OK)

def get_city_list():
    file_path = os.path.join(settings.BASE_DIR, 'static', 'jsons', 'cities.json')
    with open(file_path, 'r', encoding='utf-8') as file:
        cities = json.load(file) 
    return [city['il_adi'] for city in cities]

def translate_condition(condition):
    translations = {
        "clear sky": "Açık",
        "few clouds": "Az bulutlu",
        "scattered clouds": "Dağınık bulutlu",
        "broken clouds": "Parçalı bulutlu",
        "shower rain": "Sağanak yağışlı",
        "rain": "Yağmurlu",
        "thunderstorm": "Fırtına",
        "snow": "Karlı",
        "mist": "Sisli"
    }
    return translations.get(condition, condition)



def weather(request):
    api_key = '05c13ccf608154dea88a4e589bf16011'
    cities = get_city_list()
    city = request.GET.get('city')

    if not city:
        return render(request, 'blog/weather.html', {'cities': cities})

    if city not in cities:
        return render(request, 'blog/weather.html', {'error': 'Geçersiz şehir seçimi.', 'cities': cities})

    base_url = f'https://api.openweathermap.org/data/2.5/weather?appid={api_key}&q={city}'
    response = requests.get(base_url)
    weather_data = response.json()

    if response.status_code == 200:
        if 'main' in weather_data:
            temperature_kelvin = weather_data['main']['temp']
            temperature_celsius = round(temperature_kelvin - 273.15, 2)
            condition = translate_condition(weather_data['weather'][0]['description'])
            data = {
                'city': city,
                'temperature': temperature_celsius,
                'condition': condition,
            }
            return render(request, 'blog/weather.html', {'data': data, 'cities': cities})
        else:
            return render(request, 'blog/weather.html', {'error': 'Geçersiz API yanıtı formatı.', 'cities': cities})
    else:
        return render(request, 'blog/weather.html', {'error': 'Hava durumu verileri alınamadı.', 'cities': cities})

    

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
@permission_classes([IsAdminUser])
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.delete()
    return Response(status=status.HTTP_200_OK, content_type='application/json')

@api_view(['POST'])
@permission_classes([AllowAny])
def test_token_api(request):
    if not checkTokenIsValid(request):
       return Response({"error": "No valid token provided"},status=status.HTTP_401_UNAUTHORIZED, content_type='application/json')
    
    return Response({"success": "Landed here. "},status=status.HTTP_200_OK, content_type='application/json')

@api_view(['GET'])
@permission_classes([AllowAny])
def user_info_api(request):
    if not checkTokenIsValid(request):
       return Response({"error": "No valid token provided"},status=status.HTTP_401_UNAUTHORIZED, content_type='application/json')
    
    user = get_user(request)
    if user:
        user_data = {
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_staff": user.is_staff,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            
        }
        return Response(user_data, status=status.HTTP_200_OK, content_type='application/json')
    else:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND, content_type='application/json')
    
@api_view(['POST'])
@permission_classes([AllowAny])
def update_user_info(request):
    try:
        header = request.headers["Authorization"] 
        
        token = Token.objects.get(key=header, is_deleted=False)
        requestFromUser = User.objects.get(pk=token.user_id)

        request_data = request.data

        user_id = request_data.get("id")
        updatedUser = User.objects.get(pk=user_id)

        # print("user id from data : ",user_id )
        # print("user id from token : ",user.id )

        if requestFromUser.is_superuser == False:
            if str(requestFromUser.id) != user_id:
                return Response({"error": "You can only update your own information"}, status=status.HTTP_403_FORBIDDEN)
        
        new_username = request_data.get("username")

        if new_username != updatedUser.username and User.objects.filter(username=new_username).exists():
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        updatedUser.username = new_username
        updatedUser.email = request_data.get("email")
        updatedUser.first_name = request_data.get("first_name")
        updatedUser.last_name = request_data.get("last_name")
        
        
        if requestFromUser.is_superuser:
            #   user.username = data.get("username", user.username) 
            #   user.email = data.get("email", user.email)    
            #   user.first_name = data.get("first_name", user.first_name)
            #   user.last_name = data.get("last_name", user.last_name)
          updatedUser.is_staff = request_data.get("is_staff")
          updatedUser.is_active = request_data.get("is_active")
          updatedUser.is_superuser = request_data.get("is_superuser")
        
        updatedUser.save()

        return Response({"success": "User info updated successfully"}, status=status.HTTP_200_OK)
    except Token.DoesNotExist:
        return Response({"error": "Token does not exist"}, status=status.HTTP_404_NOT_FOUND)
    except KeyError:
        return Response({"error": "No Authorization header provided"}, status=status.HTTP_400_BAD_REQUEST)
    except IndexError:
        return Response({"error": "Authorization header format is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
def checkTokenIsValid(request):
    try:
        header = request.headers["Authorization"]
        token = Token.objects.get(key=header, is_deleted=False, valid_to__gt=timezone.now())
       
        token.valid_to = timezone.now() + timedelta(days=30)
        token.save()

        return True
    except Token.DoesNotExist:
        return False
    except KeyError:
        return False


def get_user(request):
    if checkTokenIsValid(request):
        try:
            header = request.headers["Authorization"]
            token = Token.objects.get(key=header)
            return token.user
        except Token.DoesNotExist:
            pass

    return None

