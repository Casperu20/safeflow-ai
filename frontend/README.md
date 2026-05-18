# SafeFlow AI Frontend

React + JavaScript + Vite frontend for the SafeFlow stack.

## Local Port

- Frontend dev server: `http://127.0.0.1:5173`

## Run

Use a separate terminal for the frontend:

```powershell
Set-Location frontend
npm install
$env:VITE_API_BASE_URL = "http://127.0.0.1:8000/api"
npm run dev
```

The frontend calls the backend API from `VITE_API_BASE_URL`. If the variable is missing, it falls back to `http://127.0.0.1:8000/api`.

## Auth And History Integration

- Login page calls `POST /api/auth/login`
- Sign-up page calls `POST /api/auth/register`
- Session restore calls `GET /api/auth/me`
- Logout calls `POST /api/auth/logout`
- History page calls `GET /api/analysis-history`
- Clicking a history item loads `GET /api/analysis-history/{analysisId}` and opens the existing result page

## Token Storage

For this MVP, the frontend stores the JWT and current user in `localStorage` so the session can survive a page refresh.

That is acceptable for local development, but it has an XSS trade-off. A production-hardened version should prefer httpOnly cookies or a stronger token/session strategy.
