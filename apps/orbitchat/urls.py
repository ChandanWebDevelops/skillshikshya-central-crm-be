from django.urls import path

from apps.orbitchat.views import sync_state

urlpatterns = [
    path('orbitchat/sync-state/', sync_state, name='orbitchat-sync-state'),
]