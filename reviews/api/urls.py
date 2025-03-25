from django.urls import path

from . import views

urlpatterns = [
    path('reviews/', views.ReviewListView.as_view()),
    path('reviews/<int:pk>/', views.ReviewDetailsview.as_view()),
]