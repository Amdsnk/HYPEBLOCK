# HYPEBLOCK — Graffiti Gremlins (PRD)

## Original Problem Statement
Koleksi 200 PFP maskot "graffiti gremlin" original (Bold, edgy, streetwear, spray-paint neon). Format PFP + trait + rarity, maskot 100% original. Situs showcase (React + FastAPI + MongoDB) + listing di Rarible (Polygon, ERC-721 Single, lazy mint). Rarity 4 tier. Waitlist email capture + admin.

## User Choices
- Generate art untuk gremlin (AI) — semua 200 dipetakan ke library art original.
- Generate 200 metadata otomatis dengan distribusi rarity persis (Common 120 / Rare 50 / Epic 24 / Legendary 6).
- Waitlist disimpan di MongoDB + halaman admin lihat daftar.
- Creator wallet: 0x0d7704E370b21DB2Ae66CF6b599b71B819E1BA9c (Polygon, ERC-721 Single, lazy mint).

## Architecture
- Backend: FastAPI + MongoDB (Motor). Deterministic collection generator (seed=42) auto-seeds 200 NFTs on startup (idempotent). Endpoints: /api/stats, /api/nfts (filter/search/sort/paginate), /api/nfts/{token_id}, /api/traits, /api/waitlist (POST), /api/waitlist/count, /api/admin/waitlist (GET/POST contacted/DELETE, static key).
- Frontend: React (react-router, framer-motion, sonner, shadcn/ui, tailwind). Pages: Home, Gallery (/gremlins), NftDetail (/gremlin/:id), Admin (/admin). Dark neon street-art theme.
- Art: 20 original AI-generated graffiti-gremlin artworks (Gemini nano-banana), mapped to 200 items by skin + tier + gender.

## Implemented (2026-06)
- 200-item collection with exact rarity distribution, rarity score + rank, per-trait rarity %, prices per tier.
- Hero + stats ticker, Top Gremlins ranking, rarity tiers, roadmap, FAQ, waitlist form.
- Gallery: tier + 8 trait-category filters, search (id/name), 6 sort modes, pagination, mobile filter drawer.
- NFT detail: image, tier/rank/score/price, trait matrix w/ rarity %, contract info, prev/next, Rarible buy link.
- Admin waitlist: static-key gate (hypeblock2026), search, CSV export, mark contacted, delete.

## Updated (2026-09) — founding-spec alignment
- Recreated missing backend/.env & frontend/.env (services were down); app live again.
- Website copy fully in ENGLISH (Home, Gallery, Admin, WaitlistForm, NftCard/Detail).
- Restored ORIGINAL trait scheme (Skin/Eyes/Headwear/Mouth/Outfit/Background/Accessory/Gender).
- 5 tiers now: Common120/Rare50/Epic24/Legendary5/Mythic1 (=200). Added a 1-of-1 "Mythic" Genesis King (price 0 = auction), forced rarity rank #1.
- Integrated the 5 supplied base renders; Mythic uses the gold-cap HYPEBLOCK hero render. All 200 released (RELEASED_BATCHES=10). COLLECTION_VERSION v4.
- Mint Kit: /api/metadata/export (200-item OpenSea/Rarible JSON) + one-click "Mint Kit JSON" download in Admin. Saved copy at /app/hypeblock-metadata.json.
- Rarible link now points to creator wallet profile.
- Added /app/HYPEBLOCK_PLAN.md — full architecture + Rarible/OpenSea listing steps + go-to-market plan.
- Backend retested: 31/31 pass.

## Updated (2026-09) — round 4: rebuilt from user-uploaded art
- Collection REBUILT from the user's HYPEBLOCK.zip: 96 UNIQUE renders (6 exact dups removed). Each token serves its own uploaded image via /api/render/{id}. No duplicates.
- Traits classified per-image with vision (8 labeled grids). collection_data.json drives seeding; generate_collection loads it (no procedural art).
- Dynamic COLLECTION_SIZE=96 (v6). Tiers Common50/Rare24/Epic13/Legendary6/Mythic3. Mythic 3 crown-jewel 1-of-1s (auction).
- Removed drip/"coming soon": everything released, no countdown.
- Added Trait Lab (/trait-lab) + POST /api/trait-lab/estimate for live rarity estimates.
- Added image render endpoints (/api/render/{id}, /api/render-status). Frontend copy updated 200 -> 96 (COLLECTION_TOTAL).
- Backend retested: 87/87 pass. Mint Kit metadata (96) at /app/hypeblock-metadata.json.

## Notes / Mocked (current)
- Social links (X/IG/Discord) in `src/config.js` are PLACEHOLDERS; Rarible link = creator wallet profile until the collection URL exists.
- Images served from backend disk (/app/backend/generated). For on-chain listing, pin them + metadata to IPFS.
- Admin is a static-key gate (key hypeblock2026).

## Updated (2026-06) — round 5: MERGED to 296 (restore 200 + keep 96)
- FIX of prior mistake: previous round replaced the 200 procedural NFTs with only the 96 uploaded ones. User demanded both be combined (ADD, not replace).
- New source of truth: backend/merged_collection.json = 296 items = 96 uploaded (real art) + 200 procedural (from token_meta.json). RANDOM token numbering (shuffle seed=4207, token_id 1..296).
- Restored 35 previously-generated procedural PNG renders from git commit 1b1d0f8 (they had been deleted). User asked to RESTORE previous images, not regenerate — no AI generation run.
- Images: 131 tokens have real art via /api/render/{id} (96 uploaded jpeg + 35 restored png); remaining 165 procedural use fallback hosted library images baked into item.image. build_merged.py rearranges generated/ files to {new_token_id}.ext.
- generate_collection() rewritten to load merged_collection.json; image=/api/render/{tid} when has_render else _fallback_image(). COLLECTION_VERSION v7, COLLECTION_SIZE=296.
- Tiers now Common170/Rare74/Epic37/Legendary12/Mythic3 (=296). 3 Mythic 1-of-1s forced to top ranks.
- Frontend copy 96 -> 296 (config COLLECTION_TOTAL, Home stats/FAQ/ticker/tiers, Footer, Gallery sort labels).
- Retested: backend 25/25 pass, frontend 100% (0 broken images, Mythic filter=3, detail #1 & #296 OK, Trait Lab live, Admin login OK).

## Backlog
- P1: Generate full 200 unique gremlin renders (batch, one per token).
- P1: Interactive "Trait Lab" remix previewer with live rarity estimate.
- P2: Real IPFS pinning + on-chain metadata export JSON download.
- P2: Drip-release scheduler / "coming soon" locked states per batch.
