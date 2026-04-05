from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import transaction

import secrets
import random
import hashlib

from core.exceptions import ServiceError
from core.utils.cache import add_cache, set_cache, get_cache, delete_cache, incr_cache
from users.models import EmailAddress
from users.tasks import send_verification_email_task
from logs.logging import get_logger

logger = get_logger(__name__)
User = get_user_model()


def _generate_6_digit_code():
    """
    Return a random 6 digits verification code.
    """
    code = f"{secrets.randbelow(1_000_000):06d}"
    return code


def _hash_code(email, code):
    raw = f"{email}:{code}:{settings.SECRET_KEY}"
    return hashlib.blake2b(raw.encode("utf-8")).hexdigest()


def _prepare_verification_code(*, email):
    """
    Generate, store and send the code.
    Another code can only be generated and sent after 60 seconds.
    """
    namespace = 'email_verification'

    # Cooldown check: cannot generate and send another code in 60 seconds
    success = add_cache(
        namespace=namespace, entity='cooldown_check', identifier=email,
        value='60', timeout=settings.VERIFICATION_CODE_RESEND_COOLDOWN
    )
    if not success:
        raise ServiceError(
            detail="Please wait before requesting another code", code='within_verify_cooldown'
        )

    code = _generate_6_digit_code()

    # Generate another code and override the original code
    set_cache(
        namespace=namespace, entity='code', identifier=email,
        value=_hash_code(email, code), timeout=settings.VERIFICATION_CODE_TTL
    )
    set_cache(
        namespace=namespace, entity='attempts', identifier=email,
        value=0, timeout=settings.VERIFICATION_CODE_TTL
    )

    return {
        "to_email": email,
        "code": code,
        "resend_cooldown_seconds": settings.VERIFICATION_CODE_RESEND_COOLDOWN,
        "code_ttl_seconds": settings.VERIFICATION_CODE_TTL,
    }


@transaction.atomic
def register(*, username, email, password):
    """
    Register a new user.
    """
    def pick_random_avatar():
        avatar = random.choice(settings.DEFAULT_AVATARS)
        return avatar

    user = User(
        username=username,
        avatar=pick_random_avatar(),
    )

    user.set_password(password)
    user.save()

    email_address = EmailAddress.objects.create(
        user=user,
        email=email,
        is_verified=False,
        is_primary=True,
    )

    result = _prepare_verification_code(email=email_address.email)

    # Email is only sent when the transaction is finished
    transaction.on_commit(
        lambda: send_verification_email_task.enqueue(
            to_email=result['to_email'],
            code=result['code'],
        )
    )

    logger.info(f"User {user.id} successfully registered")

    return {
        "user_id": user.id,
        "username": user.username,
        "email": email_address.email,
        "email_verified": email_address.is_verified,
        "resend_cooldown_seconds": result.get("resend_cooldown_seconds"),
        "code_ttl_seconds": result.get("code_ttl_seconds"),
    }


def _get_locked_email_address(user, email):
    """
    Return a locked EmailAddress for business logic.
    If the EmailAddress does not exist, a ServiceError will be raised.
    """
    try:
        email_address = EmailAddress.objects.select_for_update().get(
            user=user, email=email
        )
        return email_address

    except EmailAddress.DoesNotExist:
        raise ServiceError(
            detail="Email address not found", code='email_address_not_found'
        )


@transaction.atomic
def verify_email(*, user, email, code):
    """
    Verify a email verification code.
    """
    namespace = 'email_verification'
    email_address = _get_locked_email_address(user, email)
    stored_code = get_cache(
        namespace=namespace, entity='code', identifier=email
    )

    if not stored_code:
        raise ServiceError(
            detail="The verification code is either expired or not sent", code='code_not_found'
        )

    if stored_code != _hash_code(email, code):
        attempts = incr_cache(
            namespace=namespace, entity="attempts", identifier=email, delta=1, timeout=600
        )
        if attempts >= settings.MAX_VERIFICATION_ATTEMPTS:
            raise ServiceError(
                detail="Maximum number of attempts reached",
                code="max_attempts_reached",
            )
        raise ServiceError(
            detail="Incorrect verification code", code='incorrect_code'
        )

    if not email_address.is_verified:
        email_address.is_verified = True
        email_address.save(update_fields=["is_verified"])

    if not user.is_email_verified:
        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])

    delete_cache(namespace=namespace, entity='code', identifier=email)
    delete_cache(namespace=namespace, entity="cooldown_check", identifier=email)

    logger.info(f"Email {email} successfully verified")

    return {
        "email": email_address.email
    }
