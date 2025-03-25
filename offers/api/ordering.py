from django.db.models import QuerySet


class OrderingHelperOffers:
    """
    Utility-Klasse zur Sortierung von Offer-Querysets basierend auf definierten Parametern.
    Diese Klasse stellt eine zentrale Stelle bereit, um Sortierlogik für Angebotlisten zu kapseln.

    Aktuell unterstützte Felder:
    - 'min_price', '-min_price'
    - 'created_at', '-created_at'
    - 'updated_at', '-updated_at'
    """
    @staticmethod
    def apply_ordering(queryset: QuerySet, ordering: str) -> QuerySet:
        """
        Wendet ein Ordering auf ein QuerySet von Angeboten an.

        Args:
            queryset (QuerySet): Das ursprüngliche QuerySet der Angebote.
            ordering (str): Das Sortierfeld als String, z. B. '-min_price'.

        Returns:
            QuerySet: Das sortierte QuerySet.
        """
        ordering_map = {
            'min_price': 'min_price',
            '-min_price': '-min_price',
            'created_at': 'created_at',
            '-created_at': '-created_at',
            'updated_at': 'updated_at',
            '-updated_at': '-updated_at',
        }
        ordering_field = ordering_map.get(ordering, 'created_at')
        return queryset.order_by(ordering_field)