from django.test import TestCase
from django.core.cache import cache
from rest_framework.test import APITestCase

from .mixins import (
    APIClientMixin,
    StandardResponseAssertionsMixin,
    UUIDAssertionsMixin,
)


class BaseTestCase(UUIDAssertionsMixin,
                   TestCase):
    """
    Base class for model and service tests.
    """
    def _pre_setup(self):
        super()._pre_setup()
        cache.clear()


class BaseAPITestCase(UUIDAssertionsMixin,
                      StandardResponseAssertionsMixin,
                      APIClientMixin,
                      APITestCase,):
    """
    Base class for API tests.
    """
    def _pre_setup(self):
        super()._pre_setup()
        cache.clear()
