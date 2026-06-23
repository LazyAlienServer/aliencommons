import re
from urllib.parse import quote

from django.conf import settings
from django.contrib.auth import get_user_model

from drf_std_response import ServiceError


H1_RE = re.compile(r"^#(?!#)\s+(.+?)\s*$")
CLOSING_HASHES_RE = re.compile(r"\s+#+\s*$")
MENTION_TOKEN_PATTERN = re.compile(r"\{\{mention:(\d+)}}")
MAX_MENTION_COUNT = 20


def extract_title_from_markdown(markdown, *, max_length=None):
    """
    Return the article title from the first-line H1.
    """
    return validate_article_markdown(markdown, max_length=max_length)


def validate_article_markdown(markdown, *, max_length=None):
    """
    Article markdown must start with exactly one first-level heading.
    """
    lines = markdown.splitlines()
    if not lines:
        raise ServiceError(
            detail="Article markdown must start with a first-level heading.",
            code="invalid_article_markdown",
        )

    first_line_match = H1_RE.match(lines[0])
    if not first_line_match:
        raise ServiceError(
            detail="Article markdown must start with a first-level heading.",
            code="invalid_article_markdown",
        )

    h1_lines = [line for line in lines if H1_RE.match(line)]
    if len(h1_lines) != 1:
        raise ServiceError(
            detail="Article markdown can contain only one first-level heading.",
            code="invalid_article_markdown",
        )

    title = CLOSING_HASHES_RE.sub("", first_line_match.group(1)).strip()
    if not title:
        raise ServiceError(
            detail="Article title cannot be blank.",
            code="invalid_article_markdown",
        )

    if max_length is not None and len(title) > max_length:
        raise ServiceError(
            detail=f"Article title cannot be more than {max_length} characters.",
            code="invalid_article_markdown",
        )

    return title


def _ordered_unique_indexes(indexes):
    seen = set()
    ordered = []
    for index in indexes:
        if index in seen:
            continue
        seen.add(index)
        ordered.append(index)
    return ordered


def validate_markdown_mentions(*, body, mentions):
    if mentions is None:
        mentions = []

    if not isinstance(mentions, list):
        raise ServiceError(
            detail={"mentions": "Mentions must be a list of user IDs"},
            code="invalid_mentions",
        )

    if len(mentions) > MAX_MENTION_COUNT:
        raise ServiceError(
            detail={"mentions": f"Mentions cannot contain more than {MAX_MENTION_COUNT} users"},
            code="too_many_mentions",
        )

    indexes = [int(match.group(1)) for match in MENTION_TOKEN_PATTERN.finditer(body)]
    used_indexes = _ordered_unique_indexes(indexes)

    if len(used_indexes) != len(mentions):
        raise ServiceError(
            detail="Each mention must be used by at least one mention token",
            code="unused_mention",
        )

    for index in used_indexes:
        if index >= len(mentions):
            raise ServiceError(
                detail=f"Mention token index {index} does not exist",
                code="mention_index_out_of_range",
            )

    expected_indexes = set(range(len(mentions)))
    if set(used_indexes) != expected_indexes:
        raise ServiceError(
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
        raise ServiceError(
            detail={"mentions": f"Unknown mentioned users: {', '.join(missing_user_ids)}"},
            code="mentioned_user_not_found",
        )

    return [str(user_id) for user_id in mentions]


def serialize_markdown_mentions(mentions):
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


def render_markdown_mentions(body, mentions):
    users = serialize_markdown_mentions(mentions)

    def replace(match):
        index = int(match.group(1))
        if index >= len(users):
            return match.group(0)

        username = users[index]["username"]
        quoted_username = quote(username)
        return f"[@{username}]({settings.SITE_URL}/users/{quoted_username})"

    return MENTION_TOKEN_PATTERN.sub(replace, body)
