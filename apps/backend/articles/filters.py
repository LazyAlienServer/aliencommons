from django_filters import rest_framework as filters
from .models import Article


class ArticleFilter(filters.FilterSet):
    article_status = filters.NumberFilter(field_name='status')

    class Meta:
        model = Article
        fields = ['status']
