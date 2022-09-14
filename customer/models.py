from django.db import models

from base.models import User, PublicId
from vendor.models import Vendor, Society

SHIFTS = ((1, "morning"), (2, "evening"), (3, "both"))


class Customer(User):
    class Meta:
        db_table = "Customer"

    start_date = models.DateField()
    shift = models.CharField(choices=SHIFTS, max_length=10, null=True, blank=True)
    milk_unit = models.IntegerField()
    unit_price = models.DecimalField(max_digits=7, decimal_places=2)
    seller = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="vendor_customer")
    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name="vendor_customer_society")

    def __str__(self):
        return "{}".format(self.username)

    def save(self, *args, **kwargs):
        if not self.id:
            self.public_id = PublicId.create_public_id()
        super(User, self).save(*args, **kwargs)

    @property
    def fullname(self):
        if self.first_name and self.last_name:
            return self.first_name + ' ' + self.last_name
        return self.username
