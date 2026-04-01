def is_moderator(user):
    return getattr(user, 'is_moderator', False)
