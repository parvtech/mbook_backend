from django.urls import path

from customer.views import CustomerView

urlpatterns = [
    path("", CustomerView.as_view(), name="create"),
    path("<str:public_id>/", CustomerView.as_view(), name="create"),


]
