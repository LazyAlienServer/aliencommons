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
        default=timezone.now, db_index=True, editable=False
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
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)


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

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        update_fields = ['is_deleted']

        # If 'TimeStampedMixin' is used
        if hasattr(self, 'updated_at'):
            update_fields.append('updated_at')

        self.save(update_fields=update_fields)

    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)

    def restore(self, using=None):
        self.is_deleted = False
        update_fields = ['is_deleted']

        # If 'TimeStampedMixin' is used
        if hasattr(self, 'updated_at'):
            update_fields.append('updated_at')

        self.save(update_fields=update_fields, using=using)

    class Meta:
        abstract = True
