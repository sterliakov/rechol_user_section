from __future__ import annotations

import os
import secrets
import string
from typing import TYPE_CHECKING

from django.core.mail import send_mail
from django.core.management import BaseCommand

if TYPE_CHECKING:
    from argparse import ArgumentParser

ALPHABET = string.ascii_letters + string.digits
PASSWORD_LENGTH = 12
MAIL_TOPIC = "ПХО: Пароль для входа в личный кабинет"
MAIL_CONTENT = """Аккаунт администратора создан.

Данные для входа:

email: {email}
password: {password}

Личный кабинет расположен по адресу:
https://{SERVER_NAME}/profile/update/

Страницы администратора:
https://{SERVER_NAME}/master/admin/
"""


class Command(BaseCommand):
    help = "Send password to new admins"

    def add_arguments(self, parser: ArgumentParser):
        super().add_arguments(parser)
        parser.add_argument("email")

    def handle(self, *_args, **options):
        from users.models import User

        email = options["email"]

        password = "".join(secrets.choice(ALPHABET) for _ in range(PASSWORD_LENGTH))
        user = User.objects.create_superuser(email, password)
        send_mail(
            MAIL_TOPIC,
            MAIL_CONTENT.format(
                password=password,
                email=user.email,
                SERVER_NAME=os.getenv("SERVER_NAME", "localhost"),
            ),
            None,
            [user.email],
        )
