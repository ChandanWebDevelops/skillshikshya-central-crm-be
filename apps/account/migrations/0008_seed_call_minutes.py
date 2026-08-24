from django.db import migrations


def seed_balances(apps, schema_editor):
    User = apps.get_model('account', 'User')
    User.objects.filter(is_active=True).update(call_minutes_balance=100)


def reverse_seed(apps, schema_editor):
    User = apps.get_model('account', 'User')
    User.objects.update(call_minutes_balance=0)


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0007_user_call_minutes_balance'),
    ]

    operations = [
        migrations.RunPython(seed_balances, reverse_seed),
    ]