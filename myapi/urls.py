from django.urls import path
from .views import login_request, register_request, logout_request, weather_view

urlpatterns = [
    path('login/', login_request, name='api-login'),
    path('register/', register_request, name='api-register'),
    path('logout/', logout_request, name='api-logout'),
   
    
]
