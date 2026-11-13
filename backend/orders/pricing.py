from decimal import Decimal, ROUND_HALF_UP


def estimate_geometry(*, volume_cm3, density_g_cm3, infill_percent, nozzle_mm,
                      layer_mm, machine):
    """
    برآورد تجربی FDM از حجم هندسی؛ جایگزین Slicer نیست.
    پوسته و پرشدگی با یک ضریب تقریبی مدل می‌شوند.
    """
    volume = Decimal(str(volume_cm3 or 0))
    if volume <= 0:
        return Decimal("0"), Decimal("0")

    infill = max(Decimal("0"), min(Decimal("100"), Decimal(str(infill_percent)))) / Decimal("100")
    printed_fraction = Decimal("0.22") + (infill * Decimal("0.65"))
    printed_cm3 = volume * printed_fraction
    weight_g = printed_cm3 * Decimal(str(density_g_cm3))

    nozzle = max(Decimal("0.2"), Decimal(str(nozzle_mm)))
    layer = max(Decimal("0.04"), Decimal(str(layer_mm)))
    speed = Decimal(str(getattr(machine, "max_print_speed_mm_s", 0) or 40))
    # ضریب 0.45 شکل مقطع رشته و افت سرعت در حرکت‌های واقعی را تقریب می‌زند.
    flow_mm3_s = max(Decimal("0.1"), nozzle * layer * speed * Decimal("0.45"))
    hours = (printed_cm3 * Decimal("1000") / flow_mm3_s / Decimal("3600")) * Decimal("1.25")
    return weight_g.quantize(Decimal("0.01")), hours.quantize(Decimal("0.01"))


def estimate_price(*, material, machine, weight_g, hours, infill_percent, supports, quantity, rule=None):
    """برآورد تعرفه‌ای بر اساس وزن/زمان تخمینی؛ قیمت نهایی پس از اسلایس و بازبینی است."""
    weight = Decimal(str(weight_g))
    runtime = Decimal(str(hours))
    material_cost = weight * material.price_per_gram_toman
    machine_cost = runtime * (machine.hourly_rate_toman if machine else 0)
    setup = machine.setup_fee_toman if machine else 0

    support_factor = (
        Decimal(str(rule.support_multiplier)) if rule and supports
        else (Decimal("1.00") if rule else (Decimal("1.12") if supports else Decimal("1.00")))
    )
    infill_factor = Decimal(str(rule.infill_multiplier)) if rule else Decimal("1.00")

    per_piece = (material_cost + machine_cost) * support_factor * infill_factor
    total = int((per_piece * quantity + setup).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    if rule:
        total = max(total, rule.minimum_order_toman)
    return total
