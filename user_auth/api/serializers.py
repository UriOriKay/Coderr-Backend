from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from django.contrib.auth.models import User
from user_auth.models import Profile

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer für das Django User-Modell.

    Wird verwendet, um Benutzerinformationen wie ID, Benutzernamen
    und Namen (Vor- und Nachname) zu serialisieren.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')

class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer zur Registrierung eines neuen Benutzers mit Passwortwiederholung
    und Angabe des Benutzertyps ('business' oder 'customer').

    Validiert:
    - E-Mail (Format, Eindeutigkeit)
    - Benutzername (Eindeutigkeit)
    - Passwortfelder (z. B. Konsistenz)
    - Auswahl eines gültigen Profils
    """
    email = serializers.EmailField(
        required=True,
        error_messages={
            "requiered": "E-Mail ist erfolgreich.",
            "invalid": "E-Mail ist ungültig.",
            "unique": "E-Mail bereits vorhanden."
        }
    )
    username = serializers.CharField(
        required=True,
        error_messages={"unique": ["Benutzername bereits vorhanden."]}
    )
    password = serializers.CharField(
       write_only=True,
       required=True
   )
    repeated_password = serializers.CharField(
        write_only=True,
        required=True
    )

    type = serializers.ChoiceField(
        choices=[('business', 'business'), ('customer', 'customer')],
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'repeated_password', 'type')

    def validate(self, data):
        """
        Überprüft:
        - Einzigartigkeit von Benutzername und E-Mail
        - Übereinstimmung von Passwort und Wiederholung
        """
        if User.objects.filter(username=data['username']).exists() or User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError(
                "Benutzername oder Email bereits vorhanden."
                )
        
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError(
                {"details": ["Die Passwörter stimmen nicht überein."]}
                )
        return data

    def create(self, validated_data):
        """
        Erstellt einen neuen Benutzer mit zugehörigem Profil.
        - Das Passwort wird automatisch gehashed.
        - Ein zugehöriges Profil wird mit dem Typ erstellt.
        """
        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']
        user_type = validated_data['type']
        user = User.objects.create_user(username=username, email=email, password=password)
        Profile.objects.create(user=user, email=email, type=user_type, first_name=username)
        return user

class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer für das Benutzerprofil.

    - Erlaubt das Anzeigen und Bearbeiten von Profilinformationen.
    - Bestimmte Felder sind mit benutzerdefinierten Fehlermeldungen ausgestattet.
    - Die Validierung stellt sicher, dass nur explizit erlaubte Felder verändert werden.
    """
    class Meta:
        model = Profile
        fields = '__all__'
        extra_kwargs = {
            'email': {'error_messages': {'blank': ['Dieses Feld darf nicht leer sein'], 'required': 'Dieses Feld ist erforderlich', 'unique': 'Diese E-Mail ist bereits vergeben'}},
            'first_name': {'error_messages': {'blank': ['Dieses Feld darf nicht leer sein']}},
            'last_name': {'error_messages': {'blank': ['Dieses Feld darf nicht leer sein']}},
            'location': {'error_messages': {'blank': ['Dieses Feld darf nicht leer sein']}},
            'description': {'error_messages': {'blank': ['Dieses Feld darf nicht leer sein']}},
            'working_hours': {'error_messages': {'blank': ['Dieses Feld darf nicht leer sein']}},
            'tel': {'error_messages': {'blank': ['Dieses Feld darf nicht leer sein']}}
        }

    def validate(self, attrs):
        """
        Validiert, ob nur zulässige Felder übermittelt wurden.
        Gibt bei unzulässigen Feldern eine klare Fehlermeldung zurück.
        """
        allowed_fields = {
            'email', 'first_name', 'last_name', 'location', 'description', 'working_hours', 'tel'
        }
        extra_fields = [field for field in attrs.keys() if field not in allowed_fields]

        if extra_fields:
            raise serializers.ValidationError(
                {"detail": [f"Die Felder {', '.join(extra_fields)} können nicht aktualisiert werden. Nur die Felder {', '.join(allowed_fields)} dürfen aktualisiert werden."]}
            )
        return attrs
    
    def update(self, instance, validated_data):
        """
        Aktualisiert nur die erlaubten Felder im Profil.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
    
class LoginSerializer(serializers.Serializer):
    """
    Serializer für den Login-Prozess.

    - Nimmt `username` und `password` entgegen.
    - Prüft, ob der Benutzer existiert und das Passwort korrekt ist.
    - Gibt bei Erfolg den Token sowie Benutzerdaten zurück.
    - Bei Fehlern wird eine konsistente Fehlermeldung ausgegeben.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validiert den Login-Vorgang.

        Schritte:
        - Benutzer anhand des Benutzernamens suchen
        - Passwort überprüfen
        - Token erstellen oder abrufen
        """
        username = data.get('username')
        password = data.get('password')
        user = User.objects.filter(username=username).first()
        if not user:
            raise serializers.ValidationError({"details": ["Falsche Username oder Passwort."]})
        if not user.check_password(password):
            raise serializers.ValidationError({"details": ["Falsche Username oder Passwort."]})
        token, created = Token.objects.get_or_create(user=user)
        data['user_id'] = user.id
        data['token'] = token.key
        data['email'] = user.email
        return data
    

class BusinessProfilesListSerializer(serializers.ModelSerializer):
    """
    Serializer für die Anzeige von Business-Profilen in Listenansichten.

    Enthält:
    - Benutzerinformationen über verschachtelten `UserSerializer`
    - Basisprofilinformationen wie Name, Bild, Standort etc.
    - Konvertiert verschachtelte Benutzerinformationen in eine einfache ID im Output
    """
    user = UserSerializer()
    class Meta:
        model = Profile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'location', 'tel', 'description', 'working_hours', 'type']

    def to_representation(self, instance):
        """
        Überschreibt die Standardausgabe und ersetzt die verschachtelte User-Darstellung
        durch die einfache User-ID.
        """
        representation = super().to_representation(instance)
        representation['user'] = representation['user']['id']
        return representation
    

class CustomerProfilesListSerializer(serializers.ModelSerializer):
    """
    Serializer zur Darstellung von Kundenprofilen in Listenansichten.

    Stellt wichtige Felder des Kundenprofils dar, einschließlich:
    - Benutzer-ID (extrahiert aus verschachteltem User-Objekt)
    - Profilinformationen wie Name, Profilbild, Registrierungszeitpunkt, Typ
    """
    user = UserSerializer()
    class Meta:
        model = Profile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'uploaded_at', 'type']

    def to_representation(self, instance):
        """
        Überschreibt die Standardausgabe, um statt des verschachtelten User-Objekts
        nur die Benutzer-ID auszugeben.
        """
        representation = super().to_representation(instance)
        representation['user'] = representation['user']['id']
        return representation