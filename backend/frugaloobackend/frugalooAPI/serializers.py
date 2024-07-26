# serializers.py (or any appropriate file in your Django app)

from rest_framework import serializers
from .models import UserTripInfo, UserTripProgressInfo, FinanceLog


class UserTripInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTripInfo
        fields = "__all__"  # Serialize all fields in the UserTripInfo model


class GeneratedPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTripInfo
        fields = ['generated_plan']

class UserTripProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTripProgressInfo
        fields = ["day"]


class FinanceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinanceLog
        fields = '__all__'
