from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("orders", "0004_product_images")]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="x_url",
            field=models.URLField(blank=True),
        ),
    ]
