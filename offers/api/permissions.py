from rest_framework.permissions import BasePermission

class IsOwnerOrAdmin(BasePermission):
    """
    Custom-Permission-Klasse für Schreibrechte:
    Erlaubt nur dem Eigentümer (`obj.user`) oder einem Administrator (`is_staff`),
    auf das Objekt zuzugreifen bzw. es zu verändern.

    Wird typischerweise bei Angeboten (Offers) verwendet, um sicherzustellen,
    dass nur berechtigte Nutzer Inhalte bearbeiten oder löschen können.
    """
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user or request.user.is_staff