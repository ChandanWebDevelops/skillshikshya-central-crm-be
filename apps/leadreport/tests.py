from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase, APIRequestFactory

from apps.branch.models import Branch
from apps.course.models import Course
from apps.lead.models import (
    Enrollment, Lead, LeadSource, LeadStatus, LeadType, Payment,
)
from apps.leadreport import services


class LeadReportServiceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='admin@test.com', name='Admin', password='pass', is_staff=True,
        )
        self.branch = Branch.objects.create(name='Kathmandu', code='KTM')
        self.source = LeadSource.objects.create(name='Website')
        self.status = LeadStatus.objects.create(name='New')
        self.lead_type = LeadType.objects.create(name='Course Inquiry')
        self.course = Course.objects.create(name='Python')

        self.lead = Lead.objects.create(
            full_name='Rahul Sharma',
            phone='9812345678',
            branch=self.branch,
            source=self.source,
            status=self.status,
            lead_type=self.lead_type,
            primary_course=self.course,
            expected_revenue=30000,
        )
        self.enrollment = Enrollment.objects.create(
            lead=self.lead,
            course=self.course,
            enrollment_date=timezone.now().date(),
            listed_fee=30000,
            agreed_amount=28000,
            status='confirmed',
            branch=self.branch,
        )
        Payment.objects.create(
            enrollment=self.enrollment,
            amount=14000,
            payment_date=timezone.now(),
            payment_method='cash',
            status='successful',
            branch=self.branch,
        )

    def _request(self, params=None):
        factory = APIRequestFactory()
        request = factory.get('/api/reports/overview/', params or {})
        request.user = self.user
        return request

    def test_overview(self):
        data = services.lead_overview_report(self._request())
        self.assertEqual(data['leads']['total'], 1)
        self.assertEqual(data['enrollments']['revenue_collected'], '14000.00')

    def test_leads_by_status(self):
        data = services.leads_by_status_report(self._request())
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['results'][0]['count'], 1)

    def test_leads_by_source(self):
        data = services.leads_by_source_report(self._request())
        self.assertEqual(data['results'][0]['source__name'], 'Website')

    def test_revenue(self):
        data = services.revenue_report(self._request())
        self.assertEqual(data['summary']['total_collected'], '14000.00')
        self.assertEqual(data['by_payment_method'][0]['payment_method'], 'cash')

    def test_revenue_outstanding(self):
        data = services.revenue_report(self._request())
        self.assertEqual(data['summary']['outstanding_to_collect'], '14000.00')

    def test_enrollments(self):
        data = services.enrollment_report(self._request())
        self.assertEqual(data['summary']['total_enrollments'], 1)
        self.assertEqual(data['summary']['collected'], '14000.00')

    def test_lead_trend(self):
        data = services.lead_trend_report(self._request({'group_by': 'day'}))
        self.assertEqual(data['results'][0]['leads'], 1)

    def test_conversion(self):
        data = services.lead_conversion_report(self._request())
        self.assertEqual(data['funnel']['total_leads'], 1)
        self.assertEqual(data['funnel']['enrolled'], 1)

    def test_invalid_date(self):
        data = services.lead_overview_report(self._request({'start_date': 'not-a-date'}))
        self.assertIn('error', data)

    def test_branch_scoping_for_non_staff(self):
        other_user = get_user_model().objects.create_user(
            email='c@test.com', name='Counselor', password='pass',
        )
        branch2 = Branch.objects.create(name='Pokhara', code='PKR')
        other_user.branch = branch2
        other_user.save()
        request = self._request()
        request.user = other_user
        data = services.lead_overview_report(request)
        self.assertEqual(data['leads']['total'], 0)


class LeadReportViewTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='admin@test.com', name='Admin', password='pass', is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def _path(self, name):
        from django.urls import reverse
        return reverse(f'report-{name}')

    def test_requires_authentication(self):
        client = self.client_class(force=False)
        response = client.get(self._path('overview'))
        self.assertIn(response.status_code, (401, 403))

    def test_overview_endpoint(self):
        response = self.client.get(self._path('overview'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('leads', response.json())

    def test_all_report_endpoints_ok(self):
        endpoints = [
            'overview', 'leads-by-status', 'leads-by-source', 'leads-by-type',
            'leads-by-branch', 'leads-by-campaign', 'leads-by-counselor',
            'lead-trend', 'revenue', 'enrollments', 'conversion',
            'counselor-performance',
        ]
        for name in endpoints:
            response = self.client.get(self._path(name))
            self.assertEqual(response.status_code, 200, msg=name)

    def test_reports_list(self):
        response = self.client.get(self._path('list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('available_reports', response.json())