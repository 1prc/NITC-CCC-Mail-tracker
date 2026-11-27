# NITC CCC Terminal Booking Tracker

<p align="center">
  **A Smart Room Availability and Booking Management System for NIT Calicut**
</p>

<p align="center">
  A web-based platform to monitor Central Computer Centre (CCC) room availability, track terminal bookings, and manage reservations through an interactive 30-minute timeline.
</p>

---

## Overview

The **NITC CCC Terminal Booking Tracker** is a web application designed to simplify room availability monitoring and terminal booking management at the National Institute of Technology Calicut (NITC).

The platform allows users to browse room availability for **1–4 weeks**, monitor terminals T1–T6, and manage bookings using a structured 30-minute time-slot system.

The project aims to provide a centralized, transparent, and convenient interface for managing CCC terminal reservations.

## Key Features

- **Room Availability Tracking:** Browse room availability for up to four weeks.
- **Terminal Management:** Track bookings across terminals T1–T6.
- **Interactive Timeline:** View reservations through a 30-minute time-slot interface.
- **Booking Management:** Support booking workflows and reservation tracking.
- **Email Integration:** Gmail integration using IMAP and OAuth 2.0 XOAUTH2.
- **Role-Based Dashboard:** Provide dashboard functionality based on user roles.
- **Centralized Database:** Store booking and application data using PostgreSQL.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite, JavaScript |
| Styling | Tailwind CSS |
| Backend | Python, FastAPI |
| API Architecture | REST API |
| Database | PostgreSQL (Neon) |
| ORM | SQLAlchemy |
| Email Integration | Gmail IMAP |
| Authentication | OAuth 2.0 XOAUTH2 |
| Deployment | Vercel |

## System Architecture

The application follows a frontend-backend architecture.

```text
          Users
            |
            v
     React + Vite
      Frontend
            |
            v
      FastAPI Backend
            |
       +----+-----+
       |          |
       v          v
   PostgreSQL   Gmail IMAP
    (Neon)      OAuth 2.0
       |
       v
 Booking & Availability Data
```

## Project Structure

```text
NITC-CCC-Mail-tracker/
│
├── frontend/                 # React + Vite application
│
├── backend/                  # FastAPI backend
│   └── .env.example          # Environment configuration template
│
├── docs/
│   ├── architecture.md       # System architecture
│   ├── development.md        # Development and setup guide
│   ├── roadmap.md            # Project milestone roadmap
│   └── deployment-vercel.md  # Vercel deployment guide
│
└── README.md
```

## Local Development

### Prerequisites

Make sure the following tools are installed:

- Python
- Node.js and npm
- PostgreSQL or a Neon PostgreSQL account
- Git

### Setup Instructions

**1. Clone the repository**

```bash
git clone https://github.com/1prc/NITC-CCC-Mail-tracker.git
cd NITC-CCC-Mail-tracker
```

**2. Configure environment variables**

Copy the backend environment template:

```bash
cp backend/.env.example backend/.env
```

Update the environment variables with your local database credentials and required application configuration.

**3. Install dependencies and run the application**

Follow the frontend and backend installation commands provided in:

[Development and Runbook](docs/development.md)

## Deployment

The application uses separate deployment projects for the frontend and backend.

- **Frontend:** Vercel
- **Backend:** Vercel
- **Database:** Neon PostgreSQL

For detailed deployment instructions, refer to:

[Deployment Guide](docs/deployment-vercel.md)

## Project Documentation

Explore the documentation for more information:

- [Architecture Plan](docs/architecture.md)
- [Development Guide](docs/development.md)
- [Milestone Roadmap](docs/roadmap.md)
- [Vercel Deployment Guide](docs/deployment-vercel.md)

## Security

- Keep environment variables in `.env` files.
- Never commit OAuth client credentials.
- Never expose Gmail access or refresh tokens.
- Use secure OAuth 2.0 authentication.
- Protect database credentials and sensitive application configuration.

## Future Improvements

- Enhanced booking analytics and reporting.
- Real-time booking availability updates.
- Improved notification and email tracking.
- Better administrative controls.
- Enhanced user experience and responsive dashboard.

## Contributing

Contributions, suggestions, and bug reports are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Open a Pull Request.

---

<p align="center">
  **Developed for NIT Calicut**
</p>

<p align="center">
  NITC CCC Terminal Booking Tracker
</p>
