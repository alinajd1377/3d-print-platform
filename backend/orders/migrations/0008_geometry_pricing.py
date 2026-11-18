from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("orders", "0007_resin_layer_precision")]

    operations = [
        migrations.AddField(
            model_name="material",
            name="density_g_cm3",
            field=models.DecimalField(
                decimal_places=3,
                default=1.24,
                help_text="چگالی تقریبی ماده بر حسب گرم بر سانتی‌متر مکعب",
                max_digits=5,
            ),
        ),
        migrations.AddField(
            model_name="printorder",
            name="model_volume_cm3",
            field=models.DecimalField(
                decimal_places=3,
                default=0,
                help_text="حجم هندسی استخراج‌شده از فایل؛ برآورد اولیه و نه نتیجه اسلایسر",
                max_digits=10,
            ),
        ),
    ]
