# Local Development

## Prerequisites

- Node.js and npm
- Python 3.11 or newer (the scaffold uses standard Python features and pinned-compatible package ranges)
- Git
- MongoDB Atlas connection details later, when database work starts

## Frontend

```powershell
cd "E:\NITC\SS lab\NITC CCC tracker\frontend"
npm install
npm run dev
```

Vite prints the local URL, normally `http://localhost:5173`. The development server proxies `/api` and `/health` to the local FastAPI server.

## Backend

```powershell
cd "E:\NITC\SS lab\NITC CCC tracker\backend"
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

The API is normally at `http://127.0.0.1:8000`; interactive docs are at `/docs` and liveness is at `/health`. For the backend foundation, set `MONGODB_URI` in `backend/.env` to your Atlas connection string. Run the idempotent initial data setup from the backend directory with `py -m scripts.bootstrap`. Set `BOOTSTRAP_ADMIN_PASSWORD` in `.env` if you want it to create the initial administrator. The script ensures rooms T1–T6 and will not overwrite an existing user.

## Configuration and secrets

Use `backend/.env` for local settings. The checked-in `.env.example` contains placeholders only. Never place OAuth credentials, tokens, database passwords, or real user passwords in source files or commit them. The Google OAuth client JSON provided by the user is for the later Gmail integration milestone; it is not read, copied, or used by this backend foundation.

## Foundation API

- `POST /api/v1/auth/login` accepts application username/password and returns a short-lived bearer token.
- `GET /api/v1/auth/me` returns the authenticated user's safe profile.
- `GET /api/v1/rooms` returns active rooms to authenticated users.
- `GET /health` is a non-sensitive liveness endpoint.

Public signup and user provisioning are not implemented. For now, the bootstrap script can create only the initial admin; faculty/student account management is a later auth milestone refinement.

## Gmail worker setup

The OAuth client file is not stored in this repository. Set `GMAIL_CLIENT_SECRET_FILE` to its protected absolute path in `backend/.env`, set `GMAIL_MAILBOX` to the exact authorized mailbox, and set `GMAIL_ALLOWED_SENDERS` to a comma-separated allowlist of official sender addresses. Leave the allowlist empty only in a controlled test mailbox. The requested `https://mail.google.com/` OAuth scope grants broad mailbox access; protect the client/token files and revoke access when no longer needed.

Run the worker from the backend directory with `py worker.py`. The first run establishes a current UID high-water baseline and does not import mailbox history. Subsequent polling occurs every 30 seconds using read-only selection and `BODY.PEEK`. The first authorization opens the Google consent flow. The generated token file must remain outside source control.

Supported plain-text booking format (labels are case-insensitive):

```text
Room: T1
Date: 2026-11-20
Start: 09:00
End: 11:00
Purpose: Example lab session
```

The date must be `YYYY-MM-DD`, and start/end times must be whole-hour IST values in the 08:00–20:00 window. Messages that do not match are retained in the admin email log as invalid; no full email body is displayed or stored.

## Admin-created user accounts

After signing in as administrator, create accounts with `POST /api/v1/admin/users` using `{ "username", "display_name", "password", "role" }`. Passwords must be at least 12 characters. Roles are `STUDENT`, `FACULTY`, or `ADMIN`. Do not send credentials over an insecure channel.

## Limitations at this stage

- Live API, worker, login, and data flows require a reachable MongoDB Atlas deployment and local `.env` configuration.
- Slot allocation uses unique MongoDB documents and compensating cleanup, not multi-document transactions. For stronger atomic guarantees, deploy on a transaction-capable Atlas replica set and convert booking lifecycle operations to transactions before production use.
- Gmail sender policy and exact official email template need confirmation with CCC. The parser is intentionally strict and deterministic.
- Initial bootstrap admin creation is optional and idempotent; changing an existing admin password is not supported by the bootstrap command.
- Cancellation email notifications and email-driven amendments are not implemented because requirements do not define their behavior.

## Current assumptions

`Asia/Kolkata` and 60-minute slots are provisional configuration defaults for development. Slot duration and booking rules require user confirmation before implementing the booking engine. The UI is only a setup preview and does not represent live availability.
