from django.db import migrations


def add_default_print_options(apps, schema_editor):
    PrintOption = apps.get_model("orders", "PrintOption")
    rows = []
    def add(technology, key, label, values):
        for order, value in enumerate(values, start=1):
            rows.append(PrintOption(
                technology=technology, key=key, label=label,
                value=str(value), is_active=True, sort_order=order
            ))
    add("FDM", "nozzle_diameter", "قطر نازل (میلی‌متر)", ["0.40"])
    add("FDM", "layer_height", "ارتفاع لایه (میلی‌متر)", ["0.20", "0.30", "0.40"])
    add("FDM", "infill", "درصد تراکم داخلی", ["10", "20", "40", "60", "80", "100"])
    add("FDM", "supports", "ساپورت", ["true", "false"])
    add("FDM", "color", "رنگ", ["سفید", "مشکی", "خاکستری", "قرمز", "آبی"])
    add("RESIN", "layer_height", "ارتفاع لایه (میلی‌متر)", ["0.025", "0.05", "0.10"])
    add("RESIN", "supports", "ساپورت", ["true", "false"])
    PrintOption.objects.bulk_create(rows, ignore_conflicts=True)


def remove_default_print_options(apps, schema_editor):
    # Keep admin-managed values intact if this migration is rolled back.
    pass


class Migration(migrations.Migration):
    dependencies = [("orders", "0005_sitesettings_x_url")]
    operations = [migrations.RunPython(add_default_print_options, remove_default_print_options)]
