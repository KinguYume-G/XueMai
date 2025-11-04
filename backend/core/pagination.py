"""
自定义分页类
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'limit'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'data': data,
            'paging': {
                'count': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'page_size': self.page_size
            },
            'error': None
        })

