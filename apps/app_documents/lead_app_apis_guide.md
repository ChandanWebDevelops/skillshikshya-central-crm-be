# Lead App — API Guide

## Overview

The Lead app manages leads from inquiry through conversion, enrollment, and payment tracking. Includes configuration models (sources, campaigns, statuses, priorities, tags) and nested child records (calls, activities, followups, documents, course interests, enrollments, payments).

**Base URL:** `http://localhost:8188`

---

## Lead Configuration Endpoints

These endpoints manage lookup/dropdown values. All follow the same pattern:

- **GET** — List (paginated), any authenticated user
- **POST** — Create, staff or `<model>.add_*` permission required
- **GET/PUT/PATCH/DELETE** — By ID, mutation requires staff or `<model>.change_*`/`<model>.delete_*` permission

### Lead Sources

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/lead-sources/` | List sources |
| POST | `/api/lead-sources/` | Create source |
| GET/PUT/PATCH/DELETE | `/api/lead-sources/{id}/` | CRUD |

**Fields:** `id`, `name`, `description`, `is_active`

**Query params:** `?search=web&name=web&is_active=true`

### Campaigns

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/campaigns/` | List campaigns |
| POST | `/api/campaigns/` | Create campaign |
| GET/PUT/PATCH/DELETE | `/api/campaigns/{id}/` | CRUD |

**Fields:** `id`, `name`, `source` (FK), `start_date`, `end_date`, `budget`, `is_active`

**Query params:** `?search=summer&source=1&is_active=true`

### Lead Statuses

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/lead-statuses/` | List statuses |
| POST | `/api/lead-statuses/` | Create status |
| GET/PUT/PATCH/DELETE | `/api/lead-statuses/{id}/` | CRUD |

**Fields:** `id`, `name`, `color` (hex), `sort_order`, `is_final`, `is_active`

**Query params:** `?search=new&is_active=true&is_final=false`

### Lead Priorities

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/lead-priorities/` | List priorities |
| POST | `/api/lead-priorities/` | Create priority |
| GET/PUT/PATCH/DELETE | `/api/lead-priorities/{id}/` | CRUD |

**Fields:** `id`, `name`, `color` (hex), `sort_order`, `is_active`

### Lead Tags

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/lead-tags/` | List tags |
| POST | `/api/lead-tags/` | Create tag |
| GET/PUT/PATCH/DELETE | `/api/lead-tags/{id}/` | CRUD |

**Fields:** `id`, `name`, `color` (hex), `is_active`

### Lead Types

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/lead-types/` | List types |
| POST | `/api/lead-types/` | Create type |
| GET/PUT/PATCH/DELETE | `/api/lead-types/{id}/` | CRUD |

**Fields:** `id`, `name`, `description`, `is_active`

**Default types:** Course Inquiry (1), Master Class (2), Corporate (3), General Inquiry (4)

**Query params:** `?search=course&is_active=true`

---

## Lead Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/leads/` | List leads (paginated, excludes archived + deleted) | Authenticated |
| POST | `/api/leads/` | Create a lead | Staff or `lead.add_lead` permission |
| GET | `/api/leads/{id}/` | Get lead detail (includes `enrollment_summary`) | Authenticated |
| PUT | `/api/leads/{id}/` | Full update | Staff or `lead.change_lead` permission |
| PATCH | `/api/leads/{id}/` | Partial update | Staff or `lead.change_lead` permission |
| DELETE | `/api/leads/{id}/` | Soft delete (`is_deleted=true`) | Staff or `lead.delete_lead` permission |
| GET | `/api/leads/export_csv/` | Export filtered leads to CSV | Authenticated |
| POST | `/api/leads/{id}/archive/` | Archive lead (`is_archived=true`) | Staff or `lead.change_lead` |
| POST | `/api/leads/{id}/restore/` | Restore lead (`is_archived=false`) | Staff or `lead.change_lead` |
| POST | `/api/leads/{id}/purge/` | Permanently delete lead | Staff only |
| GET | `/api/leads/recycle_bin/` | List soft-deleted leads | Authenticated |

### Lead Model Fields

