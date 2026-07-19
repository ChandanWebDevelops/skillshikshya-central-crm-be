# Account App — API Guide

## Overview

The Account app manages users, groups (roles), permissions, and JWT-based authentication. Tokens are set as **httpOnly cookies** (not returned in the body) for secure, simple use.

**Base URL:** `http://localhost:8188`

---

## Authentication Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/auth/register/` | Register a new user & auto-login (sets cookies) | Admin or `account.add_user` permission |
| POST | `/api/auth/login/` | Login — sets `access_token` + `refresh_token` cookies | Public |
| POST | `/api/auth/refresh/` | Refresh access token (reads refresh cookie automatically) | Public |
| POST | `/api/auth/logout/` | Logout — blacklists refresh token & clears cookies | Authenticated |
| POST | `/api/auth/change-password/` | Change current user's password | Authenticated |
| POST | `/api/auth/forgot-password/` | Request password reset OTP via email | Public |
| POST | `/api/auth/verify-otp/` | Verify OTP for password reset | Public |
| POST | `/api/auth/reset-password/` | Reset password after OTP verification | Public |

> Login/Refresh/Logout are public or auto-authenticated via cookies. **Register requires admin or proper permission.**

---

### POST `/api/auth/register/` — Register & Auto-login

Creates a new user and immediately issues JWT tokens as cookies.

**Request:**
```json
{
    "name": "Ram Sharma",
    "email": "ram@skillskhikshya.com",
    "password": "securepass123",
    "phone": "9841234567",
    "designation": "Sales Executive",
    "daily_call_target_min": 50,
    "monthly_enrollment_target": "500000.00",
    "shift_start": "09:00:00",
    "shift_end": "18:00:00",
    "work_mon": true,
    "work_tue": true,
    "work_wed": true,
    "work_thu": true,
    "work_fri": true
}
```

Only `name`, `email`, and `password` are required — all other fields are optional.

**Response `201 Created`** — cookies set automatically:
```json
{
    "message": "Registration successful",
    "user": {
        "id": 1,
        "name": "Ram Sharma",
        "email": "ram@skillskhikshya.com",
        "daily_call_target_min": 50,
        "monthly_enrollment_target": "500000.00",
        "designation": "Sales Executive",
        "phone": "9841234567",
        "shift_start": "09:00:00",
        "shift_end": "18:00:00",
        "custom_weekly_offs": false,
        "work_sun": false,
        "work_mon": true,
        "work_tue": true,
        "work_wed": true,
        "work_thu": true,
        "work_fri": true,
        "work_sat": false,
        "exclude_from_calls": false,
        "exclude_from_enrollment": false,
        "is_active": true,
        "is_staff": false,
        "is_superuser": false,
        "groups": [],
        "last_login": null
    }
}
```

**Cookies set (httpOnly, path=/):**
| Cookie | Value |
|--------|-------|
| `access_token` | JWT access token (1hr expiry) |
| `refresh_token` | JWT refresh token (7 day expiry) |

> `password` is **write-only** — never returned. `is_staff` and `is_superuser` cannot be set via registration.
>
> **Auth required:** Only admins (`is_staff=True`) or users with `account.add_user` permission can register new users. Send `Authorization: Bearer <token>` or use existing session cookies.

---

### POST `/api/auth/login/` — Login

**Request:**
```json
{
    "email": "admin@skillskhikshya.com",
    "password": "admin123"
}
```

**Response `200 OK`** — cookies set automatically:
```json
{
    "message": "Login successful",
    "user": {
        "id": 1,
        "name": "Admin",
        "email": "admin@skillskhikshya.com",
        "is_staff": true,
        "is_superuser": true,
        "groups": [1],
        "user_permissions": []
    }
}
```

### POST `/api/auth/refresh/` — Refresh Token

The refresh token is automatically read from the `refresh_token` cookie. No body needed.

**Request:** *(empty body or `{}`)*

**Response `200 OK`** — new `access_token` cookie set:
```json
{
    "message": "Token refreshed"
}
```

### POST `/api/auth/logout/` — Logout

The refresh token is automatically read from the `refresh_token` cookie, blacklisted, and both cookies are cleared.

**Request:** *(empty body)*

**Response `200 OK`:**
```json
{
    "message": "Logged out successfully"
}
```

---

### POST `/api/auth/change-password/` — Change Password

Updates the authenticated user's password. Requires the old password for verification.

**Headers:**
```
Content-Type: application/json
```
*(Auth via cookies — no Bearer header needed)*

