from django.urls import path
from . import views

urlpatterns = [
    path('async-stream/', views.async_streaming_view, name='async_streaming_view'),
]