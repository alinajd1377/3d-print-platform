import requests
from django.conf import settings

def _base_url():
    return "https://sandbox.zarinpal.com" if settings.ZARINPAL_SANDBOX else "https://api.zarinpal.com"

def request_payment(*, amount_toman, callback_url, description, email="", mobile=""):
    if not settings.ZARINPAL_MERCHANT_ID:
        raise RuntimeError("ZARINPAL_MERCHANT_ID تنظیم نشده است.")
    payload = {
        "merchant_id": settings.ZARINPAL_MERCHANT_ID,
        "amount": int(amount_toman) * 10,  # زرین‌پال: ریال؛ برنامه: تومان
        "callback_url": callback_url,
        "description": description[:255],
        "metadata": {"email": email, "mobile": mobile},
    }
    response = requests.post(
        f"{_base_url()}/pg/v4/payment/request.json",
        json=payload, timeout=20,
        headers={"accept": "application/json", "content-type": "application/json"},
    )
    response.raise_for_status()
    data = response.json().get("data", {})
    if data.get("code") != 100 or not data.get("authority"):
        raise ValueError(f"خطا در ایجاد پرداخت زرین‌پال: {response.text[:500]}")
    start_base = "https://sandbox.zarinpal.com/pg/StartPay/" if settings.ZARINPAL_SANDBOX else "https://www.zarinpal.com/pg/StartPay/"
    return data["authority"], start_base + data["authority"], response.json()

def verify_payment(*, authority, amount_toman):
    payload = {
        "merchant_id": settings.ZARINPAL_MERCHANT_ID,
        "amount": int(amount_toman) * 10,
        "authority": authority,
    }
    response = requests.post(
        f"{_base_url()}/pg/v4/payment/verify.json",
        json=payload, timeout=20,
        headers={"accept": "application/json", "content-type": "application/json"},
    )
    response.raise_for_status()
    body = response.json()
    return body.get("data", {}), body
