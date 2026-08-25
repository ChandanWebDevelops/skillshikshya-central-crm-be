# Lead App — Enrollments & Payments API Guide

**Base URL:** `http://localhost:8188`

---

## Global List Endpoints

Flat read-only lists across all leads are available at:
- `GET /api/enrollments/` — All enrollments
- `GET /api/payments/` — All payments

See [Global List Endpoints Guide](lead_app_global_list_api_guide.md) for details.

## Branch Scoping

All list endpoints support `?branch_id=X`. **Staff/superusers** can pass it to filter; non-staff users are automatically scoped to their own branch. See [Lead App Overview](lead_app_overview.md#branch-scoping) for the full rules.

```
GET /api/leads/?branch_id=2
GET /api/enrollments/?branch_id=2
GET /api/leads/5/enrollments/?branch_id=2
```

## Enrollment Lifecycle

Enrollment `status` is a plain string — the API does not enforce transitions, but the intended workflow is:

```
pending ──► confirmed ──► active ──► completed
   │                         
   ├──► cancelled            
                              
active ──► dropped_out        
active ──► transferred        
```

| Status | Meaning |
|--------|---------|
| `pending` | Created, awaiting confirmation/down payment |
| `confirmed` | Confirmed by counselor (e.g., first payment received) |
| `active` | Student attending classes |
| `completed` | Course finished |
| `cancelled` | Cancelled before/at start |
| `dropped_out` | Student quit mid-course |
| `transferred` | Moved to another branch/batch |

> **Note:** Creating an enrollment does **not** automatically flip the lead's conversion state or create a student record. Those are separate manual steps:
> - Set lead status via `PATCH /api/leads/{id}/` (conversion flags `is_converted`/`converted_at` are system-managed/read-only).
> - Create the student profile via `POST /api/students/`, then optionally link it back by setting `student` on the enrollment.

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
| `branch` | int (FK, nullable) | Branch owning this enrollment |
| `total_paid` | decimal (read-only) | Sum of successful payments |
| `remaining_amount` | decimal (read-only) | `agreed_amount - total_paid` |
| `is_full_paid` | bool (read-only) | `remaining_amount <= 0` |
| `created_by` | int (FK, read-only) | |
| `created_by_name` | string (read-only) | |
| `updated_by` | int (FK, read-only) | |
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

### PATCH `/api/leads/{lead_id}/enrollments/{id}/`

Partial update — send only the fields being changed. Read-only fields are ignored if sent.

**Request:**
```json
{
    "status": "confirmed",
    "agreed_amount": "42000.00"
}
```

**Response `200 OK`:** same shape as the POST response above (with updated values).

### Validation Errors — `400 Bad Request`

Required fields on create: `course`, `enrollment_date`, `listed_fee`, `agreed_amount`. Decimal fields must be strings or numbers; dates use `YYYY-MM-DD`, datetimes use ISO 8601.

```json
{
    "course": ["This field is required."],
    "agreed_amount": ["A valid number is required."]
}
```

Invalid enum value:
```json
{
    "status": ["\"finished\" is not a valid choice."]
}
```

Non-existent FK:
```json
{
    "course": ["Invalid pk \"999\" - object does not exist."]
}
```

Permission failures return `403 Forbidden` with `{"detail": ...}`; unknown IDs return `404 Not Found`.

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
| PATCH/PUT | `/api/leads/{lead_id}/enrollments/{enrollment_id}/payments/{id}/` | Correct a payment | Staff or `lead.change_payment` permission |
| DELETE | `/api/leads/{lead_id}/enrollments/{enrollment_id}/payments/{id}/` | Delete payment | Staff or `lead.delete_payment` permission |

### PATCH `/api/leads/{lead_id}/enrollments/{enrollment_id}/payments/{id}/`

Partial update for corrections (wrong amount, method, reference, status…). Editable fields: `amount`, `payment_date`, `payment_method`, `transaction_reference`, `status`, `notes`. Read-only: `enrollment`, `received_by`, `created_at`.

**Request:**
```json
{
    "amount": "21000.00",
    "status": "successful"
}
```

**Response `200 OK`:** same shape as the POST response.

> **Invoice side-effects:**
> - A payment created with `status: "successful"` gets an invoice emailed automatically.
> - If a payment was recorded as `pending` and later **corrected to `successful` via PATCH**, the invoice is generated at that moment (once — no duplicates on further edits).
> - Editing a *successful* payment's amount does NOT regenerate its already-issued receipt. Prefer correcting before marking successful; otherwise issue a manual adjustment and inform the student.

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
| `branch` | int (FK, nullable, read-only) | Set to the recording user's branch context |
| `received_by` | int (FK, read-only) | Auto-set to the logged-in user |
| `received_by_name` | string (read-only) | |
| `created_at` | datetime (read-only) | |

> Only `status: "successful"` payments count toward `total_paid` on the enrollment.

> **Invoice:** recording a payment with `status: "successful"` automatically generates an invoice and emails it to the student with configured CCs. See [Invoices Guide](invoice_app_apis_guide.md).

### POST `/api/leads/{lead_id}/enrollments/{enrollment_id}/payments/`

Required fields: `amount`, `payment_date`. `received_by` and `enrollment` are auto-set (logged-in user / URL).

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

**Response `201 Created`:**
```json
{
    "id": 7,
    "received_by_name": "Sita Rai",
    "amount": "20000.00",
    "payment_date": "2026-07-21T12:00:00Z",
    "payment_method": "esewa",
    "status": "successful",
    "transaction_reference": "ESEWA-12345",
    "notes": "First installment",
    "enrollment": 1,
    "received_by": 2,
    "branch": 1,
    "created_at": "2026-07-21T12:05:00Z"
}
```

**Validation error — `400 Bad Request`:**
```json
{
    "payment_date": ["This field is required."],
    "status": ["\"paid\" is not a valid choice."]
}
```
Recording a successful payment immediately reflects in the parent enrollment's computed `total_paid`, `remaining_amount`, and `is_full_paid`.

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
