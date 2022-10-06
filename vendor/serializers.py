import calendar

from django.db.models import Sum
from django.utils.datetime_safe import datetime

from rest_framework import serializers

from customer.models import CustomerOrder
from vendor.models import Society, Vendor, VendorDeliveryPartner


class AddVendorSerializer(serializers.Serializer):
    dairy_name = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=50)
    mobile_no = serializers.CharField(max_length=50)
    address = serializers.CharField(max_length=255)
    pincode = serializers.IntegerField()
    avatar = serializers.ImageField(required=False)
    lat = serializers.DecimalField(max_digits=11, decimal_places=2, required=True)
    long = serializers.DecimalField(max_digits=11, decimal_places=2, required=True)


class VerifyOtpSerializer(serializers.Serializer):
    public_id = serializers.IntegerField()
    otp = serializers.IntegerField()


class ResendOtpSerializer(serializers.Serializer):
    public_id = serializers.IntegerField()


class ProfileDetailSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    def get_avatar(self, vendor):
        try:
            return self.context["request"].build_absolute_uri(vendor.avatar.url)
        except:
            return None

    class Meta:
        model = Vendor
        fields = [
            "public_id",
            "dairy_name",
            "name",
            "mobile_no",
            "address",
            "avatar",
            "pincode",
        ]


class VendorProfileSerailizer(serializers.Serializer):
    dairy_name = serializers.CharField(max_length=50, required=False)
    name = serializers.CharField(max_length=50, required=False)
    mobile_no = serializers.CharField(max_length=50, required=False)
    address = serializers.CharField(max_length=255, required=False)
    pincode = serializers.IntegerField(required=False)
    avatar = serializers.ImageField(required=False)
    lat = serializers.DecimalField(max_digits=11, decimal_places=2, required=True)
    long = serializers.DecimalField(max_digits=11, decimal_places=2, required=True)


class CreateDeliveryPartnerSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)
    mobile_no = serializers.CharField(max_length=15)


class DeliveryPartnerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorDeliveryPartner
        fields = ["public_id", "first_name", "mobile_no"]


class SocietySerializer(serializers.ModelSerializer):
    liter = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Society
        fields = [
            "public_id",
            "name",
            "address",
            "pincode",
            "lat",
            "long",
            "liter",
            "price",
        ]

    def get_liter(self, obj):
        total_milk = 0
        if self.context["request"].GET.get("date"):
            date = datetime.strptime(
                self.context["request"].GET.get("date"), "%Y-%m"
            ).date()

            last_date = calendar.monthrange(date.year, date.month)[1]
            customer_orders = CustomerOrder.objects.filter(
                vendor=obj.vendor,
                order_date__day__gte=1,
                order_date__day__lte=last_date,
                order_date__month=date.month,
                is_payment=False,
                customer__society=obj,
            )
        else:
            customer_orders = CustomerOrder.objects.filter(
                vendor=obj.vendor, is_payment=False, customer__society=obj
            )
        for customer_order in customer_orders:
            total_milk += customer_order.milk_quantity

        return total_milk

    def get_price(self, obj):
        total_price = 0
        if self.context["request"].GET.get("date"):
            date = datetime.strptime(
                self.context["request"].GET.get("date"), "%Y-%m"
            ).date()

            last_date = calendar.monthrange(date.year, date.month)[1]
            customer_orders = CustomerOrder.objects.filter(
                vendor=obj.vendor,
                order_date__day__gte=1,
                order_date__day__lte=last_date,
                order_date__month=date.month,
                is_payment=False,
                customer__society=obj,
            )
        else:
            customer_orders = CustomerOrder.objects.filter(
                vendor=obj.vendor, is_payment=False, customer__society=obj
            )
        for customer_order in customer_orders:
            price = customer_order.milk_quantity * customer_order.price
            total_price += price

        return total_price


class CreateSocietySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    address = serializers.CharField(max_length=255)
    pincode = serializers.IntegerField()
    lat = serializers.DecimalField(max_digits=11, decimal_places=2, required=True)
    long = serializers.DecimalField(max_digits=11, decimal_places=2, required=True)


class LoginSerializer(serializers.Serializer):
    mobile_no = serializers.CharField(max_length=15)
    # user_type = serializers.ChoiceField(choices=(('vendor', 'vendor'),
    #                                              ('customer', 'customer'),
    #                                              ('delivery_partner', 'delivery_partner')), required=True)


class CalendarSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(source="customer.public_id")
    order_id = serializers.IntegerField(source="public_id")

    class Meta:
        model = CustomerOrder
        fields = ["customer_id", "order_id", "order_date", "milk_quantity", "price"]


class CalendarDetailSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(source="customer.public_id")
    order_id = serializers.IntegerField(source="public_id")

    class Meta:
        model = CustomerOrder
        fields = [
            "customer_id",
            "order_id",
            "shift",
            "order_date",
            "milk_quantity",
            "price",
        ]


class OrderDetailSerializer(serializers.Serializer):
    date = serializers.IntegerField()
    morning_milk = serializers.SerializerMethodField()
    evening_milk = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()


class GetMonthlyBillDetailSerializer(serializers.ModelSerializer):
    milk_quantity = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = CustomerOrder
        fields = ["order_date", "milk_quantity", "price"]

    def get_milk_quantity(self, obj):
        morning_milk = None
        evening_milk = None
        orders = CustomerOrder.objects.filter(
            order_date=obj.order_date, customer=obj.customer
        )
        for order in orders:
            if order.shift == "morning":
                morning_milk = order.milk_quantity
            else:
                evening_milk = order.milk_quantity
            result = {"morning_milk": morning_milk, "evening_milk": evening_milk}
        return result

    def get_price(self, obj):
        price = 0
        orders = CustomerOrder.objects.filter(
            order_date=obj.order_date, customer=obj.customer
        )
        for order in orders:
            price += order.milk_quantity * order.price

        return price
