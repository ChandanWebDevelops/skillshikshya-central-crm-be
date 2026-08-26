from django.contrib.auth import get_user_model
from django.db import transaction

from rest_framework.exceptions import ValidationError

from apps.callminutes.models import CallMinutesTransaction

User = get_user_model()


def seconds_for_duration(duration_seconds):
    """Exact seconds charged — no rounding. 0-duration calls cost nothing."""
    try:
        return max(0, int(duration_seconds or 0))
    except (TypeError, ValueError):
        return 0


def charge_for_call(user, duration_seconds, create_call):
    """
    Atomically check the user's balance, create the call via `create_call()`,
    deduct the exact seconds and write a ledger transaction.

    Zero-second calls are recorded without any deduction or ledger row.

    Raises ValidationError (-> 400) when the balance is insufficient; in that
    case no call is created.
    """
    seconds = seconds_for_duration(duration_seconds)

    with transaction.atomic():
        locked_user = User.objects.select_for_update().get(pk=user.pk)
        if locked_user.call_seconds_balance < seconds:
            raise ValidationError({
                'detail': (
                    f'Insufficient call minutes '
                    f'(required {seconds} seconds, '
                    f'available {locked_user.call_seconds_balance} seconds).'
                )
            })

        call = create_call()

        if seconds:
            locked_user.call_seconds_balance -= seconds
            locked_user.save(update_fields=['call_seconds_balance'])
            CallMinutesTransaction.objects.create(
                user=locked_user,
                amount=-seconds,
                type=CallMinutesTransaction.Type.DEDUCTION,
                balance_after=locked_user.call_seconds_balance,
                call=call,
            )

    call.seconds_used = seconds
    call.remaining_seconds = locked_user.call_seconds_balance
    return call


def add_minutes(user_id, amount_minutes, note='', created_by=None):
    """Top up a user's balance. Amount is in MINUTES, stored as seconds."""
    try:
        amount = int(amount_minutes)
    except (TypeError, ValueError):
        raise ValidationError({'amount': ['A valid integer is required.']})
    if amount <= 0:
        raise ValidationError({'amount': ['Amount must be greater than zero.']})

    with transaction.atomic():
        target = User.objects.select_for_update().get(pk=user_id)
        target.call_seconds_balance += amount * 60
        target.save(update_fields=['call_seconds_balance'])
        txn = CallMinutesTransaction.objects.create(
            user=target,
            amount=amount * 60,
            type=CallMinutesTransaction.Type.TOPUP,
            balance_after=target.call_seconds_balance,
            note=(note or '')[:255],
            created_by=created_by,
        )
    return target, txn