# Lead App — Global List Endpoints

**Base URL:** `http://localhost:8188`

## Overview

Three flat, read-only list endpoints for cross-lead workspace pages (`/follow-ups`, `/enrollments`, `/payments`). These complement the existing nested endpoints — all writes (create/update/delete) remain on the nested routes.

All three support the same pagination envelope as `/api/leads/`:
```json
{
    "count": 25,
    "page_size": 10,
    "total_pages": 3,
    "current_page": 1,
    "next": "...",
    "previous": null,
    "results": [...]
}
```

**Permissions:** `lead.view_followup` / `lead.view_enrollment` / `lead.view_payment`. Read-only — `POST`/`PATCH`/`DELETE` return `405 Method Not Allowed`.

**Branch scoping:** Standard — non-staff auto-scoped, staff pass `?branch_id=X`.

---

## GET `/api/followups/` — Global Follow-ups

Flat list of follow-ups across all leads. Each row denormalizes lead details for display.

**Response:**
```json
{
    "id": 12,
    "lead": 1,
    "lead_name": "Rahul Sharma",
    "lead_phone": "9812345678",
    "assigned_to": 3,
    "assigned_to_name": "Sita Sharma",
    "scheduled_at": "2026-07-25T10:00:00Z",
    "purpose": "Discuss pricing",
    "status": "pending",
    "branch": 1,
    "branch_name": "Kathmandu"
}
```

**Query params:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by status |
| `assigned_to` | int | Filter by assignee user ID |
| `lead` | int | Filter by lead ID |
| `branch_id` | int | Filter by branch |
| `scheduled_at__gte` | datetime | Scheduled after |
| `scheduled_at__lte` | datetime | Scheduled before |
| `ordering` | string | `scheduled_at`, `-scheduled_at`, `created_at`, `-created_at` |
| `page` | int | Page number |
| `page_size` | int | Items per page (max 100) |

**Examples:**
```
GET /api/followups/?status=pending&ordering=scheduled_at
GET /api/followups/?assigned_to=3&scheduled_at__lte=2026-07-31T23:59:59Z
GET /api/followups/?branch_id=1&status=pending
```

---

## GET `/api/enrollments/` — Global Enrollments

Flat enrollments register across all leads. Includes computed money fields.

**Response:**
```json
{
    "id": 5,
    "lead": 1,
    "lead_name": "Rahul Sharma",
    "student": 9,
    "student_name": "Rahul Sharma",
    "course": 2,
    "course_name": "Python Advanced",
    "batch": "PY-2026-01",
    "status": "active",
    "enrollment_date": "2026-07-20",
    "listed_fee": "50000.00",
    "agreed_amount": "45000.00",
    "total_paid": "20000.00",
    "remaining_amount": "25000.00",
    "is_full_paid": false,
    "branch": 1,
    "branch_name": "Kathmandu",
    "created_at": "2026-07-20T10:00:00Z"
}
```

**Query params:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `lead` | int | Filter by lead ID |
| `course` | int | Filter by course ID |
| `status` | string | Filter by status |
| `status__in` | string | Filter by multiple statuses |
| `batch` | string | Filter by batch name |
| `branch_id` | int | Filter by branch |
| `enrollment_date__gte` | date | Enrolled after |
| `enrollment_date__lte` | date | Enrolled before |
| `ordering` | string | `enrollment_date`, `-enrollment_date`, `agreed_amount`, `-agreed_amount`, `created_at`, `-created_at` |
| `page` | int | Page number |
| `page_size` | int | Items per page (max 100) |

**Examples:**
```
GET /api/enrollments/?status=active&ordering=-created_at
GET /api/enrollments/?branch_id=1&course=2
GET /api/enrollments/?course=2&enrollment_date__gte=2026-07-01
```

---

## GET `/api/payments/` — Global Payments

Flat payments ledger across all enrollments/leads.

**Response:**
```json
{
    "id": 88,
    "enrollment": 5,
    "lead": 1,
    "lead_name": "Rahul Sharma",
    "course_name": "Python Advanced",
    "amount": "20000.00",
    "payment_date": "2026-07-21T14:30:00Z",
    "payment_method": "esewa",
    "transaction_reference": "ESW-99213",
    "status": "successful",
    "received_by": 2,
    "received_by_name": "Sita Sharma",
    "branch": 1,
    "branch_name": "Kathmandu"
}
```

**Query params:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `enrollment` | int | Filter by enrollment ID |
| `lead` | int | Filter by lead ID |
| `payment_method` | string | Filter by method |
| `status` | string | Filter by status |
| `status__in` | string | Filter by multiple statuses |
| `branch_id` | int | Filter by branch |
| `payment_date__gte` | datetime | Paid after |
| `payment_date__lte` | datetime | Paid before |
| `ordering` | string | `payment_date`, `-payment_date`, `amount`, `-amount`, `created_at`, `-created_at` |
| `page` | int | Page number |
| `page_size` | int | Items per page (max 100) |

**Examples:**
```
GET /api/payments/?status=successful&ordering=-payment_date
GET /api/payments/?payment_method=esewa&payment_date__gte=2026-07-01T00:00:00Z
GET /api/payments/?branch_id=1
```
