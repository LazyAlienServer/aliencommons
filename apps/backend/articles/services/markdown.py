import re

from core.exceptions import ServiceError


H1_RE = re.compile(r"^#(?!#)\s+(.+?)\s*$")
CLOSING_HASHES_RE = re.compile(r"\s+#+\s*$")


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
