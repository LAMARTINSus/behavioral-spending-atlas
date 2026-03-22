# Behavioral Spending Atlas™ Sample App — Render Deployment Version

This package is prepared for deployment on Render as a Python web service.

## What is included
- Mobile-first Flask app
- 36-question Behavioral Spending Atlas assessment
- Creator attribution through the incoming URL
- Name capture
- Social platform selection + optional username
- Gender + age range capture
- Email capture
- Full free report screen
- CSV export for pilot results

## Creator attribution
Use links like:

- `https://your-render-url.onrender.com/?creator=luis`
- `https://your-render-url.onrender.com/?cid=luis`

The app will store the creator value with the session.

## Deploy on Render

### Option 1 — Fastest
1. Create a new GitHub repository.
2. Upload all files from this folder to that repository.
3. Log into Render.
4. Click **New +** → **Web Service**.
5. Connect your GitHub repo.
6. Render should detect:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
7. Add environment variable:
   - `FLASK_SECRET_KEY` = any long random string
8. Click **Create Web Service**.

### Option 2 — Using render.yaml
If Render detects `render.yaml`, it can prefill the service settings automatically.

## Notes about storage
This pilot app uses a local SQLite file:
- `bsa_sample.db`

That is acceptable for a small sample test, but Render disks on free services are not permanent in the same way as a managed database.
For a serious live rollout, migrate data storage to PostgreSQL.

## Export pilot data
Once deployed, you can export responses from:

`https://your-render-url.onrender.com/admin/export.csv`

## Local run
```bash
pip install -r requirements.txt
python app.py
```

## Production server
This deployment uses Gunicorn in production:

```bash
gunicorn app:app
```
