from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from app.infrastructure.database.models import EntranceExam, Subject, Specialty, Region
from app.presentation.rest.v1.serializers import (
    EntranceExamSerializer, SubjectSerializer, SpecialtySerializer,
    ExamDetailSerializer, SpecialtyDetailSerializer,
    RegionAdmissionSerializer,
)
from app.presentation.rest.v1.pagination import PAGE_PARAMS, StandardPagination


class ExamListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description=(
            "Ähli giriş synaglarynyň sanawyny getirýär (paginated). "
            "Synaglary hünäre görä süzmek üçin ?specialty=<id> parametrini ulanyň. "
            "Her synag: id, specialty, specialty_name, faculty_name, university_name, title, description."
        ),
        manual_parameters=PAGE_PARAMS + [
            openapi.Parameter(
                'specialty', openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description='Hünär boýunça filtr (specialty ID)'
            ),
        ],
        responses={
            200: openapi.Response(
                description="Üstünlikli. Synaglar sanawy (paginated).",
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
        exams = EntranceExam.objects.all()
        specialty_id = request.query_params.get('specialty')
        if specialty_id:
            exams = exams.filter(specialty_id=specialty_id)
        pg = StandardPagination()
        page = pg.paginate_queryset(exams, request, view=self)
        serializer = EntranceExamSerializer(page, many=True)
        return pg.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        request_body=EntranceExamSerializer,
        responses={
            201: openapi.Response(description="Üstünlikli synag döredildi. Täze synagyň ID-si we maglumatlary gaýtarylýar."),
            400: openapi.Response(description="Nädogry maglumat. Validasiýa şäheri düşünükli görkezilýär."),
        },
        operation_description=(
            "Täze giriş synagy döredýär. Synag bir hünäre (specialty) bagly bolmaly. "
            "Şeýle-de bolsa, synagyň ady (title) we beýleki maglumatlary iberiň."
        ),
    )
    def post(self, request):
        serializer = EntranceExamSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExamDetailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description=(
            "Synagyň jikme-jik maglumatlaryny we oňa degişli dersleriň sanawyny getirýär. "
            "Synag ID-si bilen soralýar. Netijede synagyň ady, hünär, fakultet, uniwersitet we dersler sanawy bar."
        ),
        responses={
            200: openapi.Response(description="Üstünlikli. Synagyň jikme-jigi we dersleri.", schema=ExamDetailSerializer),
            404: openapi.Response(description="Synag tapylmady."),
        },
    )
    def get(self, request, pk):
        try:
            exam = EntranceExam.objects.get(pk=pk)
        except EntranceExam.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        subjects = Subject.objects.filter(exams=exam)
        data = EntranceExamSerializer(exam).data
        data['subjects'] = SubjectSerializer(subjects, many=True).data
        return Response(data)


REGION_PARAM = openapi.Parameter(
    'region', openapi.IN_QUERY,
    type=openapi.TYPE_INTEGER,
    description='Etrap boýunça filtr (region ID). region_admissions içinde çap edilýär.',
    required=False,
)


class SpecialtyListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description=(
            "Ähli hünärleriň sanawyny getirýır. "
            "Hünäri etrap boýunça süzmek üçin ?region=<id> parametrini ulanyň. "
            "Ulanyjy giriş etse, her hünäriň region_admissions-di ol ulanyjynyň "
            "saylan etrap (region) boýunça süzgülen bolýar. "
            "Her hünär: id, faculty, faculty_name, university_name, name, description, "
            "required_documents, application_deadline we region_admissions (etrap boýunça "
            "kabul sany, tapşyryk sany, synag wagty)."
        ),
        manual_parameters=PAGE_PARAMS + [REGION_PARAM],
        responses={
            200: openapi.Response(
                description="Üstünlikli. Hünärler sanawy (paginated). region_admissions ulanyjynyň etrapynyň diýen birnäçe görkeziler.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER, description="Jemi hünär sany"),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True),
                        'results': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT),
                        ),
                    },
                ),
            ),
        },
    )
    def get(self, request):
        specialties = Specialty.objects.all()
        region_id = request.query_params.get('region')
        if region_id:
            specialties = specialties.filter(region_admissions__region_id=region_id).distinct()

        pg = StandardPagination()
        page = pg.paginate_queryset(specialties, request, view=self)
        serializer = SpecialtySerializer(page, many=True, context={'request': request})
        return pg.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        request_body=SpecialtySerializer,
        responses={
            201: openapi.Response(description="Üstünlikli hünär döredildi."),
            400: openapi.Response(description="Nädogry maglumat. Validasiýa şäheri düşünükli görkezilýär."),
        },
        operation_description=(
            "Täze hünär döredýır. Hünär bir fakultete (faculty) bagly bolmaly. "
            "2-5 sany synag we dersleri bir hatda goşmak bolýar. "
            "Gerekli resminamalar, mugallymçylyk ýaly maglumatlary hem ýazyp bilersiňiz. "
            "region_admissions ile etrap boýunça kabul sany, tapşyryk sany we synag wagty goşup bileriň."
        ),
    )
    def post(self, request):
        serializer = SpecialtySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SpecialtyDetailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description=(
            "Hünäriň jikme-jik maglumatlaryny we oňa degişli synaglaryň sanawyny getirýır. "
            "Synaglaryň içinde bolsa dersleri hem bar. "
            "region_admissions ulanyjy giriş etse, şol ulanyjynyň saylan etrap "
            "(region) boýunça süzgülen. Giriş etmedik bolsa, ähli etraplar görkezilýär. "
            "Her region üçin: region, region_name, admission_capacity, applications_count, exam_start_at."
        ),
        responses={
            200: openapi.Response(
                description="Üstünlikli. Hünär, synaglar we ulanyjynyň etrapyna görä süzgülen region_admissions.",
                schema=SpecialtyDetailSerializer,
            ),
            404: openapi.Response(description="Hünär tapylmady."),
        },
    )
    def get(self, request, pk):
        try:
            specialty = Specialty.objects.get(pk=pk)
        except Specialty.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        data = SpecialtySerializer(specialty, context={'request': request}).data
        data['exams'] = ExamDetailSerializer(specialty.exams.all(), many=True).data
        return Response(data)


