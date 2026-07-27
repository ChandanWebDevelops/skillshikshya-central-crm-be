# Lead App — Followups API Guide

**Base URL:** `http://localhost:8188`

## Global List Endpoint

A flat read-only list across all leads is available at `GET /api/followups/`. See [Global List Endpoints Guide](lead_app_global_list_api_guide.md) for details.

## Endpoints

All CRUD endpoints are nested under a specific lead.

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/leads/{lead_id}/followups/` | List followups (paginated) | Authenticated |
| POST | `/api/leads/{lead_id}/followups/` | Create followup | Staff or `lead.add_followup` permission |
| GET | `/api/leads/{lead_id}/followups/{id}/` | Get followup detail | Authenticated |
| PATCH | `/api/leads/{lead_id}/followups/{id}/` | Update followup | Staff or `lead.change_followup` permission |
| DELETE | `/api/leads/{lead_id}/followups/{id}/` | Delete followup | Staff or `lead.delete_followup` permission |

---

## Model Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Auto-generated |
| `lead` | int (FK, read-only) | Auto-set from URL |
| `assigned_to` | int (FK) | User assigned to perform followup |
| `assigned_to_name` | string (read-only) | Assignee display name |
| `scheduled_at` | datetime | When the followup is scheduled |
| `purpose` | text | Purpose of the followup |
| `reminder_at` | datetime | When to send a reminder (Celery Beat checks every 5 min) |
| `reminder_sent` | bool (read-only) | Whether the reminder email/notification has been sent |
| `status` | string | `pending`, `completed`, `missed`, `cancelled` |
| `completed_at` | datetime | When actually completed |
| `notes` | text | Followup notes after completion |
| `branch` | int (FK) | Branch ID |
| `created_by` | int (FK, read-only) | Auto-set |
| `created_by_name` | string (read-only) | Creator display name |
| `updated_by` | int (FK, read-only) | Auto-set on update |
| `created_at` | datetime (read-only) | |
| `updated_at` | datetime (read-only) | |

### Auto-updates on Lead

## Automatic Reminders

When a followup is created with a `reminder_at` datetime, a Celery Beat task runs every 5 minutes and:

1. Finds all pending followups where `reminder_at` is within the current 5-minute window and `reminder_sent` is `false`
2. Creates an in-app `Notification` for the `assigned_to` user (or the lead's `assigned_counselor` if no assignee)
3. Sends an HTML email with followup details and a "View Lead" link
4. Sets `reminder_sent = true` to prevent duplicate reminders

**Fields:** `reminder_at` (writable datetime), `reminder_sent` (read-only boolean, auto-set by the task)

---

When a followup is created with `status: "pending"`:

| Lead field | Effect |
|------------|--------|
| `next_followup_at` | Set to `scheduled_at` if it's earlier than the existing value |
| `lead_score` | Recalculated |

When a followup is updated, `lead_score` is recalculated.

---

## POST `/api/leads/{lead_id}/followups/` — Create Followup

**Request:**
```json
{
    "assigned_to": 1,
    "scheduled_at": "2026-07-25T10:00:00Z",
    "purpose": "Follow up on pricing questions",
    "reminder_at": "2026-07-25T09:00:00Z",
    "status": "pending",
    "notes": "Customer wants to discuss installment options"
}
```

`status` defaults to `pending` if not provided.

---

## PATCH `/api/leads/{lead_id}/followups/{id}/` — Mark Complete

```json
{
    "status": "completed",
    "completed_at": "2026-07-25T10:30:00Z",
    "notes": "Customer agreed to enroll next week"
}
```

When a followup is completed (or its status changes), the parent lead's `lead_score` is recalculated. If there is no longer a pending future followup, the pending followup points are removed from the score.

---

## GET `/api/leads/{lead_id}/followups/` — List Followups

**Query params:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by status (`pending`, `completed`, `missed`, `cancelled`) |
| `assigned_to` | int | Filter by assignee user ID |
| `scheduled_at__gte` | datetime | Scheduled after |
| `scheduled_at__lte` | datetime | Scheduled before |
| `ordering` | string | Order by `scheduled_at` (prefix `-` for desc) |
| `page` | int | Page number |
| `page_size` | int | Items per page (max 100) |

**Examples:**
```
GET /api/leads/1/followups/?status=pending
GET /api/leads/1/followups/?assigned_to=1
GET /api/leads/1/followups/?scheduled_at__gte=2026-07-01T00:00:00Z&status=pending
```

---

## DELETE `/api/leads/{lead_id}/followups/{id}/` — Delete

**Response:** `204 No Content`
