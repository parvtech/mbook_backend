from django.urls import path

from vendor.views import (
    AddDeliveryPartnerView,
    AddVendorView,
    DashboardView,
    DeliveryPartnerView,
    SocietyView,
    VendorDetailView,
)

urlpatterns = [
    path("add/", AddVendorView.as_view(), name="vendor-create"),
    path("dashboard/", DashboardView.as_view(), name="vendor-dashboard"),
    path("partner/", AddDeliveryPartnerView.as_view(), name="delivery-partner"),
    path(
        "partner/<str:public_id>/",
        DeliveryPartnerView.as_view(),
        name="delivery-partner-detail",
    ),
    path("society/", SocietyView.as_view(), name="vendor-society"),

]
