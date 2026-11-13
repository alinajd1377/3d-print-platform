from django.contrib import admin
from django import forms
from .models import (
    Material, Machine, PricingRule, PrintOption, PrintOrder,
    OrderRevision, Invoice, Payment,
)
from .pricing import estimate_price, estimate_geometry


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("name", "technology", "price_per_gram_toman", "density_g_cm3", "is_active")
    list_filter = ("technology", "is_active")
    list_editable = ("price_per_gram_toman", "density_g_cm3", "is_active")
    search_fields = ("name",)


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ("name", "technology", "hourly_rate_toman", "setup_fee_toman", "is_active")
    list_filter = ("technology", "is_active")
    filter_horizontal = ("supported_materials",)
    fieldsets = (
        ("اطلاعات پایه", {"fields": ("name", "technology", "is_active")}),
        ("تعرفه", {"fields": ("hourly_rate_toman", "setup_fee_toman")}),
        ("محدوده چاپ (میلی‌متر)", {"fields": ("build_x_mm", "build_y_mm", "build_z_mm")}),
        ("محدودیت‌های فنی", {"fields": ("nozzle_diameters", "min_layer_height_mm",
                                      "max_layer_height_mm", "max_print_speed_mm_s",
                                      "resin_exposure_seconds_per_layer", "resin_lift_seconds_per_layer",
                                      "supported_materials", "slicer_profile")}),
    )


@admin.register(PrintOption)
class PrintOptionAdmin(admin.ModelAdmin):
    list_display = ("label", "technology", "key", "value", "is_active", "sort_order")
    list_filter = ("technology", "is_active", "key")
    list_editable = ("value", "is_active", "sort_order")
    search_fields = ("label", "key", "value")


@admin.register(PricingRule)
class PricingRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "support_multiplier", "infill_multiplier", "minimum_order_toman", "is_active")
    list_editable = ("support_multiplier", "infill_multiplier", "minimum_order_toman", "is_active")


class PrintOrderAdminForm(forms.ModelForm):
    revision_reason = forms.CharField(
        label="دلیل تغییر سفارش (برای ثبت در تاریخچه)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
    )

    class Meta:
        model = PrintOrder
        fields = "__all__"


class OrderRevisionInline(admin.TabularInline):
    model = OrderRevision
    extra = 0
    can_delete = False
    readonly_fields = ("created_at", "changed_by", "reason", "snapshot")
    fields = ("created_at", "changed_by", "reason", "snapshot")
    ordering = ("-created_at",)


