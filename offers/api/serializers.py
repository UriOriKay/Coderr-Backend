from rest_framework import serializers
from offers.models import Offer, OfferDetail
from django.urls import reverse
from django.db import models


class OfferDetailSerializer(serializers.ModelSerializer):
    """
    Serializer für ein einzelnes Angebotspaket (OfferDetail).
    Validiert Felder wie Preis, Lieferzeit und Features und passt Fehlermeldungen an.
    """
    class Meta:
        model = OfferDetail
        fields = ['title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type', 'id']
        extra_kwargs = {
            'id': {'read_only': True},
        }
    
    def __init__(self, instance=None, data=..., **kwargs):
        """
        Initialisiert den Serializer und erweitert die Standardfehlermeldungen.
        """
        super().__init__(instance, data, **kwargs)
        self._customize_errors_messages()
    
    def _customize_errors_messages(self):
        """
        Überschreibt die Standardfehlermeldungen für bestimmte Felder.
        """
        self.fields['delivery_time_in_days'].error_messages.update({
            'invalid': 'Ungültiger Wert.',
            'min_value': "Die Lieferzeit muss mindestens 1 Tag betragen.",
            'required': 'Diese Feld ist erforderlich.'
        })
        self.fields['price'].error_messages.update({
            'invalid': 'Ungültiger Wert.',
            'min_value': "Die Preis muss mindestens 51,00€ betragen.",
            'required': 'Diese Feld ist erforderlich.'
        })
        self.fields['revisions'].error_messages.update({
            'invalid': 'Ungültiger Wert für Revisionen.',
            'min_value': "Revisionen müssen -1 (unbegrenzt) oder eine positive Zahl sein.",
            'required': 'Diese Feld ist erforderlich.'
        })

    def validate_delivery_time_in_days(self, value):
        """
        Stellt sicher, dass die Lieferzeit mindestens 1 Tag beträgt.
        """
        if value < 1:
            raise serializers.ValidationError("Die Lieferzeit muss mindestens 1 Tag betragen.")
        return value
    
    def validate_price(self, value):
        """
        Stellt sicher, dass der Preis mindestens 51,00€ beträgt.
        """
        if value < 50:
            raise serializers.ValidationError("Die Preis muss mindestens 51,00€ betragen.")
        return value
    
    def validate_revisions(self, value):
        """
        Validiert, dass Revisionen entweder -1 (unbegrenzt) oder eine positive Zahl sind.
        """
        if value < -1:
            raise serializers.ValidationError("Revisionen sollten -1 (unbegrenzt) oder eine positive Zahl sein.")
        return value
    
    def validate_features(self, value):
        """
        Stellt sicher, dass mindestens ein Feature angegeben wurde.
        """
        if not value or len(value) == 0:
            raise serializers.ValidationError("Es muss mindestens ein Feature vorhanden sein.")
        return value


class OfferDetailURLSerializer(serializers.Serializer):
    """
    Serialisiert eine reduzierte Darstellung eines OfferDetail-Objekts,
    bestehend aus dessen ID und der URL zur Detailansicht.
    """
    id = serializers.IntegerField() 
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        """
        Liefert die URL zum jeweiligen OfferDetail anhand seiner ID.
        """
        return reverse('offerdetails', args=[obj.id])



class OfferSerializer(serializers.ModelSerializer):
    """
    Serialisiert das Offer-Modell inkl. verschachtelter Details, minimalem Preis, 
    minimaler Lieferzeit und Benutzerinformationen.
    """
    details = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time', 'user_details']
        extra_kwargs = {
            'user': {'read_only': True},
        }

    def to_representation(self, instance):
        """
        Entfernt bestimmte Felder aus der Ausgabe bei POST-Anfragen.
        """
        representation = super().to_representation(instance)
    
        request = self.context.get('request')
        if request and request.method == 'POST':
            fields_to_exclude = ['created_at', 'updated_at', 'min_price', 'min_delivery_time', 'user_details', 'user']
            for field in fields_to_exclude:
                representation.pop(field, None)

        return representation
    
    def validate(self, attrs):
        """
        Validiert die verschachtelten Angebotsdetails manuell.
        """
        details_data_list = self.initial_data.get('details', [])
        errors = []
        validated_details = []
        for detail_data in details_data_list:
            serializer = OfferDetailSerializer(data=detail_data)
            if serializer.is_valid():
                validated_details.append(serializer.validated_data)
            else:
                errors.append(serializer.errors)
        
        if errors:
            raise serializers.ValidationError({"details": errors})
        attrs['validated_details'] = validated_details
        return attrs
    
    def create(self, validated_data):
        """
        Erstellt ein Offer-Objekt und die zugehörigen OfferDetails.
        """
        validated_details = validated_data.pop('validated_details', [])
        offer = Offer.objects.create(**validated_data)

        for detail in validated_details:
            OfferDetail.objects.create(offer=offer, **detail)

        return offer
    
    def get_details(self, offer):
        """
        Gibt vollständige Details für POST, sonst nur URLs zurück.
        """
        request = self.context.get('request')
        if request and request.method == 'POST':
            return OfferDetailSerializer(offer.details.all(), many=True).data
        return OfferDetailURLSerializer(offer.details.all(), many=True).data
    
    def get_min_price(self, offer):
        """
        Gibt den niedrigsten Preis aus den Angebotsdetails zurück.
        """
        return offer.details.aggregate(models.Min('price'))['price__min']
    
    def get_min_delivery_time(self, offer):
        """
        Gibt die kürzeste Lieferzeit aus den Angebotsdetails zurück.
        """
        return offer.details.aggregate(models.Min('delivery_time_in_days'))['delivery_time_in_days__min']
    
    def get_user_details(self, offer):
        """
        Gibt Informationen zum Benutzer des Angebots zurück.
        """
        user = offer.user
        return {
            'username': user.username, 
            'first_name': user.first_name,
            'last_name': user.last_name
            }
    
    

