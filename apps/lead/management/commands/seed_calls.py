import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.apps import apps as django_apps

from apps.lead.models import (
    Lead, LeadCall, LeadType, LeadSource, LeadStatus, LeadPriority, Campaign,
)

User = get_user_model()
Branch = django_apps.get_model("branch", "Branch")

FIRST_NAMES = ["Aarav", "Priya", "Rohan", "Sita", "Bikash", "Anjali", "Suman",
               "Kabita", "Nabin", "Puja", "Rajesh", "Sabina", "Dipesh", "Kriti"]
LAST_NAMES = ["Shrestha", "Thapa", "Gurung", "Tamang", "Rai", "Karki",
              "Bhattarai", "Adhikari", "Magar", "Lama"]

DIRECTIONS = [LeadCall.Direction.INBOUND, LeadCall.Direction.OUTBOUND]
OUTCOMES = ["connected", "no_answer", "busy", "voicemail", "wrong_number"]

DEFAULT_NUM_LEADS = 25
CALLS_PER_LEAD = (1, 6)


class Command(BaseCommand):
    help = "Seed Leads and LeadCalls with randomized test data across all branches."

    def add_arguments(self, parser):
        parser.add_argument("--leads", type=int, default=DEFAULT_NUM_LEADS)
        parser.add_argument(
            "--clear", action="store_true",
            help="Delete previously seeded (name starts with 'Seed Lead') leads/calls first.",
        )

    def handle(self, *args, **options):
        num_leads = options["leads"]

        branches = list(Branch.objects.all())
        if not branches:
            self.stderr.write(self.style.ERROR(
                "No branches found. Run the frontend seed script "
                "(npm run seed:backend) first, or create a Branch in the admin."
            ))
            return

        users = list(User.objects.filter(is_active=True))
        if not users:
            self.stderr.write(self.style.ERROR(
                "No users found. Create one: python manage.py createsuperuser"
            ))
            return

        # Optional lookup data — used if present, skipped (left null) if not seeded yet.
        lead_types = list(LeadType.objects.all())
        lead_sources = list(LeadSource.objects.all())
        lead_statuses = list(LeadStatus.objects.all())
        lead_priorities = list(LeadPriority.objects.all())
        campaigns = list(Campaign.objects.all())

        if options["clear"]:
            deleted_calls, _ = LeadCall.objects.filter(
                lead__full_name__startswith="Seed Lead"
            ).delete()
            deleted_leads, _ = Lead.objects.filter(
                full_name__startswith="Seed Lead"
            ).delete()
            self.stdout.write(self.style.WARNING(
                f"Cleared {deleted_leads} leads and {deleted_calls} calls."
            ))

        total_calls_created = 0

        for i in range(num_leads):
            branch = random.choice(branches)
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            phone = f"98{random.randint(10000000, 99999999)}"

            lead = Lead.objects.create(
                full_name=f"Seed Lead {first} {last}",
                phone=phone,
                branch=branch,
                lead_type=random.choice(lead_types) if lead_types else None,
                source=random.choice(lead_sources) if lead_sources else None,
                status=random.choice(lead_statuses) if lead_statuses else None,
                priority=random.choice(lead_priorities) if lead_priorities else None,
                campaign=random.choice(campaigns) if campaigns else None,
                assigned_counselor=random.choice(users),
                # province/city intentionally omitted — optional, and the
                # dropdown for them is broken anyway; not needed for Lead creation.
            )

            num_calls = random.randint(*CALLS_PER_LEAD)
            for _ in range(num_calls):
                caller_user = random.choice(users)
                direction = random.choice(DIRECTIONS)
                outcome = random.choice(OUTCOMES)
                duration = random.randint(10, 900) if outcome == "connected" else 0

                days_ago = random.randint(0, 30)
                hour = random.randint(8, 20)
                call_time = timezone.now() - timedelta(days=days_ago)
                call_time = call_time.replace(
                    hour=hour, minute=random.randint(0, 59), second=random.randint(0, 59)
                )

                LeadCall.objects.create(
                    lead=lead,
                    call_timestamp=call_time,
                    direction=direction,
                    caller=(
                        getattr(caller_user, "get_full_name", lambda: None)()
                        or getattr(caller_user, "full_name", None)
                        or getattr(caller_user, "name", None)
                        or getattr(caller_user, "email", None)
                        or caller_user.get_username()
                    ),
                    phone_number=lead.phone or phone,
                    duration_seconds=duration,
                    outcome=outcome,
                    notes=f"Seed note for {lead.full_name}" if random.random() > 0.5 else "",
                    branch=branch,
                    created_by=caller_user,
                )
                total_calls_created += 1

            if (i + 1) % 5 == 0:
                self.stdout.write(f"  ...{i + 1}/{num_leads} leads done")

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Done. Created {num_leads} leads and {total_calls_created} calls "
            f"across {len(branches)} branches."
        ))