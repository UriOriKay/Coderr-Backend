from django.urls import path
from . import views

urlpatterns = [
    path('offers/', views.OffersList.as_view(), name='offers list'),
    path('offers/<int:pk>/', views.OfferDetailsView.as_view(), name='offerdetails'),
    path('offerdetails/<int:pk>/', views.OfferSingleView.as_view(), name='offer single'),
]