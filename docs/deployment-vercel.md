# Vercel deployment

Deploy this repository as two Vercel projects so the Vite site and FastAPI API can be configured independently while sharing the same GitHub repository.

## API project

1. Import `1prc/NITC-CCC-Mail-tracker` into Vercel.
2. Set **Root Directory** to `backend` and deploy. Vercel detects the FastAPI application in `app/main.py`.
3. Add these Production environment variables in Project Settings:
   - `DATABASE_URL`: Neon connection string for the `production` branch.
   - `JWT_SECRET_KEY`: a unique random value at least 24 characters long.
   - `FRONTEND_ORIGIN`: the deployed frontend origin, for example `https://your-frontend.vercel.app`.
   - `APP_ENV`: `production`.
   - `ACCESS_TOKEN_MINUTES`: `30`.
4. Redeploy after adding the environment variables. Verify `/health` and `/docs` on the API deployment.

## Frontend project

1. Import the same GitHub repository as a second Vercel project.
2. Set **Root Directory** to `frontend`. Use the Vite framework preset, `npm run build`, and `dist` as the output directory.
3. Add the Production environment variable `VITE_API_BASE_URL` with the API deployment origin followed by `/api/v1`, for example `https://your-api.vercel.app/api/v1`.
4. Deploy and check the schedule, faculty login, and admin login against the production API.

If the frontend's production domain changes, update `FRONTEND_ORIGIN` on the API project and redeploy it. For preview deployments, add the relevant preview origins to the comma-separated `FRONTEND_ORIGIN` value if previews need API access.

## Gmail worker

The request-driven FastAPI Vercel deployment does not run the mailbox poller. The repository's `.github/workflows/mailbox-poller.yml` runs `backend/worker.py --once` every five minutes and can also be started manually from GitHub Actions. Configure these encrypted repository Actions secrets: `DATABASE_URL`, `GMAIL_MAILBOX`, `GMAIL_ALLOWED_SENDERS`, `GMAIL_CLIENT_SECRET_JSON`, and `GMAIL_TOKEN_JSON`. OAuth files are written only to the temporary runner workspace. Do not commit OAuth client secrets or token files. The first worker run establishes a current UID baseline without importing mailbox history; later runs process new mail read-only with `BODY.PEEK`.

Never commit production environment values. Configure API settings in Vercel's Environment Variables and mailbox worker credentials in GitHub Actions Secrets.
