# NITC CCC Terminal Booking Tracker

A web application for viewing and tracking room availability at the **NIT Calicut Central Computer Centre (CCC)**. The application is designed to help users browse terminal availability across **T1–T6**, view schedules over 1–4 weeks, and manage bookings using a 30-minute time-slot timeline.

## 🚀 Live Demo

**Live Application:** https://nitc-ccc-tracker-web.vercel.app/

Explore the deployed application to see the project interface.

## ✨ Key Features

- **Room Availability:** Browse availability for CCC terminals T1–T6.
- **Flexible Scheduling:** View schedules for 1–4 weeks.
- **30-Minute Time Slots:** Track bookings on a detailed timeline.
- **Booking Management:** Support for managing terminal bookings.
- **Email Integration:** Gmail integration using OAuth 2.0.
- **Role-Based Dashboard:** Dashboard functionality based on user roles.

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite, JavaScript |
| Styling | Tailwind CSS |
| Backend | Python, FastAPI |
| API | REST |
| Database | PostgreSQL |
| Database Hosting | Neon PostgreSQL |
| ORM | SQLAlchemy |
| Email Integration | Gmail IMAP |
| Authentication | OAuth 2.0 XOAUTH2 |
| Frontend Deployment | Vercel |
| Backend Deployment | Vercel |

## 🏗️ Project Architecture

The application follows a frontend-backend architecture:

- **Frontend:** React and Vite provide the user interface.
- **Backend:** FastAPI handles API requests and application logic.
- **Database:** PostgreSQL stores application data.
- **Email Worker:** Python's `imaplib` and `email` libraries support Gmail IMAP integration using OAuth 2.0 XOAUTH2.
- **Deployment:** Frontend and FastAPI API are deployed as separate Vercel projects.

## 📂 Project Documentation

For more information about the project, refer to:

- [Architecture Plan](docs/architecture.md)
- [Development Guide](docs/development.md)
- [Milestone Roadmap](docs/roadmap.md)
- [Vercel Deployment Guide](docs/deployment-vercel.md)

## 💻 Local Development

Follow these steps to run the project locally.

### Prerequisites

Make sure you have installed:

- Node.js and npm
- Python
- PostgreSQL database or a Neon PostgreSQL connection

### Setup

**1. Clone the repository**

```bash
git clone https://github.com/1prc/NITC-CCC-Mail-tracker.git
```

**2. Navigate to the project directory**

```bash
cd NITC-CCC-Mail-tracker
```

**3. Configure environment variables**

Copy the backend environment example file:

```bash
cp backend/.env.example backend/.env
```

Update `backend/.env` with your local configuration and required credentials.

**4. Install dependencies and start the application**

Refer to the [Development Guide](docs/development.md) for the exact installation commands and instructions for running the frontend, backend, and Gmail worker.

## 🔐 Environment Variables and Security

- Never commit `.env` files.
- Never upload Gmail OAuth client secrets or token files.
- Keep database credentials and API secrets private.
- Use environment variables for sensitive configuration.
- Configure production environment variables separately in Vercel.

## ☁️ Deployment

The frontend and backend are deployed as separate Vercel projects from this repository.

For deployment instructions, configuration, and environment variables, see:

[**Vercel Deployment Guide**](docs/deployment-vercel.md)

## 🗺️ Project Status

The implementation covers the initial setup, backend foundation, booking workflows, Gmail worker, and role-based dashboard.

The database target is Neon PostgreSQL.

For implementation progress and upcoming milestones, see the [Milestone Roadmap](docs/roadmap.md).

## 🤝 Contributing

Contributions, suggestions, and improvements are welcome.

1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Submit a pull request.

## 👨‍💻 Author

**Himanshu Mourya**

M.Tech – Computer Science and Information Security  
National Institute of Technology Calicut

GitHub: https://github.com/1prc

---

<p align="center">
  <b>NITC CCC Terminal Booking Tracker</b><br/>
  Built to make computer centre terminal booking and availability tracking easier.
</p>
