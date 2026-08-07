# Lead App — Enrollments & Payments API Guide

**Base URL:** `http://localhost:8188`

---

## Global List Endpoints

Flat read-only lists across all leads are available at:
- `GET /api/enrollments/` — All enrollments
- `GET /api/payments/` — All payments

See [Global List Endpoints Guide](lead_app_global_list_api_guide.md) for details.

## Enrollments

### Endpoints

All CRUD endpoints are nested under a specific lead.

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/leads/{lead_id}/enrollments/` | List enrollments (paginated) | Authenticated |
| POST | `/api/leads/{lead_id}/enrollments/` | Create enrollment | Staff or `lead.add_enrollment` permission |
| GET | `/api/leads/{lead_id}/enrollments/{id}/` | Get detail (includes computed fees) | Authenticated |
| PATCH | `/api/leads/{lead_id}/enrollments/{id}/` | Update | Staff or `lead.change_enrollment` permission |
| DELETE | `/api/leads/{lead_id}/enrollments/{id}/` | Delete | Staff or `lead.delete_enrollment` permission |

### Model Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Auto-generated |
| `lead` | int (FK, read-only) | Auto-set from URL |
| `lead_name` | string (read-only) | Lead's full name |
| `course` | int (FK) | Course being enrolled in |
| `course_name` | string (read-only) | Course display name |
| `student` | int (FK, nullable) | Linked student profile ID |
| `student_name` | string (read-only) | Student display name |
| `batch` | int (FK, nullable) | CourseBatch ID — see `/api/course-batches/` |
| `batch_name` | string (read-only) | CourseBatch display name |
| `enrollment_date` | date | Date of enrollment |
| `status` | string | See options below |
| `listed_fee` | decimal | Base/catalog fee |
| `standard_discount` | decimal | Standard discount amount |
| `additional_discount` | decimal | Additional discount amount |
| `agreed_amount` | decimal | Net fee after discounts |
| `remarks` | text | Notes |
| `total_paid` | decimal (read-only) | Sum of successful payments |
| `remaining_amount` | decimal (read-only) | `agreed_amount - total_paid` |
| `is_full_paid` | bool (read-only) | `remaining_amount <= 0` |
| `created_by` | int (FK, read-only) | |
| `created_by_name` | string (read-only) | |
| `created_at` | datetime (read-only) | |
| `updated_at` | datetime (read-only) | |

**`status` options:** `pending`, `confirmed`, `active`, `completed`, `cancelled`, `dropped_out`, `transferred`

> **Computed fields** (`total_paid`, `remaining_amount`, `is_full_paid`) are calculated from successful payments — never sent by the client.

### POST `/api/leads/{lead_id}/enrollments/`

**Request:**
```json
{
    "course": 1,
    "batch": 2,
    "enrollment_date": "2026-07-21",
    "status": "active",
    "listed_fee": "50000.00",
    "standard_discount": "5000.00",
    "additional_discount": "2000.00",
    "agreed_amount": "43000.00",
    "student": null,
    "remarks": "Monthly installment plan"
}
```

**Response `201 Created`:**
```json
{
    "id": 1,
    "course_name": "Python Advanced",
    "lead_name": "Rahul Sharma",
    "student_name": null,
    "created_by_name": "Admin",
    "total_paid": "0.00",
    "remaining_amount": "43000.00",
    "is_full_paid": false,
    "course": 1,
    "student": null,
    "batch": 2,
    "batch_name": "PY-2026-001",
    "enrollment_date": "2026-07-21",
    "status": "active",
    "listed_fee": "50000.00",
    "standard_discount": "5000.00",
    "additional_discount": "2000.00",
    "agreed_amount": "43000.00",
    "remarks": "Monthly installment plan",
    "created_at": "2026-07-21T12:00:00Z",
    "updated_at": "2026-07-21T12:00:00Z"
}
```

### GET `/api/leads/{lead_id}/enrollments/` — List

**Query params:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `course` | int | Filter by course ID |
| `status` | string | Filter by status |
| `batch` | string | Filter by batch name |
| `enrollment_date__gte` | date | Enrolled after |
| `enrollment_date__lte` | date | Enrolled before |
| `ordering` | string | Order by `id`, `enrollment_date`, `status` |
| `page` | int | Page number |
| `page_size` | int | Items per page (max 100) |

---

## Payments (nested under Enrollment)

A flat read-only list across all enrollments/leads is available at `GET /api/payments/`.

### Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/leads/{lead_id}/enrollments/{enrollment_id}/payments/` | List payments (paginated) | Authenticated |
| POST | `/api/leads/{lead_id}/enrollments/{enrollment_id}/payments/` | Record a payment | Staff or `lead.add_payment` permission |
| GET | `/api/leads/{lead_id}/enrollments/{enrollment_id}/payments/{id}/` | Get payment detail | Authenticated |
| DELETE | `/api/leads/{lead_id}/enrollments/{enrollment_id}/payments/{id}/` | Delete payment | Staff or `lead.delete_payment` permission |

### Model Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Auto-generated |
| `enrollment` | int (FK, read-only) | Auto-set from URL |
| `amount` | decimal | Payment amount |
| `payment_date` | datetime | When paid |
| `payment_method` | string | `cash`, `esewa`, `khalti`, `bank_transfer`, `card`, `connectips` |
| `transaction_reference` | string | Bank ref, esewa txn, etc. |
| `status` | string | `pending`, `successful`, `failed`, `refunded`, `voided` |
| `notes` | text | |
| `created_by` | int (FK, read-only) | |
| `created_by_name` | string (read-only) | |
| `created_at` | datetime (read-only) | |

> Only `status: "successful"` payments count toward `total_paid` on the enrollment.

### POST `/api/leads/{lead_id}/enrollments/{enrollment_id}/payments/`

**Request:**
```json
{
    "amount": "20000.00",
    "payment_date": "2026-07-21T12:00:00Z",
    "payment_method": "esewa",
    "transaction_reference": "ESEWA-12345",
    "status": "successful",
    "notes": "First installment"
}
```

### GET `/api/leads/{lead_id}/enrollments/{enrollment_id}/payments/` — List

**Query params:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `payment_method` | string | Filter by method |
| `status` | string | Filter by status |
| `payment_date__gte` | datetime | Paid after |
| `payment_date__lte` | datetime | Paid before |
| `ordering` | string | Order by `payment_date` |
| `page` | int | Page number |
| `page_size` | int | Items per page (max 100) |

### DELETE `/api/leads/{lead_id}/enrollments/{enrollment_id}/payments/{id}/`

**Response:** `204 No Content`
