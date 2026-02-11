# Fraud Detection Platform

An end-to-end fraud detection system with hybrid (Rules + ML) scoring, case management, and advanced analytics.

## Tech Stack
- **Frontend**: Next.js, Tailwind CSS, React Query, Recharts
- **Backend**: FastAPI, SQLAlchemy, Scikit-learn
- **Database**: SQLite (Local) / PostgreSQL (Production)

## Deployment on Vercel

This project is configured for deployment on Vercel as a monorepo.

### Prerequisites
1. A Vercel account.
2. A managed PostgreSQL database (e.g., Supabase, Neon, or Vercel Postgres).

### Environment Variables
Set the following environment variables in your Vercel project settings:

**Frontend:**
- `NEXT_PUBLIC_API_URL`: The URL of your deployed backend (e.g., `https://your-app.vercel.app/api`).

**Backend:**
- `DATABASE_URL`: Your production database connection string (e.g., `postgresql://user:password@host:port/dbname`).

### Steps
1. Connect your GitHub repository to Vercel.
2. Vercel will automatically detect the `vercel.json` and deploy both the frontend and the backend.
3. Once deployed, update `NEXT_PUBLIC_API_URL` to point to the production URL.

## Local Development
1. **Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

