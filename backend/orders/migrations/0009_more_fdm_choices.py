from django.db import migrations


def add_fdm_choices(apps, schema_editor):
    PrintOption = apps.get_model("orders", "PrintOption")
    additions = [
        ("nozzle_diameter", "قطر نازل (میلی‌متر)", "0.20", 1),
        ("nozzle_diameter", "قطر نازل (میلی‌متر)", "0.60", 3),
        ("nozzle_diameter", "قطر نازل (میلی‌متر)", "0.80", 4),
        ("layer_height", "ارتفاع لایه (میلی‌متر)", "0.08", 1),
        ("layer_height", "ارتفاع لایه (میلی‌متر)", "0.12", 2),
        ("layer_height", "ارتفاع لایه (میلی‌متر)", "0.16", 3),
        ("layer_height", "ارتفاع لایه (میلی‌متر)", "0.24", 5),
        ("layer_height", "ارتفاع لایه (میلی‌متر)", "0.28", 6),
    ]
    for key, label, value, order in additions:
        PrintOption.objects.get_or_create(
            technology="FDM", key=key, value=value,
            defaults={"label": label, "is_active": True, "sort_order": order},
        )


class Migration(migrations.Migration):
    dependencies = [("orders", "0008_geometry_pricing")]
    operations = [migrations.RunPython(add_fdm_choices, migrations.RunPython.noop)]
