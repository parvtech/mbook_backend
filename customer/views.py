import calendar
import datetime

from django.db import IntegrityError
from django.db.models import FloatField, Q, Value

from dateutil.relativedelta import relativedelta
from rest_framework import status
from rest_framework.response import Response

from base.models import PublicId, TempOtp
from base.pagination import custom_pagination
from base.views import BaseView
from customer.models import Customer, CustomerOrder
from customer.serializers import (
    CreateOrderSerializer,
    CustomerListByShiftSerializer,
    CustomerListBySocietySerializer,
    CustomerSerializer,
    UpdateCustomerOrderMilkSerializer,
    UpdateCustomerOrderSerializer,
)
from vendor.models import Society, Vendor, VendorDeliveryPartner
from vendor.views import vendor_delivery_obj, vendor_obj


def daterange(date1, date2):
    for n in range(int((date2 - date1).days) + 1):
        yield date1 + datetime.timedelta(n)


def create_customer_order(**data):
    date = data.get("order_date")
    three_month = date + relativedelta(months=+3)
    last_date_third_month = datetime.datetime(
        three_month.year,
        three_month.month,
        calendar.monthrange(three_month.year, three_month.month)[1],
    )
    for dt in daterange(date, last_date_third_month.date()):
        CustomerOrder.objects.create(
            public_id=PublicId.create_public_id(),
            customer=data.get("customer"),
            vendor=data.get("vendor"),
            delivery=data.get("delivery"),
            shift=data.get("shift"),
            milk_quantity=data.get("milk_quantity"),
            price=data.get("price"),
            status=data.get("status"),
            order_date=dt,
            is_payment=False,
        )


