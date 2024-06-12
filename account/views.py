from django.shortcuts import redirect,render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
def login_request(request):
    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)
            token = Token.objects.get_or_create(user=user)[0] 
            response = HttpResponseRedirect(reverse("home")) 
            response.set_cookie('user_token', token.key, max_age=3600)
            return response
        else:
            return render(request, "account/login.html", {
                "error": "kullanıcı adı ya da parola yanlış"
            })

    return render(request, "account/login.html")

def register_request(request):
    if request.user.is_authenticated:
        return redirect("home")
     
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        firstname = request.POST["firstname"]
        lastname = request.POST["lastname"]
        password = request.POST["password"]
        repassword = request.POST["repassword"]

        if password == repassword:
           if User.objects.filter(username=username).exists():
               return render(request, "account/register.html", 
               {
                  "error":"bu kullanıcı mevcut.",
                   "username":username,
                   "email":email,
                   "firstname":firstname,
                   "lastname":lastname                  
                })
           else:
              if User.objects.filter(email=email).exists():
                return render(request, "account/register.html",
                {
                    "error":"bu email mevcut.",
                    "username":username,
                    "email":email,
                    "firstname":firstname,
                    "lastname":lastname   
                })
              else:
                  user = User.objects.create_user(username=username,email=email,first_name=firstname,last_name=lastname,password=password)
                  user.save()
                  return redirect("login")
        else:
          return render(request, "account/register.html",
                {
                    "error":"parola eşleşmiyor.",
                    "username":username,
                    "email":email,
                    "firstname":firstname,
                    "lastname":lastname                      
                }) 
              
    return render(request, "account/register.html")

def logout_request(request):
    
    if request.user.is_authenticated:
        Token.objects.filter(user=request.user).delete()   
    logout(request)
    response = redirect("home")
    response.delete_cookie('user_token')
    
    return response

class CustomTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        try:
            token = Token.objects.get(key=key)
        except Token.DoesNotExist:
            raise AuthenticationFailed('Invalid token')

        if not token.user.is_active:
            raise AuthenticationFailed('User inactive or deleted')

        return (token.user, token)
    
class IsAuthenticatedWithToken(BasePermission):
    def has_permission(self, request, view):
        token_key = request.META.get('HTTP_AUTHORIZATION')
        if not token_key:
            return False

        token_key = token_key.split(' ')[0]
        try:
            token = Token.objects.get(key=token_key)
        except Token.DoesNotExist:
            return False

        request.user = token.user
        return True
    
class SecureAPIView(APIView):
    permission_classes = [IsAuthenticatedWithToken]

    def get(self, request):
        return Response({'message': 'This is a secure endpoint!'})