from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (MaterialViewSet, MachineViewSet, PrintOptionViewSet, OrderViewSet, pay_invoice, zarinpal_callback,
                    MyProfileView, PublicStoreView, StoreOrderCreateView, PublicSiteSettingsView, MobileAuthView)

router = DefaultRouter()
router.register("materials", MaterialViewSet, basename="materials")
router.register("machines", MachineViewSet, basename="machines")
router.register("options", PrintOptionViewSet, basename="options")
router.register("orders", OrderViewSet, basename="orders")

urlpatterns = [\n    path("auth/mobile/", MobileAuthView.as_view(), name="mobile-auth"),
    path("profile/", MyProfileView.as_view(), name="my-profile"),
    path("store/products/", PublicStoreView.as_view(), name="store-products"),
    path("store/orders/", StoreOrderCreateView.as_view(), name="store-order-create"),
    path("site-settings/", PublicSiteSettingsView.as_view(), name="public-site-settings"),
    path("", include(router.urls)),
    path("invoices/<int:invoice_id>/pay/", pay_invoice, name="pay-invoice"),
    path("payments/zarinpal/callback/<int:invoice_id>/", zarinpal_callback, name="zarinpal-callback"),
]
