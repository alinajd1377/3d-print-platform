import uuid
from django.conf import settings
from django.db import models

class Material(models.Model):
    TECHNOLOGY = [("FDM", "فیلامنتی"), ("RESIN", "رزینی")]
    name = models.CharField(max_length=100)
    technology = models.CharField(max_length=10, choices=TECHNOLOGY)
    price_per_gram_toman = models.PositiveIntegerField(default=0)
    density_g_cm3 = models.DecimalField(max_digits=5, decimal_places=3, default=1.240, help_text="چگالی تقریبی ماده بر حسب گرم بر سانتی‌متر مکعب")
    is_active = models.BooleanField(default=True)
    def __str__(self): return f"{self.name} ({self.technology})"

class Machine(models.Model):
    name = models.CharField(max_length=120)
    technology = models.CharField(max_length=10, choices=Material.TECHNOLOGY)
    hourly_rate_toman = models.PositiveIntegerField(default=0)
    setup_fee_toman = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    # مشخصات واقعی دستگاه برای اعتبارسنجی سفارش و اتصال آینده به Slicer
    build_x_mm = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    build_y_mm = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    build_z_mm = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    nozzle_diameters = models.JSONField(default=list, blank=True)
    min_layer_height_mm = models.DecimalField(max_digits=5, decimal_places=3, default=0.080)
    max_layer_height_mm = models.DecimalField(max_digits=5, decimal_places=3, default=0.400)
    max_print_speed_mm_s = models.PositiveSmallIntegerField(default=0)
    resin_exposure_seconds_per_layer = models.DecimalField(max_digits=5, decimal_places=2, default=8.00)
    resin_lift_seconds_per_layer = models.DecimalField(max_digits=5, decimal_places=2, default=3.00)
    supported_materials = models.ManyToManyField("Material", blank=True, related_name="compatible_machines")
    slicer_profile = models.CharField(max_length=255, blank=True, help_text="مسیر/شناسه پروفایل؛ فایل اجرایی در این فاز اجرا نمی‌شود")
    def __str__(self): return self.name

class PrintOption(models.Model):
    """گزینه‌های قابل نمایش به مشتری که مدیر از پنل مدیریت کنترل می‌کند."""
    technology = models.CharField(max_length=10, choices=Material.TECHNOLOGY)
    key = models.SlugField(max_length=50)
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("technology", "sort_order", "id")
        unique_together = (("technology", "key", "value"),)

    def __str__(self): return f"{self.label}: {self.value}"

class PricingRule(models.Model):
    name = models.CharField(max_length=120)
    support_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=1)
    infill_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=1)
    minimum_order_toman = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

class PrintOrder(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "پیش‌نویس"
        REVIEW = "REVIEW", "در انتظار بررسی"
        QUOTED = "QUOTED", "فاکتور صادر شده"
        PAID = "PAID", "پرداخت شده"
        PRINTING = "PRINTING", "در حال چاپ"
        READY = "READY", "آماده تحویل"
        SHIPPED = "SHIPPED", "ارسال شده"
        COMPLETED = "COMPLETED", "تکمیل شده"
        REJECTED = "REJECTED", "رد شده"

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="print_orders")
    file = models.FileField(upload_to="models/%Y/%m/", null=True, blank=True)
    original_filename = models.CharField(max_length=255, blank=True)
    technology = models.CharField(max_length=10, choices=Material.TECHNOLOGY)
    material = models.ForeignKey(Material, on_delete=models.PROTECT)
    machine = models.ForeignKey(Machine, on_delete=models.PROTECT, null=True, blank=True)
    color = models.CharField(max_length=60, blank=True)
    infill_percent = models.PositiveSmallIntegerField(default=20)
    layer_height_mm = models.DecimalField(max_digits=5, decimal_places=3, default=0.200)
    nozzle_diameter_mm = models.DecimalField(max_digits=4, decimal_places=2, default=0.40)
    supports = models.BooleanField(default=True)
    quantity = models.PositiveSmallIntegerField(default=1)
    model_volume_cm3 = models.DecimalField(max_digits=10, decimal_places=3, default=0, help_text="حجم هندسی استخراج‌شده از فایل؛ برآورد اولیه و نه نتیجه اسلایسر")
    model_height_mm = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text="ارتفاع هندسی مدل بر حسب میلی‌متر")
    estimated_weight_g = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    estimated_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    estimated_price_toman = models.PositiveIntegerField(default=0)
    final_price_toman = models.PositiveIntegerField(null=True, blank=True)
    admin_note = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self): return f"Order {self.public_id}"

