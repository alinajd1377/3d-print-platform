from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0002_machine_specs_options_order_revision"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomerProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("mobile", models.CharField(max_length=20, unique=True)),
                ("full_name", models.CharField(blank=True, max_length=160)),
                ("address", models.TextField(blank=True)),
                ("postal_code", models.CharField(blank=True, max_length=20)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="customer_profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="SiteSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("site_name", models.CharField(default="پرینت‌یار", max_length=120)),
                ("contact_phone", models.CharField(blank=True, max_length=40)),
                ("contact_email", models.EmailField(blank=True, max_length=254)),
                ("telegram_url", models.URLField(blank=True)),
                ("bale_url", models.URLField(blank=True)),
                ("instagram_url", models.URLField(blank=True)),
                ("whatsapp_url", models.URLField(blank=True)),
                ("contact_address", models.TextField(blank=True)),
                ("working_hours", models.CharField(blank=True, max_length=180)),
                ("enamad_image_url", models.URLField(blank=True)),
                ("payment_logo_url", models.URLField(blank=True)),
                ("payment_enabled", models.BooleanField(default=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="StoreProduct",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=180)),
                ("slug", models.SlugField(max_length=200, unique=True)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="ProductVariant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("color", models.CharField(max_length=60)),
                ("sku", models.CharField(blank=True, max_length=80, null=True, unique=True)),
                ("price_toman", models.PositiveIntegerField()),
                ("stock", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="variants", to="orders.storeproduct")),
            ],
            options={"ordering": ("product__title", "color"), "constraints": [models.UniqueConstraint(fields=("product", "color"), name="unique_product_color_variant")]},
        ),
        migrations.CreateModel(
            name="StoreOrder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("PENDING", "در انتظار بررسی"), ("COORDINATION", "نیازمند هماهنگی موجودی"), ("CONFIRMED", "تأیید شده"), ("PAID", "پرداخت شده"), ("FULFILLING", "در حال آماده‌سازی"), ("SHIPPED", "ارسال شده"), ("COMPLETED", "تکمیل شده"), ("CANCELLED", "لغو شده")], default="PENDING", max_length=20)),
                ("total_toman", models.PositiveIntegerField(default=0)),
                ("coordination_note", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("customer", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="store_orders", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="StoreOrderItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.PositiveSmallIntegerField()),
                ("unit_price_toman", models.PositiveIntegerField()),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="orders.storeorder")),
                ("variant", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="orders.productvariant")),
            ],
        ),
    ]
