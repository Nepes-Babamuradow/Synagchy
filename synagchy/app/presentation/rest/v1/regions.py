from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from app.infrastructure.database.models import Region
from app.presentation.rest.v1.serializers import RegionSerializer
from app.presentation.rest.v1.pagination import PAGE_PARAMS, StandardPagination


class RegionListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description=(
            "Ähli etraplaryň sanawyny getirýär (paginated). "
            "Ulanyjy we hünäri girişinde etrap saýlanýar. "
            "Her etrap: id, name, description."
        ),
        manual_parameters=PAGE_PARAMS,
        responses={
            200: openapi.Response(
                description="Üstünlikli. Etrap sanawy (paginated).",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER, description="Jemi etrap sany"),
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
        regions = Region.objects.all()
        pg = StandardPagination()
        page = pg.paginate_queryset(regions, request, view=self)
        serializer = RegionSerializer(page, many=True)
        return pg.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        request_body=RegionSerializer,
        responses={
            201: openapi.Response(description="Üstünlikli etrap döredildi.", schema=RegionSerializer),
            400: openapi.Response(description="Nädogry maglumat. Eger name eýýäm bar bolsa."),
        },
        operation_description=(
            "Täze etrap (region) döredýér. name tekrarlanýan bolmaly däl. "
            "description islâhiyat (iňlizje: description) işläriňiz ýok bolsa, boş bıragalyar."
        ),
    )
    def post(self, request):
        serializer = RegionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegionDetailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Etrap ID-sine göre etrapyň jikme-jik maglumatlaryny getirýär.",
        responses={
            200: openapi.Response(description="Üstünlikli. Etrap jikme-jigi.", schema=RegionSerializer),
            404: openapi.Response(description="Etrap tapylmady."),
        },
    )
    def get(self, request, pk):
        try:
            region = Region.objects.get(pk=pk)
        except Region.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(RegionSerializer(region).data)

    @swagger_auto_schema(
        request_body=RegionSerializer,
        responses={
            200: openapi.Response(description="Üstünlikli. Täzelenen etrap.", schema=RegionSerializer),
            400: openapi.Response(description="Nädogry maglumat."),
            404: openapi.Response(description="Etrap tapylmady."),
        },
        operation_description="Etrabyň maglumatlaryny täzeleýär (PUT). name we description hökmany.",
    )
    def put(self, request, pk):
        try:
            region = Region.objects.get(pk=pk)
        except Region.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = RegionSerializer(region, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=RegionSerializer,
        responses={
            200: openapi.Response(description="Üstünlikli. Täzelenen etrap.", schema=RegionSerializer),
            400: openapi.Response(description="Nädogry maglumat."),
            404: openapi.Response(description="Etrap tapylmady."),
        },
        operation_description="Etrabyň maglumatlarynyň bir bölegini täzeleýär (PATCH).",
    )
    def patch(self, request, pk):
        try:
            region = Region.objects.get(pk=pk)
        except Region.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = RegionSerializer(region, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Etraby pozýar. İlkiön bilen içinde baglanyşyk etraplar bolsa, onlar hem pozylýar.",
        responses={
            204: openapi.Response(description="Etrap pozuldy."),
            404: openapi.Response(description="Etrap tapylmady."),
        },
    )
    def delete(self, request, pk):
        try:
            region = Region.objects.get(pk=pk)
        except Region.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        region.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
