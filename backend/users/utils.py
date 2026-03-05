from django.contrib.auth.models import BaseUserManager


def normalize_email(email):
    """
    Return a normalized email address.
    'normalize_email' method provided by Django only lowercases domain,
    so in this method the whole email is lowercased.
    """
    return BaseUserManager.normalize_email(email.strip()).lower()
