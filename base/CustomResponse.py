from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.http import *

from base.status_text import status_texts


class CustomResponse(Response):
    def __init__(self, data=None, status_code=status, message=None):
        status_code = self.normalize_status_code(status_code)
        super().__init__(
            self.normalize_content(data, status_code, message),
            status_code
        )

    def normalize_content(self, data, status_code, message):
        body = {
            'error': not status.is_success(status_code),
            'message': message or status_texts.get(status_code),
            'code': status_code,
            'data': data
        }

        return {**body}

    def normalize_status_code(self, status_code):
        if not isinstance(status_code, int):
            raise ValidationError(f'{status_code} must be an integer')

        if 100 <= status_code < 600:
            return status_code

        return status.HTTP_500_INTERNAL_SERVER_ERROR

    @classmethod
    def collection(cls, content, status_code=status.HTTP_200_OK, message=None):
        return cls(content, status_code, message)

    @classmethod
    def item(cls, data=None, status_code=status.HTTP_200_OK, message=None):
        if not data and status_code == status.HTTP_200_OK:
            return cls(status_code=status.HTTP_404_NOT_FOUND)

        return cls(data, status_code, message)

    @classmethod
    def updated(cls, content, message=None):
        return cls.item(content, status.HTTP_202_ACCEPTED, message)

    @classmethod
    def stored(cls, content, message=None):
        return cls.item(content, status.HTTP_201_CREATED, message)

    @classmethod
    def destroyed(cls, content, message):
        return cls.updated(content, message)
