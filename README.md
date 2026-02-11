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
Set the following environment variables in your Vercel project settings (or create a `.env` file for local development):

**Backend & General:**
- `DATABASE_URL`: Your production database connection string (e.g., `postgresql://user:password@host:port/dbname`). Defaults to local SQLite if not set.
- `SECRET_KEY`: A secret key for JWT authentication.
- `ALGORITHM`: The algorithm used for JWT (default: HS256).

**Frontend:**
- `NEXT_PUBLIC_API_URL`: The URL of your deployed backend (e.g., `https://your-app.vercel.app/api`).

### Troubleshooting: Serverless Function Size Limit
If you encounter a "Serverless Function has exceeded the unzipped maximum size of 250 MB" error, it's usually because large dependencies (like `pandas` or `scikit-learn`) or unnecessary files are being bundled.

This project handles this by:
1. Using `includeFiles` in `vercel.json` to only bundle essential backend code.
2. Optimizing `requirements.txt` to remove heavy development tools.
3. Keeping the ML model file size small (~1MB).

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

