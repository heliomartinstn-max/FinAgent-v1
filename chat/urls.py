from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('chat/', views.chat_view, name='chat'),
    path('api/chat/', views.chat_api, name='api'),
]