| Field | Type | Description |
|-------|------|-------------|
| `reference_number` | string (read-only) | Auto-generated `LD-{YEAR}-{seq:06d}` — searchable |
| `custom_data` | JSON (writable) | Arbitrary key-value store for type-specific fields |
| `is_archived` | bool | Soft archive flag |
| `is_deleted` | bool (read-only) | Soft delete flag |
| `deleted_at` | datetime (read-only) | When soft-deleted |
| `deleted_by` | int (read-only) | User who soft-deleted |

**List defaults:** Archived and deleted leads are excluded by default. Use `?include_archived=true` to include archived, `?is_archived=true` to show only archived, or `/api/leads/recycle_bin/` to see deleted.

---

### POST `/api/leads/` — Create Lead

`reference_number` is auto-generated — do not send it.

**Request:**
```json
{
    "full_name": "Rahul Sharma",
    "phone": "9812345678",
    "email": "rahul@example.com",
    "lead_type": "course_inquiry",
    "source": 1,
    "campaign": 1,
    "priority": 1,
    "status": 1,
    "primary_course": 1,
    "assigned_counselor": 1,
    "notes": "Interested in full stack course",
    "tags": [1],
    "custom_data": {
        "preferred_learning_mode": "online",
        "preferred_shift": "evening",
        "has_laptop": true,
        "education_level": "bachelors",
        "institution_name": "ABC College",
        "emergency_contact": {
            "name": "Shyam Sharma",
            "phone": "9841111111",
            "relationship": "Brother"
        },
        "referral": {
            "code": "FRIEND10",
            "referred_by_name": "Hari",
            "referred_by_phone": "9800000000",
            "notes": "Walk-in referral"
        }
    }
}
```

**`lead_type`:** FK to `/api/lead-types/`. Send the integer ID (e.g., `1` for Course Inquiry).

---

### GET `/api/leads/` — List Leads

**Query params:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `search` | string | Search across `full_name`, `phone`, `email`, `notes`, `reference_number` |
| `lead_type` | string | Filter by type |
| `source` | int | Filter by source ID |
| `source__in` | string | Filter by multiple sources (comma-separated IDs) |
| `campaign` | int | Filter by campaign ID |
| `campaign__in` | string | Filter by multiple campaigns |
| `branch` | int | Filter by branch ID |
| `branch__in` | string | Filter by multiple branches |
| `priority` | int | Filter by priority ID |
| `status` | int | Filter by status ID |
| `status__in` | string | Filter by multiple statuses |
| `assigned_counselor` | int | Filter by counselor user ID |
| `primary_course` | int | Filter by course ID |
| `is_converted` | bool | Filter by conversion status |
| `is_archived` | bool | Filter by archive status (requires `include_archived=true`) |
| `tags` | int | Filter by tag ID |
| `include_archived` | bool | Include archived leads in results |
| `lead_type` | int | Filter by lead type ID |
| `lead_type__in` | string | Filter by multiple lead types |
| `lead_score__gte` | int | Min lead score |
| `lead_score__lte` | int | Max lead score |
| `expected_revenue__gte` | number | Min expected revenue |
| `expected_revenue__lte` | number | Max expected revenue |
| `created_at__gte` | datetime | Created after |
| `created_at__lte` | datetime | Created before |
| `next_followup_at__gte` | datetime | Followup after |
| `next_followup_at__lte` | datetime | Followup before |
| `ordering` | string | Order by `id`, `reference_number`, `full_name`, `lead_score`, `expected_revenue`, `created_at`, `updated_at`, `last_contact_at`, `next_followup_at` (prefix `-` for desc) |
| `page` | int | Page number |
| `page_size` | int | Items per page (max 100) |

**Examples:**
```
GET /api/leads/?search=LD-2026
GET /api/leads/?search=rahul
GET /api/leads/?source__in=1,2&status__in=3,4
GET /api/leads/?lead_score__gte=10&ordering=-lead_score
GET /api/leads/?include_archived=true
GET /api/leads/?is_archived=true&include_archived=true
GET /api/leads/?created_at__gte=2026-07-01T00:00:00Z
```

---

### GET `/api/leads/{id}/` — Get Lead Detail

**Response includes** `enrollment_summary`, `call_count`, `next_followup`, `reference_number`, `lead_type_name`:

