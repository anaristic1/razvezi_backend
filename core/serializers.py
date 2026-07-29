from rest_framework import serializers
from .models import Route, RouteStatusHistory


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = "__all__"
        read_only_fields = ['created_by']

class RouteStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteStatusHistory
        fields = "__all__"
        read_only_fields = ['changed_at']
