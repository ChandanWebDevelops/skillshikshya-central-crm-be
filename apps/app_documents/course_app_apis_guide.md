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
| **Staff** (`is_staff=True`) | Full CRUD on courses |
| **Regular user** with permissions | Limited by their assigned Django permissions (`course.add_course`, `course.change_course`, `course.delete_course`) |
| **Regular user** no permissions | Read-only — can list and view courses |
