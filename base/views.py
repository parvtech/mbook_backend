from rest_framework.views import APIView

from oauth2_provider.contrib.rest_framework import (
    OAuth2Authentication,
    TokenMatchesOASRequirements)


class BaseView(APIView):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenMatchesOASRequirements]

    required_alternate_scopes = {
        "POST": [["create"]],
        "GET": [["read"]],
        "PATCH": [["update"]],
        "PUT": [["update"]],
        "DELETE": [["delete"]],
    }
