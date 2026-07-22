# Lead App — Course Interests API Guide

**Base URL:** `http://localhost:8188`

## Endpoints

All endpoints are nested under a specific lead.

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/leads/{lead_id}/course-interests/` | List interests (paginated) | Authenticated |
| POST | `/api/leads/{lead_id}/course-interests/` | Add interest | Staff or `lead.add_leadcourseinterest` permission |
| GET | `/api/leads/{lead_id}/course-interests/{id}/` | Get detail | Authenticated |
| PATCH | `/api/leads/{lead_id}/course-interests/{id}/` | Update | Staff or `lead.change_leadcourseinterest` permission |
| DELETE | `/api/leads/{lead_id}/course-interests/{id}/` | Delete | Staff or `lead.delete_leadcourseinterest` permission |

---

## Model Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Auto-generated |
| `lead` | int (FK, read-only) | Auto-set from URL |
| `course` | int (FK) | Course ID |
| `course_name` | string (read-only) | Course display name |
| `is_primary` | bool | Whether this is the lead's primary course interest |
| `interest_level` | string | `high`, `medium`, `low` |
| `created_at` | datetime (read-only) | |

---

## POST `/api/leads/{lead_id}/course-interests/` — Add Interest

**Request:**
```json
{
    "course": 1,
    "is_primary": true,
    "interest_level": "high"
}
```

---

## PATCH `/api/leads/{lead_id}/course-interests/{id}/` — Update

```json
{
    "interest_level": "medium"
}
```

---

## GET `/api/leads/{lead_id}/course-interests/` — List

**Query params:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `course` | int | Filter by course ID |
| `is_primary` | bool | Filter primary only |
| `interest_level` | string | Filter by level |
| `page` | int | Page number |
| `page_size` | int | Items per page (max 100) |

---

## DELETE `/api/leads/{lead_id}/course-interests/{id}/` — Delete

**Response:** `204 No Content`
