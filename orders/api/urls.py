
from django.urls import path
from . import views

urlpatterns = [
    path('orders/', views.OrdersList.as_view()),
    path('orders/<int:pk>/', views.SingleOrderView.as_view()),
    path('completed-order-count/<int:pk>/', views.OrdersBusinessCompletedCountView.as_view()),
    path('order-count/<int:pk>/', views.OrdersBusinessUncomletedCoutView.as_view()),
]