```json
{
    "id": 1,
    "reference_number": "LD-2026-000001",
    "status_name": "New",
    "priority_name": "High",
    "priority_color": "#ef4444",
    "status_color": "#2563eb",
    "source_name": "Website",
    "campaign_name": "Summer 2026",
    "primary_course_name": "Python Advanced",
    "created_by_name": "Admin",
    "assigned_counselor_name": "Admin",
    "branch_name": "Kathmandu",
    "updated_by_name": null,
    "call_count": 3,
    "next_followup": {
        "id": 1,
        "scheduled_at": "2026-07-22T10:00:00Z",
        "purpose": "Follow up on pricing questions",
        "assigned_to": 1,
        "assigned_to_name": "Admin"
    },
    "enrollment_summary": {
        "is_enrolled": true,
        "latest_status": "active",
        "course": "Python Advanced",
        "batch": "PY-2026-01"
    },
    "custom_data": {
        "preferred_learning_mode": "online",
        "education_level": "bachelors"
    },
    "is_archived": false,
    "is_deleted": false,
    ...
}
```

---

### PATCH `/api/leads/{id}/` — Partial Update

```json
{
    "status": 2,
    "priority": 2,
    "custom_data": {
        "preferred_shift": "morning",
        "has_laptop": false
    }
}
```

---

### DELETE `/api/leads/{id}/` — Soft Delete

Sets `is_deleted=true`, `deleted_at`, `deleted_by`. The lead is hidden from standard listings and can be viewed in the recycle bin or permanently purged.

**Response:** `204 No Content`

---

### GET `/api/leads/export_csv/` — Export CSV

Exports the current filtered lead list as a CSV file. Supports all query params above.

```
GET /api/leads/export_csv/?status__in=1,2&ordering=-created_at
```

**Response:** `Content-Type: text/csv` with `Content-Disposition: attachment; filename="leads.csv"`.

---

### POST `/api/leads/{id}/archive/` — Archive Lead

Sets `is_archived=true`. Archived leads are hidden from the default list (use `?include_archived=true`).

**Response:**
```json
{ "detail": "Lead archived." }
```

### POST `/api/leads/{id}/restore/` — Restore Lead

Sets `is_archived=false`.

**Response:**
```json
{ "detail": "Lead restored." }
```

### POST `/api/leads/{id}/purge/` — Permanently Delete

Hard-deletes the lead from the database. **Staff only.** Works on both active and soft-deleted leads.

**Response:** `204 No Content`

### GET `/api/leads/recycle_bin/` — Recycle Bin

Lists all soft-deleted leads (paginated, same format as lead list).

```
GET /api/leads/recycle_bin/
```

---

## Nested Lead Endpoints

All nested endpoints are scoped under a specific lead. The `lead` field is auto-set from the URL.

### Lead Calls

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/leads/{lead_id}/calls/` | List calls (paginated) |
| POST | `/api/leads/{lead_id}/calls/` | Add a call |
| GET | `/api/leads/{lead_id}/calls/{id}/` | Get call detail |
| PATCH | `/api/leads/{lead_id}/calls/{id}/` | Update call |
| DELETE | `/api/leads/{lead_id}/calls/{id}/` | Delete call |

**POST `/api/leads/{lead_id}/calls/` — Add a Call**

```json
{
    "call_timestamp": "2026-07-21T12:00:00Z",
    "direction": "inbound",
    "caller": "Rahul Sharma",
    "phone_number": "9812345678",
    "duration_seconds": 120,
    "outcome": "Interested, requested demo",
    "notes": "Wants to know about pricing",
    "recording_url": null,
    "next_followup_at": null,
    "next_action": null
}
```

**`direction` options:** `inbound`, `outbound`

**Query params:** `?direction=inbound&outcome=interested&call_timestamp__gte=2026-07-01T00:00:00Z`

### Lead Activities

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/leads/{lead_id}/activities/` | List activities (paginated) |
| POST | `/api/leads/{lead_id}/activities/` | Add activity |
| GET | `/api/leads/{lead_id}/activities/{id}/` | Get activity detail |
| PATCH | `/api/leads/{lead_id}/activities/{id}/` | Update activity |
| DELETE | `/api/leads/{lead_id}/activities/{id}/` | Delete activity |

