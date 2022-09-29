import json
from collections import OrderedDict
from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import FloatField, IntegerField, Value
from django.utils import timezone

import requests
from oauth2_provider.models import AccessToken, Application
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from base.models import PublicId, TempOtp, User
from base.pagination import custom_pagination
from base.views import BaseView
from customer.models import Customer, CustomerOrder
from mbook_backend.settings import USER_OTP_EXPIRED
from vendor.models import Society, Vendor, VendorDeliveryPartner
from vendor.serializers import (
    AddVendorSerializer,
    CalendarSerializer,
    CreateDeliveryPartnerSerializer,
    CreateSocietySerializer,
    DeliveryPartnerListSerializer,
    LoginSerializer,
    ProfileDetailSerializer,
    ResendOtpSerializer,
    SocietySerializer,
    VerifyOtpSerializer,
)


def vendor_obj(public_id):
    return Vendor.objects.get(public_id=public_id)


class DashboardView(BaseView):
    def get(self, request):
        vendor = vendor_obj(request.user.public_id)
        data = {
            "customers": Customer.objects.filter(seller=vendor).count(),
            "delivery_partners": VendorDeliveryPartner.objects.filter(
                seller=vendor
            ).count(),
            "society": Society.objects.filter(vendor=vendor).count(),
            "today_delivered_milk": 0,
        }
        print("Hello")
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
                    first_name=data.pop("name"),
                    **data
                )
                vendor.set_password("qwerty")
                vendor.save()
                TempOtp.objects.create(
                    public_id=PublicId.create_public_id(), user=vendor, otp=0000
                )
                res = {
                    "public_id": vendor.public_id,
                    "message": "Otp send successfully.",
                }
                return Response(res)
        except IntegrityError:
            return Response(
                {"error": "Mobile number already registered."},
                status.HTTP_400_BAD_REQUEST,
            )


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
                user_obj = User.objects.get(mobile_no=data["mobile_no"])
                TempOtp.objects.create(
                    public_id=PublicId.create_public_id(), user=user_obj, otp=0000
                )
                res = {
                    "public_id": user_obj.public_id,
                    "message": "Otp send successfully.",
                }
                return Response(res, status=200)
        except ObjectDoesNotExist:
            return Response(
                {"error": "This mobile number doesn't exists."},
                status.HTTP_400_BAD_REQUEST,
            )


class ResendOtpView(APIView):
    @staticmethod
    def post(request):
        try:
            serializer = ResendOtpSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                otp = 0000
                temp_obj = TempOtp.objects.get(
                    user__public_id=serializer.validated_data["public_id"]
                )
                temp_obj.otp = otp
                temp_obj.save()
                return Response({"message": "Resend otp send successfully."})
        except TempOtp.DoesNotExist:
            return Response({"error": "Request denied."}, status.HTTP_400_BAD_REQUEST)


class VerifyOtpView(APIView):
    @staticmethod
    def post(request):
        try:
            serial_data = VerifyOtpSerializer(data=request.data)
            if serial_data.is_valid(raise_exception=True):
                data = serial_data.validated_data
                role = None
                temp_otp_obj = TempOtp.objects.filter(
                    user__public_id=data["public_id"], otp=data["otp"]
                ).last()
                if temp_otp_obj is None:
                    return Response(
                        {
                            "error": "OTP has been expired. Please generate new OTP and try again.."
                        },
                        status.HTTP_400_BAD_REQUEST,
                    )
                if Vendor.objects.filter(public_id=data["public_id"]).exists:
                    role = "vendor"
                elif Customer.objects.filter(public_id=data["public_id"]).exists:
                    role = "customer"
                elif VendorDeliveryPartner.objects.filter(
                    public_id=data["public_id"]
                ).exists:
                    role = "delivery"
                # check otp expiry time
                expiry_date = temp_otp_obj.created_at + timedelta(
                    minutes=USER_OTP_EXPIRED
                )
                if timezone.now() > expiry_date:
                    # delete expired token
                    temp_otp_obj.delete()
                    return Response(
                        {"error": "Otp expired."}, status.HTTP_400_BAD_REQUEST
                    )
                user = User.objects.get(public_id=data["public_id"])
                if Application.objects.filter(user=user).exists():
                    app = Application.objects.filter(user=user).last()
                else:
                    app = Application.objects.create(
                        user=user,
                        authorization_grant_type="password",
                        client_type="confidential",
                        name=user.username,
                    )
                data = {
                    "username": user.username,
                    "password": "qwerty",
                    "grant_type": "password",
                    "client_id": app.client_id,
                    "client_secret": app.client_secret,
                }
                token = requests.post(
                    request.build_absolute_uri("/") + "o/token/",
                    data=data,
                )
                data = token.json()
                data["name"] = user.first_name
                data["role"] = role
                data["access_token"] = (
                    data.pop("token_type") + " " + data["access_token"]
                )
                user.is_verify = True
                user.save()
                temp_otp_obj.delete()
                return Response(data, status=200)
        except TempOtp.DoesNotExist:
            return Response(
                {"error": "Please enter a valid OTP."}, status.HTTP_400_BAD_REQUEST
            )


