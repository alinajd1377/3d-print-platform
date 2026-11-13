from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from .models import Material, Machine, PricingRule, PrintOption, PrintOrder, Invoice, Payment
from .serializers import MaterialSerializer, MachineSerializer, PrintOptionSerializer, PrintOrderSerializer
from .pricing import estimate_price
from .zarinpal import request_payment, verify_payment

class IsStaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        if getattr(view, "action", None) in ("create", "submit"):
            return True
        return request.user.is_staff

class MaterialViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MaterialSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Material.objects.filter(is_active=True)

class MachineViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MachineSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Machine.objects.filter(is_active=True)

class PrintOptionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PrintOptionSerializer
    permission_classes = [permissions.AllowAny]
    queryset = PrintOption.objects.filter(is_active=True)

    def get_queryset(self):
        qs = super().get_queryset()
        technology = self.request.query_params.get("technology")
        return qs.filter(technology=technology) if technology in ("FDM", "RESIN") else qs

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = PrintOrderSerializer
    permission_classes = [IsStaffOrReadOnly]
    lookup_field = "public_id"

    def get_queryset(self):
        qs = PrintOrder.objects.select_related("material", "machine", "customer")
        return qs if self.request.user.is_staff else qs.filter(customer=self.request.user)

    def perform_create(self, serializer):
        uploaded = self.request.FILES.get("file")
        if uploaded:
            name = uploaded.name.lower()
            if not name.endswith((".stl", ".obj", ".3mf")):
                raise ValidationError({"file": "فرمت مجاز: STL، OBJ و 3MF"})
            if uploaded.size > 100 * 1024 * 1024:
                raise ValidationError({"file": "حداکثر حجم فایل ۱۰۰ مگابایت است."})
        material = serializer.validated_data["material"]
        # دستگاه واقعی از روی تکنولوژی و سازگاری متریال انتخاب می‌شود؛
        # مشتری حق انتخاب/تغییر دستگاه فیزیکی را ندارد.
        machine = Machine.objects.filter(
            is_active=True, technology=serializer.validated_data["technology"]
        ).filter(
            Q(supported_materials=material) | Q(supported_materials__isnull=True)
        ).distinct().order_by("supported_materials__isnull").first()
        if machine:
            layer_height = serializer.validated_data.get("layer_height_mm", 0.20)
            if not (machine.min_layer_height_mm <= layer_height <= machine.max_layer_height_mm):
                raise ValidationError({"layer_height_mm": "ارتفاع لایه با محدوده دستگاه انتخاب‌شده سازگار نیست."})
            nozzle = serializer.validated_data.get("nozzle_diameter_mm", 0.40)
            if machine.nozzle_diameters and str(nozzle) not in {
                str(value) for value in machine.nozzle_diameters
            } and float(nozzle) not in {
                float(value) for value in machine.nozzle_diameters
            }:
                raise ValidationError({"nozzle_diameter_mm": "قطر نازل با دستگاه انتخاب‌شده سازگار نیست."})
        # وزن و زمان از سمت مشتری پذیرفته نمی‌شوند؛ تا اتصال Slicer صفر می‌مانند.
        weight = 0
        hours = 0
        qty = serializer.validated_data.get("quantity", 1)
        infill = serializer.validated_data.get("infill_percent", 20)
        supports = serializer.validated_data.get("supports", True)
        rule = PricingRule.objects.filter(is_active=True).order_by("id").first()
        price = estimate_price(material=material, machine=machine, weight_g=weight,
                               hours=hours, infill_percent=infill, supports=supports,
                               quantity=qty, rule=rule)
        serializer.save(customer=self.request.user, machine=machine,
                        estimated_price_toman=price,
                        original_filename=uploaded.name if uploaded else "")

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def quote(self, request, public_id=None):
        order = self.get_object()
        final_price = request.data.get("final_price_toman")
        if not isinstance(final_price, int) or final_price <= 0:
            return Response({"detail": "مبلغ معتبر وارد کنید."}, status=400)
        with transaction.atomic():
            order.final_price_toman = final_price
            order.admin_note = request.data.get("admin_note", "")
            order.status = PrintOrder.Status.QUOTED
            order.save()
            Invoice.objects.update_or_create(order=order, defaults={
                "amount_toman": final_price,
                "description": f"فاکتور سفارش {str(order.public_id)[:8]}",
            })
        return Response({"status": "quoted", "amount_toman": final_price})

    @action(detail=True, methods=["post"])
    def submit(self, request, public_id=None):
        order = self.get_object()
        if order.status != PrintOrder.Status.DRAFT:
            return Response({"detail": "این سفارش قابل ارسال نیست."}, status=400)
        order.status = PrintOrder.Status.REVIEW
        order.save(update_fields=["status", "updated_at"])
        return Response({"status": order.status})

