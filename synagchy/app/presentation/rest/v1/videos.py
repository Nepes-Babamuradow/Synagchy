from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from app.infrastructure.database.models import VideoLesson
from app.presentation.rest.v1.serializers import VideoLessonSerializer


class VideoLessonListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Ähli wideo sapaklaryň sanawyny getirýär.",
        responses={
            200: openapi.Response(
                description="Üstünlikli. Wideo sapaklar sanawy.",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_OBJECT),
                ),
            ),
        },
    )
    def get(self, request):
        videos = VideoLesson.objects.all()
        return Response(VideoLessonSerializer(videos, many=True).data)

    @swagger_auto_schema(
        operation_description="Täze wideo sapak goşýär.",
        request_body=VideoLessonSerializer,
        responses={
            201: openapi.Response(description="Üstünlikli wideo sapak döredildi.", schema=VideoLessonSerializer),
            400: openapi.Response(description="Nädogry maglumat."),
        },
    )
    def post(self, request):
        serializer = VideoLessonSerializer(data=request.data)
        if serializer.is_valid():
            video = VideoLesson.objects.create(**serializer.validated_data)
            return Response(VideoLessonSerializer(video).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
