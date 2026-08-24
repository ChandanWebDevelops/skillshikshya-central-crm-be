from django.core.management.base import BaseCommand

from apps.lead.models import Lead


class Command(BaseCommand):
    help = (
        'Set lead.primary_course from the lead\'s primary course interest '
        'where primary_course is still null.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Show what would change without saving.',
        )

    def handle(self, *args, **options):
        leads = (
            Lead.objects.filter(primary_course__isnull=True)
            .filter(course_interests__course__isnull=False)
            .distinct()
        )

        updated = 0
        for lead in leads:
            interest = (
                lead.course_interests.filter(course__isnull=False)
                .order_by('-is_primary', '-created_at')
                .first()
            )
            if not interest:
                continue
            if options['dry_run']:
                self.stdout.write(
                    f'[dry-run] {lead.reference_number} -> {interest.course.name}'
                )
            else:
                lead.primary_course = interest.course
                lead.save(update_fields=['primary_course'])
                self.stdout.write(
                    f'{lead.reference_number} -> {interest.course.name}'
                )
            updated += 1

        suffix = ' (dry-run)' if options['dry_run'] else ''
        self.stdout.write(self.style.SUCCESS(f'Updated {updated} leads.{suffix}'))