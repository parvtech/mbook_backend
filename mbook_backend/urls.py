from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.static import serve
import oauth2_provider.views as oauth2_views

from mbook_backend import settings
from vendor.views import LogoutView, ResendOtpView, VerifyOtpView

urlpatterns = [
    # Admin app URLs.
    path('admin/', admin.site.urls),
    # For customer app URLs.

    # For vendor app URLs.
    path('vendor/', include('vendor.urls')),
    path("logout/", LogoutView.as_view(), name='logout'),
    path("resend_otp/", ResendOtpView.as_view(), name="resend-otp"),
    path("verify_otp/", VerifyOtpView.as_view(), name="verify-otp"),

    # For static file
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),

    # For auth2provider URLs.
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('token/', oauth2_views.TokenView.as_view(), name="token"),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
