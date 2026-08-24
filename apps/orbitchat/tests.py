from django.core.management import call_command
from django.test import TestCase
from io import StringIO

from apps.course.models import Course
from apps.lead.intake import lead_intake  # noqa: F401  (import sanity)
from apps.lead.models import Lead, LeadCourseInterest
from apps.orbitchat.services import create_lead_from_orbitchat_contact


class OrbitchatPrimaryCourseTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            name='Data Science and Machine Learning Diploma Course',
        )

    def test_contact_sets_interest_and_primary_course(self):
        contact = {
            'id': '52be7ae7-fcf7-4578-b61c-6079b0e155a1',
            'name': 'Rajan Khatri',
            'phone': None,
            'email': '',
            'channel_type': 'facebook',
            'notes': 'Data Science and Machine Learning Diploma Course',
        }
        lead = create_lead_from_orbitchat_contact(contact)

        self.assertIsNotNone(lead)
        self.assertEqual(lead.primary_course_id, self.course.id)

        interest = LeadCourseInterest.objects.get(lead=lead)
        self.assertTrue(interest.is_primary)
        self.assertEqual(interest.course_id, self.course.id)


class PublicIntakePrimaryCourseTests(TestCase):
    def setUp(self):
        self.python = Course.objects.create(name='Python Advanced')
        Course.objects.create(name='Flutter')

    def test_first_course_becomes_primary_course(self):
        from rest_framework.test import APIClient

        response = APIClient().post('/api/public/lead-intake/', {
            'name': 'Intake Person',
            'phone_number': '9812340000',
            'course_interests': ['Python Advanced', 'Flutter'],
        }, format='json')
        self.assertEqual(response.status_code, 201)

        lead = Lead.objects.get(id=response.data['id'])
        self.assertEqual(lead.primary_course_id, self.python.id)
        self.assertEqual(lead.course_interests.count(), 2)


class BackfillCommandTests(TestCase):
    def test_backfill_sets_missing_primary_courses(self):
        course = Course.objects.create(name='DevOps Course in Nepal')
        lead = Lead.objects.create(full_name='Old Lead', phone='111')
        LeadCourseInterest.objects.create(
            lead=lead, course=course, is_primary=True,
        )
        self.assertIsNone(lead.primary_course_id)

        out = StringIO()
        call_command('backfill_primary_courses', stdout=out)

        lead.refresh_from_db()
        self.assertEqual(lead.primary_course_id, course.id)
        self.assertIn('Updated 1 leads', out.getvalue())

    def test_backfill_skips_leads_with_existing_primary(self):
        keep = Course.objects.create(name='Keep Me')
        other = Course.objects.create(name='Other')
        lead = Lead.objects.create(full_name='Already Set', phone='222')
        lead.primary_course = keep
        lead.save(update_fields=['primary_course'])
        LeadCourseInterest.objects.create(lead=lead, course=other, is_primary=True)

        out = StringIO()
        call_command('backfill_primary_courses', stdout=out)

        lead.refresh_from_db()
        self.assertEqual(lead.primary_course_id, keep.id)