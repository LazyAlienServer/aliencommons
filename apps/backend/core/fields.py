from rest_framework import serializers
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_naive

from datetime import datetime


class FlexibleDateTimeField(serializers.DateTimeField):
    """
    宽松的 DateTime 解析：
    - 支持 Z 结尾（UTC）
    - 支持 +00:00 时区偏移
    - 支持无毫秒/无时区的时间

    爱来自ChatGPT-4o
    """
    def to_internal_value(self, value):
        # 如果本身是 datetime，直接返回
        if isinstance(value, datetime):
            return value

        # 使用 Django 内置 parse_datetime
        parsed = parse_datetime(value)
        if parsed is None:
            raise serializers.ValidationError(f"Invalid datetime format: {value}")

        # 如果是 naive（没有时区），默认转为 UTC
        if is_naive(parsed):
            parsed = make_aware(parsed)

        return parsed

    def to_representation(self, value):
        # 返回 ISO8601 格式，带 Z
        return value.astimezone().isoformat().replace("+00:00", "Z")
