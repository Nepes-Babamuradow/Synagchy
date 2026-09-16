from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from app.infrastructure.database.models import OnlineTutor
from app.presentation.rest.v1.serializers import OnlineTutorSerializer


class TutorListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Ähli onlaýn repetitorlaryň sanawyny getirýär.",
        responses={
            200: openapi.Response(
                description="Üstünlikli. Repetitorlar sanawy.",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_OBJECT),
                ),
            ),
        },
    )
    def get(self, request):
        tutors = OnlineTutor.objects.all()
        return Response(OnlineTutorSerializer(tutors, many=True).data)

    @swagger_auto_schema(
        operation_description="Täze onlaýn repetitor goşýär.",
        request_body=OnlineTutorSerializer,
        responses={
            201: openapi.Response(description="Üstünlikli repetitor döredildi.", schema=OnlineTutorSerializer),
            400: openapi.Response(description="Nädogry maglumat."),
        },
    )
    def post(self, request):
        serializer = OnlineTutorSerializer(data=request.data)
        if serializer.is_valid():
            tutor = OnlineTutor.objects.create(**serializer.validated_data)
            return Response(OnlineTutorSerializer(tutor).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
