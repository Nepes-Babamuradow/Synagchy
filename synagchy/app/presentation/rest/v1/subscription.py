from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from app.infrastructure.database.models import Subscription, User
from app.presentation.rest.v1.serializers import (
    SubscriptionSerializer, SubscriptionPlanSerializer, SubscriptionResponseSerializer,
)


class SubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Token bilen: öz abuna maglumatyňyz.",
        responses={200: SubscriptionSerializer},
    )
    def get(self, request):
        sub, created = Subscription.objects.get_or_create(user=request.user)
        return Response(SubscriptionSerializer(sub).data)

    @swagger_auto_schema(
        request_body=SubscriptionPlanSerializer,
        responses={201: SubscriptionResponseSerializer, 400: 'Nädogry maglumat'},
        operation_description="Abuna satyn almak / täzelemek. Token gerek.",
    )
    def post(self, request):
        plan = request.data.get('plan', 'free')
        user = request.user

        # Top 3 ulanyjy yenillik alýar
        rating_users = list(User.objects.all().order_by('-rating')[:5])
        discount = 0
        if user in rating_users:
            rank = rating_users.index(user) + 1
            discount = {1: 50, 2: 30, 3: 20}.get(rank, 0)

        sub, created = Subscription.objects.update_or_create(
            user=user,
            defaults={'plan': plan, 'is_active': True}
        )
        data = SubscriptionSerializer(sub).data
        data['discount_percent'] = discount
        return Response(data, status=status.HTTP_201_CREATED)
