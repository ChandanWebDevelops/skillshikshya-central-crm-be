# Course App — API Guide

## Overview

The Course app manages course offerings including courses, master classes, and job-ready programs.

**Base URL:** `http://localhost:8188`

---

**Branch scoping:** See [Lead App Overview](lead_app_overview.md#branch-scoping) for details. All course endpoints support `?branch_id=X`.

## Course Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/courses/` | List courses (paginated) | Authenticated |
| POST | `/api/courses/` | Create a new course | Staff or `course.add_course` permission |
| GET | `/api/courses/{id}/` | Get course detail | Authenticated |
| PUT | `/api/courses/{id}/` | Full update | Staff or `course.change_course` permission |
| PATCH | `/api/courses/{id}/` | Partial update | Staff or `course.change_course` permission |
| DELETE | `/api/courses/{id}/` | Delete course | Staff or `course.delete_course` permission |

---

### POST `/api/courses/` — Create Course

**Request:**
```json
{
    "course_type": "course",
    "name": "Python Programming",
    "full_amount": "50000.00",
    "one_time_payment_discount": "5000.00",
    "syllabus": "https://syllabi.example.com/python.pdf",
    "remarks": "Comprehensive Python course"
}
```

**`course_type` options:**
| Value | Label |
|-------|-------|
| `course` | Course |
| `master_class` | Master Class |
| `job_ready_program` | Job Ready Program |

**Response `201 Created`:**
```json
{
    "id": 1,
    "course_type": "course",
    "name": "Python Programming",
    "full_amount": "50000.00",
    "one_time_payment_discount": "5000.00",
    "syllabus": "https://syllabi.example.com/python.pdf",
    "remarks": "Comprehensive Python course"
}
```

---

### GET `/api/courses/` — List Courses

**Query params:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `search` | string | Search across `name`, `remarks` |
| `name` | string | Filter by name (icontains) |
| `course_type` | string | Filter by type (`course`, `master_class`, `job_ready_program`) |
| `ordering` | string | Order by `id`, `name`, `full_amount`, `course_type` (prefix `-` for desc) |
| `page` | int | Page number |
| `page_size` | int | Items per page (max 100) |

**Examples:**

```
GET /api/courses/?search=python
GET /api/courses/?course_type=master_class
GET /api/courses/?ordering=-full_amount
GET /api/courses/?search=django&course_type=course&ordering=name
```

**Response `200 OK` (paginated):**
```json
{
    "count": 2,
    "page_size": 10,
    "total_pages": 1,
    "current_page": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "course_type": "course",
            "name": "Python Programming",
            "full_amount": "50000.00",
            "one_time_payment_discount": "5000.00",
            "syllabus": "https://syllabi.example.com/python.pdf",
            "remarks": "Comprehensive Python course"
        }
    ]
}
```

---

### GET `/api/courses/{id}/` — Get Course Detail

**Response `200 OK`:**
```json
{
    "id": 1,
    "course_type": "course",
    "name": "Python Programming",
    "full_amount": "50000.00",
    "one_time_payment_discount": "5000.00",
    "syllabus": "https://syllabi.example.com/python.pdf",
    "remarks": "Comprehensive Python course"
}
```

---

### PATCH `/api/courses/{id}/` — Partial Update

```json
{
    "full_amount": "45000.00",
    "one_time_payment_discount": "4500.00"
}
```

---

### DELETE `/api/courses/{id}/` — Delete Course

**Response:** `204 No Content`

---

## Permission Model

| User type | Access |
|-----------|--------|
| **Staff** (`is_staff=True`) | Full CRUD on courses, batches, and course batches |
| **Regular user** with permissions | Limited by their assigned Django permissions (`course.add_course`, `course.change_course`, `course.delete_course`) |
| **Regular user** no permissions | Read-only — can list and view |

---

## Batch Endpoints

The `Batch` model represents time slots such as Morning, Day, Evening, etc.

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/batches/` | List batches (paginated) | Authenticated |
| POST | `/api/batches/` | Create a new batch | Staff or `course.add_batch` permission |
| GET | `/api/batches/{id}/` | Get batch detail | Authenticated |
| PUT | `/api/batches/{id}/` | Full update | Staff or `course.change_batch` permission |
| PATCH | `/api/batches/{id}/` | Partial update | Staff or `course.change_batch` permission |
| DELETE | `/api/batches/{id}/` | Delete batch | Staff or `course.delete_batch` permission |

### Batch Fields

| Field | Type | Notes |
|-------|------|-------|
| `id` | int | Auto |
| `name` | string | e.g. Morning, Day, Evening |
| `description` | string (nullable) | Optional |
| `is_active` | boolean | Default `true` |
| `branch` | FK (nullable) | Branch scoping |
| `created_by` | FK (read-only) | Set automatically |

### POST `/api/batches/` — Create Batch

**Request:**
```json
{
    "name": "Morning",
    "description": "Morning time slot",
    "is_active": true
}
```

**Response `201 Created`** (id, name, description, is_active, created_at, updated_at, branch, created_by).

### GET `/api/batches/` — List Batches

**Query params:** `search` (name, description), `name` (icontains), `is_active`, `ordering` (id, name), `page`, `page_size`.

**Examples:**
```
GET /api/batches/?search=morning
GET /api/batches/?is_active=true
GET /api/batches/?ordering=name
```

---

## Course Batch Endpoints

The `CourseBatch` model represents a specific run of a course (a named cohort with start/end dates tied to a batch time slot).

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/course-batches/` | List course batches (paginated) | Authenticated |
| POST | `/api/course-batches/` | Create a new course batch | Staff or `course.add_coursebatch` permission |
| GET | `/api/course-batches/{id}/` | Get course batch detail | Authenticated |
| PUT | `/api/course-batches/{id}/` | Full update | Staff or `course.change_coursebatch` permission |
| PATCH | `/api/course-batches/{id}/` | Partial update | Staff or `course.change_coursebatch` permission |
| DELETE | `/api/course-batches/{id}/` | Delete course batch | Staff or `course.delete_coursebatch` permission |

### Course Batch Fields

| Field | Type | Notes |
|-------|------|-------|
| `id` | int | Auto |
| `name` | string | Human-readable cohort name |
| `coursebatch_id` | string (read-only) | Auto-generated like `PY-2026-001` |
| `course` | FK (required) | The course being run |
| `batch` | FK (nullable) | The time slot (Morning/Day/Evening) |
| `start_date` | date (nullable) | Cohort start |
| `end_date` | date (nullable) | Cohort end |
| `is_active` | boolean | Default `true` |
| `branch` | FK (nullable) | Branch scoping |
| `created_by` | FK (read-only) | Set automatically |
| `course_name` | string (read-only) | Display name of course |
| `batch_name` | string (read-only) | Display name of batch |

### `coursebatch_id` auto-generation

When omitted, `coursebatch_id` is derived from the course name initials, the current year, and a sequential counter:

`{PREFIX}-{YEAR}-{SEQ:03d}`

Example: creating a "Python Programming" cohort in 2026 generates `PY-2026-001`, then `PY-2026-002`, etc.

**Uniqueness:** a course cannot have the same batch + start_date combination twice (`unique_together` on `course`, `batch`, `start_date`).

### POST `/api/course-batches/` — Create Course Batch

**Request:**
```json
{
    "name": "Python Bootcamp",
    "course": 1,
    "batch": 1,
    "start_date": "2026-09-01",
    "end_date": "2026-12-31"
}
```

**Response `201 Created`:**
```json
{
    "id": 1,
    "name": "Python Bootcamp",
    "coursebatch_id": "PY-2026-001",
    "course": 1,
    "course_name": "Python Programming",
    "batch": 1,
    "batch_name": "Morning",
    "start_date": "2026-09-01",
    "end_date": "2026-12-31",
    "is_active": true,
    "branch": null,
    "created_by": null,
    "created_at": "2026-08-05T17:30:00Z",
    "updated_at": "2026-08-05T17:30:00Z"
}
```

### GET `/api/course-batches/` — List Course Batches

**Query params:** `search` (name, coursebatch_id), `name`, `coursebatch_id` (icontains), `course` (FK id), `batch` (FK id), `start_date`, `end_date`, `is_active`, `ordering` (id, name, coursebatch_id, start_date, end_date), `page`, `page_size`.

**Examples:**
```
GET /api/course-batches/?course=1
GET /api/course-batches/?batch=2
GET /api/course-batches/?search=PY-2026-001
GET /api/course-batches/?ordering=-start_date
```
