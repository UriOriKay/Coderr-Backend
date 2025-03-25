from django.db.models import Avg

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from reviews.models import Review
from user_auth.models import Profile
from offers.models import Offer

class BaseInfoView(APIView):
    """
    API-Endpoint, der grundlegende Metriken zur Plattform zurückgibt.
    Enthält: Anzahl der Bewertungen, Durchschnittsbewertung, 
    Anzahl Business-Profile, Anzahl Angebote.
    """

    def get(self, request, *args, **kwargs):

        review_count = Review.objects.count()
        average_rating = Review.objects.aggregate(average_rating=Avg('rating'))['average_rating']
        average_rating = round(average_rating, 1) if average_rating else 0
        business_profile_count = Profile.objects.filter(type='business').count()
        offer_count = Offer.objects.count()

        platform_stats = {
            'review_count': review_count,
            'average_rating': average_rating,
            'business_profile_count': business_profile_count,
            'offer_count': offer_count
        }

        return Response(platform_stats, status=status.HTTP_200_OK)