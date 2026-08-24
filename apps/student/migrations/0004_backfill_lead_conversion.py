from django.db import migrations, models


def backfill_conversion(apps, schema_editor):
    Lead = apps.get_model('lead', 'Lead')
    Student = apps.get_model('student', 'Student')

    converted = (
        Student.objects.filter(lead__isnull=False)
        .values('lead')
        .annotate(first_created=models.Min('created_at'))
    )
    for row in converted:
        Lead.objects.filter(pk=row['lead'], is_converted=False).update(
            is_converted=True,
            converted_at=row['first_created'],
        )


def reverse_backfill(apps, schema_editor):
    pass  # cannot know which conversions were pre-existing; no-op


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0003_attendance'),
    ]

    operations = [
        migrations.RunPython(backfill_conversion, reverse_backfill),
    ]