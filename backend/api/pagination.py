from rest_framework.pagination import (
    PageNumberPagination as DRFPageNumberPagination
)


class PageNumberPagination(DRFPageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'
    max_page_size = 100