**`activity_type` options:** `call`, `whatsapp`, `note`, `meeting`, `status_change`, `assignment_change`, `demo_class`, `payment`, `enrollment`

**POST `/api/leads/{lead_id}/activities/`**
```json
{
    "activity_type": "call",
    "title": "Intro call with Rahul",
    "description": "Discussed course options",
    "activity_at": "2026-07-21T12:00:00Z"
}
```

### Lead Followups

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/leads/{lead_id}/followups/` | List followups (paginated) |
| POST | `/api/leads/{lead_id}/followups/` | Create followup |
| GET | `/api/leads/{lead_id}/followups/{id}/` | Get followup detail |
| PATCH | `/api/leads/{lead_id}/followups/{id}/` | Update followup |
| DELETE | `/api/leads/{lead_id}/followups/{id}/` | Delete followup |

**`status` options:** `pending`, `completed`, `missed`, `cancelled`

**POST `/api/leads/{lead_id}/followups/`**
```json
{
    "assigned_to": 1,
    "scheduled_at": "2026-07-22T10:00:00Z",
    "purpose": "Follow up on pricing questions",
    "reminder_at": "2026-07-22T09:00:00Z"
}
```

### Lead Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/leads/{lead_id}/documents/` | List documents (paginated) |
| POST | `/api/leads/{lead_id}/documents/` | Upload document URL |
| DELETE | `/api/leads/{lead_id}/documents/{id}/` | Delete document |

**POST `/api/leads/{lead_id}/documents/`**
```json
{
    "document_type": "ID Proof",
    "file": "https://pub-xxx.r2.dev/uploads/doc.pdf"
}
```

### Lead Course Interests

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/leads/{lead_id}/course-interests/` | List interests (paginated) |
| POST | `/api/leads/{lead_id}/course-interests/` | Add interest |
| GET | `/api/leads/{lead_id}/course-interests/{id}/` | Get detail |
| PATCH | `/api/leads/{lead_id}/course-interests/{id}/` | Update |
| DELETE | `/api/leads/{lead_id}/course-interests/{id}/` | Delete |

**Fields:** `id`, `course` (FK), `course_name` (read), `is_primary` (bool), `interest_level` (`high`|`medium`|`low`), `created_at`

**POST `/api/leads/{lead_id}/course-interests/`**
```json
{
    "course": 1,
    "is_primary": true,
    "interest_level": "high"
}
```

**Query params:** `?course=1&is_primary=true&interest_level=high`

### Lead Enrollments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/leads/{lead_id}/enrollments/` | List enrollments (paginated) |
| POST | `/api/leads/{lead_id}/enrollments/` | Create enrollment |
| GET | `/api/leads/{lead_id}/enrollments/{id}/` | Get detail (includes computed fees) |
| PATCH | `/api/leads/{lead_id}/enrollments/{id}/` | Update |
| DELETE | `/api/leads/{lead_id}/enrollments/{id}/` | Delete |

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `course` | int (FK) | Course being enrolled in |
| `student` | int (FK, nullable) | Linked student profile |
| `batch` | string | Batch/group name |
| `enrollment_date` | date | Date of enrollment |
| `status` | string | See status options below |
| `listed_fee` | decimal | Base/catalog fee |
| `standard_discount` | decimal | Standard discount amount |
| `additional_discount` | decimal | Additional discount amount |
| `agreed_amount` | decimal | Net fee after discounts |
| `remarks` | text | Notes |
| `total_paid` | decimal (read-only) | Sum of successful payments |
| `remaining_amount` | decimal (read-only) | `agreed_amount - total_paid` |
| `is_full_paid` | bool (read-only) | `remaining_amount <= 0` |

**`status` options:** `pending`, `confirmed`, `active`, `completed`, `cancelled`, `dropped_out`, `transferred`

**Computed fields** (`total_paid`, `remaining_amount`, `is_full_paid`) are calculated from successful payments — never sent by the client.

