# Lead App — API Overview

## Base URL

`http://localhost:8188`

---

## Branch Scoping

All endpoints support branch-level filtering via the `branch_id` query parameter.

| User type | Behavior |
|-----------|----------|
| **Staff / Superuser** | Can see data across all branches by default. Pass `?branch_id=X` to filter. |
| **Non-staff with branch** | Automatically scoped to their assigned branch — cannot see data from other branches. |
| **Non-staff without branch** | See all data (no restriction). |

The `branch_id` parameter works on every list endpoint.

**Examples:**
```
GET /api/leads/?branch_id=1
GET /api/courses/?branch_id=2
GET /api/lead-sources/?branch_id=1
GET /api/students/?branch_id=1&status=active
```

---

## Permission Model

| User type | Access |
|-----------|--------|
| **Staff** (`is_staff=True`) | Full CRUD on all endpoints + permanent purge |
| **Regular user** with permissions | Limited by assigned Django permissions |
| **Regular user** no permissions | Read-only — can list and view |

**Django permissions:**
- `lead.add_lead`, `lead.change_lead`, `lead.delete_lead`, `lead.view_lead`
- `lead.add_leadsource`, `lead.change_leadsource`, `lead.delete_leadsource`, `lead.view_leadsource`
- `lead.add_campaign`, `lead.change_campaign`, `lead.delete_campaign`, `lead.view_campaign`
- `lead.add_leadstatus`, `lead.change_leadstatus`, `lead.delete_leadstatus`, `lead.view_leadstatus`
- `lead.add_leadpriority`, `lead.change_leadpriority`, `lead.delete_leadpriority`, `lead.view_leadpriority`
- `lead.add_leadtag`, `lead.change_leadtag`, `lead.delete_leadtag`, `lead.view_leadtag`
- `lead.add_leadtype`, `lead.change_leadtype`, `lead.delete_leadtype`, `lead.view_leadtype`
- `lead.add_learningmode`, `lead.change_learningmode`, `lead.delete_learningmode`, `lead.view_learningmode`
- `lead.add_institution`, `lead.change_institution`, `lead.delete_institution`, `lead.view_institution`
- `lead.add_province`, `lead.change_province`, `lead.delete_province`, `lead.view_province`
- `lead.add_city`, `lead.change_city`, `lead.delete_city`, `lead.view_city`
- `lead.add_leadcall`, `lead.change_leadcall`, `lead.delete_leadcall`, `lead.view_leadcall`
- `lead.add_leadactivity`, `lead.change_leadactivity`, `lead.delete_leadactivity`, `lead.view_leadactivity`
- `lead.add_followup`, `lead.change_followup`, `lead.delete_followup`, `lead.view_followup`
- `lead.add_leaddocument`, `lead.change_leaddocument`, `lead.delete_leaddocument`, `lead.view_leaddocument`
- `lead.add_leadcourseinterest`, `lead.change_leadcourseinterest`, `lead.delete_leadcourseinterest`, `lead.view_leadcourseinterest`
- `lead.add_enrollment`, `lead.change_enrollment`, `lead.delete_enrollment`, `lead.view_enrollment`
- `lead.add_payment`, `lead.change_payment`, `lead.delete_payment`, `lead.view_payment`
- `lead.add_notification`, `lead.change_notification`, `lead.delete_notification`, `lead.view_notification`

---

## Configuration / Lookup Endpoints

All config endpoints follow the same pattern. Config models are **not** nested — they live at the top level.

- **GET** — List (paginated), any authenticated user
- **POST** — Create, staff or `<app>.add_*` permission required
- **GET/PUT/PATCH/DELETE** — By ID, mutation requires staff or `<app>.change_*`/`<app>.delete_*` permission

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

Lead scores use the status `sort_order` — statuses closer to the max (excluding `is_final`) contribute more to the lead score. `is_final` statuses (like "Lost") result in `lead_score = 0`.

**Query params:** `?search=new&is_active=true&is_final=false`

