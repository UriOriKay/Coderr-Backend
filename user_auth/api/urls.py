from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('registration/', views.RegisterView.as_view(), name='register'),
    path('profiles/customer/', views.CustomerProfileList.as_view(), name='customer list'),
    path('profiles/business/', views.BusinessProfileList.as_view(), name='business list'),
    path('profile/<int:pk>/', views.ProfileDetailsView.as_view(), name='profil details'),
]