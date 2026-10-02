# Deploy HYPEBLOCK on Railway

The simplest deployment uses one service for React and FastAPI. MongoDB is not required.

1. Railway → New Project → Deploy from GitHub repo → `Amdsnk/HYPEBLOCK`.
2. Leave the root directory at the repository root. Railway uses the included Dockerfile.
3. Attach a volume to the application service, mounted at `/data`.
4. Add variables:
   - `HYPEBLOCK_DATA_FILE=/data/store.json`
   - `HYPEBLOCK_ARTWORK_DIR=/data/artwork`
   - `ADMIN_KEY`: a private random password of at least 32 characters.
5. Networking → Generate Domain. Open the generated address.
6. Set `APP_URL` and `CORS_ORIGINS` to that exact HTTPS address, without a trailing slash. Redeploy.
7. Open `/admin` and enter your ADMIN_KEY. The key is sent in a header, never a URL.

The gallery, API, waitlist, admin, exports and artwork share one URL. Keep one replica and one Uvicorn worker: JSON storage is designed for a single application process. Back up `/data/store.json`; the volume preserves data across deployment but is not a backup.

Vercel can host the React frontend, but this file-backed backend needs a separate persistent service or a database/storage redesign. For this project, using Railway alone requires fewer services and settings.

## Release status

296 unique token identities and core trait combinations; 131 token image files and 165 fallback previews at the current audit. No exact duplicate files in `backend/generated`. These counts do not prove visual originality or agreement with traits. Final art review, missing original artwork, immutable IPFS metadata and real marketplace/contract configuration remain necessary before a mint launch. Deploying this website does not mint NFTs.

## Artwork review

Use `/admin` → Genesis Artwork Studio to upload final art, inspect the actual image against all eight traits, and approve it. Checked-in art starts as candidate; absence of an image is placeholder. Uploading replacement artwork automatically removes its approval. Exact duplicate uploads are rejected. Approved release exports include selected images, per-token JSON with IPFS image URIs, and SHA-256 provenance. Verify the actual image folder CID before publishing the metadata folder.

The production deployment is `https://hypeblock-production.up.railway.app`. Its administrator key is the private ADMIN_KEY variable in the HYPEBLOCK Railway service; reveal it in Railway Variables and enter it at `/admin`.
