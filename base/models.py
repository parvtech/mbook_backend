import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class CreateUpdateDate(models.Model):
    class Meta:
        abstract = True

    # Save date and time of add and update.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)


class UniqueIds(models.Model):
    class Meta:
        abstract = True

    id = models.BigAutoField(primary_key=True, unique=True)
    #  public id to share with the in url,
    #  Used for REST routes and public displays
    public_id = models.BigIntegerField(editable=False, unique=True)


class PublicId:
    # method for generating public id
    @staticmethod
    def create_public_id():
        public_id = uuid.uuid4().int >> 75
        return public_id


class BaseModel(CreateUpdateDate, UniqueIds):
    """
    Create model for inheriting purpose only.
    """

    class Meta:
        abstract = True

    pass


class User(AbstractUser, BaseModel):
    """
    This class is created for the user model to create the user with their roles.
    """

    avatar = models.ImageField(upload_to="profile/", null=True, blank=True)
    house_no = models.CharField(max_length=50, null=True, blank=True)
    block_no = models.CharField(max_length=50, null=True, blank=True)
    mobile_no = models.CharField(max_length=15, unique=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    lat = models.DecimalField(max_digits=11, decimal_places=2, null=True, blank=True)
    long = models.DecimalField(max_digits=11, decimal_places=2, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)
    is_verify = models.BooleanField(default=False)


class TempOtp(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_temp_otp"
    )
    otp = models.CharField(max_length=10)
