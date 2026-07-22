# Lead App — Documents API Guide

**Base URL:** `http://localhost:8188`

## Endpoints

All endpoints are nested under a specific lead.

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/leads/{lead_id}/documents/` | List documents (paginated) | Authenticated |
| POST | `/api/leads/{lead_id}/documents/` | Add document URL | Staff or `lead.add_leaddocument` permission |
| GET | `/api/leads/{lead_id}/documents/{id}/` | Get document detail | Authenticated |
| DELETE | `/api/leads/{lead_id}/documents/{id}/` | Delete document | Staff or `lead.delete_leaddocument` permission |

---

## Model Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Auto-generated |
| `lead` | int (FK, read-only) | Auto-set from URL |
| `document_type` | string | Type (e.g., "ID Proof", "Transcript") |
| `file` | string | Public URL of the document |
| `uploaded_by` | int (FK, read-only) | Auto-set to requesting user |
| `uploaded_by_name` | string (read-only) | Uploader display name |
| `branch` | int (FK) | Branch ID |
| `uploaded_at` | datetime (read-only) | |

---

## POST `/api/leads/{lead_id}/documents/` — Add Document

Use the [Upload API](upload_api_guide.md) first to upload the physical file, then store the returned URL.

**Request:**
```json
{
    "document_type": "ID Proof",
    "file": "https://pub-xxx.r2.dev/uploads/doc.pdf"
}
```

---

## GET `/api/leads/{lead_id}/documents/` — List Documents

**Query params:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `document_type` | string | Filter by type |
| `ordering` | string | Order by `uploaded_at` |
| `page` | int | Page number |
| `page_size` | int | Items per page (max 100) |

---

## DELETE `/api/leads/{lead_id}/documents/{id}/` — Delete

**Response:** `204 No Content`

> Note: Deletes only the database record, not the file from R2 storage.
