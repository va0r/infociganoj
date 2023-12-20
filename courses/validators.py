import re

from rest_framework.serializers import ValidationError


class ValidateYoutubeLinks:
    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        reg = re.compile(r'^https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+')
        field_value = value.get(self.field)
        if field_value is not None and not reg.match(field_value):
            raise ValidationError('Материалы могут содержать только ссылки на видео с YouTube.')
