import json
import logging

from django.http import HttpResponse

from rest_framework.response import Response

from base.constant import constants
from base.serializer import BaseResponseSerializer

logger = logging.getLogger(__name__)


class PageNotFoundMiddleware(object):
    """
    This middleware class is used to handle the error page not found.

    :param object:
    :type object: object
    :returns: JSON response with status code 404.
    :rtype: dict
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (
            response.status_code == 404
            and "application/json" not in response["content-type"]
        ):
            data = {"error": f"This url {request.path} not found."}

            response = HttpResponse(
                json.dumps(data), content_type="application/json", status=404
            )
        return response


class ResponseMakerMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if isinstance(response, Response):
            res = None
            if response.status_code in [200, 201]:
                res = BaseResponseSerializer.success_response(
                    response.data, response.status_code
                ).data
            elif response.status_code in [400, 401, 403, 404, 405, 409, 500]:
                msg = {
                    400: constants["BadRequestMessage"],
                    401: constants["Authentication"],
                    403: constants["Forbidden"],
                    404: constants["NotFound"],
                    405: constants["MethodNotAllowed"],
                    409: constants["UserAlreadyExist"],
                    500: constants["SomethingWentWrong"],
                }
                res = BaseResponseSerializer.error_response(
                    response.data,
                    status=response.status_code,
                    message=msg[response.status_code],
                ).data
            return HttpResponse(
                json.dumps(res),
                content_type="application/json",
                status=response.status_code,
            )
        return response
