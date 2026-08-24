# Lead App — Calls API Guide

**Base URL:** `http://localhost:8188`

## Endpoints

All endpoints are nested under a specific lead.

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/leads/{lead_id}/calls/` | List calls (paginated) | Authenticated |
| POST | `/api/leads/{lead_id}/calls/` | Add a call (consumes call minutes) | Staff or `lead.add_leadcall` permission |
| GET | `/api/leads/{lead_id}/calls/{id}/` | Get call detail | Authenticated |
| PATCH | `/api/leads/{lead_id}/calls/{id}/` | Update call notes/outcome etc. | Staff or `lead.change_leadcall` permission |

> **DELETE is disabled** — call records are permanent and cannot be deleted via the API (`405 Method Not Allowed`), so the call-minutes ledger stays trustworthy.

The `lead` field is auto-set from the URL. `created_by` is auto-set to the requesting user.

## Call Minutes Deduction

Creating a call **deducts minutes from the requesting user's balance**:

- Minutes charged = `duration_seconds // 60` (completed minutes only — e.g. 9m30s = 9 minutes), minimum 1 minute per call.
- If the balance is lower than the required minutes, the call is **rejected** with:
  ```json
  { "detail": "Insufficient call minutes (required 2, available 0)." }
  ```
- On success, the response includes two extra fields: `minutes_used` and `remaining_minutes`.
- Every deduction writes a row in the immutable ledger (see [Call Minutes](account_app_apis_guide.md#call-minutes)).
- `duration_seconds` and `caller` are **locked after creation** — PATCH requests silently ignore changes to them.

**Example POST response (201):**
```json
{
    "id": 21,
    "duration_seconds": 90,
    "minutes_used": 2,
    "remaining_minutes": 8,
    "...": "…other standard fields…"
}
```

---

## Model Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Auto-generated |
| `lead` | int (FK, read-only) | Auto-set from URL |
| `call_timestamp` | datetime | When the call occurred |
| `direction` | string | `inbound` or `outbound` |
| `caller` | string | Caller name |
| `phone_number` | string | Phone number called/received |
| `duration_seconds` | int | Duration in seconds |
| `outcome` | string | Call outcome description |
| `notes` | text | Notes |
| `recording_url` | string | URL to call recording |
| `next_followup_at` | datetime | Suggested next followup time |
| `next_action` | text | Suggested next action |
| `branch` | int (FK) | Branch ID |
| `created_by` | int (FK, read-only) | Auto-set |
| `created_by_name` | string (read-only) | Creator display name |
| `created_at` | datetime (read-only) | Created timestamp |

### Auto-updates on Lead

When a call is created, the parent lead is automatically updated:

| Lead field | Effect |
|------------|--------|
| `last_contact_at` | Set to `call_timestamp` if newer than existing value |
| `lead_score` | Recalculated (engagement factor) |

---

## POST `/api/leads/{lead_id}/calls/` — Add a Call

**Request:**
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

`direction` options: `inbound`, `outbound`

---

## GET `/api/leads/{lead_id}/calls/` — List Calls

**Query params:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `direction` | string | Filter by direction (`inbound`, `outbound`) |
| `call_timestamp__gte` | datetime | Called after |
| `call_timestamp__lte` | datetime | Called before |
| `ordering` | string | Order by `call_timestamp`, `duration_seconds` (prefix `-` for desc) |
| `page` | int | Page number |
| `page_size` | int | Items per page (max 100) |

**Examples:**
```
GET /api/leads/1/calls/?direction=inbound
GET /api/leads/1/calls/?call_timestamp__gte=2026-07-01T00:00:00Z
GET /api/leads/1/calls/?ordering=-call_timestamp
```

---

## PATCH `/api/leads/{lead_id}/calls/{id}/` — Update Call

```json
{
    "outcome": "Demo scheduled for July 25",
    "next_followup_at": "2026-07-25T10:00:00Z"
}
```

---

## DELETE `/api/leads/{lead_id}/calls/{id}/` — Delete Call

**Response:** `204 No Content`
