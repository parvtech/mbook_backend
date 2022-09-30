from django.db import models

from base.models import BaseModel, PublicId, User
from vendor.models import Society, Vendor, VendorDeliveryPartner

SHIFTS = ((1, "morning"), (2, "evening"), (3, "both"))
STATUS = ((1, "on_the_way"), (2, "delivered"))


class Customer(User):
    class Meta:
        db_table = "customer"

    start_date = models.DateField()
    shift = models.CharField(choices=SHIFTS, max_length=10, null=True, blank=True)
    milk_unit = models.IntegerField()
    unit_price = models.DecimalField(max_digits=7, decimal_places=2)
    seller = models.ForeignKey(
        Vendor, on_delete=models.CASCADE, related_name="vendor_customer", null=True
    )
    partner = models.ForeignKey(
        VendorDeliveryPartner,
        on_delete=models.CASCADE,
        related_name="vendor_customer_partner",
        null=True,
    )
    society = models.ForeignKey(
        Society,
        on_delete=models.CASCADE,
        related_name="vendor_customer_society",
        null=True,
    )

    def __str__(self):
        return "{}".format(self.username)

    def save(self, *args, **kwargs):
        if not self.id:
            self.public_id = PublicId.create_public_id()
        super(User, self).save(*args, **kwargs)

    @property
    def name(self):
        if self.first_name:
            return self.first_name
        return None


class CustomerOrder(BaseModel):
    class Meta:
        db_table = "customer_order"

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="cust_order"
    )
    vendor = models.ForeignKey(
        Vendor, on_delete=models.CASCADE, related_name="vendor_customer_order"
    )
    delivery = models.ForeignKey(
        VendorDeliveryPartner,
        on_delete=models.DO_NOTHING,
        related_name="vendor_delivery_partner_assign_order",
    )
    shift = models.CharField(max_length=150)
    milk_quantity = models.FloatField()
    price = models.FloatField()
    status = models.CharField(choices=STATUS, max_length=10, null=True, blank=True)
    order_date = models.DateField()
    is_payment = models.BooleanField(default=False)
