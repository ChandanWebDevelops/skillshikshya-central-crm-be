from django.db import migrations, models
import django.db.models.deletion


CHAR_TO_FK_MAP = {
    'course_inquiry': 'Course Inquiry',
    'master_class': 'Master Class',
    'corporate': 'Corporate',
    'general_inquiry': 'General Inquiry',
}


def convert_to_fk(apps, schema_editor):
    Lead = apps.get_model('lead', 'Lead')
    LeadType = apps.get_model('lead', 'LeadType')
    for lead in Lead.objects.filter(lead_type_old__isnull=False):
        name = CHAR_TO_FK_MAP.get(lead.lead_type_old.strip(), 'General Inquiry')
        lead_type = LeadType.objects.filter(name=name).first()
        if lead_type:
            lead.lead_type = lead_type
            lead.save(update_fields=['lead_type'])


class Migration(migrations.Migration):

    dependencies = [
        ('lead', '0003_convert_lead_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lead',
            name='lead_type',
        ),
        migrations.AddField(
            model_name='lead',
            name='lead_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='leads', to='lead.leadtype'),
        ),
        migrations.RunPython(convert_to_fk, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='lead',
            name='lead_type_old',
        ),
    ]
