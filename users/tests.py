from django.test import TestCase

from users.models import User


class UserStrMethodTest(TestCase):

    def setUp(self):
        self.user = User(email='test@example.com', phone='123456789', city='Test City', role='MEMBER')

    def test_str_method_returns(self):
        expected_str = 'test@example.com'
        self.assertEqual(str(self.user), expected_str)
