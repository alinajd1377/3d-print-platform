from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("orders", "0010_resin_timing")]

    operations = [
        migrations.AddField(
            model_name="printorder",
            name="model_height_mm",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text="ارتفاع هندسی مدل بر حسب میلی‌متر",
                max_digits=8,
            ),
        ),
    ]
