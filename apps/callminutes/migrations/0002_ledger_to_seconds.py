from django.db import migrations
from django.db.models import F


def minutes_to_seconds(apps, schema_editor):
    CallMinutesTransaction = apps.get_model('callminutes', 'CallMinutesTransaction')
    CallMinutesTransaction.objects.update(
        amount=F('amount') * 60,
        balance_after=F('balance_after') * 60,
    )


def reverse_conversion(apps, schema_editor):
    CallMinutesTransaction = apps.get_model('callminutes', 'CallMinutesTransaction')
    CallMinutesTransaction.objects.update(
        amount=F('amount') / 60,
        balance_after=F('balance_after') / 60,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('callminutes', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(minutes_to_seconds, reverse_conversion),
    ]