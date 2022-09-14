from django.urls import path

from vendor.views import AddVendorView, VendorDetailView, AddDeliveryPartnerView, DashboardView, SocietyView

urlpatterns = [
    path("add/", AddVendorView.as_view(), name="vendor-create"),
    path("dashboard/", DashboardView.as_view(), name="vendor-dashboard"),
    path("profile/", VendorDetailView.as_view(), name="vendor-profile"),
    path("partner/", AddDeliveryPartnerView.as_view(), name="delivery-partner"),
    path("society/", SocietyView.as_view(), name="vendor-society"),
]