@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def pay_invoice(request, invoice_id):
    if not settings.PAYMENTS_ENABLED:
        return Response({"detail": "پرداخت آنلاین هنوز فعال نشده است."}, status=503)
    invoice = get_object_or_404(Invoice.objects.select_related("order"), pk=invoice_id, order__customer=request.user)
    if invoice.is_paid:
        return Response({"detail": "این فاکتور قبلاً پرداخت شده است."}, status=400)
    callback = settings.BACKEND_URL.rstrip("/") + f"/api/payments/zarinpal/callback/{invoice.id}/"
    try:
        authority, url, raw = request_payment(
            amount_toman=invoice.amount_toman,
            callback_url=callback,
            description=invoice.description,
            email=request.user.email,
        )
        Payment.objects.create(invoice=invoice, authority=authority,
                               amount_toman=invoice.amount_toman, raw_response=raw)
        return Response({"payment_url": url})
    except Exception as exc:
        return Response({"detail": str(exc)}, status=502)

@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def zarinpal_callback(request, invoice_id):
    authority = request.query_params.get("Authority", "")
    gateway_status = request.query_params.get("Status", "")
    payment = get_object_or_404(Payment.objects.select_related("invoice", "invoice__order"),
                                invoice_id=invoice_id, authority=authority)
    if payment.status == "PAID":
        return redirect(settings.FRONTEND_URL + "/orders?payment=already-confirmed")
    if gateway_status != "OK":
        payment.status = "CANCELLED"
        payment.save(update_fields=["status"])
        return redirect(settings.FRONTEND_URL + "/orders?payment=cancelled")
    try:
        data, raw = verify_payment(authority=authority, amount_toman=payment.amount_toman)
    except Exception:
        payment.status = "VERIFY_ERROR"
        payment.save(update_fields=["status"])
        return redirect(settings.FRONTEND_URL + "/orders?payment=verify-error")
    with transaction.atomic():
        payment.raw_response = raw
        if data.get("code") == 100:
            payment.status = "PAID"
            payment.ref_id = str(data.get("ref_id", ""))
            payment.verified_at = timezone.now()
            payment.save()
            invoice = Invoice.objects.select_for_update().get(pk=invoice_id)
            invoice.is_paid = True
            invoice.save(update_fields=["is_paid"])
            order = PrintOrder.objects.select_for_update().get(pk=invoice.order_id)
            order.status = PrintOrder.Status.PAID
            order.save(update_fields=["status", "updated_at"])
            result = "success"
        elif data.get("code") == 101 and payment.status == "PAID":
            result = "already-confirmed"
        else:
            payment.status = "FAILED"
            payment.save()
            result = "failed"
    return redirect(settings.FRONTEND_URL + f"/orders?payment={result}")


from rest_framework.views import APIView
from django.db.models import F
from .models import CustomerProfile, StoreProduct, ProductVariant, StoreOrder, StoreOrderItem, SiteSettings
from .serializers import CustomerProfileSerializer, StoreProductSerializer, StoreOrderCreateSerializer, SiteSettingsSerializer


class MyProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_profile(self, user):
        profile, _ = CustomerProfile.objects.get_or_create(
            user=user, defaults={"mobile": user.username[:20]}
        )
        return profile

    def get(self, request):
        return Response(CustomerProfileSerializer(self.get_profile(request.user)).data)

    def patch(self, request):
        profile = self.get_profile(request.user)
        serializer = CustomerProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PublicStoreView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        products = StoreProduct.objects.filter(is_active=True).prefetch_related("variants")
        return Response(StoreProductSerializer(products, many=True).data)


class StoreOrderCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = StoreOrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        with transaction.atomic():
            variant = get_object_or_404(
                ProductVariant.objects.select_for_update().select_related("product"),
                pk=data["variant_id"], is_active=True, product__is_active=True
            )
            qty = data["quantity"]
            enough_stock = variant.stock >= qty
            order = StoreOrder.objects.create(
                customer=request.user,
                status=StoreOrder.Status.PENDING if enough_stock else StoreOrder.Status.COORDINATION,
                total_toman=variant.price_toman * qty,
                coordination_note="" if enough_stock else "موجودی کافی نیست؛ لطفاً برای هماهنگی با مشتری تماس گرفته شود."
            )
            StoreOrderItem.objects.create(
                order=order, variant=variant, quantity=qty, unit_price_toman=variant.price_toman
            )
            if enough_stock:
                ProductVariant.objects.filter(pk=variant.pk).update(stock=F("stock") - qty)
        return Response({
            "order_id": order.pk,
            "status": order.status,
            "total_toman": order.total_toman,
            "message": "سفارش ثبت شد." if enough_stock else "موجودی کافی نیست؛ درخواست برای هماهنگی با پشتیبانی ثبت شد."
        }, status=201)


class PublicSiteSettingsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(SiteSettingsSerializer(SiteSettings.load()).data)
