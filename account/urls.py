from django.urls import path
from . import views
from .views import SecureAPIView
urlpatterns = [
    path("login", views.login_request, name="login"),
    path("register", views.register_request, name="register"),
    path("logout", views.logout_request, name="logout"),
    path('secure-endpoint/', SecureAPIView.as_view(), name='secure-endpoint'),

]
