from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.branch.models import Branch
from apps.callminutes.models import CallMinutesTransaction
from apps.lead.models import Lead, LeadCall

User = get_user_model()


class CallMinutesBase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email='admin@test.com', name='Admin', password='pass', is_staff=True,
        )
        self.admin.call_minutes_balance = 100
        self.admin.save()
        self.counselor = User.objects.create_user(
            email='c@test.com', name='Counselor', password='pass',
        )
        self.counselor.call_minutes_balance = 10
        self.counselor.save()
        self.branch = Branch.objects.create(name='Kathmandu', code='KTM')
        self.lead = Lead.objects.create(
            full_name='Test Lead', phone='9800000009', branch=self.branch,
        )
        now = timezone.now().isoformat()
        self.call_payload = {
            'call_timestamp': now,
            'caller': 'Counselor',
            'phone_number': '9800000009',
            'duration_seconds': 90,
            'outcome': 'interested',
        }

    def _post_call(self):
        return self.client.post(
            f'/api/leads/{self.lead.id}/calls/',
            self.call_payload, format='json',
        )


class CallDeductionTests(CallMinutesBase):
    def setUp(self):
        super().setUp()
        add_perm = Permission.objects.get(
            codename='add_leadcall', content_type__app_label='lead',
        )
        change_perm = Permission.objects.get(
            codename='change_leadcall', content_type__app_label='lead',
        )
        self.counselor.user_permissions.add(add_perm, change_perm)
        self.client.force_authenticate(self.counselor)

    def test_call_deducts_minutes(self):
        response = self._post_call()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['minutes_used'], 2)
        self.assertEqual(response.data['remaining_minutes'], 8)
        self.counselor.refresh_from_db()
        self.assertEqual(self.counselor.call_minutes_balance, 8)
        txn = CallMinutesTransaction.objects.get(call=response.data['id'])
        self.assertEqual(txn.amount, -2)
        self.assertEqual(txn.type, 'deduction')
        self.assertEqual(txn.balance_after, 8)

    def test_minimum_one_minute_charged(self):
        self.call_payload['duration_seconds'] = 0
        response = self._post_call()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['minutes_used'], 1)

    def test_insufficient_balance_blocks_call(self):
        self.counselor.call_minutes_balance = 0
        self.counselor.save()
        count_before = LeadCall.objects.count()
        response = self._post_call()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Insufficient call minutes', str(response.data))
        self.assertEqual(LeadCall.objects.count(), count_before)
        self.assertEqual(
            CallMinutesTransaction.objects.count(), 0,
        )

    def test_cannot_delete_call(self):
        # Even staff/superusers must not be able to delete call records.
        self.client.force_authenticate(self.admin)
        response = self._post_call()
        call_id = response.data['id']
        delete = self.client.delete(f'/api/leads/{self.lead.id}/calls/{call_id}/')
        self.assertEqual(delete.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertTrue(LeadCall.objects.filter(pk=call_id).exists())
        self.client.force_authenticate(self.counselor)

    def test_duration_frozen_after_create(self):
        response = self._post_call()
        call_id = response.data['id']
        patch = self.client.patch(
            f'/api/leads/{self.lead.id}/calls/{call_id}/',
            {'duration_seconds': 9999}, format='json',
        )
        self.assertEqual(patch.status_code, status.HTTP_200_OK)
        call = LeadCall.objects.get(pk=call_id)
        self.assertEqual(call.duration_seconds, 90)
        self.counselor.refresh_from_db()
        self.assertEqual(self.counselor.call_minutes_balance, 8)


class TopUpTests(CallMinutesBase):
    def setUp(self):
        super().setUp()

    def test_admin_can_top_up(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            f'/api/users/{self.counselor.id}/call-minutes/add/',
            {'amount': 50, 'note': 'monthly quota'}, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance'], 60)
        self.counselor.refresh_from_db()
        self.assertEqual(self.counselor.call_minutes_balance, 60)
        txn = CallMinutesTransaction.objects.get(user=self.counselor)
        self.assertEqual(txn.amount, 50)
        self.assertEqual(txn.type, 'topup')
        self.assertEqual(txn.created_by, self.admin)

    def test_non_staff_cannot_top_up(self):
        self.client.force_authenticate(self.counselor)
        response = self.client.post(
            f'/api/users/{self.counselor.id}/call-minutes/add/',
            {'amount': 100}, format='json',
        )
        self.assertIn(response.status_code, (403, 401))

    def test_invalid_amount_rejected(self):
        self.client.force_authenticate(self.admin)
        for bad in (0, -5, 'abc', None):
            response = self.client.post(
                f'/api/users/{self.counselor.id}/call-minutes/add/',
                {'amount': bad}, format='json',
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, msg=bad)

    def test_transactions_list_admin_only(self):
        self.client.force_authenticate(self.admin)
        self.client.post(
            f'/api/users/{self.counselor.id}/call-minutes/add/',
            {'amount': 50}, format='json',
        )
        response = self.client.get(
            f'/api/users/{self.counselor.id}/call-minutes/transactions/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)


class MyCallMinutesTests(CallMinutesBase):
    def test_counselor_sees_own_balance(self):
        self.client.force_authenticate(self.counselor)
        response = self.client.get('/api/users/me/call-minutes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance'], 10)