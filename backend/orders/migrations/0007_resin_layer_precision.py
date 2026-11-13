from django.db import migrations, models
import django.db.models


class Migration(migrations.Migration):
    dependencies = [("orders", "0006_seed_default_print_options")]

    operations = [
        migrations.AlterField(
            model_name="machine",
            name="min_layer_height_mm",
            field=models.DecimalField(decimal_places=3, default=0.08, max_digits=5),
        ),
        migrations.AlterField(
            model_name="machine",
            name="max_layer_height_mm",
            field=models.DecimalField(decimal_places=3, default=0.4, max_digits=5),
        ),
        migrations.AlterField(
            model_name="printorder",
            name="layer_height_mm",
            field=models.DecimalField(decimal_places=3, default=0.2, max_digits=5),
        ),
    ]
