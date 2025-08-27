import stripe as st
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from product.models import Product
from .models import Transaction

st.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(generics.GenericAPIView):
    def post(self, request, product_id, *args, **kwargs):
        # get product from DB
        product = Product.objects.get(id=product_id)

        try:
            checkout_session = st.checkout.Session.create(
                payment_method_types=['card'],  # only 'card' is valid
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': product.name,
                            'images': [request.build_absolute_uri(product.image.url)] if product.image else [],
                        },
                        'unit_amount': int(product.price * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=settings.DOMAIN_URL + '/api/checkout/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=settings.DOMAIN_URL + '/api/checkout/cancel',
                metadata={'product_id': str(product.id)},  # useful for webhooks
            )

            # Create a transaction record in the database with "unpaid" status
            Transaction.objects.create(
                product=product,
                stripe_session_id=checkout_session.id,
                amount=product.price,
                currency='usd',
                status='unpaid'
            )

            return Response({
                'status': 'success',
                'id': checkout_session.id,
                'redirect_url': checkout_session.url
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SuccessView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        session_id = request.GET.get("session_id")
        if not session_id:
            return Response({"error": "Missing session_id"}, status=400)

        try:
            # Retrieve session from Stripe
            session = st.checkout.Session.retrieve(session_id, expand=["payment_intent"])
            payment_intent = session.payment_intent

            # Update local transaction record
            try:
                transaction = Transaction.objects.get(stripe_session_id=session_id)
                transaction.stripe_payment_intent = payment_intent.id if payment_intent else None
                transaction.status = session.payment_status  # "paid", "unpaid"
                transaction.save()
            except Transaction.DoesNotExist:
                transaction = None

            return Response({
                "message": "Payment was successful!",
                "transaction_id": transaction.id if transaction else None,
                "session_id": session.id,
                "payment_intent": payment_intent.id if payment_intent else None,
                "amount_total": session.amount_total / 100,
                "currency": session.currency,
                "payment_status": session.payment_status,
                "product_id": session.metadata.get("product_id") if session.metadata else None,
            }, status=status.HTTP_200_OK)

        except st.error.StripeError as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CancelView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        return Response({"message": "Payment was cancelled."}, status=status.HTTP_200_OK)
