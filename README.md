# HYPEBLOCK

Grim Genesis character universe: React gallery, rarity explorer, trait lab, lore, perks, waitlist and private artwork studio. Character tiers, levels and token IDs are preserved. Single-eye traits are replaced with two-eye Neon Gaze under the creator’s October 3 art direction.

## Website

Production URL: https://hypeblock-production.up.railway.app

Admin URL: https://hypeblock-production.up.railway.app/admin

The administrator key is the private `ADMIN_KEY` variable in the HYPEBLOCK Railway service. Open Railway Variables to reveal it; do not put it into source code or a frontend environment variable.

## Deployment

Use Railway with the root Dockerfile, one replica and a `/data` volume. React and FastAPI share one origin. See [deployment instructions](deploy/RAILWAY.md). No MongoDB or Emergent subscription is required for the running website.

## Artwork and release

296 token identities and unique core trait combinations. 132 image files are candidates for review; 164 token records still use concept previews. Final approved status requires a human check of each image against its traits. The website is a showcase and preparation tool; it does not contain a deployed mint contract or a verified marketplace collection.

In `/admin`, upload final artwork, review traits, approve it and select approved characters for release. Download the selected images, pin the image folder to IPFS, enter its real CID, then export the final metadata and hash manifest. Replacing artwork invalidates its approval. Exact duplicate uploads and unapproved release exports are rejected.

Audit details: [collection audit](backend/collection_audit.json), [Genesis manifest](COLLECTION_MANIFEST.md), [current plan](HYPEBLOCK_PLAN.md).

## Local development

```bash
python -m venv .venv
.venv/bin/pip install -r backend/requirements-hosting.txt
ADMIN_KEY=your-private-key .venv/bin/uvicorn backend.server:app --host 0.0.0.0 --port 8000
```

In another terminal:

```bash
cd frontend
npm ci --legacy-peer-deps --ignore-scripts
npm start
```

For production, run `npm run build` in `frontend` before starting FastAPI. The server automatically serves the production build, including SPA routes.

## Verification

```bash
.venv/bin/pip install -r backend/requirements-test.txt
PYTHONPATH=. ADMIN_KEY=your-private-key .venv/bin/pytest backend/tests -q
python backend/audit_collection.py
```

The API tests use `http://127.0.0.1:8000` by default; use `REACT_APP_BACKEND_URL` for a separate test deployment. Use a temporary data file when testing mutable endpoints. Artwork tests use an isolated temporary store and do not approve production assets.

## Artwork direction — October 3, 2026

Exactly two eyes; single-eye, forehead-eye and winking legacy artwork is excluded. Cyclops metadata is replaced by Neon Gaze for ten records. HYPEBLOCK lettering, branded chain pendants where chains are present, clothing labels and detailed graffiti/materials are required in new prompts. Six artwork candidates (3, 135, 155, 178, 196, 197) were replaced. Token 197 now lists Diamond Chain to match the requested branded jewelry. Approval additionally confirms this art direction, and older approvals require review again. Retired image hashes cannot be served from persistent overrides or re-uploaded.

Verification: production frontend build, 26 API integration tests, 5 artwork/art-direction tests, 296 unique trait combinations and no exact duplicate images. There are still 164 concept previews; these are not final NFT artwork.
