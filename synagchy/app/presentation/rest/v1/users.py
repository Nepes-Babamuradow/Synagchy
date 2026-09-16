from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.db.models import Sum

from app.infrastructure.database.models import User, ExamResult
from app.presentation.rest.v1.serializers import (
    UserSerializer, RatingSerializer, MyUniversitySerializer, ProfileSerializer,
)
from app.presentation.rest.v1.pagination import StandardPagination, PAGE_PARAMS, paginate


def _get_user_rating_stats(user):
    """
    Ulanyjynyň reýtingini we jemi wagtyny hasaplaýar.
    Reýting = ähli testleriň (dogrylyk baly + wagt bonusy) jemi.
    Wagt bonusy: iň köp +10, her minut üçin 1 bal azalýar.
    """
    total_rating = 0
    total_duration = 0
    for result in ExamResult.objects.filter(user=user):
        duration_minutes = result.duration_seconds / 60.0
        time_bonus = max(0, 10 - duration_minutes)
        test_rating = min(100, round(result.score + time_bonus))
        total_rating += test_rating
        total_duration += result.duration_seconds
    return total_rating, total_duration


class UserListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description=(
            "Ähli ulanyjylaryň sanawyny reýting boýunça(sorted by rating) getirýır. "
            "Paginated response: count, next, previous, results. "
            "Her ulanyjy: id, username, email, first_name, last_name, full_name, phone, rating, subscription_rank, "
            "specialty_name, faculty_name, university_name, region, region_name."
        ),
        manual_parameters=PAGE_PARAMS,
        responses={
            200: openapi.Response(
                description="Üstünlikli. Ulanyjylar reýting boýunça göni görnüşde sortirlen.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER, description="Jemi ulanyjy sany"),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True, description="Indiki sahypa URL"),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True, description="Öňki sahypa URL"),
                        'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT), description="Ulanyjylar listi"),
                    },
                ),
            ),
        },
    )
    def get(self, request):
        users_with_stats = []
        for user in User.objects.all():
            rating, total_duration = _get_user_rating_stats(user)
            users_with_stats.append((user, rating, total_duration))
        users_with_stats.sort(key=lambda x: (-x[1], x[2], x[0].id))

        pg = StandardPagination()
        page = pg.paginate_queryset([u[0] for u in users_with_stats], request, view=self)
        serializer = UserSerializer(page, many=True)
        return pg.get_paginated_response(serializer.data)


