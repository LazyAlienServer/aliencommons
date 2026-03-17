from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return {
            "count": self.page.paginator.count,
            "total_pages": self.page.paginator.num_pages,
            "current_page": self.page.number,
            "page_size": self.get_page_size(self.request),
            "results": data
        }
