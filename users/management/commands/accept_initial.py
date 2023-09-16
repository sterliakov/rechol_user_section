import os
import secrets
import string
from pathlib import Path

from django.core.mail import send_mail
from django.core.management import BaseCommand

ALPHABET = string.ascii_letters + string.digits
PASSWORD_LENGTH = 12
MAIL_TOPIC = 'ПХО: Пароль для входа в личный кабинет'
with (Path(__file__).parent / 'message.txt').open() as file:
    MAIL_CONTENT = file.read()


class Command(BaseCommand):
    help = 'Send password to users from external source'

    def handle(self, *_args, **_options):
        from users.models import User

        need_message = User.objects.filter(password='')
        for user in need_message:
            password = ''.join(secrets.choice(ALPHABET) for i in range(PASSWORD_LENGTH))
            user.set_password(password)
            user.save()
            send_mail(
                MAIL_TOPIC,
                MAIL_CONTENT.format(
                    password=password,
                    email=user.email,
                    name=str(user),
                    suffix=('ый' if user.gender == 'm' else 'ая'),
                    SERVER_NAME=os.getenv('SERVER_NAME', 'localhost'),
                ),
                None,
                [user.email],
            )