class RegionAdmissionListView(APIView):
    """
    Bir hünäriň etrap boýunça giriş maglumatlaryny (admission_capacity,
    applications_count, exam_start_at) getirýär.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description=(
            "Hünär ID-sine göre etrap boýunça giriş maglumatlarynyň sanawyny getirýır. "
            "Her bir etrap üçin: region, region_name, admission_capacity "
            "(Kabul edilmeli talyp sany), applications_count (Tabşyrylanlaryň sany), "
            "exam_start_at (Synagyň başlaýan wagty)."
        ),
        responses={
            200: openapi.Response(
                description="Üstünlikli. Region giriş maglumatlary sanawy.",
                schema=RegionAdmissionSerializer(many=True),
            ),
            404: openapi.Response(description="Hünär tapylmady."),
        },
    )
    def get(self, request, specialty_id):
        try:
            specialty = Specialty.objects.get(pk=specialty_id)
        except Specialty.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        admissions = specialty.region_admissions.all().order_by('region')
        return Response(RegionAdmissionSerializer(admissions, many=True).data)


class SpecialtyByRegionView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description=(
            "Hünär we etrap ID-leri bilen hünäriň şol etrap boýunça "
            "giriş maglumatlaryny getirýır. ?specialty_id=<id>&region_id=<id> "
            "parametrleri bilen soralýar. "
            "Netijede: hünäriň ady, fakultet, uniwersitet we şol etrapdaky "
            "kabul sany (admission_capacity), tapşyryk sany (applications_count), "
            "synag wagty (exam_start_at) görkezilýär."
        ),
        manual_parameters=[
            openapi.Parameter(
                'specialty_id', openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description='Hünäriň ID-si',
                required=True,
            ),
            openapi.Parameter(
                'region_id', openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description='Etrabyň ID-si (region ID)',
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Üstünlikli. Hünär we şol etrapdaky giriş maglumatlary.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description="Hünäriň ID-si"),
                        'name': openapi.Schema(type=openapi.TYPE_STRING, description="Hünäriň ady"),
                        'description': openapi.Schema(type=openapi.TYPE_STRING, description="Hünäriň beýany"),
                        'faculty_name': openapi.Schema(type=openapi.TYPE_STRING, description="Fakultetiň ady"),
                        'university_name': openapi.Schema(type=openapi.TYPE_STRING, description="Uniwersitetiň ady"),
                        'region_admission': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description="Şol etrapdaky giriş maglumatlary",
                            properties={
                                'region_name': openapi.Schema(type=openapi.TYPE_STRING),
                                'admission_capacity': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'applications_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'exam_start_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                            },
                        ),
                    },
                ),
            ),
            404: openapi.Response(description="Hünär ýa-da etrap tapylmady."),
        },
    )
    def get(self, request):
        specialty_id = request.query_params.get('specialty_id')
        region_id = request.query_params.get('region_id')

        if not specialty_id or not region_id:
            return Response(
                {'error': 'specialty_id we region_id parametrleri zerur.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            specialty = Specialty.objects.get(pk=specialty_id)
        except Specialty.DoesNotExist:
            return Response({'error': 'Hünär tapylmady.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            region = Region.objects.get(pk=region_id)
        except Region.DoesNotExist:
            return Response({'error': 'Etrap tapylmady.'}, status=status.HTTP_404_NOT_FOUND)

        admission = specialty.region_admissions.filter(region=region).first()
        if not admission:
            return Response({'error': 'Bu hünär üçin şol etrapda giriş maglumatlary ýok.'}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'id': specialty.id,
            'name': specialty.name,
            'description': specialty.description,
            'faculty_name': specialty.faculty.name if specialty.faculty else None,
            'university_name': specialty.faculty.university.name if specialty.faculty and specialty.faculty.university else None,
            'region_admission': RegionAdmissionSerializer(admission).data,
        })
