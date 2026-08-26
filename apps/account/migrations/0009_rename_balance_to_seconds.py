from django.db import migrations
from django.db.models import F


def minutes_to_seconds(apps, schema_editor):
    User = apps.get_model('account', 'User')
    # Field was just renamed; values are still in minutes — multiply to seconds.
    User.objects.update(call_seconds_balance=F('call_seconds_balance') * 60)


def reverse_conversion(apps, schema_editor):
    User = apps.get_model('account', 'User')
    User.objects.update(call_seconds_balance=F('call_seconds_balance') / 60)


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0008_seed_call_minutes'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='call_minutes_balance',
            new_name='call_seconds_balance',
        ),
        migrations.RunPython(minutes_to_seconds, reverse_conversion),
    ]