**Request:**
```json
{
    "old_password": "currentPassword123",
    "new_password": "newSecurePass456",
    "confirm_new_password": "newSecurePass456"
}
```

**Response `200 OK`:**
```json
{
    "detail": "Password changed successfully."
}
```

A confirmation email is sent asynchronously via Celery.

**Error responses:**
- `400` — Old password is incorrect
- `400` — New passwords do not match

---

### POST `/api/auth/forgot-password/` — Request OTP

Sends a 6-digit OTP to the user's email for password reset. Always returns the same response (whether the email exists or not) to prevent email enumeration.

**Request:**
```json
{
    "email": "user@skillskhikshya.com"
}
```

**Response `200 OK`:**
```json
{
    "detail": "If this email exists, an OTP has been sent."
}
```

The OTP email uses a **green theme** with **Skill Shikshya** branding. OTPs expire in **15 minutes**.

---

### POST `/api/auth/verify-otp/` — Verify OTP

Validates the OTP sent to the user's email. Must be called before resetting the password.

**Request:**
```json
{
    "email": "user@skillskhikshya.com",
    "otp": "483921"
}
```

**Response `200 OK`:**
```json
{
    "detail": "OTP verified successfully."
}
```

**Error responses:**
- `400` — Invalid or expired OTP

---

### POST `/api/auth/reset-password/` — Reset Password

Resets the password after successful OTP verification. Requires the same email used in `verify-otp`.

**Request:**
```json
{
    "email": "user@skillskhikshya.com",
    "new_password": "newSecurePass456",
    "confirm_new_password": "newSecurePass456"
}
```

**Response `200 OK`:**
```json
{
    "detail": "Password reset successfully."
}
```

**Error responses:**
- `400` — OTP not verified or expired
- `400` — New passwords do not match
- `404` — User not found

---

## User Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/users/` | List users (paginated) | All authenticated |
| ~~POST~~ | ~~`/api/users/`~~ | ~~Create user~~ | **Disabled — use `/api/auth/register/`** |
| GET | `/api/users/{id}/` | Get user detail | Self or staff |
| PUT | `/api/users/{id}/` | Full update | Staff only |
| PATCH | `/api/users/{id}/` | Partial update | Self or staff |
| DELETE | `/api/users/{id}/` | Delete user | Staff only |

**Rules:**
- **Staff users** (`is_staff=True`) → see & manage all users
- **Regular users** → only see/update their own profile
- `is_staff` & `is_superuser` are **read-only** in the API (set via Django admin or `createsuperuser`)
- Results are paginated (default 20 per page, use `?page=2&page_size=50`)

### GET `/api/users/` — List Users

**Response `200 OK` (paginated):**
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Ram Sharma",
            "email": "ram@skillskhikshya.com",
        "daily_call_target_min": 50,
        "monthly_enrollment_target": "500000.00",
        "designation": "Sales Executive",
            "phone": "9841234567",
            "shift_start": "09:00:00",
            "shift_end": "18:00:00",
            "custom_weekly_offs": false,
            "work_sun": false,
            "work_mon": true,
            "work_tue": true,
            "work_wed": true,
            "work_thu": true,
            "work_fri": true,
            "work_sat": false,
            "exclude_from_calls": false,
            "exclude_from_enrollment": false,
            "is_active": true,
            "is_staff": false,
            "is_superuser": false,
            "last_login": null
        }
    ]
}
```

**Query params:** `?page=1&page_size=20`

### PATCH `/api/users/{id}/` — Partial Update (assign groups)

```json
{
    "groups": [2],
    "daily_call_target_min": 75
}
```

When `groups` is set, the user is assigned to those permission groups (replaces any existing group memberships).

### DELETE `/api/users/{id}/` — Delete User

**Response:** `204 No Content`

---

## Group (Role) Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/groups/` | List groups (paginated) | Admin only |
| POST | `/api/groups/` | Create a new role group | Admin only |
| GET | `/api/groups/{id}/` | Get group detail | Admin only |
| PUT | `/api/groups/{id}/` | Full update group | Admin only |
| PATCH | `/api/groups/{id}/` | Partial update group | Admin only |
| DELETE | `/api/groups/{id}/` | Delete group | Admin only |

> Only **admin users** (`is_staff=True`) can manage groups.

### POST `/api/groups/` — Create a Role Group

**Request:**
```json
{
    "name": "Sales Manager",
    "permissions": [1, 2, 3]
}
```

