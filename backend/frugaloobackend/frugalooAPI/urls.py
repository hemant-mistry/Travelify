# urls.py
from django.urls import include, path
from rest_framework import routers
from .views import SaveTripDetails,FetchTripDetails, FetchPlan

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('generate-trip/', SaveTripDetails.as_view(), name='generate-trip'),
    path('fetch-trip-details/', FetchTripDetails.as_view(), name='fetch-trip-details' ),
    path('fetch-plan/', FetchPlan.as_view(), name='fetch-plan')
]