class SingleDetailOfOfferSerializer(serializers.ModelSerializer):
    """
    Serializer zur Darstellung eines einzelnen Angebotsdetails (OfferDetail).
    Wird z.B. verwendet, um ein einzelnes Paket eines Angebots zu liefern oder bearbeiten.
    """
    class Meta:
        model = OfferDetail
        fields = ['title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type', 'id']
    
class SingleFullOfferDetailSerializer(serializers.ModelSerializer):
    """
    Serializer zur vollständigen Darstellung eines Angebots (Offer) inklusive zugehöriger Angebotsdetails (OfferDetail).

    - Zeigt Basisdaten des Angebots sowie Metainformationen.
    - Gibt die verknüpften Details als URL-basierte Referenzen zurück.
    - Berechnet den minimalen Preis und die minimale Lieferzeit basierend auf verknüpften OfferDetails.
    - Beinhaltet Validierung und Update-Logik für verschachtelte OfferDetails.
    """
    details = OfferDetailURLSerializer(many=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time']

    
    def get_min_price(self, obj):
        """
        Gibt den kleinsten Preis aller verknüpften OfferDetails zurück.
        """
        return obj.details.aggregate(min_price=models.Min('price'))['min_price']
    
    def get_min_delivery_time(self, obj):
        """
        Gibt die kürzeste Lieferzeit unter den OfferDetails zurück.
        """
        return obj.details.aggregate(min_delivery=models.Min('delivery_time_in_days'))['min_delivery']
    
    def validate(self, attrs):
        """
        Validiert eingebettete Angebotsdetails vor dem Update.
        """
        allowed_fields = ['title', 'description', 'details']
        incoming_fields = set(self.initial_data.keys())

        invalid_fields = incoming_fields - set(allowed_fields)
        if invalid_fields:
            raise serializers.ValidationError({"detail": [f"Ungültige Felder: {', '.join(invalid_fields)}"]})


        details_data = self.initial_data.get('details', [])
        errors = []
        for detail in details_data:
            detail_serializer = OfferDetailSerializer(data=detail)
            if not detail_serializer.is_valid():
                errors.append(detail_serializer.errors)
        
        if errors:
            raise serializers.ValidationError({"details": errors})
        attrs['validated_details'] = [
            detail_serializer.validated_data for detail_serializer in map(lambda d: OfferDetailSerializer(data=d), details_data) if detail_serializer.is_valid()
        ]
        return attrs
    
    def update(self, instance, validated_data):
        """
        Führt ein partielles Update durch. Wenn Angebotsdetails (details) enthalten sind,
        wird `_update_details()` aufgerufen.
        """
        details_data = validated_data.pop('validated_details', [])
        validated_data.pop('details', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if details_data:
            self._update_details(instance, details_data)
        instance.save()
        return instance
    
    def _update_details(self, instance, details_data):
        """
        Aktualisiert bestehende oder erstellt neue OfferDetails anhand von offer_type.
        """
        existing_details = {detail.offer_type: detail for detail in instance.details.all()}
        required_fields = ['title', 'price', 'revisions', 'delivery_time_in_days', 'features', 'offer_type']
        allowed_types = {'basic', 'standard', 'premium'}
        for detail_data in details_data:
            offer_type = detail_data.get('offer_type')

            if not offer_type or offer_type not in allowed_types:
                raise serializers.ValidationError({
                    'details': [f"Ungültiger oder fehlender offer_type: {offer_type}"]
            })
            missing_fields = [f for f in required_fields if f not in detail_data]
            if missing_fields:
                raise serializers.ValidationError({
                    'details': [f"Fehlende Felder für {offer_type}: {', '.join(missing_fields)}"]
                })
        
            if offer_type in existing_details:
                self._update_detail_instance(existing_details.pop(offer_type), detail_data)
            else:
                OfferDetail.objects.create(offer=instance, **detail_data)
    
    def _update_detail_instance(self, detail_instance, detail_data):
        """
        Wendet Updates auf ein bestehendes OfferDetail-Objekt an.
        """
        for attr, value in detail_data.items():
            setattr(detail_instance, attr, value)
        detail_instance.save()