class UserDetailView(APIView):
    @swagger_auto_schema(
        operation_description=(
            "ID boýunça bir ulanyjynyň jikme-jig maglumatlaryny getirýır. "
            "first_name (at), last_name (familiýa), region (etrap) hem görkezilýär. "
            "Eger ulanyjynyň hünäri bar bolsa, onuň hünär, fakultet we uniwersitet adlary hem gaty gelýır."
        ),
        responses={
            200: openapi.Response(description="Üstünlikli. Ulanyjynyň doly maglumatlary."),
            404: openapi.Response(description="Ulanyjy tapylmady."),
        },
    )
    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(UserSerializer(user).data)

    def _get_user_or_404(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    @swagger_auto_schema(
        request_body=UserSerializer,
        operation_description=(
            "Ulanyjynyň maglumatlaryny doly redaktirleýır (PUT). "
            "Diňe özüňiz ýa-da admin (staff) ulanyjylary redaktirleýır. "
            "Ähli meýdanlar (username, email, first_name, last_name, phone, specialty, region) hökmany."
        ),
        responses={
            200: openapi.Response(description="Üstünlikli redaktirleme. Täzelenen ulanyjy maglumatlary."),
            400: openapi.Response(description="Nädogry maglumat. Serializer validasiýasyna laýyk däl."),
            403: openapi.Response(description="Rugsat ýok. Diňe ulanyjy özi ýa-da admin redaktirleýır."),
            404: openapi.Response(description="Ulanyjy tapylmady."),
        },
    )
    def put(self, request, pk):
        return self._update(request, pk, partial=False)

    @swagger_auto_schema(
        request_body=UserSerializer,
        operation_description=(
            "Ulanyjynyň maglumatlarynyň bir bölegini redaktirleýır (PATCH). "
            "Diňe özüňiz ýa-da admin (staff) ulanyjylary redaktirleýır. "
            "Üýtgetmek isleýän meýdanlaryňyzy iberiň, beýlekiler galýar."
        ),
        responses={
            200: openapi.Response(description="Üstünlikli redaktirleme. Täzelenen ulanyjy maglumatlary."),
            400: openapi.Response(description="Nädogry maglumat."),
            403: openapi.Response(description="Rugsat ýok."),
            404: openapi.Response(description="Ulanyjy tapylmady."),
        },
    )
    def patch(self, request, pk):
        return self._update(request, pk, partial=True)

    def _update(self, request, pk, partial=False):
        user = self._get_user_or_404(pk)
        if user is None:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        if request.user != user and not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserSerializer(user, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RatingListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description=(
            "Ulanyjylaryň reýting tablisasyny getirýır. Reýting ulanyjynyň ähli synag netijelerinden hasaplanýar: "
            "her testiň dogrylyk baly (0-100) + wagt bonusy (iň köp +10, test näçe çalt gutalsa şonça köp). "
            "Deň reýtingde jemi wagt az bolan ulanyjy öňde. "
            "Top 3-e ýerleşen ulanyjylara abuna alanda yenillik berilýär: 1-nji orun - 50%, 2-nji orun - 30%, 3-nji orun - 20%. "
            "Paginated response: count, next, previous, results. Her zatda rank we discount (yenillik) meýdanlary bar. "
            "first_name (at), last_name (familiýa), region we region_name görkezilýär."
        ),
        manual_parameters=PAGE_PARAMS,
        responses={
            200: openapi.Response(
                description="Üstünlikli. Reýting tablisasy (öň ýa-da soňky sahypa bilen).",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER, description="Jemi ulanyjy sany"),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True),
                        'results': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'username': openapi.Schema(type=openapi.TYPE_STRING),
                                    'specialty': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True),
                                    'specialty_name': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                                    'faculty_name': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                                    'university_name': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                                    'region': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True, description="Etrap ID-si"),
                                    'region_name': openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description="Etrap ady"),
                                    'first_name': openapi.Schema(type=openapi.TYPE_STRING, description="Ulanyjynyň ady (at)"),
                                    'last_name': openapi.Schema(type=openapi.TYPE_STRING, description="Ulanyjynyň familýasy"),
                                    'full_name': openapi.Schema(type=openapi.TYPE_STRING, description="Doly ady"),
                                    'phone': openapi.Schema(type=openapi.TYPE_STRING),
                                    'rating': openapi.Schema(type=openapi.TYPE_INTEGER, description="Ulanyjynyň reýtingi (dogrylyk baly + wagt bonusy jemi)"),
                                    'total_duration_seconds': openapi.Schema(type=openapi.TYPE_INTEGER, description="Ähli testleriň jemi dowamlylygy (sekunt)"),
                                    'subscription_rank': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'rank': openapi.Schema(type=openapi.TYPE_INTEGER, description="Orun (1,2,3,...)"),
                                    'discount': openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description="Yenillik (50%, 30%, 20%)"),
                                },
                            ),
                        ),
                    },
                ),
            ),
        },
    )
    def get(self, request):
        users_with_stats = []
        for user in User.objects.all():
            rating, total_duration = _get_user_rating_stats(user)
            users_with_stats.append((user, rating, total_duration))

        # Reýting boýunça aşak, deň bolanda jemi wagt boýunça ýokary (çalt gutaran öňde)
        users_with_stats.sort(key=lambda x: (-x[1], x[2], x[0].id))

        pg = StandardPagination()
        page = pg.paginate_queryset(users_with_stats, request, view=self)

        try:
            page_num = int(request.query_params.get('page', 1))
        except Exception:
            page_num = 1
        page_size = pg.get_page_size(request) or pg.page_size
        offset = (page_num - 1) * page_size

        data = []
        for i, (user, rating, total_duration) in enumerate(page):
            specialty = getattr(user, 'specialty', None)
            faculty = getattr(specialty, 'faculty', None) if specialty else None
            university = getattr(faculty, 'university', None) if faculty else None
            region = getattr(user, 'region', None)

            item = {
                'id': user.id,
                'username': user.username,
                'specialty': specialty.id if specialty else None,
                'specialty_name': specialty.name if specialty else None,
                'faculty_name': faculty.name if faculty else None,
                'university_name': university.name if university else None,
                'region': region.id if region else None,
                'region_name': region.name if region else None,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.full_name,
                'phone': user.phone,
                'rating': rating,
                'total_duration_seconds': total_duration,
                'subscription_rank': getattr(user, 'subscription_rank', None),
            }

            rank = offset + i + 1
            item['rank'] = rank
            item['discount'] = {1: '50%', 2: '30%', 3: '20%'}.get(rank, None)
            data.append(item)

        return pg.get_paginated_response(data)


