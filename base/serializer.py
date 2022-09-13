from rest_framework import serializers
from rest_framework.response import Response

from base.constant import constants


class ErrorListField(serializers.ListField):
    error = serializers.DictField()


class BaseResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    errors = ErrorListField(required=False)
    data = serializers.JSONField(required=False)
    message = serializers.CharField()
    code = serializers.IntegerField()

    @staticmethod
    def success_response(result, status):
        return Response(
            BaseResponseSerializer(
                {
                    "success": True,
                    "data": result.data
                    if isinstance(result, serializers.ModelSerializer)
                    else result,
                    "code": status,
                    "message": constants["SuccessfullyCreated"]
                    if status == 201
                    else constants["SuccessfullyCompleted"],
                }
            ).data,
            status=status,
        )

    @staticmethod
    def success_response_with_msg(result, status):
        return Response(
            BaseResponseSerializer({"code": status, "message": result}).data,
            status=status,
        )

    @staticmethod
    def error_response(error, status, message):
        if isinstance(error, Exception):
            return Response(
                BaseResponseSerializer(
                    {
                        "success": False,
                        "code": status,
                        "message": message,
                        "errors": [str(error)],
                        "data": {},
                    }
                ).data,
                status=status,
            )
        if isinstance(error, list):
            return Response(
                BaseResponseSerializer(
                    {
                        "success": False,
                        "message": message,
                        "data": {},
                        "code": status,
                        "errors": error,
                    }
                ).data,
                status=status,
            )
        return Response(
            BaseResponseSerializer(
                {
                    "success": False,
                    "message": message,
                    "data": {},
                    "code": status,
                    "errors": [error],
                }
            ).data,
            status=status,
        )
