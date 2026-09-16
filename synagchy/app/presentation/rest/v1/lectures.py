from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from app.infrastructure.database.models import Lecture, LectureTopic, Subject
from app.presentation.rest.v1.serializers import (
    LectureGSerializer, LectureSerializer, LectureDetailSerializer,
    LectureTopicSerializer, LectureTopicDetailSerializer,
)
from app.presentation.rest.v1.pagination import PAGE_PARAMS, StandardPagination
from app.infrastructure.database.models.lecture import LectureG


class LectureTopicListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description=(
            "Ähli leksiýa temalarynyň sanawyny getirýär (paginated). "
            "Her tema: id, lecture, lecture_title, lecture_subject_id, title, description, order."
        ),
        manual_parameters=PAGE_PARAMS,
        responses={
            200: openapi.Response(
                description="Üstünlikli. Tema sanawy (paginated).",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True),
                        'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                    },
                ),
            ),
        },
    )
    def get(self, request):
        topics = LectureTopic.objects.all()
        pg = StandardPagination()
        page = pg.paginate_queryset(topics, request, view=self)
        serializer = LectureTopicSerializer(page, many=True)
        return pg.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        request_body=LectureTopicSerializer,
        responses={201: LectureTopicSerializer, 400: 'Nädogry maglumat'},
        operation_description="Täze leksiýa temasy goşmak.",
    )
    def post(self, request):
        serializer = LectureTopicSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LectureTopicDetailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Leksiýa temasynyň jikme-jigi (leksiýalar bilen).",
        responses={200: LectureTopicDetailSerializer, 404: 'Tapylmady'},
    )
    def get(self, request, pk):
        try:
            topic = LectureTopic.objects.get(pk=pk)
        except LectureTopic.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = LectureTopicDetailSerializer(topic)
        return Response(serializer.data)


class TopicsByLectureView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description=(
            "Bir leksiýanyň içindäki ähli temalaryň sanawyny getirýär (paginated). "
            "lecture_id URL param bilen berilýär."
        ),
        manual_parameters=[
            openapi.Parameter(
                'lecture_id', openapi.IN_PATH,
                description='Leksiýanyň ID-si',
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            *PAGE_PARAMS,
        ],
        responses={
            200: openapi.Response(
                description="Üstünlikli. Leksiýa temalary (paginated).",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True),
                        'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                    },
                ),
            ),
            404: openapi.Response(description="Leksiýa tapylmady."),
        },
    )
    def get(self, request, lecture_id):
        try:
            lecture = Lecture.objects.get(pk=lecture_id)
        except Lecture.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        topics = LectureTopic.objects.filter(lecture=lecture)
        pg = StandardPagination()
        page = pg.paginate_queryset(topics, request, view=self)
        serializer = LectureTopicSerializer(page, many=True)
        return pg.get_paginated_response(serializer.data)


class LecturesBySubjectView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description=(
            "Bir derstiň ähli leksiýalaryny getirýär (paginated). "
            "subject_id URL param bilen berilýär. "
            "Her leksiýa: id, subject, subject_name, title, content_type, content_text, image, pdf_file, audio, video, order, created_at, topics_count."
        ),
        manual_parameters=[
            openapi.Parameter(
                'subject_id', openapi.IN_PATH,
                description='Dersiň ID-si',
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            *PAGE_PARAMS,
        ],
        responses={
            200: openapi.Response(
                description="Üstünlikli. Dersiň leksiýalary (paginated).",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True),
                        'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                    },
                ),
            ),
            404: openapi.Response(description="Ders tapylmady."),
        },
    )
    def get(self, request, subject_id):
        try:
            Subject.objects.get(pk=subject_id)
        except Subject.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        lectures = Lecture.objects.filter(subject_id=subject_id)
        pg = StandardPagination()
        page = pg.paginate_queryset(lectures, request, view=self)
        serializer = LectureSerializer(page, many=True)
        return pg.get_paginated_response(serializer.data)


