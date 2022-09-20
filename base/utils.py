from rest_framework.permissions import BasePermission


class PostTokenMatchesOASRequirement(BasePermission):
    """
    Class override for disable get permission on anonymous user.
    """

    def has_permission(self, request, view):
        # allow all GET requests
        if request.method == "POST":
            if request.headers.get("Authorization") and request.user.username == "":
                return request.user and request.user.is_authenticated
            return True
        return request.user and request.user.is_authenticated
