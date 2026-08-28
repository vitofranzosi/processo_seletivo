from contextlib import contextmanager

from django.db import transaction
from django.utils import timezone


@contextmanager
def command_context():
    with transaction.atomic():
        yield timezone.now()


def after_commit(callback) -> None:
    transaction.on_commit(callback)