**Response `201 Created`:**
```json
{
    "id": 1,
    "name": "Sales Manager",
    "permissions": [1, 2, 3]
}
```

### PATCH `/api/groups/{id}/` — Update Group Permissions

```json
{
    "permissions": [1, 2, 3, 4, 5]
}
```

---

## Permission Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/permissions/` | List all permissions (paginated) | Admin only |

### GET `/api/permissions/` — List Permissions

```json
{
    "count": 100,
    "results": [
        {
            "id": 1,
            "name": "Can add user",
            "codename": "add_user",
            "content_type": 7,
            "content_type_name": "account.User"
        }
    ]
}
```

Use the `id` from here when assigning permissions to a group.

---

## Permission Model Summary

| User type | Access |
|-----------|--------|
| **Staff** (`is_staff=True`) | Full access — all CRUD on users, groups, permissions |
| **Regular user** with groups | Limited by their groups' assigned Django permissions |
| **Regular user** no groups | Can only view/update their own profile |

- `groups` is a **M2M** field — users can belong to multiple groups
- Non-staff users **cannot** change their own `is_staff` or `is_superuser`

---

## Complete Workflow

### 1. Create Superuser

```bash
docker compose exec web python manage.py createsuperuser
# Email: admin@skillskhikshya.com
# Name: Admin
# Password: admin123
```

### 2. Admin: Login

```
POST http://localhost:8188/api/auth/login/
Content-Type: application/json

{
    "email": "admin@skillskhikshya.com",
    "password": "admin123"
}
```

### 3. Admin: Register a New User

```
POST http://localhost:8188/api/auth/register/
Content-Type: application/json

{
    "name": "Sita Poudel",
    "email": "sita@skillskhikshya.com",
    "password": "sita@123",
    "phone": "9876543210",
    "designation": "Call Agent",
    "daily_call_target_min": 40,
    "monthly_enrollment_target": "300000.00",
    "shift_start": "10:00:00",
    "shift_end": "19:00:00",
    "work_mon": true,
    "work_tue": true,
    "work_wed": true,
    "work_thu": true,
    "work_fri": true
}
```

Cookies are set automatically on success.

### 4. Admin: Create Role Group & Assign Permissions

```
POST http://localhost:8188/api/groups/
Content-Type: application/json

{
    "name": "Call Agent",
    "permissions": [37, 38, 39]
}
```

### 5. Admin: Assign Groups to User

```
PATCH http://localhost:8188/api/users/2/
Content-Type: application/json

{
    "groups": [1],
    "designation": "Senior Call Agent"
}
```

To assign multiple groups: `"groups": [1, 2, 3]`

### 6. List Users (paginated)

```
GET http://localhost:8188/api/users/?page=1&page_size=10
```

### 7. Change Password

```
POST http://localhost:8188/api/auth/change-password/
Content-Type: application/json

{
    "old_password": "currentPassword123",
    "new_password": "newSecurePass456",
    "confirm_new_password": "newSecurePass456"
}
```

### 8. Forgot Password (OTP flow)

**Step 1 — Request OTP:**
```
POST http://localhost:8188/api/auth/forgot-password/
Content-Type: application/json

{
    "email": "sita@skillskhikshya.com"
}
```

**Step 2 — Verify OTP:**
```
POST http://localhost:8188/api/auth/verify-otp/
Content-Type: application/json

{
    "email": "sita@skillskhikshya.com",
    "otp": "483921"
}
```

**Step 3 — Reset Password:**
```
POST http://localhost:8188/api/auth/reset-password/
Content-Type: application/json

{
    "email": "sita@skillskhikshya.com",
    "new_password": "newSecurePass456",
    "confirm_new_password": "newSecurePass456"
}
```

### 9. Refresh Token

```
POST http://localhost:8188/api/auth/refresh/
```

### 10. Logout

```
POST http://localhost:8188/api/auth/logout/
```

---

## Postman Test Flow

### Setup

1. Open Postman → New Collection → **Skillshikshya CRM**
2. Go to Collection **Variables** tab:

| Variable | Initial Value |
|----------|--------------|
| `base_url` | `http://localhost:8188` |
| `user_id` | *(leave empty)* |
| `group_id` | *(leave empty)* |

> **Cookies handled automatically** — Postman stores/sends them after login/register.

### Enable Cookie Handling
1. Click **Cookies** (top-right under "Send")
2. Add `localhost:8188` to domain list