class CustomerView(BaseView):
    required_alternate_scopes = {
        "POST": [["create"]],
        "GET": [["read"]],
        "PATCH": [["update"]],
        "PUT": [["update"]],
        "DELETE": [["delete"]],
    }

    def post(self, request):
        try:
            serial_data = CustomerSerializer(data=request.data)
            if serial_data.is_valid(raise_exception=True):
                data = serial_data.validated_data
                public_id = PublicId.create_public_id()
                customer = Customer.objects.create(
                    public_id=public_id,
                    username=public_id,
                    first_name=data.pop("name"),
                    society=Society.objects.get(public_id=data.pop("society_id")),
                    partner=VendorDeliveryPartner.objects.get(
                        public_id=data.pop("partner_id")
                    ),
                    seller=vendor_obj(request.user.public_id),
                    **data
                )
                customer.set_password("qwerty")
                customer.save()
                order_data = {
                    "customer": customer,
                    "vendor": customer.seller,
                    "delivery": customer.partner,
                    "shift": data["shift"],
                    "milk_quantity": data["milk_unit"],
                    "price": data["unit_price"],
                    "status": "on_the_way",
                    "order_date": data["start_date"],
                }
                if data["shift"] == "both":
                    for idx in range(2):
                        shift = "morning"
                        if idx == 0:
                            shift = "evening"
                        order_data["shift"] = shift
                        create_customer_order(**order_data)
                else:
                    create_customer_order(**order_data)
                TempOtp.objects.create(
                    public_id=PublicId.create_public_id(), user=customer, otp=0000
                )
                return Response(
                    {
                        "message": "Added successfully.",
                        "public_id": customer.public_id,
                    }
                )
        except IntegrityError:
            return Response(
                {
                    "error": "Mobile number already registered, Please try with another mobile number."
                },
                status.HTTP_400_BAD_REQUEST,
            )
        except Society.DoesNotExist:
            return Response(
                {"error": "Society does not exists."},
                status.HTTP_404_NOT_FOUND,
            )
        except VendorDeliveryPartner.DoesNotExist:
            return Response(
                {"error": "Delivery partner does not exists."},
                status.HTTP_404_NOT_FOUND,
            )

    def get(self, request):
        pagination = request.GET.get("pagination")
        society_id = request.GET.get("society_id")
        shift = request.GET.get("shift")
        order_date = request.GET.get("order_date")
        # customer = request.GET.get("customer")
        query = Q()
        limit, offset = custom_pagination(request)
        if vendor_obj(request.user.public_id):
            query.add(Q(seller=vendor_obj(request.user.public_id)), query.connector)
        else:
            query.add(
                Q(partner=vendor_delivery_obj(request.user.public_id)), query.connector
            )
        if society_id:
            query.add(Q(society__public_id=society_id), query.connector)

        # if customer:
        #     query = Q()
        customers = Customer.objects.filter(query).order_by("-id")
        if shift and society_id and order_date:
            query = Q()
            query.add(
                Q(order_date=order_date)
                & Q(customer__society__public_id=society_id)
                & Q(shift=shift),
                query.connector,
            )
            if vendor_obj(request.user.public_id):
                query.add(Q(vendor=vendor_obj(request.user.public_id)), query.connector)
            else:
                query.add(
                    Q(delivery=vendor_delivery_obj(request.user.public_id)),
                    query.connector,
                )
            customers = CustomerOrder.objects.filter(query).order_by("-id")
            response = customers[offset:limit] if pagination == "true" else customers
            customers_list = CustomerListByShiftSerializer(response, many=True).data
            society_name = Society.objects.filter(public_id=society_id).first()
            final_data = {
                "customer_list": customers_list,
                "count": customers.count(),
                "society_name": society_name.name if society_name else None,
            }
        else:
            response = customers[offset:limit] if pagination == "true" else customers
            customers_list = CustomerListBySocietySerializer(response, many=True).data
            final_data = {"customer_list": customers_list, "count": customers.count()}
        return Response(final_data)

    def put(self, request):
        try:
            serial_data = CreateOrderSerializer(data=request.data)
            if serial_data.is_valid(raise_exception=True):
                order_data = serial_data.validated_data
                customer = Customer.objects.get(public_id=order_data["customer_id"])
                order_data = {
                    "customer": customer,
                    "vendor": customer.seller,
                    "delivery": customer.partner,
                    "shift": order_data["shift"],
                    "milk_quantity": order_data["milk_unit"],
                    "price": order_data["unit_price"],
                    "status": "on_the_way",
                    "order_date": order_data["start_date"],
                }
                CustomerOrder.objects.get(
                    customer=customer,
                    order_date=order_data["order_date"],
                    shift=order_data["shift"],
                )
                create_customer_order(**order_data)
        except Customer.DoesNotExist:
            return Response(
                {"error": "Order already created with a given date and shift."}
            )


class CustomerPaymentStatusView(BaseView):
    required_alternate_scopes = {
        "POST": [["create"]],
        "GET": [["read"]],
        "PATCH": [["update"]],
        "PUT": [["update"]],
        "DELETE": [["delete"]],
    }

    def patch(self, request, public_id):
        try:
            serial_data = UpdateCustomerOrderSerializer(data=request.data)
            if serial_data.is_valid(raise_exception=True):
                serializer_data = serial_data.validated_data
                customer_order = CustomerOrder.objects.get(public_id=public_id)
                if request.data.get("is_payment"):
                    customer_order.is_payment = serializer_data["is_payment"]
                if request.data.get("status"):
                    customer_order.status = serializer_data["status"]
                customer_order.save()
                return Response(
                    {"message": "Customer Order status updated successfully."}
                )
        except CustomerOrder.DoesNotExist:
            return Response({"error": "Customer order does not exists."})


class CustomerOrderView(BaseView):
    def patch(self, request, customer_order_id):
        try:
            serial_data = UpdateCustomerOrderMilkSerializer(data=request.data)
            if serial_data.is_valid(raise_exception=True):
                serializer_data = serial_data.validated_data
            customer_order = CustomerOrder.objects.get(public_id=customer_order_id)
            if request.data.get("milk_quantity"):
                customer_order.milk_quantity = serializer_data["milk_quantity"]
            customer_order.save()
            return Response(
                {"message": "Customer Order milk quantity updated successfully."}
            )
        except CustomerOrder.DoesNotExist:
            return Response({"error": "Customer order does not exists."})
