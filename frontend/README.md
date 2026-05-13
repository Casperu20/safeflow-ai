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
