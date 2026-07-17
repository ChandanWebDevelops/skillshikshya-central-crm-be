# Account App — API Guide

## Overview

The Account app manages users, roles (groups), permissions, and JWT-based authentication. Tokens are set as **httpOnly cookies** (not returned in the body) for secure, simple use.

**Base URL:** `http://localhost:8188`

---

## Authentication (Cookie-based JWT)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login/` | Login — sets `access_token` + `refresh_token` cookies |
| POST | `/api/auth/refresh/` | Refresh access token (reads refresh cookie automatically) |
| POST | `/api/auth/logout/` | Logout — blacklists refresh token & clears cookies |

> **No `Authorization: Bearer` header needed.** The `access_token` cookie is sent automatically by the browser. For tools like Postman, cookies are stored and sent automatically after login.

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
    "message": "Login successful"
}
```

**Cookies set (httpOnly, path=/):**
| Cookie | Value |
|--------|-------|
| `access_token` | JWT access token (1hr expiry) |
| `refresh_token` | JWT refresh token (7 day expiry) |

### POST `/api/auth/refresh/` — Refresh Token

The refresh token is automatically read from the `refresh_token` cookie. No body needed.

**Request:** *(empty body or send `{}`)*

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

## User Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/users/` | List users (paginated) | All authenticated |
| POST | `/api/users/` | Create user | Staff |
| GET | `/api/users/{id}/` | Get user detail | Self or staff |
| PUT | `/api/users/{id}/` | Full update | Self or staff |
| PATCH | `/api/users/{id}/` | Partial update | Self or staff |
| DELETE | `/api/users/{id}/` | Delete user | Staff only |

**Rules:**
- **Staff users** (`is_staff=True`) → see & manage all users
- **Regular users** → only see/update their own profile
- `is_staff` & `is_superuser` are **read-only** in the API (set via Django admin or `createsuperuser`)
- Results are paginated (default 20 per page, use `?page=2&page_size=50`)

### POST `/api/users/` — Create User

**Request:**
```json
{
    "name": "Ram Sharma",
    "email": "ram@skillskhikshya.com",
    "password": "securepass123",
    "role": null,
    "daily_call_target_min": 50,
    "monthly_sales_target": "500000.00",
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
    "exclude_from_sales": false,
    "is_active": true
}
```

> `is_staff` and `is_superuser` cannot be set here. Only `role` (group FK), not `groups` or `user_permissions`.

**Response `201 Created`:**
```json
{
    "id": 1,
    "name": "Ram Sharma",
    "email": "ram@skillskhikshya.com",
    "role": null,
    "daily_call_target_min": 50,
    "monthly_sales_target": "500000.00",
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
    "exclude_from_sales": false,
    "is_active": true,
    "is_staff": false,
    "is_superuser": false,
    "last_login": null
}
```

> `password` is **write-only** — never returned.

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
            "role": null,
            "daily_call_target_min": 50,
            "monthly_sales_target": "500000.00",
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
            "exclude_from_sales": false,
            "is_active": true,
            "is_staff": false,
            "is_superuser": false,
            "last_login": null
        }
    ]
}
```

**Query params:** `?page=1&page_size=20`

### PATCH `/api/users/{id}/` — Partial Update (assign role)

```json
{
    "role": 2,
    "daily_call_target_min": 75
}
```

When `role` is set, the user is automatically added to that group's permissions.

### DELETE `/api/users/{id}/` — Delete User

**Response:** `204 No Content`

---

## Role (Group) Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/groups/` | List groups (paginated) | Admin only |
| POST | `/api/groups/` | Create a new role group | Admin only |
| GET | `/api/groups/{id}/` | Get group detail | Admin only |
| PUT | `/api/groups/{id}/` | Full update group | Admin only |
| PATCH | `/api/groups/{id}/` | Partial update group | Admin only |
| DELETE | `/api/groups/{id}/` | Delete group | Admin only |

> Only **admin users** (`is_staff=True`) can manage groups. Regular users see nothing here.

### POST `/api/groups/` — Create a Role Group

**Request:**
```json
{
    "name": "Sales Manager",
    "permissions": [1, 2, 3]
}
```

`permissions` is a list of permission IDs to assign to this group.

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

**Response:**
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
| **Staff** (`is_staff=True`) | Full access — all CRUD on users, groups, permissions, config |
| **Regular user** with role | Limited by their `role` group's assigned Django permissions |
| **Regular user** no role | Can only view/update their own profile |

- `role` FK → auto-synced to Django's `groups` M2M for permission checking
- Non-staff users **cannot** change their own `role`, `is_staff`, or `is_superuser`

---

## Complete Workflow

### 1. Create Superuser

```bash
docker compose exec web python manage.py createsuperuser
# Email: admin@skillskhikshya.com
# Name: Admin
# Password: admin123
```

### 2. Login (cookies set automatically)

