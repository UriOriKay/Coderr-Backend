from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from offers.models import Offer, OfferDetail
from django.db.models import Min
from .serializers import OfferSerializer
from offers.api.ordering import OrderingHelperOffers
from offers.api.permissions import IsOwnerOrAdmin
from django.shortcuts import get_object_or_404
from offers.api.serializers import SingleFullOfferDetailSerializer, OfferDetailSerializer, SingleDetailOfOfferSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.utils.timezone import now
from rest_framework.exceptions import PermissionDenied, ValidationError



class BusinessProfileRequiredException(APIException):
    """
    Exception für den Fall, dass ein nicht-Business-User versucht, ein Angebot zu erstellen.
    Wird verwendet in perform_create.
    """
    status_code = 403
    default_detail = {'details': ['Nur Unternehmen können Angebote erstellen.']}
    default_code = 'business_Profile_required'


class OfferPagination(PageNumberPagination):
    """
    Paginierungsklasse für Angebote.
    Erlaubt Steuerung der Seitenanzahl via QueryParam ?page_size=
    """
    page_size = 6
    page_size_query_param = 'page_size'


class OffersList(ListCreateAPIView):
    """
    API-View für:
    - GET: Auflisten aller Angebote mit optionalen Filtern (creator_id, Preis, Lieferzeit, Suche, Sortierung)
    - POST: Erstellen eines neuen Angebots (nur für Business-User)
    """
    permission_classes = [IsAuthenticated]
    queryset = Offer.objects.annotate(min_price=Min('details__price'))
    serializer_class = OfferSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    pagination_class = OfferPagination
    filterset_fields = ['user']
    search_fields = ['title', 'description']

    ALLOWED_QUERY_PARAMS = {'creator_id', 'min_price', 'max_delivery_time', 'ordering', 'search', 'page_size'}

    def get_queryset(self):
        """
        Gibt die Angebotsliste mit Annotationen zurück.
        - validiert Query-Parameter
        - filtert nach optionalen Parametern
        - wendet Sortierung an
        """        
        self._validate_query_params()

        queryset = Offer.objects.annotate(min_price=Min('details__price'), max_delivery_time=Min('details__delivery_time_in_days'))
        queryset = self._filter_queryset(queryset)
        ordering = self.get_get_ordering()

        return OrderingHelperOffers.apply_ordering(queryset, ordering)

    
    def _validate_query_params(self):
        """
        Prüft, ob nur erlaubte Query-Parameter verwendet werden.
        Gibt bei Fehlern eine lesbare Fehlermeldung zurück.
        """
        used_params = set(self.request.query_params.keys())
        invalid_params = used_params - self.ALLOWED_QUERY_PARAMS
        if invalid_params:
            raise ValidationError({
                "detail": f"Ungültige Parameter: {', '.join(invalid_params)}. Erlaubt sind: {', '.join(self.ALLOWED_QUERY_PARAMS)}"
            })
        
    def _filter_queryset(self, queryset):
        """
        Filtert das Queryset anhand von Parametern:
        - creator_id
        - min_price
        - max_delivery_time
        """
        params = self.request.query_params

        creator_id = params.get('creator_id')
        if creator_id:
            try:
                creator_id = int(creator_id)
            except ValueError:
                raise ValidationError({"detail": "creator_id muss eine ganze Zahl sein."})
            queryset = queryset.filter(user_id=creator_id)

        min_price = params.get('min_price')
        if min_price:
            try:
                min_price = float(min_price)
            except ValueError:
                raise ValidationError({"detail": "min_price muss eine Zahl sein."})
            queryset = queryset.filter(min_price__gte=min_price)

        max_delivery_time = params.get('max_delivery_time')
        if max_delivery_time:
            try:
                max_delivery_time = int(max_delivery_time)
            except ValueError:
                raise ValidationError({"detail": "max_delivery_time muss eine ganze Zahl sein."})
            queryset = queryset.filter(max_delivery_time__lte=max_delivery_time)

        return queryset
    
    def get_get_ordering(self):
        """
        Gibt das Sortierfeld zurück (default: 'updated_at').
        """
        return self.request.query_params.get('ordering', 'updated_at')


    def get_permissions(self):
        """
        Gibt unterschiedliche Berechtigungen zurück:
        - POST: nur Owner/Admin
        - sonst: Standard
        """
        if self.request.method == 'POST':
            return [IsOwnerOrAdmin()]
        return super().get_permissions()

    def perform_create(self, serializer):
        """
        Speichert ein neues Angebot ab, wenn der User ein Business-Profil hat.
        """
        user = self.request.user
        profile = getattr(user, 'profile', None)

        if not profile or profile.type != 'business':
            raise BusinessProfileRequiredException()
        serializer.save(user=user)

class OfferDetailsView(RetrieveUpdateDestroyAPIView):
    """
    API-View für ein einzelnes Angebot (GET, PATCH, DELETE).
    PATCH/DELETE nur erlaubt für Owner oder Admin.
    """
    queryset = Offer.objects.prefetch_related('details')
    serializer_class = SingleFullOfferDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        PATCH erlaubt nur Owner/Admin – ansonsten Standardrechte.
        """
        if self.request.method == 'PATCH':
            return [IsAuthenticated(), IsOwnerOrAdmin()]
        return super().get_permissions()
    
    def update(self, request, format=None, **kwargs):
        """
        Aktualisiert das Angebot samt Detail-Daten.
        Gibt reduzierte Felder als Response zurück.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        instance.updated_at = now()
        instance.refresh_from_db()

        updated_data = {
            'id': instance.id,
            'title': serializer.validated_data.get('title', instance.title),
            'description': serializer.validated_data.get('description', instance.description),
            'details': OfferDetailSerializer(instance.details.all(), many=True).data,
            'image': instance.image.url if instance.image else None
        }

        return Response(updated_data, status=status.HTTP_200_OK)
    
    def delete(self, request, pk, *args, **kwargs):
        """
        Löscht ein Angebot, wenn der Nutzer berechtigt ist.
        Nur erlaubt für: Besitzer, Admins mit Business-Profil.
        """
        offer = get_object_or_404(Offer, id=pk)
        if not (request.user == offer.user or request.user.is_staff):
            raise PermissionDenied({"details": ["Nur ein Besitzer oder ein Admin kann das Angebot löschen"],})
        if not (request.user.profile.type == 'business' or request.user.is_staff):
            raise PermissionDenied({"details": ["Nur Unternehmen kann ein Angebot löschen"],})
        offer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def _check_delete_permission(self, user, offer):
        """
        Prüft, ob der Nutzer das Angebot löschen darf.
        - Nur erlaubt für Besitzer oder Admins mit Business-Profil.
        """
        if not (user == offer.user or user.is_staff):
            raise PermissionDenied({"details": ["Nur ein Besitzer oder ein Admin kann das Angebot löschen"]})
        if not getattr(user, "profile", None) or user.profile.type != "business":
            if not user.is_staff:
                raise PermissionDenied({
                    "details": ["Nur ein Business-Profil oder ein Admin darf das Angebot löschen."]
                })

    
class OfferSingleView(APIView):
    """
    Liefert die Detaildaten eines einzelnen `OfferDetail`-Objekts anhand seiner ID.
    """
    permission_classes = [IsAuthenticated]
    def get(self, request, pk, format=None):
        """
        Holt das OfferDetail mit gegebener ID und serialisiert es vollständig.
        Nur für authentifizierte Nutzer sichtbar.
        """
        offer = get_object_or_404(OfferDetail, id=pk)
        serializer = SingleDetailOfOfferSerializer(offer)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
