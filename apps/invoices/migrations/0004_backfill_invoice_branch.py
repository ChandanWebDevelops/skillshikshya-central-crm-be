from django.db import migrations


def backfill_branch(apps, schema_editor):
    Invoice = apps.get_model('invoices', 'Invoice')
    for invoice in Invoice.objects.filter(
        branch__isnull=True,
    ).select_related('enrollment'):
        enrollment = invoice.enrollment
        if enrollment and enrollment.branch_id:
            invoice.branch_id = enrollment.branch_id
            invoice.save(update_fields=['branch'])


def reverse_backfill(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0003_invoice_branch'),
    ]

    operations = [
        migrations.RunPython(backfill_branch, reverse_backfill),
    ]