---

### 1. Admin Login

- **Method:** POST
- **URL:** `{{base_url}}/api/auth/login/`
- **Body:**
  ```json
  {
      "email": "admin@skillskhikshya.com",
      "password": "admin123"
  }
  ```

**Tests:**
```javascript
pm.test("Admin login", function () {
    pm.response.to.have.status(200);
    var json = pm.response.json();
    pm.expect(json.user).to.have.property("groups");
});
```

### 2. Admin: Register a New User

- **Method:** POST
- **URL:** `{{base_url}}/api/auth/register/`
- **Headers:**
  - `X-CSRFTOKEN`: *(leave empty — cookies handle auth)*
- **Body (raw JSON):**
  ```json
  {
      "name": "Test User",
      "email": "test@skillskhikshya.com",
      "password": "test123",
      "designation": "Agent",
      "daily_call_target_min": 30,
      "monthly_enrollment_target": "200000.00",
      "shift_start": "09:00:00",
      "shift_end": "18:00:00"
  }
  ```

**Tests tab:**
```javascript
pm.test("Registration successful", function () {
    pm.response.to.have.status(201);
    var json = pm.response.json();
    pm.expect(json.message).to.eql("Registration successful");
    pm.expect(json.user.email).to.eql("test@skillskhikshya.com");
    pm.collectionVariables.set("user_id", json.user.id);
});
```

### 3. List Users

- **Method:** GET
- **URL:** `{{base_url}}/api/users/`

**Tests:**
```javascript
pm.test("Paginated users", function () {
    pm.response.to.have.status(200);
    pm.expect(pm.response.json()).to.have.property("results");
    pm.expect(pm.response.json()).to.have.property("count");
});
```

### 4. Create Role Group

- **Method:** POST
- **URL:** `{{base_url}}/api/groups/`
- **Body:**
  ```json
  {
      "name": "Call Agent",
      "permissions": []
  }
  ```

**Tests:**
```javascript
pm.test("Group created", function () {
    pm.response.to.have.status(201);
    pm.collectionVariables.set("group_id", pm.response.json().id);
});
```

### 5. Assign Groups to User

- **Method:** PATCH
- **URL:** `{{base_url}}/api/users/{{user_id}}`
- **Body:**
  ```json
  {
      "groups": [{{group_id}}]
  }
  ```

**Tests:**
```javascript
pm.test("Groups assigned", function () {
    pm.response.to.have.status(200);
});
```

### 6. Get Single User

- **Method:** GET
- **URL:** `{{base_url}}/api/users/{{user_id}}`

### 7. Change Password

- **Method:** POST
- **URL:** `{{base_url}}/api/auth/change-password/`
- **Body (raw JSON):**
  ```json
  {
      "old_password": "test123",
      "new_password": "newTestPass456",
      "confirm_new_password": "newTestPass456"
  }
  ```

**Tests:**
```javascript
pm.test("Password changed", function () {
    pm.response.to.have.status(200);
    pm.expect(pm.response.json().detail).to.eql("Password changed successfully.");
});
```

### 8. Forgot Password — Request OTP

- **Method:** POST
- **URL:** `{{base_url}}/api/auth/forgot-password/`
- **Body:**
  ```json
  {
      "email": "test@skillskhikshya.com"
  }
  ```

**Tests:**
```javascript
pm.test("OTP sent", function () {
    pm.response.to.have.status(200);
});
```

### 10. Refresh Token

- **Method:** POST
- **URL:** `{{base_url}}/api/auth/refresh/`

**Tests:**
```javascript
pm.test("Token refreshed", function () {
    pm.response.to.have.status(200);
});
```

### 11. Logout

- **Method:** POST
- **URL:** `{{base_url}}/api/auth/logout/`

**Tests:**
```javascript
pm.test("Logged out", function () {
    pm.response.to.have.status(200);
    pm.expect(pm.response.json().message).to.eql("Logged out successfully");
});
```

### Folder Structure in Postman

```
Skillshikshya CRM
├── Auth
│   ├── Register
│   ├── Login
│   ├── Refresh Token
│   ├── Logout
│   ├── Change Password
│   ├── Forgot Password (Request OTP)
│   ├── Verify OTP
│   └── Reset Password
├── Users
│   ├── List Users
│   ├── Get User
│   ├── Assign Groups (PATCH)
│   └── Delete User
└── Roles & Permissions
    ├── Create Role Group
    ├── List Groups
    └── List Permissions
```
