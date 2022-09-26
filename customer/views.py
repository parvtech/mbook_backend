from django.db import IntegrityError
from django.db.models import Value, FloatField, Q

from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from base.models import PublicId, TempOtp
from base.utils import PostTokenMatchesOASRequirement
from customer.models import Customer
from customer.serializers import CustomerSerializer, CustomerListBySocietySerializer
from vendor.models import Society
from vendor.views import vendor_obj


class CustomerView(APIView):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [PostTokenMatchesOASRequirement]

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
                    **data
                )
                if request.user.id:
                    customer.seller = vendor_obj(request.user.public_id)
                    customer.save()
                else:
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
                {
                    "error": "Society does not exists."
                },
                status.HTTP_404_NOT_FOUND,
            )

    def get(self, request):
        society_id = request.GET.get("society_id")
        customers = Customer.objects.annotate(liter=Value(0, output_field=FloatField()),
                                              price=Value(0, output_field=FloatField())).filter(
            Q(seller=vendor_obj(request.user.public_id)) & Q(society__public_id=society_id),
        )
        return Response(CustomerListBySocietySerializer(customers, many=True).data)
