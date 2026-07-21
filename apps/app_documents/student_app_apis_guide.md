# Student App — API Guide

## Overview

The Student app manages student profiles. Students do **not** have login accounts — they are managed entirely by staff/users. Each student gets an auto-generated `student_id` (format: `STU-{year}-{seq:04d}`).

**Base URL:** `http://localhost:8188`

---

## Student Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/students/` | List students (paginated) | Authenticated |
| POST | `/api/students/` | Create a student | Staff or `student.add_student` permission |
| GET | `/api/students/{id}/` | Get student detail | Authenticated |
| PUT | `/api/students/{id}/` | Full update | Staff or `student.change_student` permission |
| PATCH | `/api/students/{id}/` | Partial update | Staff or `student.change_student` permission |
| DELETE | `/api/students/{id}/` | Delete student | Staff or `student.delete_student` permission |
| GET | `/api/students/export_csv/` | Export filtered students to CSV | Authenticated |

---

### POST `/api/students/` — Create Student

`student_id` is auto-generated — do not send it.

**Request:**
```json
{
    "full_name": "Sita Pandey",
    "phone": "9876543210",
    "email": "sita@example.com",
    "date_of_birth": "2000-05-15",
    "gender": "female",
    "address": "Baneshwor, Kathmandu",
    "city": "Kathmandu",
    "state": "Bagmati",
    "guardian_name": "Ram Pandey",
    "guardian_phone": "9841234567",
    "guardian_relation": "Father",
    "emergency_contact_name": "Shyam Pandey",
    "emergency_contact_phone": "9812345678",
    "source": 1,
    "lead": 1,
    "branch": 1,
    "assigned_counselor": 1,
    "enrolled_at": "2026-07-21",
    "status": "active",
    "photo_url": "https://pub-xxx.r2.dev/uploads/photo.jpg",
    "notes": "Enrolled in Python course"
}
```

**`gender` options:** `male`, `female`, `other`

**`status` options:**

| Value | Label |
|-------|-------|
| `active` | Active |
| `inactive` | Inactive |
| `graduated` | Graduated |
| `dropped` | Dropped |
| `transferred` | Transferred |

**Response `201 Created`:**
```json
{
    "id": 1,
    "source_name": "Website",
    "branch_name": "Kathmandu",
    "assigned_counselor_name": "Admin",
    "created_by_name": "Admin",
    "updated_by_name": null,
    "document_count": 0,
    "student_id": "STU-2026-0001",
    "full_name": "Sita Pandey",
    "phone": "9876543210",
    "secondary_phone": null,
    "email": "sita@example.com",
    "date_of_birth": "2000-05-15",
    "gender": "female",
    "address": "Baneshwor, Kathmandu",
    "city": "Kathmandu",
    "state": "Bagmati",
    "guardian_name": "Ram Pandey",
    "guardian_phone": "9841234567",
    "guardian_relation": "Father",
    "emergency_contact_name": null,
    "emergency_contact_phone": null,
    "enrolled_at": "2026-07-21",
    "status": "active",
    "photo_url": null,
    "notes": "Enrolled in Python course",
    "created_at": "2026-07-21T07:48:17Z",
    "updated_at": "2026-07-21T07:48:17Z",
    "source": 1,
    "lead": null,
    "branch": 1,
    "assigned_counselor": null,
    "created_by": 1,
    "updated_by": null
}
```

---

### GET `/api/students/` — List Students

**Query params:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `search` | string | Search across `student_id`, `full_name`, `phone`, `email`, `guardian_name`, `guardian_phone`, `notes` |
| `gender` | string | Filter by gender |
| `status` | string | Filter by status |
| `status__in` | string | Filter by multiple statuses (comma-separated) |
| `source` | int | Filter by source ID |
| `source__in` | string | Filter by multiple sources |
| `branch` | int | Filter by branch ID |
| `branch__in` | string | Filter by multiple branches |
| `assigned_counselor` | int | Filter by counselor user ID |
| `full_name` | string | Filter by name (icontains) |
| `phone` | string | Filter by phone (icontains) |
| `email` | string | Filter by email (icontains) |
| `guardian_name` | string | Filter by guardian name (icontains) |
| `notes` | string | Filter by notes (icontains) |
| `created_at__gte` | datetime | Created after |
| `created_at__lte` | datetime | Created before |
| `enrolled_at__gte` | date | Enrolled after |
| `enrolled_at__lte` | date | Enrolled before |
| `ordering` | string | Order by `id`, `student_id`, `full_name`, `status`, `enrolled_at`, `created_at`, `updated_at` (prefix `-` for desc) |
| `page` | int | Page number |
| `page_size` | int | Items per page (max 100) |

**Examples:**
```
GET /api/students/?search=STU-2026
GET /api/students/?status=active&branch=1
GET /api/students/?status__in=active,inactive
GET /api/students/?created_at__gte=2026-07-01T00:00:00Z
GET /api/students/?ordering=-enrolled_at
```

**List response (`200 OK`):**
```json
{
    "count": 1,
    "page_size": 10,
    "total_pages": 1,
    "current_page": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "student_id": "STU-2026-0001",
            "full_name": "Sita Pandey",
            "phone": "9876543210",
            "email": "sita@example.com",
            "gender": "female",
            "status": "active",
            "enrolled_at": "2026-07-21",
            "branch_name": "Kathmandu",
            "source_name": "Website",
            "assigned_counselor_name": "Admin",
            "created_by_name": "Admin",
            "created_at": "2026-07-21T07:48:17Z"
        }
    ]
}
```

---

### GET `/api/students/{id}/` — Get Student Detail

Full detail response including `document_count`, `guardian_*`, `emergency_contact_*`, `photo_url`, `notes`, `lead`, and all timestamps.

---

### PATCH `/api/students/{id}/` — Partial Update

```json
{
    "status": "inactive",
    "notes": "Student paused enrollment"
}
```

---

### DELETE `/api/students/{id}/` — Delete Student

**Response:** `204 No Content`

---

### GET `/api/students/export_csv/` — Export CSV

Exports the current filtered student list as a CSV file. Supports all query params above.

```
GET /api/students/export_csv/?status=active&ordering=-created_at
```

**Response:** `Content-Type: text/csv` with `Content-Disposition: attachment; filename="students.csv"`.

---

## Nested Endpoints

### Student Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/students/{student_id}/documents/` | List documents (paginated) |
| POST | `/api/students/{student_id}/documents/` | Add document |
| DELETE | `/api/students/{student_id}/documents/{id}/` | Delete document |

**POST `/api/students/{student_id}/documents/`**
```json
{
    "document_type": "Citizenship",
    "file": "https://pub-xxx.r2.dev/uploads/doc.pdf"
}
```

---

## Permission Model

| User type | Access |
|-----------|--------|
| **Staff** (`is_staff=True`) | Full CRUD on all student endpoints |
| **Regular user** with permissions | Limited by assigned Django permissions |
| **Regular user** no permissions | Read-only — can list and view students |

**Django permissions:** `student.add_student`, `student.change_student`, `student.delete_student`, `student.view_student`
