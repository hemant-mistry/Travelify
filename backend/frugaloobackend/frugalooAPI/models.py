from django.db import models
import uuid

#User's trip information model
class UserTripInfo(models.Model):
    trip_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user_id = models.CharField(max_length=255)
    stay_details = models.CharField(max_length=255)
    number_of_days = models.IntegerField()
    budget = models.IntegerField()
    additional_preferences = models.CharField(max_length=255)
    generated_plan = models.TextField()

