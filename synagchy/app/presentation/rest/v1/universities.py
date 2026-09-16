from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema

from app.infrastructure.database.models import University, Faculty
from app.presentation.rest.v1.serializers import (
    UniversitySerializer, FacultySerializer,
    UniversityDetailSerializer, FacultyDetailSerializer,
)
from app.presentation.rest.v1.pagination import PAGE_PARAMS, StandardPagination


class UniversityListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Ähli uniwersitetleriň sanawy (paginated).",
        manual_parameters=PAGE_PARAMS,
        responses={200: UniversitySerializer(many=True)},
    )
    def get(self, request):
        universities = University.objects.all()
        pg = StandardPagination()
        page = pg.paginate_queryset(universities, request, view=self)
        serializer = UniversitySerializer(page, many=True)
        return pg.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        request_body=UniversitySerializer,
        responses={201: UniversitySerializer, 400: 'Nädogry maglumat'},
        operation_description="Täze uniwersitet goşmak.",
    )
    def post(self, request):
        serializer = UniversitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UniversityDetailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Uniwersitetiň jikme-jigi (fakultetler bilen).",
        responses={200: UniversityDetailSerializer, 404: 'Tapylmady'},
    )
    def get(self, request, pk):
        try:
            university = University.objects.get(pk=pk)
        except University.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        faculties = Faculty.objects.filter(university=university)
        data = UniversitySerializer(university).data
        data['faculties'] = FacultySerializer(faculties, many=True).data
        return Response(data)


class FacultyListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Ähli fakultetleriň sanawy (paginated).",
        manual_parameters=PAGE_PARAMS,
        responses={200: FacultySerializer(many=True)},
    )
    def get(self, request):
        faculties = Faculty.objects.all()
        pg = StandardPagination()
        page = pg.paginate_queryset(faculties, request, view=self)
        serializer = FacultySerializer(page, many=True)
        return pg.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        request_body=FacultySerializer,
        responses={201: FacultySerializer, 400: 'Nädogry maglumat'},
        operation_description="Täze fakultet goşmak.",
    )
    def post(self, request):
        serializer = FacultySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FacultyDetailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Fakultetiň jikme-jigi (hünärler bilen).",
        responses={200: FacultyDetailSerializer, 404: 'Tapylmady'},
    )
    def get(self, request, pk):
        try:
            faculty = Faculty.objects.get(pk=pk)
        except Faculty.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        specialties = faculty.specialties.all()
        from app.presentation.rest.v1.serializers import SpecialtySerializer
        data = FacultySerializer(faculty).data
        data['specialties'] = SpecialtySerializer(specialties, many=True).data
        return Response(data)


# class LectureListView(APIView):
#     permission_classes = [AllowAny]

#     @swagger_auto_schema(
#         operation_description="Ähli fakultetleriň sanawy (paginated).",
#         manual_parameters=PAGE_PARAMS,
#         responses={200: (many=True)},
#     )
#     def get(self, request):
#         faculties = Faculty.objects.all()
#         pg = StandardPagination()
#         page = pg.paginate_queryset(faculties, request, view=self)
#         serializer = FacultySerializer(page, many=True)
#         return pg.get_paginated_response(serializer.data)

#     @swagger_auto_schema(
#         request_body=FacultySerializer,
#         responses={201: FacultySerializer, 400: 'Nädogry maglumat'},
#         operation_description="Täze fakultet goşmak.",
#     )
#     def post(self, request):
#         serializer = FacultySerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class FacultyDetailView(APIView):
#     permission_classes = [AllowAny]

#     @swagger_auto_schema(
#         operation_description="Fakultetiň jikme-jigi (hünärler bilen).",
#         responses={200: FacultyDetailSerializer, 404: 'Tapylmady'},
#     )
#     def get(self, request, pk):
#         try:
#             faculty = Faculty.objects.get(pk=pk)
#         except Faculty.DoesNotExist:
#             return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

#         specialties = faculty.specialties.all()
#         from app.presentation.rest.v1.serializers import SpecialtySerializer
#         data = FacultySerializer(faculty).data
#         data['specialties'] = SpecialtySerializer(specialties, many=True).data
#         return Response(data)
