from django.db import models
from django.utils.translation import gettext_lazy as _

import uuid


class CreatedAtMixin(models.Model):
    """
    Provide 'created_at' fields for models.
    """
    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True, editable=False,
        verbose_name=_("created at"),
        help_text=_("The created DateTime of the object"),
    )

    class Meta:
        abstract = True


class TimeStampedMixin(models.Model):
    """
    Provide 'created_at' and 'updated_at' fields for models.
    """
    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True, editable=False,
        verbose_name=_("created at"),
        help_text=_("The created DateTime of the object"),
    )
    updated_at = models.DateTimeField(
        auto_now=True, db_index=True,
        verbose_name=_("updated at"),
        help_text=_("The updated DateTime of the object"),
    )

    class Meta:
        abstract = True


class UUIDPrimaryKeyMixin(models.Model):
    """
    Provide UUID as the primary key for models.
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False,
        verbose_name=_("ID"),
        help_text=_("The UUID of the object"),
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
        default=False, db_index=True,
        verbose_name=_("deleted"),
        help_text=_("Whether the object is deleted"),
    )

    objects = SoftDeleteManager()
    all_objects = SoftDeleteQuerySet.as_manager()

    class Meta:
        abstract = True
