import re
from urllib.parse import quote

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers


MENTION_TOKEN_PATTERN = re.compile(r"\{\{mention:(\d+)\}\}")
MAX_MENTION_COUNT = 20


def _ordered_unique_indexes(indexes):
    seen = set()
    ordered = []
    for index in indexes:
        if index in seen:
            continue
        seen.add(index)
        ordered.append(index)
    return ordered


def validate_mentions(*, body, mentions):
    if mentions is None:
        mentions = []

    if not isinstance(mentions, list):
        raise serializers.ValidationError(
            detail={"mentions": "Mentions must be a list of user IDs"},
            code="invalid_mentions",
        )

    if len(mentions) > MAX_MENTION_COUNT:
        raise serializers.ValidationError(
            detail={"mentions": f"Mentions cannot contain more than {MAX_MENTION_COUNT} users"},
            code="too_many_mentions",
        )

    indexes = [int(match.group(1)) for match in MENTION_TOKEN_PATTERN.finditer(body)]
    used_indexes = _ordered_unique_indexes(indexes)

    if len(used_indexes) != len(mentions):
        raise serializers.ValidationError(
            detail="Each mention must be used by at least one mention token",
            code="unused_mention",
        )

    for index in used_indexes:
        if index >= len(mentions):
            raise serializers.ValidationError(
                detail=f"Mention token index {index} does not exist",
                code="mention_index_out_of_range",
            )

    expected_indexes = set(range(len(mentions)))
    if set(used_indexes) != expected_indexes:
        raise serializers.ValidationError(
            detail="Mention token indexes must match the mentions list",
            code="mention_index_mismatch",
        )

    User = get_user_model()
    existing_user_ids = set(
        str(user_id)
        for user_id in User.objects.filter(id__in=mentions).values_list("id", flat=True)
    )
    missing_user_ids = [str(user_id) for user_id in mentions if str(user_id) not in existing_user_ids]
    if missing_user_ids:
        raise serializers.ValidationError(
            detail={"mentions": f"Unknown mentioned users: {', '.join(missing_user_ids)}"},
            code="mentioned_user_not_found",
        )

    return [str(user_id) for user_id in mentions]


def serialize_mentions(mentions):
    User = get_user_model()
    users = {
        str(user.id): user
        for user in User.objects.filter(id__in=mentions)
    }
    return [
        {
            "user_id": str(user_id),
            "username": users[str(user_id)].username,
        }
        for user_id in mentions
        if str(user_id) in users
    ]


def render_body(body, mentions):
    users = serialize_mentions(mentions)

    def replace(match):
        index = int(match.group(1))
        if index >= len(users):
            return match.group(0)

        username = users[index]["username"]
        quoted_username = quote(username)
        return f"[@{username}]({settings.SITE_URL}/users/{quoted_username})"

    return MENTION_TOKEN_PATTERN.sub(replace, body)
