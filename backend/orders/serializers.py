from rest_framework import serializers
from decimal import Decimal, InvalidOperation
from .models import Material, Machine, PrintOption, PrintOrder


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ("id", "name", "technology", "price_per_gram_toman", "density_g_cm3")


class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = ("id", "name", "technology", "hourly_rate_toman", "setup_fee_toman",
                  "build_x_mm", "build_y_mm", "build_z_mm", "nozzle_diameters",
                  "min_layer_height_mm", "max_layer_height_mm", "max_print_speed_mm_s",
                  "resin_exposure_seconds_per_layer", "resin_lift_seconds_per_layer")


class PrintOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrintOption
        fields = ("id", "technology", "key", "label", "value", "sort_order")


class PrintOrderSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source="material.name", read_only=True)

    class Meta:
        model = PrintOrder
        fields = (
            "public_id", "file", "original_filename", "technology", "material",
            "material_name", "machine", "color", "infill_percent", "layer_height_mm",
            "nozzle_diameter_mm", "supports", "quantity", "model_volume_cm3", "model_height_mm", "estimated_weight_g", "estimated_hours",
            "estimated_price_toman", "final_price_toman", "admin_note", "status",
            "created_at",
        )
        read_only_fields = (
            "public_id", "machine", "estimated_weight_g", "estimated_hours",
            "estimated_price_toman", "final_price_toman", "admin_note",
            "status", "created_at", "original_filename",
        )

    def validate(self, attrs):
        volume = attrs.get("model_volume_cm3", getattr(self.instance, "model_volume_cm3", 0))
        if volume is not None and volume < 0:
            raise serializers.ValidationError({"model_volume_cm3": "حجم مدل نمی‌تواند منفی باشد."})
        if volume is not None and volume > 100000:
            raise serializers.ValidationError({"model_volume_cm3": "حجم مدل از محدوده مجاز بیشتر است."})
        technology = attrs.get("technology", getattr(self.instance, "technology", None))
        material = attrs.get("material", getattr(self.instance, "material", None))
        machine = attrs.get("machine", getattr(self.instance, "machine", None))
        if material and not material.is_active:
            raise serializers.ValidationError({"material": "این متریال در حال حاضر غیرفعال است."})
        if material and technology and material.technology != technology:
            raise serializers.ValidationError({"material": "این ماده با تکنولوژی انتخاب‌شده سازگار نیست."})
        if machine and technology and machine.technology != technology:
            raise serializers.ValidationError({"machine": "این دستگاه با تکنولوژی سفارش سازگار نیست."})
        if machine and material and machine.supported_materials.exists() and not machine.supported_materials.filter(pk=material.pk).exists():
            raise serializers.ValidationError({"material": "این دستگاه از ماده انتخاب‌شده پشتیبانی نمی‌کند."})
        checks = {
            "infill": str(attrs.get("infill_percent", getattr(self.instance, "infill_percent", ""))),
            "layer_height": str(attrs.get("layer_height_mm", getattr(self.instance, "layer_height_mm", ""))),
            "color": str(attrs.get("color", getattr(self.instance, "color", ""))),
            "supports": str(attrs.get("supports", getattr(self.instance, "supports", ""))).lower(),
            "nozzle_diameter": str(attrs.get("nozzle_diameter_mm", getattr(self.instance, "nozzle_diameter_mm", ""))),
        }
        for key, value in checks.items():
            if value in ("", "none"):
                continue
            allowed = PrintOption.objects.filter(
                technology=technology, key=key, is_active=True
            ).values_list("value", flat=True)
            allowed = list(allowed)
            submitted_key = {"layer_height": "layer_height_mm", "nozzle_diameter": "nozzle_diameter_mm"}.get(key, key)
            if submitted_key in self.initial_data and not allowed:
                raise serializers.ValidationError({key: "این گزینه هنوز توسط مدیر فعال نشده است."})
            matches = value in allowed
            if key in ("layer_height", "nozzle_diameter") and allowed:
                try:
                    submitted_number = Decimal(value)
                    matches = any(submitted_number == Decimal(str(candidate)) for candidate in allowed)
                except (InvalidOperation, ValueError):
                    matches = False
            if allowed and not matches:
                raise serializers.ValidationError({key: "این گزینه در حال حاضر فعال یا مجاز نیست."})
        return attrs


from .models import CustomerProfile, StoreProduct, ProductVariant, StoreOrder, StoreOrderItem, SiteSettings


class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ("mobile", "full_name", "address", "postal_code", "updated_at")
        read_only_fields = ("mobile", "updated_at")


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ("id", "color", "price_toman", "stock")


class StoreProductSerializer(serializers.ModelSerializer):
    variants = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = StoreProduct
        fields = ("id", "title", "slug", "description", "variants", "images")

    def get_variants(self, obj):
        qs = obj.variants.filter(is_active=True)
        return ProductVariantSerializer(qs, many=True).data

    def get_images(self, obj):
        request = self.context.get("request")
        result = []
        for item in obj.images.all():
            url = item.image.url
            result.append({"url": request.build_absolute_uri(url) if request else url, "alt_text": item.alt_text})
        return result


class StoreOrderCreateSerializer(serializers.Serializer):
    variant_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1, max_value=100)


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = ("site_name", "contact_phone", "contact_email", "telegram_url", "bale_url",
                  "instagram_url", "x_url", "whatsapp_url", "contact_address", "working_hours",
                  "enamad_image_url", "payment_logo_url", "payment_enabled")
