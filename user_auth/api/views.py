from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from user_auth.models import Profile
from user_auth.api.serializers import ProfileSerializer, BusinessProfilesListSerializer, CustomerProfilesListSerializer
from .serializers import RegistrationSerializer, LoginSerializer


class RegisterView(APIView):
    """
    API-Endpunkt für die Registrierung neuer Benutzer.

    - Erlaubt POST-Anfragen ohne Authentifizierung.
    - Validiert die eingegebenen Benutzerdaten mit RegistrationSerializer.
    - Erstellt automatisch ein Authentifizierungstoken für den neuen Benutzer.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Verarbeitet die Registrierung eines neuen Benutzers.

        Gibt bei Erfolg ein Token und Benutzerdaten zurück.
        """
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'username': user.username,
                'email': user.email,
                "user_id": user.id
                }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileDetailsView(APIView):
    """
    API-Endpunkt zur Anzeige und Bearbeitung eines Benutzerprofils.

    - `GET`: Gibt die Profildaten für ein bestimmtes Benutzerprofil zurück.
    - `PATCH`: Ermöglicht einem Benutzer, nur sein eigenes Profil zu aktualisieren.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """
        Gibt die Profildaten für die angegebene Benutzer-ID zurück.

        Entfernt das Feld 'uploaded_at' aus der Rückgabe, falls vorhanden.
        """
        profile = get_object_or_404(Profile, pk=pk)
        serializer = ProfileSerializer(profile)
        data = serializer.data
        data.pop('uploaded_at', None)
        return Response(data, status=status.HTTP_200_OK)
    
    def patch(self, request, pk, format=None):
        """
        Aktualisiert das Benutzerprofil mit den angegebenen Feldern, wenn der
        Benutzer der Besitzer des Profils ist.

        Nur erlaubte Felder werden berücksichtigt. Bei unzulässigen Feldern wird ein Fehler zurückgegeben.
        """
        profile = get_object_or_404(Profile, pk=pk)
        if profile.user != request.user:
            raise PermissionDenied("Sie sind nicht berechtig, dieses Profil zu ändern.")
        allowed_fields = {'email', 'first_name', 'last_name', 'file', 'location', 'description', 'working_hours', 'tel'}
        invalid_fields = [field for field in request.data if field not in allowed_fields]
        if invalid_fields:
            return Response({'detail': f"Die Felder {', '.join(invalid_fields)} sind nicht erlaubt."}, status=status.HTTP_400_BAD_REQUEST)
        data = {key: value for key, value in request.data.items() if key in allowed_fields}
        serializer = ProfileSerializer(profile, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class LoginView(APIView):
    """
    API-Endpunkt für die Benutzeranmeldung.

    - `POST`: Authentifiziert einen Benutzer und gibt Benutzerinformationen samt Token zurück.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Verarbeitet Login-Daten, validiert sie über den zugehörigen Serializer
        und gibt bei Erfolg Benutzerinformationen und Authentifizierungs-Token zurück.

        Gibt 400 zurück, wenn die Anmeldedaten ungültig sind.
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response({
                'user_id': serializer.validated_data['user_id'],
                'username': serializer.validated_data['username'],
                'email': serializer.validated_data['email'],
                'token': serializer.validated_data['token']
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomerProfileList(APIView):
    """
    API-Endpunkt zur Auflistung aller Profile mit dem Typ 'customer'.

    Nur authentifizierte Benutzer haben Zugriff.
    """
    permission_classes = [IsAuthenticated]
    pagination_classes = None

    def get(self, request):
        """
        Gibt eine Liste aller Profile mit `type='customer'` zurück.

        Rückgabeformat: Liste serialisierter Profile.
        """
        profiles = Profile.objects.filter(type='customer')
        serializer = CustomerProfilesListSerializer(profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class BusinessProfileList(APIView):
    """
    API-Endpunkt zur Auflistung aller Business-Profile.

    Nur authentifizierte Benutzer dürfen auf diese Liste zugreifen.
    """
    permission_classes = [IsAuthenticated]
    pagination_classes = None

    def get(self, request):
        """
        Gibt alle Profile mit dem Typ 'business' zurück.

        Rückgabe:
            - Liste serialisierter Business-Profile
        """
        profiles = Profile.objects.filter(type='business')
        serializer = BusinessProfilesListSerializer(profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
