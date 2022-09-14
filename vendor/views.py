from datetime import timedelta

import requests
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.utils import timezone
from oauth2_provider.models import Application, AccessToken
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from base.models import PublicId, TempOtp, User
from base.views import BaseView
from customer.models import Customer
from mbook_backend.settings import USER_OTP_EXPIRED
from vendor.models import Vendor, VendorDeliveryPartner, Society
from vendor.serializers import AddVendorSerializer, VerifyOtpSerializer, ResendOtpSerializer, ProfileDetailSerializer, \
    CreateDeliveryPartnerSerializer, DeliveryPartnerListSerializer, SocietySerializer, CreateSocietySerializer, \
    LoginSerializer
import sys


def str_to_class(classname):
    return getattr(sys.modules[__name__], classname)


def vendor_obj(public_id):
    return Vendor.objects.get(public_id=public_id)


class DashboardView(BaseView):
    def get(self, request):
        vendor = vendor_obj(request.user.public_id)
        data = {
            "customers": Customer.objects.filter(seller=vendor).count(),
            "delivery_partners": VendorDeliveryPartner.objects.filter(seller=vendor).count(),
            "society": 0,
            "today_delivered_milk": 0
        }
        return Response(data)


class AddVendorView(APIView):
    @staticmethod
    def post(request):
        try:
            serializer = AddVendorSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                data = serializer.validated_data
                vendor = Vendor.objects.create(
                    username=PublicId.create_public_id(),
                    **data
                )
                vendor.set_password("qwerty")
                vendor.save()
                otp = TempOtp.objects.create(
                    public_id=PublicId.create_public_id(),
                    user=vendor,
                    otp=0000
                )
                res = {
                    "public_id": vendor.public_id,
                    "message": "Otp send successfully."
                }
                return Response(res)
        except IntegrityError:
            return Response({"error": "Mobile number already registered."}, status.HTTP_400_BAD_REQUEST)


class LogoutView(BaseView):
    @staticmethod
    def delete(request):
        AccessToken.objects.filter(user=request.user).delete()
        return Response({"message": "Logout successfully."})


class LoginView(APIView):
    @staticmethod
    def post(request):
        try:
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                data = serializer.validated_data
                cls_instance = str_to_class(data["user_type"])
                user_obj = cls_instance.objects.get(mobile_no=data["mobile_no"])
                TempOtp.objects.create(
                    public_id=PublicId.create_public_id(),
                    user=user_obj,
                    otp=0000
                )
                res = {
                    "public_id": user_obj.public_id,
                    "message": "Otp send successfully."
                }
                return Response(res, status=200)
        except ObjectDoesNotExist:
            return Response({"error": "This mobile number doesn't exists."}, status.HTTP_400_BAD_REQUEST)


class ResendOtpView(APIView):
    @staticmethod
    def post(request):
        serializer = ResendOtpSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            otp = 0000
            temp_obj = TempOtp.objects.get(user__public_id=serializer.validated_data["public_id"])
            temp_obj.otp = otp
            temp_obj.save()
            return Response({"message": "Resend otp send successfully."})


class VerifyOtpView(APIView):
    @staticmethod
    def post(request):
        try:
            serial_data = VerifyOtpSerializer(data=request.data)
            if serial_data.is_valid(raise_exception=True):
                data = serial_data.validated_data
                temp_otp_obj = TempOtp.objects.get(user__public_id=data["public_id"], otp=data["otp"])
                # check otp expiry time
                expiry_date = temp_otp_obj.created_at + timedelta(
                    minutes=USER_OTP_EXPIRED)
                if timezone.now() > expiry_date:
                    # delete expired token
                    temp_otp_obj.delete()
                    return Response({"error": "Otp expired."}, status.HTTP_400_BAD_REQUEST)
                user = User.objects.get(public_id=data["public_id"])
                if Application.objects.filter(user=user).exists():
                    app = Application.objects.filter(user=user).last()
                else:
                    app = Application.objects.create(
                        user=user,
                        authorization_grant_type="password",
                        client_type="confidential",
                        name=user.username
                    )
                data = {
                    "username": user.username,
                    "password": "qwerty",
                    "grant_type": "password",
                    "client_id": app.client_id,
                    "client_secret": app.client_secret,
                }
                token = requests.post(request.META["wsgi.url_scheme"] + "://" + request.META["HTTP_HOST"] + "/o/token/",
                                      data=data)
                data = token.json()
                data["fullname"] = user.first_name
                data["access_token"] = data.pop("token_type") + " " + data["access_token"]
                user.is_verify = True
                user.save()
                temp_otp_obj.delete()
                return Response(data, status=200)
        except TempOtp.DoesNotExist:
            return Response({"error": "Invalid otp."}, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            return Response({"error": "Something went wrong."}, status.HTTP_500_INTERNAL_SERVER_ERROR)


class VendorDetailView(BaseView):

    def get(self, request):
        return Response(ProfileDetailSerializer(vendor_obj(request.user.public_id)).data)

    def patch(self, request):
        serial_data = AddVendorSerializer(data=request.data, partial=True)
        if serial_data.is_valid(raise_exception=True):
            data = serial_data.validated_data
            vendor = vendor_obj(request.user.public_id)
            for key, value in data.items():
                setattr(vendor, key, value)
            vendor.save()
            return Response({"message": "Profile updated."})


class AddDeliveryPartnerView(BaseView):
    @staticmethod
    def post(request):
        try:
            serial_data = CreateDeliveryPartnerSerializer(data=request.data)
            if serial_data.is_valid(raise_exception=True):
                data = serial_data.validated_data
                public = PublicId.create_public_id()
                VendorDeliveryPartner.objects.create(
                    public_id=public,
                    first_name=data["name"],
                    mobile_no=data["mobile_no"],
                    username=public,
                    seller=vendor_obj(request.user.public_id)
                )
                return Response({"message": "Delivery partner created successfully."}, status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({"error": "Mobile number already registered."}, status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        return Response(
            DeliveryPartnerListSerializer(
                VendorDeliveryPartner.objects.filter(seller=vendor_obj(request.user.public_id)),
                many=True).data
        )


class SocietyView(BaseView):
    @staticmethod
    def get(request):
        return Response(SocietySerializer(Society.objects.filter(), many=True).data)

    @staticmethod
    def post(request):
        serial_data = CreateSocietySerializer(data=request.data)
        if serial_data.is_valid(raise_exception=True):
            data = serial_data.validated_data
            society = Society.objects.create(
                public_id=PublicId.create_public_id(),
                vendor=vendor_obj(request.user.public_id),
                **data
            )
            return Response({"public_id": society.public_id, "message": "Society added successfully."},
                            status.HTTP_201_CREATED)
