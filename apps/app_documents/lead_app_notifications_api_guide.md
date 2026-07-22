# Lead App — Notifications API Guide

**Base URL:** `http://localhost:8188`

## Overview

Notifications are created automatically when a lead's `assigned_counselor` changes. Each notification is sent to the newly assigned counselor.

When a counselor is assigned:
1. An in-app `Notification` record is created
2. An email is sent to the counselor's email address (via Celery async task)

---

## Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/notifications/` | List notifications for current user | Authenticated (self only) |
| GET | `/api/notifications/{id}/` | Get notification detail | Authenticated (self only) |
| POST | `/api/notifications/{id}/mark_read/` | Mark single notification as read | Authenticated (self only) |
| POST | `/api/notifications/mark_all_read/` | Mark all notifications as read | Authenticated (self only) |
| GET | `/api/notifications/unread_count/` | Get unread count | Authenticated (self only) |

Users can only see their own notifications (auto-filtered by `user = request.user`).

---

## Model Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Auto-generated |
| `user` | int (FK) | Recipient user (auto-set to the new counselor) |
| `title` | string | Notification title |
| `message` | text | Notification body |
| `link` | string | URL linking to the lead (e.g., `/leads/1`) |
| `is_read` | bool | Read status |
| `created_at` | datetime | |

---

## GET `/api/notifications/` — List Notifications

**Query params:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `is_read` | bool | Filter by read status |
| `ordering` | string | Order by `created_at` (prefix `-` for desc) |
| `page` | int | Page number |
| `page_size` | int | Items per page (max 100) |

**Response:**
```json
{
    "count": 5,
    "results": [
        {
            "id": 1,
            "title": "New Lead Assigned",
            "message": "Lead LD-2026-000001 (Rahul Sharma) has been assigned to you.",
            "link": "/leads/1",
            "is_read": false,
            "created_at": "2026-07-21T12:00:00Z"
        }
    ]
}
```

---

## POST `/api/notifications/{id}/mark_read/` — Mark as Read

**Response:**
```json
{ "detail": "Notification marked as read." }
```

## POST `/api/notifications/mark_all_read/` — Mark All Read

**Response:**
```json
{ "detail": "All notifications marked as read." }
```

## GET `/api/notifications/unread_count/` — Unread Count

**Response:**
```json
{ "unread_count": 3 }
```

---

## Email Template

The email sent on counselor assignment uses an HTML template and includes:
- Lead name and reference number
- Phone number and email
- Source and campaign info
- Assigned course
- Link to view the lead in the frontend

## Required Environment Variables

| Variable | Purpose |
|----------|---------|
| `EMAIL_HOST` | SMTP server |
| `EMAIL_PORT` | SMTP port |
| `EMAIL_HOST_USER` | SMTP username |
| `EMAIL_HOST_PASSWORD` | SMTP password |
| `DEFAULT_FROM_EMAIL` | Sender email |
| `FRONTEND_URL` | Base URL for links in email |
