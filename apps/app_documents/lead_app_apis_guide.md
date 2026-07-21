# Lead App — API Guide

## Overview

The Lead app manages leads from inquiry through conversion. Includes configuration models (sources, campaigns, statuses, priorities, tags) and nested child records (calls, activities, followups, documents).

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

---

## Lead Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/leads/` | List leads (paginated) | Authenticated |
| POST | `/api/leads/` | Create a lead | Staff or `lead.add_lead` permission |
| GET | `/api/leads/{id}/` | Get lead detail | Authenticated |
| PUT | `/api/leads/{id}/` | Full update | Staff or `lead.change_lead` permission |
| PATCH | `/api/leads/{id}/` | Partial update | Staff or `lead.change_lead` permission |
| DELETE | `/api/leads/{id}/` | Delete lead | Staff or `lead.delete_lead` permission |
| GET | `/api/leads/export_csv/` | Export filtered leads to CSV | Authenticated |

---

### POST `/api/leads/` — Create Lead

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
    "tags": [1]
}
```

**`lead_type` options:**

| Value | Label |
|-------|-------|
| `course_inquiry` | Course Inquiry |
| `master_class` | Master Class |
| `corporate` | Corporate |
| `general_inquiry` | General Inquiry |

---

### GET `/api/leads/` — List Leads

**Query params:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `search` | string | Search across `full_name`, `phone`, `email`, `notes` |
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
| `tags` | int | Filter by tag ID |
| `lead_score__gte` | int | Min lead score |
| `lead_score__lte` | int | Max lead score |
| `expected_revenue__gte` | number | Min expected revenue |
| `expected_revenue__lte` | number | Max expected revenue |
| `created_at__gte` | datetime | Created after |
| `created_at__lte` | datetime | Created before |
| `next_followup_at__gte` | datetime | Followup after |
| `next_followup_at__lte` | datetime | Followup before |
| `ordering` | string | Order by `id`, `full_name`, `lead_score`, `expected_revenue`, `created_at`, `updated_at`, `last_contact_at`, `next_followup_at` (prefix `-` for desc) |
| `page` | int | Page number |
| `page_size` | int | Items per page (max 100) |

**Examples:**
```
GET /api/leads/?search=rahul
GET /api/leads/?source__in=1,2&status__in=3,4
GET /api/leads/?lead_score__gte=10&ordering=-lead_score
GET /api/leads/?status=1&lead_type=course_inquiry
GET /api/leads/?assigned_counselor=1&is_converted=false
GET /api/leads/?created_at__gte=2026-07-01T00:00:00Z
```

---

### GET `/api/leads/{id}/` — Get Lead Detail

**Response `200 OK`:**
```json
{
    "id": 1,
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
    "id": 1,
    "full_name": "Rahul Sharma",
    "phone": "9812345678",
    "secondary_phone": null,
    "email": "rahul@example.com",
    "address": null,
    "lead_type": "course_inquiry",
    "lead_score": 0,
    "expected_revenue": null,
    "next_followup_at": null,
    "last_contact_at": null,
    "notes": "Interested in full stack course",
    "is_converted": false,
    "converted_at": null,
    "created_at": "2026-07-21T07:04:55Z",
    "updated_at": "2026-07-21T07:04:55Z",
    "source": 1,
    "campaign": 1,
    "branch": null,
    "priority": 1,
    "status": 1,
    "assigned_counselor": 1,
    "primary_course": 1,
    "created_by": 1,
    "updated_by": null,
    "tags": []
}
```

---

### PATCH `/api/leads/{id}/` — Partial Update

```json
{
    "status": 2,
    "priority": 2,
    "notes": "Updated notes"
}
```

---

### DELETE `/api/leads/{id}/` — Delete Lead

**Response:** `204 No Content`

---

### GET `/api/leads/export_csv/` — Export CSV

Exports the current filtered lead list as a CSV file. Supports all query params above.

```
GET /api/leads/export_csv/?status__in=1,2&ordering=-created_at
```

**Response:** `Content-Type: text/csv` with `Content-Disposition: attachment; filename="leads.csv"`.

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

**Response `201 Created`:**
```json
{
    "id": 1,
    "caller_name": "Rahul Sharma",
    "created_by_name": "Admin",
    "call_timestamp": "2026-07-21T12:00:00Z",
    "direction": "inbound",
    "caller": "Rahul Sharma",
    "phone_number": "9812345678",
    "duration_seconds": 120,
    "outcome": "Interested, requested demo",
    "notes": "Wants to know about pricing",
    "recording_url": null,
    "next_followup_at": null,
    "next_action": null,
    "created_at": "2026-07-21T07:05:18Z",
    "lead": 1,
    "created_by": 1
}
```

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

---

## Permission Model

| User type | Access |
|-----------|--------|
| **Staff** (`is_staff=True`) | Full CRUD on all lead endpoints |
| **Regular user** with permissions | Limited by assigned Django permissions |
| **Regular user** no permissions | Read-only — can list and view leads |

**Django permissions:**
- `lead.add_lead`, `lead.change_lead`, `lead.delete_lead`, `lead.view_lead`
- `lead.add_leadsource`, `lead.change_leadsource`, `lead.delete_leadsource`, `lead.view_leadsource`
- `lead.add_campaign`, `lead.change_campaign`, `lead.delete_campaign`, `lead.view_campaign`
- `lead.add_leadstatus`, etc.
- `lead.add_leadpriority`, etc.
- `lead.add_leadtag`, etc.
- `lead.add_leadcall`, `lead.change_leadcall`, `lead.delete_leadcall`, `lead.view_leadcall`
- `lead.add_leadactivity`, `lead.change_leadactivity`, `lead.delete_leadactivity`, `lead.view_leadactivity`
- `lead.add_followup`, `lead.change_followup`, `lead.delete_followup`, `lead.view_followup`
- `lead.add_leaddocument`, `lead.change_leaddocument`, `lead.delete_leaddocument`, `lead.view_leaddocument`
