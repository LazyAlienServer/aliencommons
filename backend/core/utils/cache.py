from django.core.cache import cache


def _get_key(namespace, entity, identifier):
    """
    Generate a standard cache key. All cache keys should be generated using this function.
    e.g. key("article", "slug", slug) -> "article:slug:name-of-the-article"
    """
    key = f"{namespace}:{entity}:{identifier}"

    return key


def get_cache(*, namespace, entity, identifier):
    """
    Retrieve a value using the corresponding key.
    """
    key = _get_key(namespace, entity, identifier)

    return cache.get(key)


def add_cache(*, namespace, entity, identifier, value, timeout=None):
    """
    Only add a key-value pair when the key does not exist.
    Return True or False.
    """
    key = _get_key(namespace, entity, identifier)

    return cache.add(key, value, timeout=timeout)


def set_cache(*, namespace, entity, identifier, value, timeout=None):
    """
    Set a key-value pair, no matter whether the key exists.
    You usually do not need the return value.
    """
    key = _get_key(namespace, entity, identifier)

    return cache.set(key, value, timeout=timeout)


def delete_cache(*, namespace, entity, identifier):
    """
    Delete a key-value pair.
    Return True or False.
    """
    key = _get_key(namespace, entity, identifier)

    return cache.delete(key)


def get_or_set_cache(*, namespace, entity, identifier, creator, timeout=None):
    """
    Retrieves a key value from the cache and sets the value if it does not exist.
    "Cache Aside Pattern"
    """
    key = _get_key(namespace, entity, identifier)
    return cache.get_or_set(key, creator, timeout=timeout)


def delete_cache_pattern(*, namespace, entity, identifier, version=None):
    """
    Delete keys matching pattern 'namespace:entity:identifier' (identifier may include wildcards)
    """
    key = _get_key(namespace, entity, identifier)

    return cache.delete_pattern(key, version=version)
