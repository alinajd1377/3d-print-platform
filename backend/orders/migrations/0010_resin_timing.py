from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("orders", "0009_more_fdm_choices")]

    operations = [
        migrations.AddField(
            model_name="machine",
            name="resin_exposure_seconds_per_layer",
            field=models.DecimalField(decimal_places=2, default=8.0, max_digits=5),
        ),
        migrations.AddField(
            model_name="machine",
            name="resin_lift_seconds_per_layer",
            field=models.DecimalField(decimal_places=2, default=3.0, max_digits=5),
        ),
    ]
