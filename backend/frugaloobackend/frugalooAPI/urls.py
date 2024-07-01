# urls.py
from django.urls import include, path
from rest_framework import routers
from .views import GenerateMessageView

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('generate-message/', GenerateMessageView.as_view(), name='generate-message')
    
]