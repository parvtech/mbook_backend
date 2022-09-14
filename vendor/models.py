from django.db import models

from base.models import User, PublicId, BaseModel


class Vendor(User):
    class Meta:
        db_table = 'vendor'

    dairy_name = models.CharField(max_length=255)

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


class VendorDeliveryPartner(User):
    class Meta:
        db_table = "vendor_delivery_partner"

    # vendor.VendorDeliveryPartner.vendor: (models.E006) The field 'vendor' clashes with the field 'vendor' from
    # model 'base.user'.
    seller = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="seller")


class Society(BaseModel):
    class Meta:
        db_table = "society"

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="vendor_society")
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True, blank=True)
    pincode = models.CharField(max_length=8, null=True, blank=True)
    lat = models.DecimalField(max_digits=11, decimal_places=2, null=True, blank=True)
    long = models.DecimalField(max_digits=11, decimal_places=2, null=True, blank=True)
