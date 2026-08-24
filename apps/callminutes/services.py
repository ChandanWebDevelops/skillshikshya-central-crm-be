import math

from django.contrib.auth import get_user_model
from django.db import transaction

from rest_framework.exceptions import ValidationError

from apps.callminutes.models import CallMinutesTransaction

User = get_user_model()


def minutes_for_duration(duration_seconds):
    try:
        seconds = int(duration_seconds or 0)
    except (TypeError, ValueError):
        seconds = 0
    return max(1, math.ceil(seconds / 60))


def charge_minutes_for_call(user, duration_seconds, create_call):
    """
    Atomically check the user's balance, create the call via `create_call()`,
    deduct minutes and write a ledger transaction.

    Raises ValidationError (-> 400) when the balance is insufficient; in that
    case no call is created.
    """
    minutes = minutes_for_duration(duration_seconds)

    with transaction.atomic():
        locked_user = User.objects.select_for_update().get(pk=user.pk)
        if locked_user.call_minutes_balance < minutes:
            raise ValidationError({
                'detail': (
                    f'Insufficient call minutes '
                    f'(required {minutes}, available {locked_user.call_minutes_balance}).'
                )
            })

        call = create_call()

        locked_user.call_minutes_balance -= minutes
        locked_user.save(update_fields=['call_minutes_balance'])

        CallMinutesTransaction.objects.create(
            user=locked_user,
            amount=-minutes,
            type=CallMinutesTransaction.Type.DEDUCTION,
            balance_after=locked_user.call_minutes_balance,
            call=call,
        )

    call.minutes_used = minutes
    call.remaining_minutes = locked_user.call_minutes_balance
    return call


def add_minutes(user_id, amount, note='', created_by=None):
    """Top up a user's balance. Amount must be a positive integer."""
    try:
        amount = int(amount)
    except (TypeError, ValueError):
        raise ValidationError({'amount': ['A valid integer is required.']})
    if amount <= 0:
        raise ValidationError({'amount': ['Amount must be greater than zero.']})

    with transaction.atomic():
        target = User.objects.select_for_update().get(pk=user_id)
        target.call_minutes_balance += amount
        target.save(update_fields=['call_minutes_balance'])
        txn = CallMinutesTransaction.objects.create(
            user=target,
            amount=amount,
            type=CallMinutesTransaction.Type.TOPUP,
            balance_after=target.call_minutes_balance,
            note=(note or '')[:255],
            created_by=created_by,
        )
    return target, txn