class OrderRevision(models.Model):
    """ثبت نسخه قبلی/جدید سفارش برای جلوگیری از حذف سابقه تغییرات."""
    order = models.ForeignKey(PrintOrder, on_delete=models.CASCADE, related_name="revisions")
    snapshot = models.JSONField(default=dict)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.SET_NULL)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self): return f"Revision {self.order.public_id} - {self.created_at:%Y-%m-%d %H:%M}"

class Invoice(models.Model):
    order = models.OneToOneField(PrintOrder, on_delete=models.PROTECT, related_name="invoice")
    amount_toman = models.PositiveIntegerField()
    description = models.CharField(max_length=255, default="فاکتور خدمات چاپ سه‌بعدی")
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name="payments")
    authority = models.CharField(max_length=64, unique=True, null=True, blank=True)
    amount_toman = models.PositiveIntegerField()
    ref_id = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=20, default="PENDING")
    raw_response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

class CustomerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer_profile")
    mobile = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=160, blank=True)
    address = models.TextField(blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name or self.mobile


class StoreProduct(models.Model):
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title


class ProductVariant(models.Model):
    product = models.ForeignKey(StoreProduct, on_delete=models.CASCADE, related_name="variants")
    color = models.CharField(max_length=60)
    sku = models.CharField(max_length=80, blank=True, unique=True, null=True)
    price_toman = models.PositiveIntegerField()
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("product__title", "color")
        constraints = [
            models.UniqueConstraint(fields=("product", "color"), name="unique_product_color_variant")
        ]

    def __str__(self):
        return f"{self.product.title} - {self.color}"


class StoreOrder(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "در انتظار بررسی"
        COORDINATION = "COORDINATION", "نیازمند هماهنگی موجودی"
        CONFIRMED = "CONFIRMED", "تأیید شده"
        PAID = "PAID", "پرداخت شده"
        FULFILLING = "FULFILLING", "در حال آماده‌سازی"
        SHIPPED = "SHIPPED", "ارسال شده"
        COMPLETED = "COMPLETED", "تکمیل شده"
        CANCELLED = "CANCELLED", "لغو شده"

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="store_orders")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total_toman = models.PositiveIntegerField(default=0)
    coordination_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Store order #{self.pk}"


class StoreOrderItem(models.Model):
    order = models.ForeignKey(StoreOrder, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
    unit_price_toman = models.PositiveIntegerField()


class SiteSettings(models.Model):
    """Single editable row for public contact details and payment visibility."""
    site_name = models.CharField(max_length=120, default="پرینت‌یار")
    contact_phone = models.CharField(max_length=40, blank=True)
    contact_email = models.EmailField(blank=True)
    telegram_url = models.URLField(blank=True)
    bale_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    x_url = models.URLField(blank=True)
    whatsapp_url = models.URLField(blank=True)
    contact_address = models.TextField(blank=True)
    working_hours = models.CharField(max_length=180, blank=True)
    enamad_image_url = models.URLField(blank=True)
    payment_logo_url = models.URLField(blank=True)
    payment_enabled = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "تنظیمات سایت"


class ProductImage(models.Model):
    product = models.ForeignKey(StoreProduct, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="store/products/%Y/%m/")
    alt_text = models.CharField(max_length=180, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("sort_order", "id")

    def __str__(self):
        return self.alt_text or f"تصویر {self.product.title}"
