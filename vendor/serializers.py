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
    liter = serializers.FloatField()

    class Meta:
        model = Society
        fields = ["public_id", "name", "address", "pincode", "lat", "long", "liter"]


class CreateSocietySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    address = serializers.CharField(max_length=255)
    pincode = serializers.IntegerField()
    lat = serializers.DecimalField(max_digits=11, decimal_places=2, required=True)
    long = serializers.DecimalField(max_digits=11, decimal_places=2, required=True)


class LoginSerializer(serializers.Serializer):
    mobile_no = serializers.CharField(max_length=15)


class CalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerOrder
        fields = "__all__"