**POST `/api/leads/{lead_id}/enrollments/`**
```json
{
    "course": 1,
    "batch": "PY-2026-01",
    "enrollment_date": "2026-07-21",
    "status": "active",
    "listed_fee": "50000.00",
    "standard_discount": "5000.00",
    "additional_discount": "2000.00",
    "agreed_amount": "43000.00",
    "remarks": "Monthly installment plan"
}
```

**Response `201 Created`:**
```json
{
    "id": 1,
    "course_name": "Python Advanced",
    "lead_name": "Anita Thapa",
    "student_name": null,
    "created_by_name": "Admin",
    "total_paid": "0.00",
    "remaining_amount": "43000.00",
    "is_full_paid": false,
    "course": 1,
    "student": null,
    "batch": "PY-2026-01",
    "enrollment_date": "2026-07-21",
    "status": "active",
    "listed_fee": "50000.00",
    "standard_discount": "5000.00",
    "additional_discount": "2000.00",
    "agreed_amount": "43000.00",
    "remarks": "Monthly installment plan",
    "created_at": "...",
    "updated_at": "..."
}
```

**Query params:** `?course=1&status=active&batch=PY-2026&enrollment_date__gte=2026-07-01`

### Enrollment Payments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/leads/{lead_id}/enrollments/{enrollment_id}/payments/` | List payments (paginated) |
| POST | `/api/leads/{lead_id}/enrollments/{enrollment_id}/payments/` | Record a payment |
| GET | `/api/leads/{lead_id}/enrollments/{enrollment_id}/payments/{id}/` | Get payment detail |
| DELETE | `/api/leads/{lead_id}/enrollments/{enrollment_id}/payments/{id}/` | Delete payment |

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `amount` | decimal | Payment amount |
| `payment_date` | datetime | When paid |
| `payment_method` | string | See method options |
| `transaction_reference` | string | Bank ref, esewa txn, etc. |
| `status` | string | `pending`, `successful`, `failed`, `refunded`, `voided` |
| `notes` | text | |

**`payment_method` options:** `cash`, `esewa`, `khalti`, `bank_transfer`, `card`, `connectips`

**POST `/api/leads/{lead_id}/enrollments/{enrollment_id}/payments/`**
```json
{
    "amount": "20000.00",
    "payment_date": "2026-07-21T12:00:00Z",
    "payment_method": "esewa",
    "transaction_reference": "ESEWA-12345",
    "status": "successful"
}
```

**Query params:** `?payment_method=esewa&status=successful&payment_date__gte=2026-07-01T00:00:00Z`

---

## Permission Model

| User type | Access |
|-----------|--------|
| **Staff** (`is_staff=True`) | Full CRUD on all lead endpoints + permanent purge |
| **Regular user** with permissions | Limited by assigned Django permissions |
| **Regular user** no permissions | Read-only — can list and view leads |

**Django permissions:**
- `lead.add_lead`, `lead.change_lead`, `lead.delete_lead`, `lead.view_lead`
- `lead.add_leadsource`, `lead.change_leadsource`, `lead.delete_leadsource`, `lead.view_leadsource`
- `lead.add_campaign`, `lead.change_campaign`, `lead.delete_campaign`, `lead.view_campaign`
- `lead.add_leadstatus`, etc.
- `lead.add_leadpriority`, etc.
- `lead.add_leadtag`, etc.
- `lead.add_leadtype`, `lead.change_leadtype`, `lead.delete_leadtype`, `lead.view_leadtype`
- `lead.add_leadcall`, `lead.change_leadcall`, `lead.delete_leadcall`, `lead.view_leadcall`
- `lead.add_leadactivity`, `lead.change_leadactivity`, `lead.delete_leadactivity`, `lead.view_leadactivity`
- `lead.add_followup`, `lead.change_followup`, `lead.delete_followup`, `lead.view_followup`
- `lead.add_leaddocument`, `lead.change_leaddocument`, `lead.delete_leaddocument`, `lead.view_leaddocument`
- `lead.add_leadcourseinterest`, `lead.change_leadcourseinterest`, `lead.delete_leadcourseinterest`, `lead.view_leadcourseinterest`
- `lead.add_enrollment`, `lead.change_enrollment`, `lead.delete_enrollment`, `lead.view_enrollment`
- `lead.add_payment`, `lead.change_payment`, `lead.delete_payment`, `lead.view_payment`
