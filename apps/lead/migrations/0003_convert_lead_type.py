from django.db import migrations, models


TYPE_MAP = ['Course Inquiry', 'Master Class', 'Corporate', 'General Inquiry']


def seed_lead_types(apps, schema_editor):
    LeadType = apps.get_model('lead', 'LeadType')
    for name in TYPE_MAP:
        LeadType.objects.create(name=name)


def copy_lead_type_values(apps, schema_editor):
    Lead = apps.get_model('lead', 'Lead')
    for lead in Lead.objects.all():
        raw = getattr(lead, 'lead_type_old', None)
        if raw is None:
            raw = getattr(lead, 'lead_type', None)
        if raw:
            lead.lead_type_old = str(raw)
            lead.save(update_fields=['lead_type_old'])


class Migration(migrations.Migration):

    dependencies = [
        ('lead', '0002_enrollment_lead_custom_data_lead_deleted_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeadType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'lead_types',
                'ordering': ['name'],
            },
        ),
        migrations.RunPython(seed_lead_types, migrations.RunPython.noop),
        migrations.AddField(
            model_name='lead',
            name='lead_type_old',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
        migrations.RunPython(copy_lead_type_values, migrations.RunPython.noop),
    ]
