from rest_framework.pagination import PageNumberPagination
from drf_yasg import openapi


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


PAGE_PARAMS = [
    openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                      description='Sahypa belgisi (1-den başlap)'),
    openapi.Parameter('page_size', openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                      description='Bir sahypadaky element sany (default 20)'),
]


def paginate(qs, request, view):
    """Paginated response gaýtarýar."""
    pg = StandardPagination()
    page = pg.paginate_queryset(qs, request, view=view)
    return pg, page
