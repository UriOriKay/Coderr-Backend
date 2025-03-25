from rest_framework import serializers
from orders.models import Order

class OrderListSerializer(serializers.ModelSerializer):
    """
    Serializer für die Darstellung von Bestellungen (Orders) in Listenansichten
    oder Detailansichten (GET).

    Beinhaltet alle relevanten Felder für eine vollständige Anzeige.
    """
    class Meta:
        model = Order
        fields = ['id', 'customer_user', 'business_user', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type','status', 'created_at', 'updated_at']

class OrdersPostSerializer(serializers.ModelSerializer):
    """
    Serializer für das Erstellen einer neuen Bestellung (POST).

    Erwartet lediglich die Übergabe der `offer_detail_id`. Alle anderen
    Felder werden automatisch vom Backend ergänzt (z.B. Preis, Dauer, etc.),
    basierend auf den Daten der verknüpften OfferDetail-Instanz.
    """
    class Meta:
        model = Order
        fields = ['offer_detail_id']

class OrdersPatchSerializer(serializers.ModelSerializer):
    """
    Serializer für Teilaktualisierungen (PATCH) von Bestellungen.

    Unterstützt ausschließlich die Aktualisierung des `status`-Feldes.
    Dies stellt sicher, dass nur autorisierte Änderungen an der
    Auftragsabwicklung erfolgen.
    """
    class Meta:
        model = Order
        fields = ['status']

    def update(self, instance, validated_data):
        """
        Aktualisiert den Status der Bestellung. Falls kein neuer Status
        übermittelt wird, bleibt der aktuelle Status bestehen.
        """
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance