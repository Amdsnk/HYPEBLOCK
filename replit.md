# HYPEBLOCK on Replit

## Preview

The `HYPEBLOCK Preview` workflow starts the FastAPI backend on port 8000 and
the React frontend on port 5000. Open the Replit Preview to view the app.

When `MONGO_URL` is not configured, the backend uses an in-memory demo store
seeded from `backend/merged_collection.json`. This is enough to preview the
collection, filters, detail pages, renders, and wallpaper pack. Waitlist
entries are temporary in this mode and reset when the backend restarts.

For persistent waitlist and collection data, configure `MONGO_URL` and
`DB_NAME`; the backend will use MongoDB automatically instead of demo mode.