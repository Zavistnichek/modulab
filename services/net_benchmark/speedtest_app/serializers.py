from rest_framework import serializers
from .models import SpeedTestResult


class SpeedTestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeedTestResult
        fields = "__all__"
