# NITC CCC Terminal Booking Tracker

A web application concept for viewing weekly availability and managing terminal bookings for NITC Central Computer Centre rooms T1–T6.

## Project status

Implementation now covers the initial setup, backend foundation, booking workflows, Gmail worker, and role-based dashboard. Live data workflows require MongoDB Atlas configuration. Read [the architecture plan](docs/architecture.md), [the development/runbook](docs/development.md), and [the milestone roadmap](docs/roadmap.md).

## Planned stack

- Frontend: React, Vite, Tailwind CSS, JavaScript
- API: Python, FastAPI, REST
- Data: MongoDB Atlas and PyMongo
- Mail integration: Gmail IMAP with OAuth 2.0 XOAUTH2, implemented with Python standard-library `imaplib` and `email`

## Local development

See [docs/development.md](docs/development.md) for setup and run commands. Copy `backend/.env.example` to `backend/.env` and set local values as needed. Never commit `.env`, OAuth client files, or token files.
