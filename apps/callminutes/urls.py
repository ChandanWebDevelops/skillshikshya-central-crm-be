from django.urls import path

from apps.callminutes.views import (
    add_call_minutes, my_call_minutes, CallMinutesTransactionListView,
)

urlpatterns = [
    path('users/me/call-minutes/', my_call_minutes, name='my_call_minutes'),
    path('users/<int:user_id>/call-minutes/add/', add_call_minutes, name='add_call_minutes'),
    path('users/<int:user_id>/call-minutes/transactions/', CallMinutesTransactionListView.as_view(), name='call_minutes_transactions'),
]