from rest_framework import serializers

from customer.models import Customer, CustomerOrder


class CustomerSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    mobile_no = serializers.CharField(max_length=15)
    house_no = serializers.CharField(max_length=50)
    block_no = serializers.CharField(max_length=50)
    address = serializers.CharField(max_length=255)
    pincode = serializers.IntegerField(required=False)
    avatar = serializers.ImageField(required=False)
    lat = serializers.DecimalField(max_digits=11, decimal_places=2, required=False)
    long = serializers.DecimalField(max_digits=11, decimal_places=2, required=False)
    start_date = serializers.DateField()
    shift = serializers.ChoiceField(choices=["morning", "evening", "both"])
    milk_unit = serializers.FloatField()
    unit_price = serializers.FloatField()
    society_id = serializers.IntegerField()
    partner_id = serializers.IntegerField()


class CustomerListBySocietySerializer(serializers.ModelSerializer):
    liter = serializers.FloatField(source="milk_unit")
    price = serializers.FloatField(source="unit_price")
    society_id = serializers.IntegerField(source="society.public_id")
    is_payment = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            "public_id",
            "name",
            "house_no",
            "block_no",
            "address",
            "pincode",
            "lat",
            "long",
            "liter",
            "price",
            "society_id",
            "is_payment"
        ]

    def get_is_payment(self, obj):
        is_payment = False
        customer_orders = CustomerOrder.objects.filter(customer=obj)
        for order in customer_orders:
            is_payment = order.is_payment
        return is_payment


class CustomerListByShiftSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="customer.name")
    customer_public_id = serializers.IntegerField(source="customer.public_id")
    order_public_id = serializers.IntegerField(source="public_id")
    house_no = serializers.CharField(source="customer.house_no")
    block_no = serializers.CharField(source="customer.block_no")
    address = serializers.CharField(source="customer.address")
    pincode = serializers.CharField(source="customer.pincode")
    lat = serializers.CharField(source="customer.lat")
    long = serializers.CharField(source="customer.long")

    class Meta:
        model = CustomerOrder
        fields = [
            "customer_public_id",
            "order_public_id",
            "name",
            "house_no",
            "block_no",
            "address",
            "pincode",
            "lat",
            "long",
            "shift",
            "milk_quantity",
            "price",
            "status",
            "order_date",
        ]


class CreateOrderSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    shift = serializers.CharField()
    milk_quantity = serializers.FloatField()
    price = serializers.FloatField()
    order_date = serializers.DateField()


STATUS = ((1, "on_the_way"), (2, "delivered"))


class UpdateCustomerOrderSerializer(serializers.Serializer):
    is_payment = serializers.BooleanField(required=False)
    status = serializers.ChoiceField(choices=STATUS, required=False)

