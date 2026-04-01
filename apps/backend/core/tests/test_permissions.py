from types import SimpleNamespace

from core.tests.testcases import BaseTestCase
from core.utils.permissions import is_moderator


class PermissionUtilsTests(BaseTestCase):
    def test_is_moderator_returns_true_for_moderator_like_object(self):
        user = SimpleNamespace(is_moderator=True)

        self.assertTrue(is_moderator(user))

    def test_is_moderator_returns_false_when_flag_missing(self):
        user = SimpleNamespace()

        self.assertFalse(is_moderator(user))

    def test_is_moderator_returns_false_when_flag_is_false(self):
        user = SimpleNamespace(is_moderator=False)

        self.assertFalse(is_moderator(user))
