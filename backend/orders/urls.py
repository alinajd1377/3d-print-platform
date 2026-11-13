from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MaterialViewSet, MachineViewSet, PrintOptionViewSet, OrderViewSet, pay_invoice, zarinpal_callback

router = DefaultRouter()
router.register("materials", MaterialViewSet, basename="materials")
router.register("machines", MachineViewSet, basename="machines")
router.register("options", PrintOptionViewSet, basename="options")
router.register("orders", OrderViewSet, basename="orders")

urlpatterns = [
    path("", include(router.urls)),
    path("invoices/<int:invoice_id>/pay/", pay_invoice, name="pay-invoice"),
    path("payments/zarinpal/callback/<int:invoice_id>/", zarinpal_callback, name="zarinpal-callback"),
]