### Lead Priorities

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/lead-priorities/` | List priorities |
| POST | `/api/lead-priorities/` | Create priority |
| GET/PUT/PATCH/DELETE | `/api/lead-priorities/{id}/` | CRUD |

**Fields:** `id`, `name`, `color` (hex), `sort_order`, `is_active`

Lead score uses `sort_order` — priority 1 (highest) gives the most points.

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

## Learning Mode & Institution Endpoints

### Course Interests from External Intake

The external intake endpoint accepts course interests as plain text names — not IDs:

| Field | Format | Example |
|-------|--------|---------|
| `course_interests` | `array` of strings | `["Python Advanced", "Flutter"]` |
| `course` | `string` (singular, alternative) | `"Python Advanced"` |
| `courses` | `string` (comma-separated, alternative) | `"Python Advanced, Flutter"` |

**How it's stored:**

| Scenario | `course` (FK) | `course_name` (fallback) |
|---|---|---|
| Name matches an existing course in the CRM | Linked to matched course | `null` |
| Name does NOT match any course | `null` | Stores the raw submitted name |

The `course_name` field on the response always shows the correct display name regardless of how it was stored.

---

### Learning Modes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/learning-modes/` | List learning modes |
| POST | `/api/learning-modes/` | Create learning mode |
| GET/PUT/PATCH/DELETE | `/api/learning-modes/{id}/` | CRUD |

**Fields:** `id`, `name`, `code` (unique), `is_active`

**Query params:** `?search=online&name=Online&code=ONLINE&is_active=true`

**Default examples:** Online, Offline, Hybrid

### Institutions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/institutions/` | List institutions |
| POST | `/api/institutions/` | Create institution |
| GET/PUT/PATCH/DELETE | `/api/institutions/{id}/` | CRUD |

**Fields:** `id`, `name`, `code` (unique), `address`, `phone`, `is_active`

**Query params:** `?search=tribhuvan&name=university&code=TU&phone=01&is_active=true`

---

## Location Endpoints

### Provinces

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/provinces/` | List provinces |
| POST | `/api/provinces/` | Create province |
| GET/PUT/PATCH/DELETE | `/api/provinces/{id}/` | CRUD |

**Fields:** `id`, `name`, `code`, `is_active`

**Query params:** `?search=bag&name=bagmati&is_active=true`

### Cities

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cities/` | List cities |
| POST | `/api/cities/` | Create city |
| GET/PUT/PATCH/DELETE | `/api/cities/{id}/` | CRUD |

**Fields:** `id`, `name`, `province` (FK), `province_name` (read), `is_active`

**Query params:** `?search=kath&province=1&is_active=true`

---

## Public Lead Intake

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/public/lead-intake/` | Create a lead from external forms | Public (no auth) |

This endpoint allows unauthenticated lead creation from external websites, landing pages, etc.

**Request:**
```json
{
    "full_name": "Rahul Sharma",
    "phone": "9812345678",
    "email": "rahul@example.com",
    "source_name": "Website",
    "heard_from": "Google Ads",
    "course_interests": [1, 2],
    "custom_data": {
        "preferred_learning_mode": "online",
        "preferred_shift": "evening"
    }
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `full_name` | Yes | Lead's full name |
| `phone` | Yes | Contact phone |
| `email` | No | Email address |
| `source_name` | No | Matches `LeadSource.name` (case-insensitive). If no match, source is set to null. |
| `heard_from` | No | Free-text "how did you hear about us" |
| `course_interests` | No | Array of course IDs |
| `custom_data` | No | Any extra fields as JSON object |

**Response `201 Created`:**
```json
{
    "id": 1,
    "reference_number": "LD-2026-000001",
    "full_name": "Rahul Sharma",
    "phone": "9812345678"
}
```

---

## Related Documents

| Guide | Description |
|-------|-------------|
| [Lead API Guide](lead_app_lead_api_guide.md) | Lead CRUD, actions, lead_score |
| [Calls API Guide](lead_app_calls_api_guide.md) | LeadCall endpoints |
| [Activities API Guide](lead_app_activities_api_guide.md) | LeadActivity endpoints |
| [Followups API Guide](lead_app_followup_api_guide.md) | FollowUp endpoints |
| [Documents API Guide](lead_app_documents_api_guide.md) | LeadDocument endpoints |
| [Course Interests API Guide](lead_app_course_interests_api_guide.md) | LeadCourseInterest endpoints |
| [Enrollments & Payments API Guide](lead_app_enrollments_payments_api_guide.md) | Enrollment + Payment endpoints |
| [Global List Endpoints API Guide](lead_app_global_list_api_guide.md) | Flat cross-lead lists for followups, enrollments, payments |
| [Notifications API Guide](lead_app_notifications_api_guide.md) | Notification endpoints |
