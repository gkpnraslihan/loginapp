from django.urls import path
from .views import login_request, register_request, logout_request, weather, users, user_detail, edit_user, delete_user
from . import views


urlpatterns = [
    path('login/', login_request, name='api-login'),
    path('register/', register_request, name='api-register'),
    path('logout/', logout_request, name='api-logout'),
    path('weather/', weather, name='api-weather'),
    path('users/', users, name='users'), 
    path('users/<int:pk>/', user_detail, name='api-user-detail'),
    path('api/edit-user/<int:pk>/', views.edit_user, name='edit-user'),
    path('api/delete-user/<int:pk>/', delete_user, name='delete-user'),
    
    
]