class LecturesGBySubjectView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description=(
            "Bir derstiň ähli gutardys egzamen leksiýalaryny getirýär (paginated). "
            "Bu ýönekeý leksiýalar bolup, umumy synaga taýýarlyk üçin ulanýar. "
            "subject_id URL param bilen berilýär."
        ),
        manual_parameters=[
            openapi.Parameter(
                'subject_id', openapi.IN_PATH,
                description='Dersiň ID-si',
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            *PAGE_PARAMS,
        ],
        responses={
            200: openapi.Response(
                description="Üstünlikli. Dersiň gutardys leksiýalary (paginated).",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True),
                        'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                    },
                ),
            ),
            404: openapi.Response(description="Ders tapylmady."),
        },
    )
    def get(self, request, subject_id):
        try:
            Subject.objects.get(pk=subject_id)
        except Subject.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        lectures = LectureG.objects.filter(subject_id=subject_id)
        pg = StandardPagination()
        page = pg.paginate_queryset(lectures, request, view=self)
        serializer = LectureGSerializer(page, many=True)
        return pg.get_paginated_response(serializer.data)




class TopicsWithLecturesBySubjectView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description=(
            "Bir derstiň ähli leksiýa temalaryny we olara degişli leksiýalary bir hatda getirýär (paginated). "
            "Bu endpoint frontendde dersiň temalaryny we olaryň içindäki leksiýalary görmek üçin ulanýar."
        ),
        manual_parameters=[
            openapi.Parameter(
                'subject_id', openapi.IN_PATH,
                description='Dersiň ID-si',
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            *PAGE_PARAMS,
        ],
        responses={
            200: openapi.Response(
                description="Üstünlikli. Tema we leksiýalar sanawy (paginated).",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True),
                        'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                    },
                ),
            ),
            404: openapi.Response(description="Ders tapylmady."),
        },
    )
    def get(self, request, subject_id):
        topics = LectureTopic.objects.filter(lecture__subject_id=subject_id)
        pg = StandardPagination()
        page = pg.paginate_queryset(topics, request, view=self)
        serializer = LectureTopicDetailSerializer(page, many=True)
        return pg.get_paginated_response(serializer.data)


class LectureListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description=(
            "Ähli leksiýalaryň sanawyny getirýär (paginated). "
            "Her leksiýa: id, subject, subject_name, title, content_type, content_text, image, pdf_file, audio, video, order, created_at, topics_count."
        ),
        manual_parameters=PAGE_PARAMS,
        responses={
            200: openapi.Response(
                description="Üstünlikli. Leksiýalar sanawy (paginated).",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True),
                        'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                    },
                ),
            ),
        },
    )
    def get(self, request):
        lectures = Lecture.objects.all()
        pg = StandardPagination()
        page = pg.paginate_queryset(lectures, request, view=self)
        serializer = LectureSerializer(page, many=True)
        return pg.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        request_body=LectureSerializer,
        responses={
            201: openapi.Response(description="Üstünlikli leksiýa döredildi."),
            400: openapi.Response(description="Nädogry maglumat."),
        },
        operation_description=(
            "Täze leksiýa döredýär. Leksiýa bir derse (subject) bagly bolmaly. "
            "content_type: text, formula, image, audio, video, pdf. "
            "Meselem: text üçin content_text, image üçin image faýly we ş.m."
        ),
    )
    def post(self, request):
        serializer = LectureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class LectureGListView(APIView):
#     permission_classes = [AllowAny]

#     @swagger_auto_schema(
#         operation_description="Ähli gutardys egz sanawy (paginated).",
#         manual_parameters=PAGE_PARAMS,
#         responses={200: LectureGSerializer(many=True)},
#     )
#     def get(self, request):
#         lectures = LectureG.objects.all()
#         pg = StandardPagination()
#         page = pg.paginate_queryset(lectures, request, view=self)
#         serializer = LectureGSerializer(page, many=True)
#         return pg.get_paginated_response(serializer.data)



class LectureDetailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description=(
            "Leksiýanyň jikme-jik maglumatlaryny we içindäki temalaryň sanawyny getirýär. "
            "Leksiýa ID-si bilen soralýar."
        ),
        responses={
            200: openapi.Response(description="Üstünlikli. Leksiýanyň jikme-jigi we temalary.", schema=LectureDetailSerializer),
            404: openapi.Response(description="Leksiýa tapylmady."),
        },
    )
    def get(self, request, pk):
        try:
            lecture = Lecture.objects.get(pk=pk)
        except Lecture.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = LectureDetailSerializer(lecture)
        return Response(serializer.data)


class LectureGDetailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Gutardys egz leksiyanyn jikme-jigi.",
        responses={200: LectureGSerializer, 404: 'Tapylmady'},
    )
    def get(self, request, pk):
        try:
            lecture = LectureG.objects.get(pk=pk)
        except LectureG.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = LectureGSerializer(lecture)
        return Response(serializer.data)
