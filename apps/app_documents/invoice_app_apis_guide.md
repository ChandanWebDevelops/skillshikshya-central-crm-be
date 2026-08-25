# Invoices App — API Guide

## Overview

Invoices are generated **automatically** and emailed to students (with CC support):

| Trigger | Document created |
|---------|------------------|
| **Student created** from a lead that has active enrollments | `enrollment` invoice per enrollment (course fee = `agreed_amount`) |
| **Successful payment recorded** (`POST .../payments/`) | `payment` receipt (amount paid + running total + remaining) |

Each invoice is sent as a **styled HTML email** (with the Skill Shikshya logo) via Celery. Failed/pending payments and standalone students without enrollments generate nothing.

> The email goes to `student.email`, falling back to `lead.email`. If neither exists, the invoice is still generated but not emailed (a warning is logged). Email failures never block invoice creation.

**Base URL:** `http://localhost:8188`

---

## Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/invoices/` | Flat list, paginated + filters | Authenticated |
| GET | `/api/students/{student_id}/invoices/` | Per-student invoice history | Authenticated |
| POST | `/api/invoices/{id}/resend/` | Re-send email | Admin only |
| GET/PUT | `/api/invoices/email-config/` | Read/update global email config (CC list) | Admin only |

### GET `/api/invoices/`

**Query params:** `?type=enrollment|payment&student=10&enrollment=7&created_at__gte=&created_at__lte=&ordering=-created_at&page=1&page_size=20`

```json
{
  "count": 2,
  "results": [
    {
      "id": 5,
      "invoice_number": "INV-2026-000002",
      "type": "payment",
      "type_display": "Payment Receipt",
      "enrollment": 7,
      "student": 10,
      "student_name": "Ram Bahadur Test",
      "payment": 8,
      "course_name": "Digital Marketing Course In Nepal",
      "amount": "23000.00",
      "total_paid_so_far": "43000.00",
      "remaining_balance": "0.00",
      "emailed_to": "ram@example.com",
      "cc_emails": ["accounts@skillshikshya.com"],
      "sent_at": "2026-08-23T12:05:11Z",
      "created_at": "2026-08-23T12:05:02Z"
    }
  ]
}
```

### GET `/api/students/{student_id}/invoices/`

Same shape, pre-filtered to one student.

### POST `/api/invoices/{id}/resend/`

Queues the email task again (uses stored `emailed_to`, or re-resolves student → lead email).

```json
{ "detail": "Invoice INV-2026-000002 queued for re-send.", "to": "ram@example.com" }
```

Returns `400` if no address can be resolved; `403` for non-admin users.

---

## Email Config (`/api/invoices/email-config/`)

Singleton config controlling who gets CC'd on every invoice email.

**GET response / PUT request body:**
```json
{
    "cc_emails": ["accounts@skillshikshya.com", "billing@skillshikshya.com"],
    "subject_prefix": "Skill Shikshya",
    "is_active": true,
    "updated_at": "2026-08-23T12:00:00Z"
}
```

| Field | Type | Notes |
|-------|------|-------|
| `cc_emails` | JSON array of emails | Deduplicated on send; empty by default |
| `subject_prefix` | string | Prefixed to subject lines |
| `is_active` | bool | When `false`, CCs are skipped entirely |

CC addresses are also editable in Django Admin (**Invoices → Invoice Email Config**) and recorded per-invoice in `cc_emails`.

---

## Invoice Model Reference

| Field | Type | Description |
|-------|------|-------------|
| `invoice_number` | string (read-only) | `INV-{year}-{seq}` e.g. `INV-2026-000001` |
| `type` | string | `enrollment` (course fee) or `payment` (receipt) |
| `enrollment` / `student` / `payment` | FK | Related records (nullable for student/payment) |
| `course_name` | string | Snapshot of course name at generation time |
| `amount` | decimal | This document's amount (fee or payment) |
| `total_paid_so_far` | decimal (read-only) | Successful payments at generation time |
| `remaining_balance` | decimal (read-only) | `agreed_amount - total_paid_so_far` (floor 0) |
| `emailed_to` / `cc_emails` / `sent_at` | read-only | Populated when the email is sent |

---

## Behavior Notes & Limitations

1. **Creation & status-correction triggers** — receipts generate when a payment is created `successful`, **or** when a pending payment is later corrected to `successful` via PATCH (once only). Editing the amount of an already-successful payment does not regenerate its issued receipt.
2. Students are auto-linked to unclaimed enrollments from their lead at creation (sets `Enrollment.student` when it was null).
3. Duplicate protection: an enrollment gets at most one `enrollment`-type fee invoice.
4. Emails require working SMTP + Redis/Celery; check worker logs (`docker compose logs -f celery_worker`) if invoices show `sent_at = null`.
5. The email header logo is configurable via the `INVOICE_LOGO_URL` env var (defaults to the Skill Shikshya logo).

---

## Related Documents

| Guide | Description |
|-------|-------------|
| [Enrollments & Payments Guide](lead_app_enrollments_payments_api_guide.md) | Where receipts are triggered |
| [Students API Guide](student_app_apis_guide.md) | Student creation trigger |
