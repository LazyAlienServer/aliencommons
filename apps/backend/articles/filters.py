from django_filters import rest_framework as filters
from .models import SourceArticle


class SourceArticleFilter(filters.FilterSet):
    article_status = filters.NumberFilter(field_name='status')

    class Meta:
        model = SourceArticle
        fields = ['status']