class VendorDetailView(BaseView):
    def get(self, request):
        return Response(
            ProfileDetailSerializer(
                vendor_obj(request.user.public_id), context={"request": request}
            ).data
        )

    def patch(self, request):
        try:
            serial_data = AddVendorSerializer(data=request.data, partial=True)
            if serial_data.is_valid(raise_exception=True):
                data = serial_data.validated_data
                vendor = vendor_obj(request.user.public_id)
                for key, value in data.items():
                    try:
                        setattr(vendor, key, value)
                    except:
                        vendor.first_name = value
                vendor.save()
                return Response({"message": "Profile updated."})
        except IntegrityError:
            return Response(
                {"error": "This mobile number associated with another user."},
                status.HTTP_400_BAD_REQUEST,
            )


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
                    seller=vendor_obj(request.user.public_id),
                )
                return Response(
                    {"message": "Delivery partner created successfully."},
                    status.HTTP_201_CREATED,
                )
        except IntegrityError:
            return Response(
                {"error": "Mobile number already registered."},
                status.HTTP_400_BAD_REQUEST,
            )

    def get(self, request):
        pagination = request.GET.get("pagination")
        limit, offset = custom_pagination(request)
        partner = VendorDeliveryPartner.objects.filter(
            seller=vendor_obj(request.user.public_id)
        )
        response = partner[offset:limit] if pagination == "true" else partner
        partner_list = DeliveryPartnerListSerializer(
            response,
            many=True,
        ).data
        return Response({"partner_list": partner_list, "count": partner.count()})


class SocietyView(BaseView):
    @staticmethod
    def get(request):
        society = Society.objects.annotate(
            liter=Value(0, output_field=FloatField())
        ).filter(vendor=vendor_obj(request.user.public_id))
        serial_data = SocietySerializer(society, many=True).data
        return Response(serial_data)

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
            return Response(
                {
                    "public_id": society.public_id,
                    "message": "Society added successfully.",
                },
                status.HTTP_201_CREATED,
            )


class DeliveryPartnerView(BaseView):
    @staticmethod
    def delete(request, public_id):
        try:
            vendor_partner = VendorDeliveryPartner.objects.get(public_id=public_id)
            vendor_partner.delete()
            return Response({"message": "Partner deleted successfully."})
        except VendorDeliveryPartner.DoesNotExist:
            return Response(
                {"error": "Partner id does not exists."}, status.HTTP_404_NOT_FOUND
            )


class CalendarView(BaseView):
    def get(self, request):
        month = request.GET.get("month")
        year = request.GET.get("year")
        customer_id = request.GET.get("customer_id")
        if month and year:
            order_data = CustomerOrder.objects.filter(
                order_date__month=month,
                order_date__year=year,
                customer__public_id=customer_id,
                vendor=vendor_obj(request.user.public_id),
            )
            result = json.loads(
                json.dumps(CalendarSerializer(order_data, many=True).data)
            )
            filter_data = []
            ids = []
            for order in result:
                customer_id = order["customer_id"]
                if customer_id in ids:
                    index = ids.index(customer_id)
                    update_data = filter_data[index]
                    old_milk = update_data["milk"]
                    update_data["milk"] = old_milk + order["milk_quantity"]
                else:
                    data_prepare = {
                        "order_date": order["order_date"],
                        "milk": order["milk_quantity"],
                        "customer_id": customer_id,
                        "order_id": order["order_id"],
                    }
                    filter_data.append(data_prepare)
                    ids.append(customer_id)
            return Response(filter_data)
        return Response({"message": "Record not found"})
