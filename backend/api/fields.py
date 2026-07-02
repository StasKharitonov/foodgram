import base64
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError('Изображение обязательно')
        if isinstance(data, str) and data.startswith('data:image'):
            try:
                format, imgstr = data.split(';base64,')
                ext = format.split('/')[-1]
                filename = f'{uuid.uuid4()}.{ext}'
                file = ContentFile(base64.b64decode(imgstr), name=filename)
                return super().to_internal_value(file)
            except (ValueError, TypeError, base64.binascii.Error) as e:
                raise serializers.ValidationError(
                    f'Некорректный формат изображения: {e}'
                )
        return super().to_internal_value(data)
