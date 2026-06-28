from datetime import datetime

from django.core.exceptions import ValidationError


def namevalidator(value):
    if value.lower() == 'me':
        raise ValidationError(
            'Нельзя использовать "me" в качестве имени.'
        )