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

For cPanel/Passenger hosting, use `backend/passenger_wsgi.py` as the startup
file and install the smaller runtime dependency set from
`backend/requirements-hosting.txt`. The complete cPanel walkthrough is in
`deploy/traditional-hosting/README.md`.

### Admin on traditional hosting

The admin page is already included in the frontend at `/admin`. The included
`frontend/public/.htaccess` keeps that route working after a browser refresh on
Apache/cPanel hosting. For Nginx, use `try_files $uri /index.html` for the
frontend site instead.

Copy `backend/.env.example` to `backend/.env` on the server and set a private
`ADMIN_KEY`, `APP_URL`, and `CORS_ORIGINS`. If the API is on a separate
subdomain, copy `frontend/.env.example` to `frontend/.env`, set
`REACT_APP_BACKEND_URL` to the API URL, and rebuild the frontend. Then open:

```text
https://your-frontend-domain.com/admin
```

There is no username; the page uses the `ADMIN_KEY` value. Never commit the
real `.env` files or expose the admin key in frontend code.

## Replit preview

The `HYPEBLOCK Preview` workflow starts the FastAPI backend and React
development server. Open the Replit Preview to view the app.