class MyUniversityView(APIView):
    """
    Ulanyjynyň hünärine (specialty) görä:
    uniwersiteti, fakulteti we hünäri görkezýär.
    """
    @swagger_auto_schema(
        operation_description=(
            "Token bilen (Authorization: Bearer <access_token>) ulanyjy özüniň hünärine görä "
            "bagly uniwersitet, fakultet, hünär, at, familýa we etrap (region) maglumatlaryny getirýır. "
            "Bu endpoint ulanyjynyň profil sahypasynda görkezme üçin ulanýar."
        ),
        responses={
            200: openapi.Response(
                description="Üstünlikli. Ulanyjynyň hünär, fakultet, uniwersitet we etrap maglumatlary.",
                schema=MyUniversitySerializer(),
            ),
            404: openapi.Response(description="Ulanyjynyň hünäri kesgitlenmedik. Öň hünär saýlamaly."),
            401: openapi.Response(description="Token ýok ýa-da ýalňyş."),
        },
    )
    def get(self, request):
        user = request.user

        if not user.specialty:
            return Response(
                {'error': 'Bu ulanyjynyň hünäri kesgitlenmedik.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        specialty = user.specialty
        faculty = specialty.faculty
        university = faculty.university
        region = getattr(user, 'region', None)

        return Response({
            'user': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'specialty': {
                'id': specialty.id,
                'name': specialty.name,
                'description': specialty.description,
            },
            'faculty': {
                'id': faculty.id,
                'name': faculty.name,
                'description': faculty.description,
            },
            'university': {
                'id': university.id,
                'name': university.name,
                'city': university.city,
                'description': university.description,
            },
            'region': {
                'id': region.id,
                'name': region.name,
                'description': region.description,
            } if region else None,
        }, status=status.HTTP_200_OK)


class ProfileView(APIView):
    """
    Ulanyjynyň profil maglumatlaryny view/edit etmek üçin.
    GET: profil maglumatlary
    PUT/PATCH: profil redaktirleme (at, familiýa, telefon, etrap)
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description=(
            "Token bilen (Authorization: Bearer <access_token>) ulanyjynyň profil maglumatlaryny getirýär. "
            "Ähli meýdanlar: username, email, first_name (at), last_name (familiýa), phone (telefon), "
            "region (etrap), region_name, full_name (doly ady), rating, subscription_rank."
        ),
        responses={
            200: openapi.Response(
                description="Üstünlikli. Ulanyjynyň profil maglumatlary.",
                schema=ProfileSerializer(),
            ),
            401: openapi.Response(description="Token ýok ýa-da ýalňyş."),
        },
    )
    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=ProfileSerializer,
        operation_description=(
            "Ulanyjynyň profil maglumatlaryny doly redaktirleýär (PUT). "
            "Diňe özüňiz ulanyp biler. "
            "Ütgetmek isleýän meýdanlar: first_name (at), last_name (familiýa), phone (telefon), region (etrap). "
            "username, email we beýlekiler redaktirlemeýär."
        ),
        responses={
            200: openapi.Response(description="Üstünlikli redaktirleme. Täzelenen profil maglumatlary."),
            400: openapi.Response(description="Nädogry maglumat. Serializer validasiýasyna laýyk däl."),
            401: openapi.Response(description="Token ýok ýa-da ýalňyş."),
        },
    )
    def put(self, request):
        user = request.user
        serializer = ProfileSerializer(user, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=ProfileSerializer,
        operation_description=(
            "Ulanyjynyň profil maglumatlarynyň bir bölegini redaktirleýär (PATCH). "
            "Diňe özüňiz ulanyp biler. "
            "Ütgetmek isleýän meýdanlar: first_name (at), last_name (familiýa), phone (telefon), region (etrap). "
            "Diňe şol meýdanlary iberiň, beýlekiler galýar."
        ),
        responses={
            200: openapi.Response(description="Üstünlikli redaktirleme. Täzelenen profil maglumatlary."),
            400: openapi.Response(description="Nädogry maglumat."),
            401: openapi.Response(description="Token ýok ýa-da ýalňyş."),
        },
    )
    def patch(self, request):
        user = request.user
        serializer = ProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
