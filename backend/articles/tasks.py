from django.conf import settings
from django.utils import timezone
from django.tasks import task

from pathlib import Path
from urllib.parse import urlparse

from articles.models import SourceArticle


def _extract_media_relpaths_from_tiptap(doc):
    """
    Extract relative storage paths from TipTap JSON doc.
    Example src:
      - "/media/article_images/2026/01/xx.webp"
      - "http://localhost:8000/media/article_images/2026/01/xx.webp"
    Return:
      - "article_images/2026/01/xx.webp"
    """
    media_url = settings.MEDIA_URL.rstrip("/") + "/"
    relpaths = set()

    def normalize_src(src):
        if not src:
            return None

        # absolute url -> take path part
        if src.startswith("http://") or src.startswith("https://"):
            src = urlparse(src).path  # "/media/xxx"

        # only handle MEDIA_URL files
        if not src.startswith(media_url):
            return None

        return src[len(media_url):]  # strip "/media/" -> "article_images/..."

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "image":
                attrs = node.get("attrs") or {}
                src = attrs.get("src")
                rel = normalize_src(src)
                if rel:
                    relpaths.add(rel)

            for v in node.values():
                walk(v)

        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(doc)
    return relpaths


def _iter_article_image_files():
    """
    Iterate all files under MEDIA_ROOT/article_images recursively.
    Only for local FileSystemStorage (your current setup).
    """
    root = Path(settings.MEDIA_ROOT) / "article_images"
    if not root.exists():
        return []
    return (p for p in root.rglob("*") if p.is_file())


@task
def cleanup_unreferenced_article_images(grace_days=1):
    """
    Delete article_images/* files that are not referenced by any SourceArticle.content.

    grace_days:
      - Only delete files older than N days to avoid removing images uploaded
        but not yet saved into content (or in-flight edits).
    """
    # 1) Build a set of all referenced storage-relative paths
    referenced = set()

    qs = SourceArticle.objects.filter(is_deleted=False).values_list("content", flat=True)
    for content in qs:
        if not content:
            continue
        # content is a JSONField dict
        referenced |= _extract_media_relpaths_from_tiptap(content)

    # 2) Walk media/article_images and delete unreferenced, older-than-grace files
    deleted = 0
    kept = 0
    skipped_recent = 0

    cutoff = timezone.now().timestamp() - grace_days * 24 * 3600

    for file_path in _iter_article_image_files():
        # Convert absolute file path -> storage-relative path (under MEDIA_ROOT)
        rel_to_media = file_path.relative_to(settings.MEDIA_ROOT).as_posix()  # "article_images/..."
        if rel_to_media in referenced:
            kept += 1
            continue

        # grace period
        try:
            mtime = file_path.stat().st_mtime
        except OSError:
            continue

        if mtime > cutoff:
            skipped_recent += 1
            continue

        try:
            file_path.unlink(missing_ok=True)
            deleted += 1
        except OSError:
            # ignore failures, report counts only
            pass

    return {
        "referenced_count": len(referenced),
        "deleted": deleted,
        "kept": kept,
        "skipped_recent": skipped_recent,
        "grace_days": grace_days,
    }
