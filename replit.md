# HYPEBLOCK

## Storage

The app does not require MongoDB. The FastAPI backend stores mutable data in
`backend/data/store.json` and writes it atomically, so waitlist entries survive
restarts on a traditional host. Set `HYPEBLOCK_DATA_FILE` if the host requires
the data file to live outside the application directory.

NFT metadata is seeded from `backend/merged_collection.json` on first start.
The existing art remains in `backend/generated`, and fallback source images
are stored in `backend/fallback_assets`; no runtime image requests depend on
MongoDB or external asset storage.

## Traditional hosting

Run the backend with Uvicorn from the project root:

```bash
pip install -r backend/requirements.txt
uvicorn backend.server:app --host 0.0.0.0 --port 8000
```

Build the React frontend with `cd frontend && yarn install && yarn build`, then
serve `frontend/build` through the host's web server. Configure the web server
to proxy `/api` to the FastAPI process, or set `REACT_APP_BACKEND_URL` before
building when frontend and backend use different domains.

## Replit preview

The `HYPEBLOCK Preview` workflow starts the FastAPI backend and React
development server. Open the Replit Preview to view the app.