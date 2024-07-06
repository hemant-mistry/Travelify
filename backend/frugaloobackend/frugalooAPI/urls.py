# urls.py
from django.urls import include, path
from rest_framework import routers
from .views import GenerateMessageView,SaveTripDetails

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('generate-message/', GenerateMessageView.as_view(), name='generate-message'),
    path('save-trip-details/', SaveTripDetails.as_view(), name='save-trip-details')
    
]