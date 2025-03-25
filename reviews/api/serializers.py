from rest_framework import serializers
from reviews.models import Review

class ReviewsSerializer(serializers.ModelSerializer):
    """
    Serializer für das Review-Modell.
    
    - Behandelt Erstellen und Validieren von Bewertungen.
    - Stellt sicher, dass nur Kunden Bewertungen erstellen.
    - Eine Bewertung pro Business-User ist erlaubt.
    """
    class Meta:
        model = Review
        fields = ['id', 'reviewer', 'business_user', 'rating', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'reviewer']

    def validate(self, data):
        """
        Führt benutzerdefinierte Validierung durch:
        - Nutzer muss authentifiziert sein
        - Nutzer muss Kundentyp haben
        - Nur ein Review pro Business-User erlaubt
        - Business-User muss ein gültiges Business-Profil haben
        """
        reviewer = self.context['request'].user

        if not reviewer.is_authenticated:
            raise serializers.ValidationError({'detail:' ["Sie müssen angemeldet sein, um eine Bewertung abgeben zu können"]})
        
        if not reviewer.profile.type == 'customer':
            raise serializers.ValidationError({'detail:' ["Nur User mit einem Kundenprofil können Bewertungen abgeben"]})

        if 'reviewer' in self.initial_data and int(self.initial_data['reviewer']) != reviewer.id:
            raise serializers.ValidationError({'detail:' ["Sie können keine Bewertung im Namen eines anderen Users abgeben"]})

        business_user = data.get('business_user') or getattr(self.instance, 'business_user', None)

        if not business_user or not hasattr(business_user, 'profile') or business_user.profile.type != 'business':
            raise serializers.ValidationError({'detail': ["Dieser Benutzer ist kein Business-Profil."]})

        if self.instance is None and Review.objects.filter(business_user=business_user, reviewer=reviewer).exists():
            raise serializers.ValidationError({'detail': ["Sie haben bereits eine Bewertung abgegeben"]})
        return data
    
    def create(self, validated_data):
        """
        Setzt den Reviewer automatisch auf den aktuellen Nutzer.
        """
        validated_data['reviewer'] = self.context['request'].user
        return super().create(validated_data)