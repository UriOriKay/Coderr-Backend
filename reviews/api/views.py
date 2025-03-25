from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from reviews.models import Review
from .serializers import ReviewsSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status


class ReviewListView(generics.ListCreateAPIView):
    """
    API-Endpunkt für das Abrufen und Erstellen von Bewertungen.

    - `GET`: Gibt alle Bewertungen zurück, filterbar nach `business_user_id` und `reviewer_id`.
    - `POST`: Erstellt eine neue Bewertung, nur erlaubt für authentifizierte Nutzer mit einem Kundenprofil.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewsSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['business_user_id', 'reviewer_id']
    ordering_fields = ['updated_at', 'rating']
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_permissions(self):
        """
        Gibt spezifische Berechtigungen je nach HTTP-Methode zurück.
        POST erfordert Authentifizierung, ansonsten greifen die Standardrechte.
        """
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        """
        Führt zusätzliche Prüfung beim Erstellen einer Bewertung durch:
        Nur Kunden dürfen Bewertungen abgeben.
        """
        if not self.request.user.profile.type == 'customer':
            raise PermissionDenied("Nur User mit einem Kundenprofil können Bewertungen abgeben.")
        serializer.save(reviewer=self.request.user)

class ReviewDetailsview(generics.RetrieveUpdateDestroyAPIView):
    """
    API-Endpunkt zur Anzeige, Aktualisierung oder Löschung einer einzelnen Bewertung.

    - `GET`: Für alle Benutzer erlaubt.
    - `PATCH/PUT`: Nur erlaubt für den Ersteller oder einen Admin.
    - `DELETE`: Nur erlaubt für den Ersteller oder einen Admin.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewsSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Gibt für GET-Requests `AllowAny` zurück, ansonsten `IsAuthenticated`.
        """
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def perform_update(self, serializer):
        """
        Speichert die Bewertung nur, wenn der Nutzer der Ersteller oder ein Superuser ist.
        """
        if serializer.instance.reviewer != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied("Nur der Ersteller oder ein Admin kann eine Bewertung bearbeiten.")
        serializer.save()

    def perform_destroy(self, instance):
        """
        Löscht die Bewertung nur, wenn der Nutzer der Ersteller oder ein Admin ist.
        """
        if instance.reviewer != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Nur der Ersteller oder ein Admin kann eine Bewertung löschen.")
        instance.delete()
        
    def update(self, request, *args, **kwargs):
        """
        Führt ein Update der Bewertung durch, erlaubt sind nur `rating` und `description`.

        - Gibt 403 zurück, wenn der Nutzer nicht der Ersteller ist.
        - Gibt 400 zurück, wenn unerlaubte Felder im Patch enthalten sind.
        """
        instance = self.get_object()

        if instance.reviewer != request.user:
            return Response({'detail': 'Sie dürfen diese Bewertung nicht bearbeiten.'}, status=status.HTTP_403_FORBIDDEN)

        allowed_fields = {'rating', 'description'}
        invalid_fields = [field for field in request.data if field not in allowed_fields]
        if invalid_fields:
            return Response({'detail': f"Ungültige Felder: {', '.join(invalid_fields)}"}, status=status.HTTP_400_BAD_REQUEST)
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)