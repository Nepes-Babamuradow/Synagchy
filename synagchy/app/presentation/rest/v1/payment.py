from decimal import Decimal
from datetime import timedelta

from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from app.infrastructure.database.models import Payment, Subscription, User, SubscriptionPlanPrice
from app.presentation.rest.v1.serializers import (
    PaymentSerializer, PaymentRequestSerializer, PaymentConfirmSerializer,
    MessageSerializer,
)

# ============================================================
#  BANK API KONFIGURASIÝASY
#  ------------------------------------------------------------
#  Şu ýerde hakyky bank API-iňiziň maglumatlaryny ýazmaly:
#  BANKA_API_URL   - bank API-nyň esasy URL-i (meselem /api/v1/pay)
#  BANKA_API_KEY   - bank API-nyň açar (token / merchant key)
#  ------------------------------------------------------------
BANKA_API_URL = "https://bank-nu.gov.tm/api/v1/payment"   # <-- bank API URL
BANKA_API_KEY = "BANK_API_ACAR_YAZYN"                      # <-- bank API acary
# ============================================================

# Premium abuna bahalary (manat)
PLAN_PRICES = {
    'premium': Decimal('50.00'),
    'vip': Decimal('100.00'),
}                 


def get_plan_price(plan: str) -> Decimal:
    """Abuna bahasyny admin panelden (DB) okar, ýogsa fallback baha berýär."""
    try:
        price_obj = SubscriptionPlanPrice.objects.filter(plan=plan, is_active=True).first()
        if price_obj is not None:
            return Decimal(str(price_obj.price))
    except Exception:
        pass
    return PLAN_PRICES.get(plan, Decimal('0.00'))