@admin.register(PrintOrder)
class PrintOrderAdmin(admin.ModelAdmin):
    form = PrintOrderAdminForm
    list_display = ("public_id", "customer", "technology", "material", "machine",
                    "status", "estimated_price_toman", "final_price_toman", "created_at")
    list_filter = ("status", "technology", "material")
    search_fields = ("public_id", "customer__username", "customer__email", "original_filename")
    readonly_fields = ("public_id", "created_at", "updated_at", "original_filename")
    inlines = (OrderRevisionInline,)
    fieldsets = (
        ("مشتری و فایل", {"fields": ("public_id", "customer", "file", "original_filename")}),
        ("تنظیمات چاپ (قابل ویرایش مدیر)", {"fields": (
            "technology", "material", "machine", "color", "infill_percent",
            "layer_height_mm", "nozzle_diameter_mm", "supports", "quantity", "model_volume_cm3", "model_height_mm")}),
        ("برآورد و مبلغ نهایی", {"fields": (
            "estimated_weight_g", "estimated_hours", "estimated_price_toman",
            "final_price_toman")}),
        ("وضعیت و یادداشت", {"fields": ("status", "admin_note", "revision_reason", "created_at", "updated_at")}),
    )

    def save_model(self, request, obj, form, change):
        if change:
            old = PrintOrder.objects.get(pk=obj.pk)
            fields = ("technology", "material_id", "machine_id", "color", "infill_percent",
                      "layer_height_mm", "nozzle_diameter_mm", "supports", "quantity", "model_volume_cm3", "model_height_mm", "estimated_weight_g",
                      "estimated_hours", "estimated_price_toman", "final_price_toman",
                      "status", "admin_note", "file")
            before = {}
            for field in fields:
                value = getattr(old, field)
                before[field] = str(value) if value is not None else None
        # پس از تغییر تنظیمات فنی، وزن و زمان تخمینی نیز دوباره محاسبه می‌شوند.
        if obj.technology == "FDM":
            obj.estimated_weight_g, obj.estimated_hours = estimate_geometry(
                volume_cm3=obj.model_volume_cm3,
                density_g_cm3=obj.material.density_g_cm3,
                infill_percent=obj.infill_percent,
                nozzle_mm=obj.nozzle_diameter_mm,
                layer_mm=obj.layer_height_mm,
                machine=obj.machine,
            )
        else:
            from decimal import Decimal
            obj.estimated_weight_g = (Decimal(str(obj.model_volume_cm3 or 0)) * Decimal(str(obj.material.density_g_cm3))).quantize(Decimal("0.01"))
            obj.estimated_hours = Decimal("0")
        rule = PricingRule.objects.filter(is_active=True).order_by("id").first()
        obj.estimated_price_toman = estimate_price(
            material=obj.material, machine=obj.machine,
            weight_g=obj.estimated_weight_g, hours=obj.estimated_hours,
            infill_percent=obj.infill_percent, supports=obj.supports,
            quantity=obj.quantity, rule=rule,
        )
        super().save_model(request, obj, form, change)
        if change:
            OrderRevision.objects.create(
                order=obj, changed_by=request.user,
                reason=request.POST.get("revision_reason", "").strip(),
                snapshot={"before": before, "after": {
                    field: str(getattr(obj, field)) if getattr(obj, field) is not None else None
                    for field in fields
                }},
            )


@admin.register(OrderRevision)
class OrderRevisionAdmin(admin.ModelAdmin):
    list_display = ("order", "changed_by", "created_at")
    readonly_fields = ("order", "snapshot", "changed_by", "reason", "created_at")
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "amount_toman", "is_paid", "created_at")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "invoice", "amount_toman", "status", "authority", "ref_id")


from .models import CustomerProfile, StoreProduct, ProductVariant, StoreOrder, StoreOrderItem, SiteSettings, ProductImage


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("mobile", "full_name", "postal_code", "updated_at")
    search_fields = ("mobile", "full_name", "user__username")


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(StoreProduct)
class StoreProductAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = (ProductVariantInline, ProductImageInline)


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("product", "color", "price_toman", "stock", "is_active")
    list_filter = ("is_active",)
    search_fields = ("product__title", "color", "sku")


class StoreOrderItemInline(admin.TabularInline):
    model = StoreOrderItem
    extra = 0
    readonly_fields = ("variant", "quantity", "unit_price_toman")


@admin.register(StoreOrder)
class StoreOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "status", "total_toman", "created_at")
    list_filter = ("status",)
    search_fields = ("customer__username", "customer__customer_profile__mobile")
    inlines = (StoreOrderItemInline,)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("مشخصات", {"fields": ("site_name", "contact_phone", "contact_email", "contact_address", "working_hours")}),
        ("شبکه‌های اجتماعی", {"fields": ("telegram_url", "bale_url", "instagram_url", "x_url", "whatsapp_url")}),
        ("نشان‌ها و پرداخت", {"fields": ("enamad_image_url", "payment_logo_url", "payment_enabled")}),
    )
    list_display = ("site_name", "contact_phone", "contact_email", "updated_at")
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        from django.shortcuts import redirect
        from django.urls import reverse

        obj = self.model.objects.order_by("pk").first()
        if obj:
            url = reverse(
                f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change",
                args=(obj.pk,),
            )
        else:
            url = reverse(
                f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_add"
            )
        return redirect(url)
