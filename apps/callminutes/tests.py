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
        self.admin.call_seconds_balance = 100 * 60  # 100 minutes
        self.admin.save()
        self.counselor = User.objects.create_user(
            email='c@test.com', name='Counselor', password='pass',
        )
        self.counselor.call_seconds_balance = 10 * 60  # 10 minutes
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

    def _post_call(self, payload_overrides=None):
        payload = dict(self.call_payload)
        if payload_overrides:
            payload.update(payload_overrides)
        return self.client.post(
            f'/api/leads/{self.lead.id}/calls/', payload, format='json',
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

    def test_call_deducts_exact_seconds(self):
        response = self._post_call()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['seconds_used'], 90)
        self.assertEqual(response.data['remaining_seconds'], 510)
        # backward-compatible floored minute fields
        self.assertEqual(response.data['minutes_used'], 1)
        self.assertEqual(response.data['remaining_minutes'], 8)

        self.counselor.refresh_from_db()
        self.assertEqual(self.counselor.call_seconds_balance, 510)
        txn = CallMinutesTransaction.objects.get(call=response.data['id'])
        self.assertEqual(txn.amount, -90)
        self.assertEqual(txn.type, 'deduction')
        self.assertEqual(txn.balance_after, 510)

    def test_four_minutes_thirty_seconds_deducts_270(self):
        self.call_payload['duration_seconds'] = 270  # 4:30
        response = self._post_call()
        self.assertEqual(response.data['seconds_used'], 270)
        self.assertEqual(response.data['remaining_seconds'], 330)
        self.counselor.refresh_from_db()
        self.assertEqual(self.counselor.call_seconds_balance, 330)

    def test_partial_minute_not_rounded_up(self):
        # 9 min 30 sec -> charges exactly 570s, not 600s
        self.counselor.call_seconds_balance = 100 * 60
        self.counselor.save()
        response = self._post_call({'duration_seconds': 570})
        self.assertEqual(response.data['seconds_used'], 570)
        self.assertEqual(response.data['remaining_seconds'], 100 * 60 - 570)
        self.assertEqual(response.data['minutes_used'], 9)  # floored display

    def test_zero_duration_call_costs_nothing_but_is_recorded(self):
        count_before = LeadCall.objects.count()
        response = self._post_call({'duration_seconds': 0})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['seconds_used'], 0)
        self.assertEqual(response.data['remaining_seconds'], 600)
        self.assertEqual(LeadCall.objects.count(), count_before + 1)
        self.assertFalse(
            CallMinutesTransaction.objects.filter(amount=0).exists(),
        )

    def test_sub_minute_call_charges_exact_seconds(self):
        response = self._post_call({'duration_seconds': 45})
        self.assertEqual(response.data['seconds_used'], 45)
        self.assertEqual(response.data['remaining_seconds'], 555)
        self.counselor.refresh_from_db()
        self.assertEqual(self.counselor.call_seconds_balance, 555)

    def test_insufficient_balance_blocks_call(self):
        self.counselor.call_seconds_balance = 0
        self.counselor.save()
        count_before = LeadCall.objects.count()

        # a call longer than the balance is rejected...
        response = self._post_call({'duration_seconds': 3600})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Insufficient call minutes', str(response.data))
        self.assertEqual(LeadCall.objects.count(), count_before)

        # ...but an exact-balance call goes through
        ok = self._post_call({'duration_seconds': 0})
        self.assertEqual(ok.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CallMinutesTransaction.objects.count(), 0)

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
        self.assertEqual(self.counselor.call_seconds_balance, 510)


class TopUpTests(CallMinutesBase):
    def setUp(self):
        super().setUp()

    def test_admin_can_top_up_in_minutes(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            f'/api/users/{self.counselor.id}/call-minutes/add/',
            {'amount': 50, 'note': 'monthly quota'}, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance_minutes'], 60)   # 10 + 50
        self.assertEqual(response.data['balance_seconds'], 3600)
        self.counselor.refresh_from_db()
        self.assertEqual(self.counselor.call_seconds_balance, 3600)
        txn = CallMinutesTransaction.objects.get(user=self.counselor)
        self.assertEqual(txn.amount, 3000)  # stored in seconds
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
        self.assertEqual(response.data['balance_seconds'], 600)
        self.assertEqual(response.data['balance_minutes'], 10)
        self.assertEqual(response.data['balance_display'], '10:00')