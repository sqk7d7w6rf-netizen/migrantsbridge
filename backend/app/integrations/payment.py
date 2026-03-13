"""Payment gateway integration with Stripe."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)


class PaymentGateway:
    """Stripe-based payment gateway adapter."""

    def __init__(self, secret_key: str | None = None) -> None:
        self.secret_key = secret_key or settings.STRIPE_SECRET_KEY
        self._stripe = None

    def _get_stripe(self):
        """Lazily initialize the Stripe client."""
        if self._stripe is None:
            try:
                import stripe
                stripe.api_key = self.secret_key
                self._stripe = stripe
            except ImportError:
                logger.warning("stripe package not installed; payment processing will be a no-op")
                return None
        return self._stripe

    async def create_payment_intent(
        self,
        amount_cents: int,
        currency: str = "usd",
        customer_id: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> dict[str, Any] | None:
        """Create a Stripe PaymentIntent."""
        stripe_mod = self._get_stripe()
        if stripe_mod is None:
            logger.warning("Payment not processed (no stripe): amount=%d", amount_cents)
            return None

        try:
            params: dict[str, Any] = {
                "amount": amount_cents,
                "currency": currency,
                "metadata": metadata or {},
            }
            if customer_id:
                params["customer"] = customer_id

            intent = stripe_mod.PaymentIntent.create(**params)
            logger.info("PaymentIntent created: %s, amount=%d", intent.id, amount_cents)
            return {
                "id": intent.id,
                "client_secret": intent.client_secret,
                "status": intent.status,
                "amount": intent.amount,
                "currency": intent.currency,
            }
        except Exception:
            logger.exception("Failed to create PaymentIntent")
            return None

    async def create_customer(
        self,
        email: str,
        name: str,
        metadata: dict[str, str] | None = None,
    ) -> dict[str, Any] | None:
        """Create a Stripe Customer."""
        stripe_mod = self._get_stripe()
        if stripe_mod is None:
            return None

        try:
            customer = stripe_mod.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {},
            )
            logger.info("Stripe customer created: %s", customer.id)
            return {
                "id": customer.id,
                "email": customer.email,
                "name": customer.name,
            }
        except Exception:
            logger.exception("Failed to create Stripe customer")
            return None

    async def retrieve_payment_intent(self, payment_intent_id: str) -> dict[str, Any] | None:
        """Retrieve a PaymentIntent by ID."""
        stripe_mod = self._get_stripe()
        if stripe_mod is None:
            return None

        try:
            intent = stripe_mod.PaymentIntent.retrieve(payment_intent_id)
            return {
                "id": intent.id,
                "status": intent.status,
                "amount": intent.amount,
                "currency": intent.currency,
                "metadata": dict(intent.metadata) if intent.metadata else {},
            }
        except Exception:
            logger.exception("Failed to retrieve PaymentIntent %s", payment_intent_id)
            return None

    async def refund_payment(
        self,
        payment_intent_id: str,
        amount_cents: int | None = None,
    ) -> dict[str, Any] | None:
        """Issue a refund."""
        stripe_mod = self._get_stripe()
        if stripe_mod is None:
            return None

        try:
            params: dict[str, Any] = {"payment_intent": payment_intent_id}
            if amount_cents is not None:
                params["amount"] = amount_cents

            refund = stripe_mod.Refund.create(**params)
            logger.info("Refund created: %s for PaymentIntent %s", refund.id, payment_intent_id)
            return {
                "id": refund.id,
                "status": refund.status,
                "amount": refund.amount,
            }
        except Exception:
            logger.exception("Failed to refund PaymentIntent %s", payment_intent_id)
            return None

    @staticmethod
    def verify_webhook_signature(payload: bytes, sig_header: str) -> dict[str, Any] | None:
        """Verify a Stripe webhook signature and return the event."""
        try:
            import stripe
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            return {
                "id": event.id,
                "type": event.type,
                "data": event.data.object,
            }
        except Exception:
            logger.exception("Webhook signature verification failed")
            return None


payment_gateway = PaymentGateway()
