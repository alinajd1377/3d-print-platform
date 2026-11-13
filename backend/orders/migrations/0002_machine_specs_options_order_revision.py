from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("orders", "0001_initial"), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.AddField(
            model_name="printorder", name="nozzle_diameter_mm",
            field=models.DecimalField(decimal_places=2, default=0.40, max_digits=4),
        ),
        migrations.AddField(
            model_name="machine", name="build_x_mm",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7),
        ),
        migrations.AddField(
            model_name="machine", name="build_y_mm",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7),
        ),
        migrations.AddField(
            model_name="machine", name="build_z_mm",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7),
        ),
        migrations.AddField(
            model_name="machine", name="nozzle_diameters",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="machine", name="min_layer_height_mm",
            field=models.DecimalField(decimal_places=2, default=0.08, max_digits=4),
        ),
        migrations.AddField(
            model_name="machine", name="max_layer_height_mm",
            field=models.DecimalField(decimal_places=2, default=0.40, max_digits=4),
        ),
        migrations.AddField(
            model_name="machine", name="max_print_speed_mm_s",
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="machine", name="slicer_profile",
            field=models.CharField(blank=True, help_text="مسیر/شناسه پروفایل؛ فایل اجرایی در این فاز اجرا نمی‌شود", max_length=255),
        ),
        migrations.CreateModel(
            name="PrintOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("technology", models.CharField(choices=[("FDM", "فیلامنتی"), ("RESIN", "رزینی")], max_length=10)),
                ("key", models.SlugField(max_length=50)),
                ("label", models.CharField(max_length=100)),
                ("value", models.CharField(blank=True, max_length=100)),
                ("is_active", models.BooleanField(default=True)),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
            ],
            options={"ordering": ("technology", "sort_order", "id"),
                     "unique_together": {("technology", "key", "value")}},
        ),
        migrations.AddField(
            model_name="machine", name="supported_materials",
            field=models.ManyToManyField(blank=True, related_name="compatible_machines", to="orders.material"),
        ),
        migrations.CreateModel(
            name="OrderRevision",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("snapshot", models.JSONField(default=dict)),
                ("reason", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("changed_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="revisions", to="orders.printorder")),
            ],
            options={"ordering": ("-created_at",)},
        ),
    ]
