from decimal import Decimal, ROUND_HALF_UP


def estimate_price(*, material, machine, weight_g, hours, infill_percent, supports, quantity, rule=None):
    """برآورد تعرفه‌ای؛ تا اتصال Slicer جایگزین محاسبه واقعی وزن و زمان نیست."""
    weight = Decimal(str(weight_g))
    runtime = Decimal(str(hours))
    material_cost = weight * material.price_per_gram_toman
    machine_cost = runtime * (machine.hourly_rate_toman if machine else 0)
    setup = machine.setup_fee_toman if machine else 0

    support_factor = (
        Decimal(str(rule.support_multiplier)) if rule
        else (Decimal("1.12") if supports else Decimal("1.00"))
    )
    infill_factor = Decimal("0.75") + (
        Decimal(infill_percent) / Decimal("100")
    ) * Decimal("1.25")
    if rule:
        infill_factor *= Decimal(str(rule.infill_multiplier))

    subtotal = (material_cost + machine_cost) * support_factor * infill_factor + setup
    total = int((subtotal * quantity).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    if rule:
        total = max(total, rule.minimum_order_toman)
    return total
