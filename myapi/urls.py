from django.urls import path
from .views import login_api, register_request, logout_request, weather, users, user_detail, edit_user, delete_user,users_list,generate_token,test_token_api,user_info_api
from . import views


urlpatterns = [
    path('login/',  login_api, name='api-login'),
    path('register/', register_request, name='api-register'),
    path('logout/', logout_request, name='api-logout'),
    path('weather/', views.weather, name='api-weather'),
    path('users/', users_list, name='users'), 
    path('users/<int:pk>/', user_detail, name='api-user-detail'),
    path('edit-user/<int:pk>/', views.edit_user, name='edit-user'),
    path('generate_token/<int:pk>/', generate_token, name='generate_token'),
    path('delete-user/<int:pk>/', delete_user, name='delete-user'),
    path('test-token/',test_token_api, name='test_token_api'),
    path('user-info/',user_info_api, name='user_info_api'),
    
    
]
