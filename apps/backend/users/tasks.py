from django.conf import settings
from django.core.mail import send_mail
from django.tasks import task

from logs.logging.logger import get_logger

logger = get_logger(__name__)


@task(queue_name='email')
def send_verification_email_task(*, to_email, code):
    """
    Send a verification email.
    """
    send_mail(
        subject="Your Verification Code",
        message=f"Your verification code is {code}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to_email],
        fail_silently=False,
    )
    logger.info(f"Email sent to {to_email}")
