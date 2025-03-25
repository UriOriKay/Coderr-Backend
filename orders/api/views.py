from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from orders.models import Order
from orders.api.serializers import OrderListSerializer, OrdersPostSerializer, OrdersPatchSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

class OrdersList(APIView):
    """
    API-Endpunkt für das Abrufen und Erstellen von Bestellungen (Orders).
    Nur authentifizierte Nutzer haben Zugriff.

    - GET: Gibt alle Bestellungen zurück, bei denen der Nutzer Kunde oder Anbieter ist.
    - POST: Erstellt eine neue Bestellung, nur wenn der Nutzer ein Kundenprofil hat.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """
        Gibt eine Liste der Bestellungen zurück, die dem angemeldeten Nutzer zugeordnet sind,
        entweder als Kunde oder Anbieter.
        """
        if request.user.is_authenticated:
            orders = Order.objects.filter(Q(business_user=request.user) | Q(customer_user=request.user.id))
        else:
            orders = Order.objects.none()
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        """
        Erstellt eine neue Bestellung. Nur Benutzer mit Kundenprofil dürfen diesen Vorgang durchführen.
        Gibt bei Erfolg die vollständige Bestellung zurück.
        """
        serializer = OrdersPostSerializer(data=request.data)
        if self.request.user.profile.type != 'customer':
            return Response({'details': ['Nur Kunden können Aufträge erteilen']},status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            order =serializer.save(customer_user=request.user.id)
            full_serializer = OrderListSerializer(order)
            return Response(full_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SingleOrderView(APIView):
    """
    API-Endpunkt zum Abrufen, Aktualisieren und Löschen einer einzelnen Bestellung.

    Zugriff:
    - GET: Nur authentifizierte Nutzer.
    - PATCH: Nur der zugehörige Anbieter oder ein Admin.
    - DELETE: Nur für Admins.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        """
        Gibt eine einzelne Bestellung anhand der Primärschlüssel-ID zurück.
        """
        order = Order.objects.get(pk=pk)
        serializer = OrderListSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk, format=None):
        """
        Erlaubt die teilweise Aktualisierung einer Bestellung.
        Nur der zugehörige Anbieter oder ein Admin darf Änderungen vornehmen.

        Validiert außerdem, dass nur erlaubte Felder übermittelt werden.
        """
        order = get_object_or_404(Order, pk=pk)
        is_company = order.business_user == request.user
        is_admin = request.user.is_staff
        if not (is_company or is_admin):
            return Response({'detail': 'Sie sind nicht berechtigt diese Bestellung zu ändern'}, status=status.HTTP_403_FORBIDDEN)
        
        allowed_fields = {'status', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type', 'description', 'file'}

        invalid_keys = [key for key in request.data if key not in allowed_fields]
        if invalid_keys:
            return Response(
                {'detail': f"Ungültige Felder: {', '.join(invalid_keys)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serialier = OrdersPatchSerializer(order, data=request.data, partial=True)
        if serialier.is_valid():
            serialier.save()
            full_serialier = OrderListSerializer(order)
            return Response(full_serialier.data, status=status.HTTP_200_OK)
        return Response(serialier.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        """
        Löscht eine Bestellung. Nur Admins dürfen diese Aktion durchführen.
        """
        if not (request.user.is_staff):
            return Response({'detail': 'Sie sind nicht berechtigt diese Bestellung zu löschen'}, status=status.HTTP_403_FORBIDDEN)
        order = get_object_or_404(Order, pk=pk)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class OrdersBusinessUncomletedCoutView(APIView):
    """
    API-Endpunkt zur Abfrage der Anzahl unbearbeiteter (in_progress) Bestellungen
    eines bestimmten Business-Users.

    Zugriff: Nur authentifizierte Nutzer.
    """
    permission_classes = [IsAuthenticated]
    def get(self, request, pk, format=None):
        """
        Gibt die Anzahl der offenen Bestellungen für einen Business-User zurück.

        Validierung:
        - Existiert der User?
        - Ist er ein Business-Profil?
        """
        try:
            business_user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'Dieser Business User existiert nicht.'}, status=status.HTTP_404_NOT_FOUND)
        if not hasattr(business_user, 'profile') or business_user.profile.type != 'business':
            return Response({'detail': 'Dieser Benutzer ist kein Business-Profil.'}, status=status.HTTP_404_NOT_FOUND)
        order_count = Order.objects.filter(business_user=business_user, status='in_progress').count()
        return Response({'order_count': order_count})

class OrdersBusinessCompletedCountView(APIView):
    """
    API-Endpunkt zur Abfrage der Anzahl abgeschlossener Bestellungen
    eines bestimmten Business-Users.

    Zugriff: Nur für authentifizierte Nutzer geeignet, wenn Absicherung nötig ist.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        """
        Gibt die Anzahl abgeschlossener Bestellungen ('completed') eines Business-Users zurück.

        Validierung:
        - Existiert der User?
        - Hat der User ein Business-Profil?
        """
        try:
            business_user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'Dieser Business User existiert nicht.'}, status=status.HTTP_404_NOT_FOUND)
        if not hasattr(business_user, 'profile') or business_user.profile.type != 'business':
            return Response({'detail': 'Dieser Benutzer ist kein Business-Profil.'}, status=status.HTTP_404_NOT_FOUND)
        completed_order_count = Order.objects.filter(business_user=business_user, status='completed')
        return Response({'completed_order_count': completed_order_count.count()})