from django.db import models


#User's trip information model
class UserTripInfo(models.Model):
    user_id = models.CharField(max_length=255)
    stay_details = models.CharField(max_length=255)
    number_of_days = models.IntegerField()
    budget = models.IntegerField()
    additional_preferences = models.CharField(max_length=255)

    