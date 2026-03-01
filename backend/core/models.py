from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import uuid


class TimeStampedMixin(models.Model):
    """
    Provide 'created_at' and 'updated_at' fields for models.
    """
    created_at = models.DateTimeField(
        verbose_name=_("created at"),
        auto_now_add=True, db_index=True, editable=False
    )
    updated_at = models.DateTimeField(
        verbose_name=_("updated at"),
        auto_now=True, db_index=True
    )

    class Meta:
        abstract = True


class UUIDPrimaryKeyMixin(models.Model):
    """
    Provide UUID as the primary key for models.
    """
    id = models.UUIDField(
        verbose_name=_("ID"),
        primary_key=True, default=uuid.uuid4, editable=False
    )

    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.QuerySet):
    """
    Provide a queryset with soft delete functionality.
    """
    def delete(self, using=None, keep_parents=False):
        # Override 'queryset.delete()' with soft delete
        return super().update(is_deleted=True)

    def hard_delete(self):
        # Reserve the hard delete entrance
        return super().delete()

    def alive(self):
        return self.filter(is_deleted=False)

    def dead(self):
        return self.filter(is_deleted=True)


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).alive()


class SoftDeleteMixin(models.Model):
    """
    Provide 'is_deleted' field and soft delete functionality for models.
    """
    # Corresponds to 'self.filter(is_deleted=True)'
    is_deleted = models.BooleanField(
        verbose_name=_("deleted"),
        default=False, db_index=True
    )

    objects = SoftDeleteManager()
    all_objects = SoftDeleteQuerySet.as_manager()

    class Meta:
        abstract = True
