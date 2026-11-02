from django.test import TestCase
from apps.lead.serializers import LeadCallSerializer
from apps.lead.models import LeadCall, Lead
from django.contrib.auth import get_user_model
from django.utils import timezone

class TestDurationInputSerializer(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(email='test@test.com', name='Test User', password='pass')
        self.lead = Lead.objects.create(full_name='Test Lead', phone='9811111111')

    def test_serializer_parses_duration_input(self):
        data = {
            'duration_input': '4:19',
            'direction': 'outbound',
            'call_timestamp': timezone.now(),
            'caller': self.user.name,
            'phone_number': '9811111111',
        }
        serializer = LeadCallSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save(lead=self.lead, created_by=self.user)
        self.assertEqual(instance.duration_seconds, 259)

        data = {
            'duration_input': '4m19s',
            'direction': 'outbound',
            'call_timestamp': timezone.now(),
            'caller': self.user.name,
            'phone_number': '9811111111',
        }
        serializer = LeadCallSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save(lead=self.lead, created_by=self.user)
        self.assertEqual(instance.duration_seconds, 259)