class PaymentView(APIView):
    """
    Töleg görmek / döretmek.
    POST /api/v1/payment/
    Ulanyjy bank tölegi üçin maglumatlary dolduryp, töleýär.
    Top 1,2,3-nji orundakylara yenillik degişli.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description=(
            "Token bilen ulanyjynyň töleg taryhyny getirýär. "
            "Authorization header-da Bearer token hökmany. "
            "Her töleg: id, user, user_username, plan, amount, discount_percent, final_amount, bank_ref, status, created_at."
        ),
        responses={
            200: openapi.Response(
                description="Üstünlikli. Töleg taryhy.",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_OBJECT),
                ),
            ),
            401: openapi.Response(description="Token ýok ýa-da ýalňyş."),
        },
    )
    def get(self, request):
        """Ulanyjynyň töleg taryhy"""
        payments = Payment.objects.filter(user=request.user).order_by('-created_at')
        return Response(PaymentSerializer(payments, many=True).data)

    @swagger_auto_schema(
        request_body=PaymentRequestSerializer,
        responses={
            201: openapi.Response(
                description="Üstünlikli töleg başlady. Töleg maglumatlary we bank referansy gaýtarylýar.",
                schema=PaymentSerializer,
            ),
            400: openapi.Response(description="Nädogry abuna görnüşi. Diňe premium ýa-da VIP saýlap bilersiňiz."),
            401: openapi.Response(description="Token ýok ýa-da ýalňyş."),
        },
        operation_description=(
            "Töleg başlatmak üçin ulanýar. Token gerek. "
            "Plan: premium (50 TMT) ýa-da vip (100 TMT). "
            "Reýtingde 1, 2, 3-nji orun bolsa, yenillik (50%, 30%, 20%) hasaba alynýar. "
            "Netijede: amount (asyl baha), discount_percent, final_amount, bank_ref, status berilýär. "
            "Bu demo üçin mock ulanylýar, hakyky bank API birleşdirilende çalşyrylýar."
        ),
    )
    def post(self, request):
        """Töleg başlatmak"""
        plan = request.data.get('plan', 'premium')
        if plan not in PLAN_PRICES:
            return Response(
                {'error': 'Nädogry abuna görnüşi'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
        amount = get_plan_price(plan)

        # Top ulanyjylar (1, 2, 3-nji) üçin yenillik hasapla
        discount_percent = self._get_discount(user)
        final_amount = (amount * (Decimal(100) - Decimal(discount_percent))) / Decimal(100)

        # Bank API-e töleg soragy ugrat
        bank_response = self._bank_api_initiate(
            user, amount, final_amount, discount_percent
        )
        bank_ref = bank_response.get('bank_ref', '')

        payment = Payment.objects.create(
            user=user,
            plan=plan,
            amount=amount,
            discount_percent=discount_percent,
            final_amount=final_amount,
            bank_ref=bank_ref,
            status='pending',
        )

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_201_CREATED
        )

    def _get_discount(self, user):
        """Top 3 ulanyjy üçin yenillik (1:50%, 2:30%, 3:20%)"""
        rating_users = list(User.objects.all().order_by('-rating')[:5])
        if user in rating_users:
            rank = rating_users.index(user) + 1
            return {1: 50, 2: 30, 3: 20}.get(rank, 0)
        return 0

    def _bank_api_initiate(self, user, amount, final_amount, discount_percent):
        """
        BANK API-e töleg soragyny ugradýan funksiýa.
        ------------------------------------------------------------
        #  ŞU ÝERDE BANK API-E SORAG IBERMEK ÜÇIN KODY ÝAZMALY!
        #
        #  Hakyky bank bilen baglanyşanda şu funksiýanyň içini
        #  doldurmaly. Meselem `requests` kitaphanasy bilen:
        #
        #  import requests
        #  resp = requests.post(
        #      BANKA_API_URL,
        #      json={
        #          'amount': str(final_amount),
        #          'card_number': request.data.get('card_number'),
        #          'expiry': request.data.get('expiry'),
        #          'cvv': request.data.get('cvv'),
        #          'api_key': BANKA_API_KEY,
        #      }
        #  )
        #  return resp.json()
        #
        #  Häzirki wagtda bu ýerde PLACEHOLDER (mock) ulanylyar.
        #  Bank API-iňiz birleşdirilende, aşakdaky mock koddan
        #  hakyky `requests` çaýgyryşyna çalşyň.
        ------------------------------------------------------------
        """
        # ---- PLACEHOLDER: Bank API-e sorag ----
        # Aşakdaky satyrlar diňe demo üçin. Hakyky bank API bilen
        # işleýänden soň bu bölümi çalyşyn.
        mock_ref = f"BANK-{user.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        return {
            'bank_ref': mock_ref,
            'status': 'pending',
        }


class PaymentConfirmView(APIView):
    """
    Bank API-synyň habarçysy (webhook / callback).
    POST /api/v1/payment/confirm/
    Töleg tassyklanda, ulanyjynyň abunasy premium bolýar.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=PaymentConfirmSerializer,
        responses={
            200: openapi.Response(description="Töleg tassyklandy. Abuna işjeňleşdirildi."),
            404: openapi.Response(description="Töleg tapylmady. Bank referans ýa-da ulanyjy ýalňyş."),
            400: openapi.Response(description="Töleg başartsyz. Töleg üstünlikli bolmady."),
        },
        operation_description=(
            "Bank API-dan gelen habarçy (webhook/callback). "
            "Töleg tassyklanda, ulanyjynyň abunasy premium/VIP we 30 günluň güýjünli bolýar. "
            "Bu endpoint-i diňe bank API-iň webhook-y çağyrýar, frontend ulanmaz."
        ),
    )
    def post(self, request):
        bank_ref = request.data.get('bank_ref')
        success = request.data.get('success', True)

        try:
            payment = Payment.objects.get(bank_ref=bank_ref, user=request.user)
        except Payment.DoesNotExist:
            return Response(
                {'error': 'Töleg tapylmady'},
                status=status.HTTP_404_NOT_FOUND
            )

        if success:
            payment.status = 'paid'
            payment.save()

            # Abunany premium edýäris (tölegde saýlanan plan bahasy)
            Subscription.objects.update_or_create(
                user=payment.user,
                defaults={
                    'plan': payment.plan,
                    'is_active': True,
                    'started_at': timezone.now(),
                    'expires_at': timezone.now() + timedelta(days=30),
                }
            )
            return Response({'message': f'{payment.plan} abuna işjeňleşdirildi'})
        else:
            payment.status = 'failed'
            payment.save()
            return Response(
                {'message': 'Töleg başartsyz'},
                status=status.HTTP_400_BAD_REQUEST
            )
