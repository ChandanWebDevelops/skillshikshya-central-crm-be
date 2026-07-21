# File Upload — API Guide

## Overview

A single global upload endpoint accepts files and stores them in Cloudflare R2 (S3-compatible object storage). Returns a public URL that can be saved on any model (Lead documents, Student documents, etc.).

Only the **URL** is stored on models — not the file itself.

**Base URL:** `http://localhost:8188`

---

## Upload Endpoint

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/upload/` | Upload a file | Authenticated (staff or permission not required) |

---

### POST `/api/upload/` — Upload File

**Headers:** *(multipart/form-data — cookies handle auth)*

**Request:**
```
POST /api/upload/
Content-Type: multipart/form-data

file: <binary file>
folder: uploads    (optional, default: "uploads")
```

**Allowed file types:**

| Type | MIME |
|------|------|
| JPEG | `image/jpeg` |
| PNG | `image/png` |
| GIF | `image/gif` |
| WebP | `image/webp` |
| PDF | `application/pdf` |
| CSV | `text/csv` |
| DOCX | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` |
| XLSX | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` |
| DOC | `application/msword` |
| XLS | `application/vnd.ms-excel` |
| TXT | `text/plain` |

**Limits:** Max file size is **10MB**.

**Response `201 Created`:**
```json
{
    "key": "uploads/a1b2c3d4e5f6g7h8i9j0.pdf",
    "url": "https://pub-3a712783614d44db9c5b349676a4cff8.r2.dev/uploads/a1b2c3d4e5f6g7h8i9j0.pdf",
    "filename": "original-name.pdf",
    "size": 123456
}
```

| Field | Description |
|-------|-------------|
| `key` | Object key in the R2 bucket |
| `url` | Public URL (can be stored on models) |
| `filename` | Original filename from upload |
| `size` | File size in bytes |

---

### Usage with Lead Documents

```json
{
    "document_type": "ID Proof",
    "file": "https://pub-xxx.r2.dev/uploads/a1b2c3d4e5f6g7h8i9j0.pdf"
}
```

### Usage with Student Documents

```json
{
    "document_type": "Transcript",
    "file": "https://pub-xxx.r2.dev/uploads/a1b2c3d4e5f6g7h8i9j0.pdf"
}
```

### Usage with photo_url

```json
{
    "photo_url": "https://pub-xxx.r2.dev/uploads/a1b2c3d4e5f6g7h8i9j0.jpg"
}
```

---

## File Proxy (Fallback)

If `R2_PUBLIC_URL` is not configured, files are served through a Django proxy:

`GET /api/files/{key}` — e.g., `/api/files/uploads/a1b2c3d4e5f6g7h8i9j0.pdf`

This endpoint is **unauthenticated** (for frontend display) and streams the file directly from R2.

**Response:** `200 OK` with `Content-Type` matching the uploaded file, `Content-Disposition: inline`.

**Errors:** `404` if the file does not exist in R2.
