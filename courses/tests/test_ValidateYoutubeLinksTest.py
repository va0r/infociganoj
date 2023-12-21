from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from courses.validators import ValidateYoutubeLinks


class ValidateYoutubeLinksTest(APITestCase):
    def test_valid_url(self):
        validator = ValidateYoutubeLinks('videos')
        value = {'videos': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'}
        errors = validator(value)
        self.assertEqual(errors, None)

    def test_invalid_url(self):
        validator = ValidateYoutubeLinks('videos')
        value = {'videos': 'https://www.youtobe.com/watch?v=dQw4w9WgXcQ'}

        with self.assertRaises(ValidationError) as context:
            validator(value)

        errors = context.exception.detail
        self.assertTrue(errors)  # Проверяем, что есть ошибка
        self.assertTrue('invalid' in str(errors))  # Проверяем, что ошибка содержит 'invalid'

    def test_empty_value(self):
        validator = ValidateYoutubeLinks('videos')
        value = {}
        errors = validator(value)
        self.assertEqual(errors, None)
