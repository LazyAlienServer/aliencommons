from types import SimpleNamespace

from core.pagination import StandardPagination
from core.tests.testcases import BaseTestCase


class StandardPaginationTests(BaseTestCase):
    def test_get_paginated_response_returns_response_with_pagination_data(self):
        paginator = StandardPagination()
        paginator.page = SimpleNamespace(
            paginator=SimpleNamespace(count=21, num_pages=3),
            number=2,
        )
        paginator.request = object()
        paginator.get_page_size = lambda request: 10

        response = paginator.get_paginated_response([{"id": 1}, {"id": 2}])

        self.assertEqual(
            response.data,
            {
                "count": 21,
                "total_pages": 3,
                "current_page": 2,
                "page_size": 10,
                "results": [{"id": 1}, {"id": 2}],
            },
        )
