# serializers.py (or any appropriate file in your Django app)

from rest_framework import serializers
from .models import UserTripInfo


class UserTripInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTripInfo
        fields = "__all__"  # Serialize all fields in the UserTripInfo model


class GeneratedPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTripInfo
        fields = ["generated_plan"]
