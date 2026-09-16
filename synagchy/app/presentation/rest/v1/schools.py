from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from app.infrastructure.database.models import School, Subject, SchoolSubjectPDF, SchoolClass
from app.presentation.rest.v1.serializers import SchoolSerializer, SubjectSerializer


class SchoolListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Ähli mekdepleriň sanawyny getirýär.",
        responses={
            200: openapi.Response(
                description="Üstünlikli. Mekdepler sanawy.",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_OBJECT),
                ),
            ),
        },
    )
    def get(self, request):
        schools = School.objects.all()
        return Response(SchoolSerializer(schools, many=True).data)

    @swagger_auto_schema(
        operation_description="Täze mekdep döredýär.",
        request_body=SchoolSerializer,
        responses={
            201: openapi.Response(description="Üstünlikli mekdep döredildi.", schema=SchoolSerializer),
            400: openapi.Response(description="Nädogry maglumat."),
        },
    )
    def post(self, request):
        serializer = SchoolSerializer(data=request.data)
        if serializer.is_valid():
            school = School.objects.create(name=serializer.validated_data.get('name'), address=serializer.validated_data.get('address', ''))
            return Response(SchoolSerializer(school).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SchoolDetailView(APIView):
    @swagger_auto_schema(
        operation_description="ID boýunça mekdepiň jikme-jik maglumatlaryny getirýär.",
        responses={
            200: openapi.Response(description="Üstünlikli. Mekdep jikme-jigi.", schema=SchoolSerializer),
            404: openapi.Response(description="Mekdep tapylmady."),
        },
    )
    def get(self, request, pk):
        try:
            school = School.objects.get(pk=pk)
        except School.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(SchoolSerializer(school).data)


class SubjectExamPdfView(APIView):
    """Get subject exam PDF URL."""
    @swagger_auto_schema(
        operation_description="Dersiň synag PDF faýlynyň URL-sini we maglumatlaryny getirýär.",
        responses={
            200: openapi.Response(description="Üstünlikli. Dersiň maglumatlary we exam_pdf URL.", schema=SubjectSerializer),
            404: openapi.Response(description="Ders tapylmady."),
        },
    )
    def get(self, request, subject_id):
        try:
            subject = Subject.objects.get(pk=subject_id)
        except Subject.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        data = SubjectSerializer(subject).data
        # include exam_pdf URL if present
        return Response(data)


class SchoolSubjectPdfView(APIView):
    """
    Mekdep, klas we ders bagly leksiýa, sorag we jogap PDF faýllaryny getirýär.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description=(
            "Mekdep (school_id), klas (class_id) we ders (subject_id) bagly leksiýa, "
            "sorag we jogap PDF faýllarynyň URL-sini getirýär. "
            "Admin panelde SchoolSubjectPDF modeline goşulan faýllar gaýtarýär. "
            "class_id berilmezse mekdepýň umumy faýllary gaýtarýär. "
            "Faýl ýoksa None gaýtarýar."
        ),
        responses={
            200: openapi.Response(
                description="Üstünlikli. Mekdep-Klas-Ders PDF faýllary we maglumatlary.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'school_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="Mekdep ID-si"),
                        'class_id': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True, description="Klas ID-si (mesele: 9-A)"),
                        'class_name': openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description="Klas ady"),
                        'subject_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="Ders ID-si"),
                        'subject_name': openapi.Schema(type=openapi.TYPE_STRING, description="Ders ady"),
                        'lecture_pdf_url': openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description="Leksiýa PDF URL"),
                        'questions_pdf_url': openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description="Soraglar PDF URL"),
                        'answers_pdf_url': openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description="Jogaplar PDF URL"),
                    },
                ),
            ),
            404: openapi.Response(description="Mekdep, klas ýa-da ders tapylmady."),
        },
    )
    def get(self, request, school_id, subject_id):
        class_id = request.query_params.get('class_id')

        try:
            school = School.objects.get(pk=school_id)
        except School.DoesNotExist:
            return Response({'error': 'Mekdep tapylmady'}, status=status.HTTP_404_NOT_FOUND)

        try:
            subject = Subject.objects.get(pk=subject_id)
        except Subject.DoesNotExist:
            return Response({'error': 'Ders tapylmady'}, status=status.HTTP_404_NOT_FOUND)

        qs = SchoolSubjectPDF.objects.filter(school=school, subject=subject)
        if class_id:
            qs = qs.filter(school_class_id=class_id)

        pdf = qs.first()

        class_name = None
        if pdf and pdf.school_class:
            class_name = pdf.school_class.name

        return Response({
            'school_id': school.id,
            'class_id': pdf.school_class.id if pdf and pdf.school_class else None,
            'class_name': class_name,
            'subject_id': subject.id,
            'subject_name': subject.name,
            'lecture_pdf_url': pdf.lecture_pdf.url if pdf and pdf.lecture_pdf else None,
            'questions_pdf_url': pdf.questions_pdf.url if pdf and pdf.questions_pdf else None,
            'answers_pdf_url': pdf.answers_pdf.url if pdf and pdf.answers_pdf else None,
        })


class SchoolClassListView(APIView):
    """
    Mekdepdäki klaslar sanawy.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description=(
            "Mekdepdäki ähli klaslaryň sanawyny getirýär. "
            "Her klas: id, name (klas ady), school, subjects (dersler ID sanawy), subjects_count (dersler sany)."
        ),
        responses={
            200: openapi.Response(
                description="Üstünlikli. Klaslar sanawy.",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description="Klas ID-si"),
                            'name': openapi.Schema(type=openapi.TYPE_STRING, description="Klas ady (9-A, 10-B)"),
                            'school': openapi.Schema(type=openapi.TYPE_INTEGER, description="Mekdep ID-si"),
                            'subjects': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                description="Dersler ID sanawy",
                                items=openapi.Schema(type=openapi.TYPE_INTEGER),
                            ),
                            'subjects_count': openapi.Schema(type=openapi.TYPE_INTEGER, description="Dersler sany"),
                        },
                    ),
                ),
            ),
        },
    )
    def get(self, request, school_id):
        try:
            school = School.objects.get(pk=school_id)
        except School.DoesNotExist:
            return Response({'error': 'Mekdep tapylmady'}, status=status.HTTP_404_NOT_FOUND)

        classes = SchoolClass.objects.filter(school=school)
        data = []
        for cls in classes:
            data.append({
                'id': cls.id,
                'name': cls.name,
                'school': cls.school_id,
                'subjects': list(cls.subjects.values_list('id', flat=True)),
                'subjects_count': cls.subjects_count,
            })
        return Response(data)
