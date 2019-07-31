from django.contrib.auth import get_user_model

from config import celery_app

from .utils import send_simple_template_mail

User = get_user_model()


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


@celery_app.task
def send_bulk_mail(user_ids, subject, body):
    chunks = chunker(user_ids, 200)
    for chunk in chunks:
        users = User.objects.filter(id__in=chunk)
        for user in users:
            send_simple_template_mail(
                user, subject, body,
                priority=False
            )
