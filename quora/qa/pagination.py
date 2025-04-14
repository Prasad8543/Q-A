from rest_framework.pagination import CursorPagination
from rest_framework.response import Response

class CursorSetPagination(CursorPagination):
    ordering = "id" 
    page_size_query_param = 'page_size'
    page_size = 10 


    def get_paginated_response(self, data):
        next_url = self.get_next_link()
        previous_url = self.get_previous_link() if self.page else None
        headers = {'Prev': previous_url, 'Next': next_url, 'Page-Size': self.page_size}

        return Response(data, headers=headers)