from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.static import serve

import oauth2_provider.views as oauth2_views

from customer.views import CustomerPaymentStatusView, CustomerOrderView
from mbook_backend import settings
from vendor.views import (
    CalendarView,
    LoginView,
    LogoutView,
    ResendOtpView,
    VerifyOtpView, DetailMilkQuantity, MonthlyBillDetail, VendorDetailView,
)

urlpatterns = [
    # Admin app URLs.
    path("admin/", admin.site.urls),
    # For customer app URLs.
    path("customer/", include("customer.urls")),
    path("customer_status/<str:public_id>/", CustomerPaymentStatusView.as_view(), name="payment_status"),
    path("customer_order/<int:customer_order_id>/", CustomerOrderView.as_view(), name="customer_order"),
    # For vendor app URLs.
    path("vendor/", include("vendor.urls")),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("resend_otp/", ResendOtpView.as_view(), name="resend-otp"),
    path("verify_otp/", VerifyOtpView.as_view(), name="verify-otp"),
    path("calendar/", CalendarView.as_view(), name="calendar"),
    path("profile/", VendorDetailView.as_view(), name="vendor-profile"),
    path("detail_milk_quantity/", DetailMilkQuantity.as_view(), name="milk"),
    path("monthly_bill_detail/<int:customer_id>/", MonthlyBillDetail.as_view(), name="detail_milk_quantity"),
    # For static file
    url(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    url(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
    # For auth2provider URLs.
    path("o/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    path("token/", oauth2_views.TokenView.as_view(), name="token"),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
