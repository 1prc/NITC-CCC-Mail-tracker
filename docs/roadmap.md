# Development Roadmap

This plan follows the project's requested milestones. Milestones should be completed in order unless a dependency is explicitly resolved. Milestones 1–6 have implementation work in the repository. Live database-backed verification and production deployment remain dependent on external configuration.

| Milestone | Scope | Depends on | Completion evidence |
|---|---|---|---|
| 1. Architecture and planning | Requirements, architecture, target structure, data model, APIs, worker, security, roadmap, decisions, AGENTS.md | None | Completed; slot size and timezone confirmed. |
| 2. Project setup | Initialize React/Vite/Tailwind and FastAPI; environment examples; Git hygiene; Mongo config; docs/run instructions | Milestone 1 approval | Completed. |
| 3. Backend foundation | Mongo connection/index bootstrap, room seed, users, auth/RBAC, room and read APIs | Milestone 2 | Scaffold implemented; needs configured Atlas for live operation. |
| 4. Booking engine | Requests, approval/rejection/cancellation, availability, slot allocations, conflicts, audit | Milestone 3; slot size/timezone confirmed | Implemented with unique slot claims and compensating cleanup; transaction hardening remains. |
| 5. Gmail integration | OAuth, IMAP read-only UID polling, extraction, parser/validator, dedupe, logs, retries, controlled baseline | Milestones 3–4; mailbox/sender/template configuration | Implemented; first authorization and live mailbox validation remain. |
| 6. Frontend | Student availability, faculty request/history, admin review and email logs; API integration | Milestones 3–5 | Implemented; live API use requires Atlas. |
| 7. Integration and verification | End-to-end workflow, conflict/concurrency, auth boundaries, parser cases, failure handling, security review | Milestones 3–6; Atlas available | Local static/API checks done; Atlas-backed scenarios remain. |
| 8. Documentation and deployment | Installation, configuration, API, architecture, deployment, worker operations, backup/recovery | Milestones 2–7; deployment target decision | Local runbook present; production deployment target and transaction support remain. |

## Dependency notes

- Milestone 1 decisions about slot granularity, timezone, user provisioning, visibility, and email trust affect schema/API behavior and should be resolved before implementing the dependent logic.
- The API and worker must share booking rules. Implementing the booking service before the importer reduces divergence.
- The worker can be developed and run independently from FastAPI, but it depends on shared configuration, database setup, and booking services.
- The admin email-log UI depends on the log schema and endpoints from the email integration milestone.
- MongoDB transactions should be confirmed against the selected Atlas deployment before the booking engine relies on multi-document atomicity.
