# Branch App — API Guide

## Overview

The Branch app manages physical/branch office locations.

**Base URL:** `http://localhost:8188`

---

**Branch scoping:** Branches themselves are not branch-scoped (they are the source of the scoping). See [Lead App Overview](lead_app_overview.md#branch-scoping) for how branches are used for scoping other resources.

## Branch Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/branches/` | List branches (paginated) | Authenticated |
| POST | `/api/branches/` | Create a branch | Staff or `branch.add_branch` permission |
| GET | `/api/branches/{id}/` | Get branch detail | Authenticated |
| PUT | `/api/branches/{id}/` | Full update | Staff or `branch.change_branch` permission |
| PATCH | `/api/branches/{id}/` | Partial update | Staff or `branch.change_branch` permission |
| DELETE | `/api/branches/{id}/` | Delete branch | Staff or `branch.delete_branch` permission |

---

### POST `/api/branches/` — Create Branch

**Request:**
```json
{
    "name": "Kathmandu",
    "code": "KTM",
    "address": "Maitidevi, Kathmandu",
    "phone": "01-4512345",
    "email": "kathmandu@skillshikshya.com"
}
```

**Response `201 Created`:**
```json
{
    "id": 1,
    "name": "Kathmandu",
    "code": "KTM",
    "address": "Maitidevi, Kathmandu",
    "phone": "01-4512345",
    "email": "kathmandu@skillshikshya.com",
    "is_active": true,
    "created_at": "2026-07-21T07:00:03.490175Z",
    "updated_at": "2026-07-21T07:00:03.490190Z"
}
```

---

### GET `/api/branches/` — List Branches

**Query params:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `search` | string | Search across `name`, `code`, `address` |
| `name` | string | Filter by name (icontains) |
| `code` | string | Filter by code (icontains) |
| `is_active` | bool | Filter by active status |
| `ordering` | string | Order by `id`, `name`, `code`, `is_active` (prefix `-` for desc) |
| `page` | int | Page number |
| `page_size` | int | Items per page (max 100) |

---

### PATCH `/api/branches/{id}/` — Update Branch

```json
{
    "is_active": false
}
```

---

### DELETE `/api/branches/{id}/` — Delete Branch

**Response:** `204 No Content`
