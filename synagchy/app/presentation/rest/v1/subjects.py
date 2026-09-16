from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from app.infrastructure.database.models import Subject
from app.presentation.rest.v1.serializers import SubjectSerializer
from app.presentation.rest.v1.pagination import PAGE_PARAMS, StandardPagination


class SubjectListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description=(
            "Ähli dersleriň sanawyny getirýär (paginated). "
            "Her ders: id, exams (synaglaryň ID sanawy), name, max_score, image, "
            "exam_pdf (synag PDF), questions_pdf (soraglar PDF), answers_pdf (jogaplar PDF)."
        ),
        manual_parameters=PAGE_PARAMS,
        responses={
            200: openapi.Response(
                description="Üstünlikli. Dersler sanawy (paginated).",
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
        subjects = Subject.objects.all()
        pg = StandardPagination()
        page = pg.paginate_queryset(subjects, request, view=self)
        serializer = SubjectSerializer(page, many=True)
        return pg.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        request_body=SubjectSerializer,
        responses={
            201: openapi.Response(description="Üstünlikli ders döredildi."),
            400: openapi.Response(description="Nädogry maglumat."),
        },
        operation_description=(
            "Täze ders döredýär. Dersiň ady we iň ýokary bal (max_score) hökmany. "
            "Şeýle-de bolsa, synaglary birikdirýän exams meýdanyny hem belläň. "
            "Faýllary (exam_pdf, questions_pdf, answers_pdf) hem goşmak bolýar."
        ),
    )
    def post(self, request):
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubjectDetailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description=(
            "ID boýunça bir derstiň jikme-jik maglumatlaryny getirýär. "
            "Dersiň synaglara bagly bolsa, exams meýdannda synaglaryň ID sanawy görkezilýär. "
            "Şeýle-de exam_pdf, questions_pdf, answers_pdf faýllaryň URL-lary hem gaýtarýär."
        ),
        responses={
            200: openapi.Response(description="Üstünlikli. Derstiň jikme-jigi.", schema=SubjectSerializer),
            404: openapi.Response(description="Ders tapylmady."),
        },
    )
    def get(self, request, pk):
        try:
            subject = Subject.objects.get(pk=pk)
        except Subject.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = SubjectSerializer(subject)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=SubjectSerializer,
        operation_description=(
            "Derstiň maglumatlaryny doly redaktirleýär (PUT). "
            "Ähli meýdanlar: name, max_score, exams, exam_pdf, questions_pdf, answers_pdf, image."
        ),
        responses={
            200: openapi.Response(description="Üstünlikli redaktirleme. Täzelenen ders maglumatlary."),
            400: openapi.Response(description="Nädogry maglumat."),
            404: openapi.Response(description="Ders tapylmady."),
        },
    )
    def put(self, request, pk):
        try:
            subject = Subject.objects.get(pk=pk)
        except Subject.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = SubjectSerializer(subject, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=SubjectSerializer,
        operation_description=(
            "Derstiň maglumatlarynyň bir bölegini redaktirleýär (PATCH). "
            "Ütgetmek isleýän meýdanlaryňyzy iberiň, beýlekiler galýar."
        ),
        responses={
            200: openapi.Response(description="Üstünlikli redaktirleme. Täzelenen ders maglumatlary."),
            400: openapi.Response(description="Nädogry maglumat."),
            404: openapi.Response(description="Ders tapylmady."),
        },
    )
    def patch(self, request, pk):
        try:
            subject = Subject.objects.get(pk=pk)
        except Subject.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = SubjectSerializer(subject, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)