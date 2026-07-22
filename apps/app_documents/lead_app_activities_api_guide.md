# Lead App — Activities API Guide

**Base URL:** `http://localhost:8188`

## Overview

Activities track all types of interactions with a lead (calls, WhatsApp messages, notes, meetings, status changes, etc.). Unlike calls which have structured fields (duration, direction, recording), activities are more generic.

---

## Endpoints

All endpoints are nested under a specific lead.

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/leads/{lead_id}/activities/` | List activities (paginated) | Authenticated |
| POST | `/api/leads/{lead_id}/activities/` | Add activity | Staff or `lead.add_leadactivity` permission |
| GET | `/api/leads/{lead_id}/activities/{id}/` | Get activity detail | Authenticated |
| PATCH | `/api/leads/{lead_id}/activities/{id}/` | Update activity | Staff or `lead.change_leadactivity` permission |
| DELETE | `/api/leads/{lead_id}/activities/{id}/` | Delete activity | Staff or `lead.delete_leadactivity` permission |

---

## Model Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Auto-generated |
| `lead` | int (FK, read-only) | Auto-set from URL |
| `activity_type` | string | Type of activity (see options below) |
| `title` | string | Activity title/summary |
| `description` | text | Detailed description |
| `activity_at` | datetime | When the activity occurred |
| `performed_by` | int (FK, read-only) | Auto-set to requesting user |
| `performed_by_name` | string (read-only) | Performer display name |
| `metadata` | JSON | Extra data (e.g., old/new values for status change) |
| `branch` | int (FK) | Branch ID |
| `created_at` | datetime (read-only) | Created timestamp |

**`activity_type` options:**

| Value | Label |
|-------|-------|
| `call` | Call |
| `whatsapp` | WhatsApp |
| `note` | Note |
| `meeting` | Meeting |
| `status_change` | Status Change |
| `assignment_change` | Assignment Change |
| `demo_class` | Demo Class |
| `payment` | Payment |
| `enrollment` | Enrollment |

### Auto-updates on Lead

When an activity is created, the parent lead is automatically updated:

| Lead field | Effect |
|------------|--------|
| `last_contact_at` | Set to `activity_at` if newer than existing value |
| `lead_score` | Recalculated (engagement factor) |

---

## POST `/api/leads/{lead_id}/activities/` — Add Activity

**Request:**
```json
{
    "activity_type": "call",
    "title": "Intro call with Rahul",
    "description": "Discussed course options and pricing",
    "activity_at": "2026-07-21T12:00:00Z",
    "metadata": {"duration_minutes": 15}
}
```

For status change activities, include old/new values in `metadata`:
```json
{
    "activity_type": "status_change",
    "title": "Status changed to Follow Up",
    "description": "Moved from New to Follow Up",
    "activity_at": "2026-07-21T12:00:00Z",
    "metadata": {
        "old_status": 1,
        "new_status": 2,
        "old_status_name": "New",
        "new_status_name": "Follow Up"
    }
}
```

---

## GET `/api/leads/{lead_id}/activities/` — List Activities

**Query params:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `activity_type` | string | Filter by type |
| `activity_at__gte` | datetime | After date |
| `activity_at__lte` | datetime | Before date |
| `ordering` | string | Order by `activity_at` (prefix `-` for desc) |
| `page` | int | Page number |
| `page_size` | int | Items per page (max 100) |

**Examples:**
```
GET /api/leads/1/activities/?activity_type=whatsapp
GET /api/leads/1/activities/?activity_at__gte=2026-07-01T00:00:00Z
```

---

## PATCH `/api/leads/{lead_id}/activities/{id}/` — Update

```json
{
    "description": "Updated notes after second discussion"
}
```

---

## DELETE `/api/leads/{lead_id}/activities/{id}/` — Delete

**Response:** `204 No Content`
