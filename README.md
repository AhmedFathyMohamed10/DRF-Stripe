# Django + Stripe Checkout Integration

This project demonstrates how to integrate **Stripe Checkout** with a
Django REST Framework backend.

## 🚀 Features

-   Create Stripe Checkout Sessions for products.
-   Store transactions in your local database.
-   Update transaction status after successful payment.
-   Return useful transaction details (session_id, payment_intent,
    amount, etc).
-   Cancel and success endpoints.

------------------------------------------------------------------------

## 📦 Requirements

-   Python 3.9+
-   Django 4.x+
-   Django REST Framework
-   Stripe Python SDK

Install dependencies:

``` bash
pip install django djangorestframework stripe
```

------------------------------------------------------------------------

## ⚙️ Configuration

### 1. Add Stripe keys in `settings.py`

``` python
STRIPE_SECRET_KEY = "your_stripe_secret_key"
STRIPE_PUBLISHABLE_KEY = "your_stripe_publishable_key"
DOMAIN_URL = "http://127.0.0.1:8000"
```

### 2. Create Transaction Model

In `checkout/models.py`:

``` python
from django.db import models
from product.models import Product

class Transaction(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stripe_session_id = models.CharField(max_length=255, unique=True)
    stripe_payment_intent = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)
    status = models.CharField(max_length=20, default="unpaid")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction {self.id} - {self.status}"
```

Run migrations:

``` bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Add URLs

In `checkout/urls.py`:

``` python
from django.urls import path
from . import views

urlpatterns = [
    path("create-checkout-session/<int:product_id>/", views.CreateCheckoutSessionView.as_view(), name="create-checkout-session"),
    path("success/", views.SuccessView.as_view(), name="success"),
    path("cancel/", views.CancelView.as_view(), name="cancel"),
]
```

### 4. Views

The main logic is in `checkout/views.py`: - `CreateCheckoutSessionView`:
Creates a Stripe Checkout session and a Transaction. - `SuccessView`:
Retrieves the session, updates the Transaction, and returns useful
info. - `CancelView`: Handles cancelled payments.

------------------------------------------------------------------------

## ▶️ Usage

1.  Start Django server:

``` bash
python manage.py runserver
```

2.  Create a checkout session:

``` http
POST http://127.0.0.1:8000/api/checkout/create-checkout-session/<product_id>/
```

Response:

``` json
{
  "status": "success",
  "id": "cs_test_12345",
  "redirect_url": "https://checkout.stripe.com/c/pay/cs_test_12345"
}
```

3.  Complete the payment → Stripe redirects to:

-   Success:
    `http://127.0.0.1:8000/api/checkout/success?session_id=cs_test_12345`
-   Cancel: `http://127.0.0.1:8000/api/checkout/cancel`

4.  Success response example:

``` json
{
  "message": "Payment was successful!",
  "transaction_id": 1,
  "session_id": "cs_test_12345",
  "payment_intent": "pi_12345",
  "amount_total": 20.0,
  "currency": "usd",
  "payment_status": "paid",
  "product_id": "2"
}
```

------------------------------------------------------------------------

## ⚠️ Important

For production use: - Always implement a **Stripe webhook** to handle
`checkout.session.completed` events (in case user does not return to
success URL). - Use environment variables for Stripe keys.