```
POST http://localhost:8188/api/auth/login/
Content-Type: application/json

{
    "email": "admin@skillskhikshya.com",
    "password": "admin123"
}
```

### 3. Create a Role Group with Permissions

```
POST http://localhost:8188/api/groups/
Content-Type: application/json

{
    "name": "Call Agent",
    "permissions": [37, 38, 39]
}
```

### 4. Create a User with that Role

```
POST http://localhost:8188/api/users/
Content-Type: application/json

{
    "name": "Sita Poudel",
    "email": "sita@skillskhikshya.com",
    "password": "sita@123",
    "role": 1,
    "designation": "Call Agent",
    "daily_call_target_min": 40,
    "monthly_sales_target": "300000.00",
    "shift_start": "10:00:00",
    "shift_end": "19:00:00",
    "work_mon": true,
    "work_tue": true,
    "work_wed": true,
    "work_thu": true,
    "work_fri": true
}
```

### 5. List Users (paginated)

```
GET http://localhost:8188/api/users/?page=1&page_size=10
```

### 6. Update a User's Role

```
PATCH http://localhost:8188/api/users/2/
Content-Type: application/json

{
    "role": 2,
    "designation": "Senior Call Agent"
}
```

### 7. Refresh Token

```
POST http://localhost:8188/api/auth/refresh/
```

### 8. Logout

```
POST http://localhost:8188/api/auth/logout/
```

---

## Postman Test Flow

### Setup

1. Open Postman → New Collection → **Skillshikshya CRM**
2. Go to Collection **Variables** tab and add:

| Variable | Initial Value |
|----------|--------------|
| `base_url` | `http://localhost:8188` |
| `user_id` | *(leave empty)* |

> **No need for `access_token`/`refresh_token` variables.** Postman manages cookies automatically.

### Enable Cookie Handling in Postman

1. Click the **Cookies** button (top-right under "Send")
2. Add `localhost:8188` to the domain list
3. Postman will automatically store and send cookies for all requests

### 1. Login

- **Method:** POST
- **URL:** `{{base_url}}/api/auth/login/`
- **Body (raw JSON):**
  ```json
  {
      "email": "admin@skillskhikshya.com",
      "password": "admin123"
  }
  ```

**Tests tab:**
```javascript
pm.test("Login successful", function () {
    pm.response.to.have.status(200);
    pm.expect(pm.response.json().message).to.eql("Login successful");
});
```

### 2. Create Role Group

- **Method:** POST
- **URL:** `{{base_url}}/api/groups/`
- **Body (raw JSON):**
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

### 3. Create User

- **Method:** POST
- **URL:** `{{base_url}}/api/users/`
- **Body (raw JSON):**
  ```json
  {
      "name": "Test User",
      "email": "test@skillskhikshya.com",
      "password": "test123",
      "role": null,
      "designation": "Agent",
      "daily_call_target_min": 30,
      "monthly_sales_target": "200000.00",
      "shift_start": "09:00:00",
      "shift_end": "18:00:00"
  }
  ```

**Tests:**
```javascript
pm.test("User created", function () {
    pm.response.to.have.status(201);
    pm.collectionVariables.set("user_id", pm.response.json().id);
});
```

### 4. List Users

- **Method:** GET
- **URL:** `{{base_url}}/api/users/`

**Tests:**
```javascript
pm.test("Users list paginated", function () {
    pm.response.to.have.status(200);
    pm.expect(pm.response.json()).to.have.property("results");
    pm.expect(pm.response.json()).to.have.property("count");
});
```

### 5. Get Single User

- **Method:** GET
- **URL:** `{{base_url}}/api/users/{{user_id}}`

### 6. Assign Role to User (PATCH)

- **Method:** PATCH
- **URL:** `{{base_url}}/api/users/{{user_id}}`
- **Body (raw JSON):**
  ```json
  {
      "role": {{group_id}}
  }
  ```

**Tests:**
```javascript
pm.test("Role assigned", function () {
    pm.response.to.have.status(200);
    pm.expect(pm.response.json().role).to.eql(parseInt(pm.collectionVariables.get("group_id")));
});
```

### 7. Delete User

- **Method:** DELETE
- **URL:** `{{base_url}}/api/users/{{user_id}}`
- **Expected status:** `204 No Content`

### 8. Refresh Token

- **Method:** POST
- **URL:** `{{base_url}}/api/auth/refresh/`

**Tests:**
```javascript
pm.test("Token refreshed", function () {
    pm.response.to.have.status(200);
});
```

### 9. Logout

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
│   ├── Login
│   ├── Refresh Token
│   └── Logout
├── Users
│   ├── Create User
│   ├── List Users
│   ├── Get User
│   ├── Assign Role (PATCH)
│   └── Delete User
└── Roles & Permissions
    ├── Create Role Group
    ├── List Groups
    └── List Permissions
```
